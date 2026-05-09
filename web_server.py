"""
FastAPI web server for Four-in-a-Row game
Lightweight server with WebSocket support for AI progress updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict
from threat_detector import detect_must_block_moves
from collections import defaultdict
import uuid
import json
import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import threading

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress
from rust_ai_wrapper import compute_move_rust, is_rust_ai_available

# Import Rust Python extension for Vercel deployment (fastest, smallest)
try:
    from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move
    RUST_EXTENSION_AVAILABLE = True
    print("✓ Rust Python extension successfully imported")
except ImportError as e:
    RUST_EXTENSION_AVAILABLE = False
    rust_get_best_move = None
    print(f"⚠️ Rust extension import failed: {e}")
except Exception as e:
    RUST_EXTENSION_AVAILABLE = False
    rust_get_best_move = None
    print(f"⚠️ Rust extension error: {e}")

# Numba removed - Rust Python extension is faster and 1000x smaller

# Game session storage
# Use Vercel Blob for serverless persistence
import json
import os
import io

# Make vercel_blob optional for local/test environments
try:
    from vercel_blob import put, list as blob_list, delete as blob_delete, download_file
    BLOB_AVAILABLE = True
    print("✓ Blob storage available")
except ImportError:
    BLOB_AVAILABLE = False
    print("⚠️ vercel_blob not installed - blob persistence disabled")

# In-memory mapping of game_id to blob URL
game_urls: Dict[str, str] = {}

def serialize_game(game_data: dict) -> bytes:
    """Serialize game data to JSON (avoiding pickle lambda issues)"""
    # Convert Board and other non-JSON objects to serializable format
    serializable = {
        'board': game_data['board'].board if hasattr(game_data['board'], 'board') else game_data['board'],
        'cols': game_data['board'].cols if hasattr(game_data['board'], 'cols') else 7,
        'rows': game_data['board'].rows if hasattr(game_data['board'], 'rows') else 6,
        'max_hight': dict(game_data['board'].max_hight) if hasattr(game_data['board'], 'max_hight') else {},
        'search_depth': game_data['search_depth'],
        'current_player': game_data['current_player'],
        'number_of_play': game_data['number_of_play'],
        'last_column': game_data['last_column'],
        'game_over': game_data['game_over'],
        'winner': game_data['winner'],
        'move_history': game_data['move_history'],
    }
    return json.dumps(serializable).encode('utf-8')

def deserialize_game(data: bytes) -> dict:
    """Deserialize game data from JSON and reconstruct objects"""
    serialized = json.loads(data.decode('utf-8'))

    # Reconstruct Board object
    board = Board(serialized['cols'], serialized['rows'])
    board.board = serialized['board']
    board.max_hight = defaultdict(lambda: serialized['rows']-1, serialized['max_hight'])

    return {
        'board': board,
        'ai_engine': None,  # Will be set when accessed
        'search_depth': serialized['search_depth'],
        'current_player': serialized['current_player'],
        'number_of_play': serialized['number_of_play'],
        'last_column': serialized['last_column'],
        'game_over': serialized['game_over'],
        'winner': serialized['winner'],
        'move_history': serialized['move_history'],
        'tree_depth': 8,  # Default value
    }

def load_game(game_id: str) -> dict:
    """Load game from Vercel Blob"""
    if not BLOB_AVAILABLE:
        return None
    try:
        print(f"📥 Loading game {game_id} from blob...")

        # Public blob - no token needed
        options = {}

        # Check if we have the URL cached
        if game_id in game_urls:
            blob_url = game_urls[game_id]
            print(f"✓ Found cached URL for game {game_id}")
        else:
            # Search for the blob
            print(f"🔍 Searching for game {game_id} in blob...")
            # Public blob - no token needed
            list_options = {"prefix": f"games/{game_id}"}
            response = blob_list(list_options)
            if response and 'blobs' in response and len(response['blobs']) > 0:
                blob_url = response['blobs'][0]['url']
                game_urls[game_id] = blob_url
                print(f"✓ Found game {game_id} in blob")
            else:
                print(f"⚠️  Game {game_id} not found in blob")
                return None

        # Download and deserialize
        data = download_file(blob_url, options=options)
        game_data = deserialize_game(data)
        print(f"✓ Loaded game {game_id} from blob")
        return game_data
    except Exception as e:
        print(f"❌ Failed to load game {game_id}: {e}")
        import traceback
        traceback.print_exc()
    return None

def save_game(game_id: str, game_data: dict):
    """Save game to Vercel Blob"""
    if not BLOB_AVAILABLE:
        print("⚠️ Blob not available - game state not persisted")
        return
    try:
        blob_path = f"games/{game_id}.json"
        serialized_data = serialize_game(game_data)

        print(f"💾 Saving game {game_id} to blob (size: {len(serialized_data)} bytes)...")

        # Upload and store the URL with token for private blob access
        token = os.getenv('BLOB_READ_WRITE_TOKEN')
        print(f"🔑 Token present: {bool(token)}, starts with: {token[:15] if token else 'N/A'}...")

        options = {
            "allowOverwrite": "true"
            # Public blob - no access or token needed
        }

        print(f"📤 Calling put() with options keys: {list(options.keys())}")
        response = put(blob_path, serialized_data, options=options)

        if response and 'url' in response:
            game_urls[game_id] = response['url']
            print(f"✓ Game {game_id} saved to blob: {response['url']}")
        else:
            print(f"⚠️  Unexpected response from blob put: {response}")
    except Exception as e:
        print(f"❌ Failed to save game {game_id}: {e}")
        import traceback
        traceback.print_exc()

def delete_game(game_id: str):
    """Delete game from Vercel Blob"""
    try:
        if game_id in game_urls:
            # Public blob - no token needed
            blob_delete(game_urls[game_id])
            del game_urls[game_id]
    except Exception as e:
        print(f"Failed to delete game {game_id}: {e}")

# Keep in-memory cache for performance
games: Dict[str, dict] = {}

# Opening book - loaded on startup (static initial positions)
opening_book = None

# Dynamic tree cache - extends during gameplay (per-game)
# Format: {game_id: {board_hash: [score, best_move]}}
dynamic_cache: Dict[str, Dict[str, list]] = {}

# Separate thread pool for tree extension (doesn't block main requests)
tree_extension_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tree_ext")


class ProgressCallback:
    """Callback to capture AI progress and send via WebSocket"""
    def __init__(self, websocket: Optional[WebSocket] = None):
        self.websocket = websocket
        self.last_update = 0

    async def update(self, message: str):
        """Send progress update via WebSocket"""
        if self.websocket:
            try:
                await self.websocket.send_json({"type": "progress", "message": message})
            except:
                pass  # WebSocket might be closed


def extend_tree_branch_sync(game_id: str):
    """
    Synchronous version of tree extension for use in separate thread.
    Extend the current game branch to maintain deep lookahead.
    Computes the NEXT AI move position at search_depth.
    """
    if game_id not in games:
        return

    game = games[game_id]
    board = game['board']
    ai_engine = game['ai_engine']
    target_depth = game['search_depth']  # Match AI search depth (10)

    # Calculate how many moves have been played
    moves_played = len(game['move_history'])

    print(f"🔄 Extending tree for game {game_id[:8]}... (moves played: {moves_played})")

    # Generate positions along ALL possible branches up to target_depth
    from collections import deque
    queue = deque()
    queue.append((Board(board), game['current_player'], game['number_of_play'], game['last_column'], 0))

    positions_to_compute = []
    visited = set()

    while queue:
        pos_board, player, num_play, last_col, depth = queue.popleft()

        if depth >= target_depth:
            continue

        board_hash = str(pos_board.to_hash())

        # Skip if already cached
        if board_hash in visited:
            continue
        if opening_book and board_hash in opening_book:
            visited.add(board_hash)
            continue
        if game_id in dynamic_cache and board_hash in dynamic_cache[game_id]:
            visited.add(board_hash)
            continue

        visited.add(board_hash)

        # Only compute positions where it's AI's turn
        if player == 'O':
            positions_to_compute.append((Board(pos_board), player, num_play, last_col))

        # Generate next positions
        for col, _ in pos_board.possible_moves():
            next_board = Board(pos_board)
            next_board.play_move(col, player)

            if next_board.is_winner(player, 4) or next_board.is_end_of_game():
                continue

            is_first = depth == 0 and moves_played == 0
            next_player = ai_engine.next_player(player, num_play, first_play=is_first)
            next_num = ai_engine.next_number_of_play(num_play, first_play=is_first)

            queue.append((next_board, next_player, next_num, col, depth + 1))

    # Compute evaluations for new AI positions
    if positions_to_compute:
        # Limit computation to avoid overwhelming - only compute immediate next moves
        max_positions = 5  # Compute up to 5 positions per extension (much faster!)
        positions_to_compute = positions_to_compute[:max_positions]

        print(f"  Computing {len(positions_to_compute)} AI positions...")

        for pos_board, player, num_play, last_col in positions_to_compute:
            try:
                # Use Rust AI if available (10-50x faster!)
                if RUST_EXTENSION_AVAILABLE:
                    # Use Rust Python extension
                    board_str = '\n'.join(''.join(row) for row in pos_board.board)
                    player_num = 1 if player == 'X' else 2
                    eval_score, best_move = rust_get_best_move(
                        board_str,
                        target_depth,
                        player_num,
                        num_play
                    )
                elif is_rust_ai_available():
                    # Use Rust binary (local only)
                    eval_score, best_move = compute_move_rust(
                        pos_board,
                        target_depth,
                        player,
                        num_play
                    )
                else:
                    # Fallback to Python AI
                    eval_score, best_move = ai_engine.minimax_alpha_beta(
                        pos_board,
                        target_depth,
                        -float('inf'),
                        float('inf'),
                        player,
                        num_play,
                        last_col,
                        False
                    )

                # Store in dynamic cache
                board_hash = str(pos_board.to_hash())
                dynamic_cache[game_id][board_hash] = [eval_score, best_move]
            except Exception as e:
                print(f"  ⚠️  Error computing position: {e}")

        print(f"  ✓ Extended tree: +{len(positions_to_compute)} positions cached")
    else:
        print(f"  ✓ Tree already complete")


async def extend_tree_branch(game_id: str):
    """
    Extend the current game branch to maintain deep lookahead.
    Computes the NEXT AI move position at search_depth.
    Runs in background after each move.
    """
    if game_id not in games:
        return

    game = games[game_id]
    board = game['board']
    ai_engine = game['ai_engine']
    target_depth = game['search_depth']  # Match AI search depth (10)

    # Calculate how many moves have been played
    moves_played = len(game['move_history'])

    print(f"🔄 Extending tree for game {game_id[:8]}... (moves played: {moves_played})")

    loop = asyncio.get_event_loop()

    # Generate positions along ALL possible branches up to target_depth
    # This way when player moves, we'll have ALL responses pre-computed
    from collections import deque
    queue = deque()
    queue.append((Board(board), game['current_player'], game['number_of_play'], game['last_column'], 0))

    positions_to_compute = []
    visited = set()

    while queue:
        pos_board, player, num_play, last_col, depth = queue.popleft()

        if depth >= target_depth:
            continue

        board_hash = str(pos_board.to_hash())

        # Skip if already cached
        if board_hash in visited:
            continue
        if opening_book and board_hash in opening_book:
            visited.add(board_hash)
            continue
        if game_id in dynamic_cache and board_hash in dynamic_cache[game_id]:
            visited.add(board_hash)
            continue

        visited.add(board_hash)

        # Only compute positions where it's AI's turn
        if player == 'O':
            positions_to_compute.append((Board(pos_board), player, num_play, last_col))

        # Generate next positions
        for col, _ in pos_board.possible_moves():
            next_board = Board(pos_board)
            next_board.play_move(col, player)

            if next_board.is_winner(player, 4) or next_board.is_end_of_game():
                continue

            is_first = depth == 0 and moves_played == 0
            next_player = ai_engine.next_player(player, num_play, first_play=is_first)
            next_num = ai_engine.next_number_of_play(num_play, first_play=is_first)

            queue.append((next_board, next_player, next_num, col, depth + 1))

    # Compute evaluations for new AI positions (in parallel would be better, but sequential for now)
    if positions_to_compute:
        # Limit computation to avoid overwhelming - only compute immediate next moves
        max_positions = 5  # Compute up to 5 positions per extension (much faster!)
        positions_to_compute = positions_to_compute[:max_positions]

        print(f"  Computing {len(positions_to_compute)} AI positions...")

        for pos_board, player, num_play, last_col in positions_to_compute:
            try:
                # Run minimax evaluation
                eval_score, best_move = await loop.run_in_executor(
                    None,
                    ai_engine.minimax_alpha_beta,
                    pos_board,
                    target_depth,
                    -float('inf'),
                    float('inf'),
                    player,
                    num_play,
                    last_col,
                    False
                )

                # Store in dynamic cache
                board_hash = str(pos_board.to_hash())
                dynamic_cache[game_id][board_hash] = [eval_score, best_move]
            except Exception as e:
                print(f"  ⚠️  Error computing position: {e}")

        print(f"  ✓ Extended tree: +{len(positions_to_compute)} positions cached")
    else:
        print(f"  ✓ Tree already complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load opening book on startup"""
    import os
    global opening_book

    # Check Vercel Blob configuration (handle both correct and duplicated env var names)
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN') or os.getenv('BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN')
    if blob_token:
        # Set the correct env var name if using the duplicated one
        if not os.getenv('BLOB_READ_WRITE_TOKEN'):
            os.environ['BLOB_READ_WRITE_TOKEN'] = blob_token
        print(f"✓ Vercel Blob configured (token: {blob_token[:10]}...)")
    else:
        print("⚠️  Vercel Blob NOT configured - games won't persist across instances!")

    # Always skip opening book in test mode - we're not using it anyway
    # (opening book disabled in favor of depth-12 Rust AI)
    opening_book = {}

    # Check if we're in test/CI mode
    is_test_mode = os.getenv('PYTEST_CURRENT_TEST') or os.getenv('CI') or os.getenv('GITHUB_ACTIONS')

    if is_test_mode:
        print("⚠ Test/CI mode: Fast startup, skipping heavy initialization")
    else:
        # In production, we can optionally load opening book (currently disabled)
        print("⚠ Opening book disabled - using depth-12 Rust AI for all moves")

    # Check which AI engines are available
    if RUST_EXTENSION_AVAILABLE:
        print("✓ Rust Python extension available - depth 12 FAST mode enabled!")
    elif is_rust_ai_available():
        print("✓ Rust AI binary available (local only)")
    else:
        print("⚠ No Rust AI available - will use Python fallback (slower)")

    # Clean up old games on startup (only in production, not test mode)
    if BLOB_AVAILABLE and not is_test_mode:
        try:
            from datetime import datetime, timedelta
            response = blob_list({"prefix": "games/"})
            if response and 'blobs' in response:
                cutoff_time = datetime.now() - timedelta(hours=24)
                deleted_count = 0
                for blob in response['blobs']:
                    try:
                        uploaded_at = datetime.fromisoformat(blob['uploadedAt'].replace('Z', '+00:00'))
                        if uploaded_at < cutoff_time:
                            blob_delete(blob['url'])
                            deleted_count += 1
                    except Exception as e:
                        print(f"Failed to delete old game: {e}")
                if deleted_count > 0:
                    print(f"🗑️ Cleaned up {deleted_count} old games (>24h)")
        except Exception as e:
            print(f"Startup cleanup failed: {e}")

    yield

    # Cleanup
    print("🧹 Cleaning up on shutdown...")
    games.clear()
    game_urls.clear()  # Clear blob URL cache
    dynamic_cache.clear()
    print("✓ In-memory caches cleared")

    # Shutdown thread pool executor gracefully
    try:
        tree_extension_executor.shutdown(wait=False, cancel_futures=True)
        print("✓ Thread pool executor shut down")
    except Exception:
        pass  # Ignore shutdown errors in test mode


app = FastAPI(title="Four-in-a-Row", lifespan=lifespan)


# Models
class NewGameRequest(BaseModel):
    player_starts: bool = True  # True if human starts, False if AI starts


class MoveRequest(BaseModel):
    column: int


class GameState(BaseModel):
    game_id: str
    board: list  # 2D array
    current_player: str  # 'X' or 'O'
    game_over: bool
    winner: Optional[str]
    valid_moves: list
    last_move: Optional[int]


# API Endpoints
@app.post("/api/game/new", response_model=GameState)
async def new_game(request: NewGameRequest):
    """Create a new game"""
    game_id = str(uuid.uuid4())

    board = Board(7, 6)

    # Adjust AI engine and depth based on environment
    import os
    if os.getenv('VERCEL_DEPLOYMENT') or os.getenv('DISABLE_RUST_AI'):
        # Vercel: Priority order - Rust extension > Python fallback
        if RUST_EXTENSION_AVAILABLE:
            # Rust Python extension: fastest + smallest (~170KB)
            ai_engine = None  # Will use rust_get_best_move directly
            search_depth = 12  # Rust at depth 12 (depth 14 might timeout on Vercel)
            print("✓ Vercel mode: Using Rust Python extension at depth 12 (FAST!)")
        else:
            # Fallback: Python AI at depth 9
            ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                             consec_moves=2, show_progress=False)
            search_depth = 9  # Good balance: stronger than 6, faster than 10
            print("⚠️  Vercel mode: Using Python AI at depth 9 (~10-20s per move)")
    elif os.getenv('PYTEST_CURRENT_TEST') or os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        # Test/CI: Very low depth for speed
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                         consec_moves=2, show_progress=False)
        search_depth = 4
        print("⚠️  Test/CI mode: Using depth 4 for speed")
    else:
        # Local: Standard AI
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                         consec_moves=2, show_progress=False)
        search_depth = 14  # Local: Rust AI can handle depth 14!

    # Human is always 'X', AI is always 'O'
    current_player = 'X' if request.player_starts else 'O'

    games[game_id] = {
        'board': board,
        'ai_engine': ai_engine,
        'search_depth': search_depth,
        'current_player': current_player,
        'number_of_play': 1,  # First move is always 1 coin, then 2 per turn
        'last_column': None,
        'game_over': False,
        'winner': None,
        'move_history': [],
        'tree_depth': 8  # Always maintain 8 moves lookahead
    }

    # Initialize dynamic cache for this game
    dynamic_cache[game_id] = {}

    # Save game to disk for serverless persistence
    save_game(game_id, games[game_id])

    return GameState(
        game_id=game_id,
        board=board.board,
        current_player=current_player,
        game_over=False,
        winner=None,
        valid_moves=[col for col, _ in board.possible_moves()],
        last_move=None
    )


@app.post("/api/game/{game_id}/move", response_model=GameState)
async def make_move(game_id: str, move: MoveRequest):
    """Make a move (human only, use WebSocket for AI moves)"""
    # Load from disk if not in memory
    if game_id not in games:
        game_data = load_game(game_id)
        if game_data:
            games[game_id] = game_data
        else:
            raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    if game['game_over']:
        raise HTTPException(status_code=400, detail="Game is over")

    if game['current_player'] != 'X':
        raise HTTPException(status_code=400, detail="Not player's turn")

    board = game['board']

    if not board.is_possible_move(move.column):
        raise HTTPException(status_code=400, detail="Invalid move")

    # Check if this is the first move BEFORE adding to history
    is_first_move = len(game['move_history']) == 0

    # Make the move
    board.play_move(move.column, 'X')
    game['move_history'].append(('X', move.column))
    game['last_column'] = move.column

    # Check if player won
    if board.is_winner('X', 4):
        game['game_over'] = True
        game['winner'] = 'X'
    elif board.is_end_of_game():
        game['game_over'] = True
        game['winner'] = None  # Draw
    else:
        # Update player turn based on consecutive moves rule
        ai_engine = game['ai_engine']

        if ai_engine:
            # Determine next player and number of plays
            next_player = ai_engine.next_player('X', game['number_of_play'], first_play=is_first_move)
            next_number = ai_engine.next_number_of_play(game['number_of_play'], first_play=is_first_move)
        else:
            # Manual logic when using Rust extension (no ai_engine object)
            if game['number_of_play'] == 1:
                next_player = 'O'
                next_number = 2
            else:
                next_player = 'X'
                next_number = game['number_of_play'] - 1

        game['current_player'] = next_player
        game['number_of_play'] = next_number

    # Save game state to disk
    save_game(game_id, game)

    # Return immediately - don't block on tree extension
    result = GameState(
        game_id=game_id,
        board=board.board,
        current_player=game['current_player'],
        game_over=game['game_over'],
        winner=game['winner'],
        valid_moves=[col for col, _ in board.possible_moves()] if not game['game_over'] else [],
        last_move=move.column
    )

    # Trigger tree extension ONLY when player completes their turn (AI's turn next)
    # This happens in separate thread so it doesn't block
    if not game['game_over'] and result.current_player == 'O':
        print(f"🔄 Triggering tree extension (player completed turn)")
        tree_extension_executor.submit(extend_tree_branch_sync, game_id)

    return result


@app.get("/api/game/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: str):
    """Get current game state"""
    # Load from disk if not in memory
    if game_id not in games:
        game_data = load_game(game_id)
        if game_data:
            games[game_id] = game_data
        else:
            raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]
    board = game['board']

    return GameState(
        game_id=game_id,
        board=board.board,
        current_player=game['current_player'],
        game_over=game['game_over'],
        winner=game['winner'],
        valid_moves=[col for col, _ in board.possible_moves()] if not game['game_over'] else [],
        last_move=game.get('last_column')
    )


@app.post("/api/game/{game_id}/ai-move", response_model=GameState)
async def make_ai_move(game_id: str):
    """Make AI move (REST endpoint, no WebSocket)"""
    # Load from disk if not in memory
    if game_id not in games:
        game_data = load_game(game_id)
        if game_data:
            games[game_id] = game_data
        else:
            raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    if game['game_over']:
        raise HTTPException(status_code=400, detail="Game is over")

    if game['current_player'] != 'O':
        raise HTTPException(status_code=400, detail="Not AI's turn")

    # Check caches (dynamic cache → compute)
    # NOTE: Opening book disabled - using depth 12 for stronger play
    board = game['board']
    board_hash = str(board.to_hash())
    best_column = None
    cache_hit = False

    # PRIORITY 0: Check for immediate win/block threats (bypasses cache!)
    # Only check if game is somewhat advanced (at least 6 pieces on board)
    total_pieces = sum(1 for row in board.board for cell in row if cell != ' ')
    if total_pieces >= 6:
        try:
            # Enable 2-move detection to catch tactical sequences
            forced_type, forced_moves = detect_must_block_moves(board, 'O', consec_to_win=4, check_two_moves=True)
            if forced_type == 'win' and forced_moves:
                # We can win immediately!
                best_column = forced_moves[0]  # Just take first winning move
                print(f"  ⚡ IMMEDIATE WIN available! Playing column {best_column}")
            elif forced_type == 'block' and forced_moves:
                # Opponent can win next turn - MUST block!
                best_column = forced_moves[0]  # Take first blocking move
                print(f"  🛡️  BLOCKING opponent 1-move threat! Playing column {best_column}")
            elif forced_type == 'block_2move' and forced_moves:
                # Opponent can win in 2 moves - block their setup!
                best_column = forced_moves[0]  # Take first blocking move
                print(f"  🛡️  BLOCKING opponent 2-move threat! Playing column {best_column}")
        except Exception as e:
            print(f"  ⚠️  Threat detection error: {e}, falling back to normal search")

    # Priority 1: Check dynamic cache (if no forced move from threat detection)
    if best_column is None and game_id in dynamic_cache and board_hash in dynamic_cache[game_id]:
        cache_entry = dynamic_cache[game_id][board_hash]
        best_column = cache_entry[1] if isinstance(cache_entry, list) else cache_entry
        cache_hit = True
        print(f"  ✓ Dynamic cache hit")

    # Priority 2: Compute with Rust AI (if not set by threat detection or cache)
    if best_column is None:
        search_depth = game['search_depth']

        # Priority 1: Rust Python extension (Vercel-compatible, ~170KB)
        if RUST_EXTENSION_AVAILABLE:
            try:
                loop = asyncio.get_event_loop()
                # Convert board to string format for Rust extension
                board_str = '\n'.join(''.join(row) for row in board.board)
                player_num = 2  # 'O' = 2

                eval_score, best_column = await loop.run_in_executor(
                    None,
                    rust_get_best_move,
                    board_str,
                    search_depth,
                    player_num,
                    game['number_of_play']
                )
                print(f"  🚀 Rust extension (depth {search_depth}) - FAST! Column: {best_column}, Score: {eval_score}")
            except Exception as e:
                print(f"  ❌ Rust extension error: {e}")
                best_column = None
        # Priority 2: Standalone Rust AI binary (local only)
        elif is_rust_ai_available():
            loop = asyncio.get_event_loop()
            eval_score, best_column = await loop.run_in_executor(
                None,
                compute_move_rust,
                board,
                search_depth,
                'O',
                game['number_of_play']
            )
            print(f"  🚀 Rust AI binary (depth {search_depth}) - FAST!")
        # Priority 3: Python AI fallback
        else:
            ai_engine = game['ai_engine']
            loop = asyncio.get_event_loop()
            eval_score, best_column = await loop.run_in_executor(
                None,
                ai_engine.fixed_depth_search,
                board,
                search_depth,
                'O',
                game['number_of_play'],
                game['last_column']
            )
            print(f"  ⏱️  Python AI (depth {search_depth}) - slow")

    if best_column is None:
        print(f"  ❌ CRITICAL: best_column is None! Threat detection: total_pieces={total_pieces}, Cache hit: {cache_hit}")
        print(f"  Rust available: {RUST_EXTENSION_AVAILABLE}, Game engine: {game.get('ai_engine') is not None}")
        # Fallback: just pick any valid move
        valid_moves = [col for col, _ in board.possible_moves()]
        if valid_moves:
            best_column = valid_moves[len(valid_moves) // 2]  # Pick middle column
            print(f"  ⚠️  EMERGENCY FALLBACK: selecting middle valid column {best_column}")
        else:
            raise HTTPException(status_code=500, detail="No valid moves available (board full?)")

    # Check if this is the first move BEFORE adding to history
    is_first_move = len(game['move_history']) == 0

    # Make AI move
    board.play_move(best_column, 'O')
    game['move_history'].append(('O', best_column))
    game['last_column'] = best_column

    # Check if AI won
    if board.is_winner('O', 4):
        game['game_over'] = True
        game['winner'] = 'O'
    elif board.is_end_of_game():
        game['game_over'] = True
        game['winner'] = None
    else:
        # Update player turn based on consecutive moves rule
        ai_engine = game['ai_engine']
        if ai_engine:
            next_player = ai_engine.next_player('O', game['number_of_play'], first_play=is_first_move)
            next_number = ai_engine.next_number_of_play(game['number_of_play'], first_play=is_first_move)
        else:
            # Manual logic when using Rust extension (no ai_engine object)
            if game['number_of_play'] == 1:
                next_player = 'X'
                next_number = 2
            else:
                next_player = 'O'
                next_number = game['number_of_play'] - 1
        game['current_player'] = next_player
        game['number_of_play'] = next_number

    # Don't extend tree here - the player move endpoint will trigger it
    # after player completes their turn

    # Save game state to disk
    save_game(game_id, game)

    return GameState(
        game_id=game_id,
        board=board.board,
        current_player=game['current_player'],
        game_over=game['game_over'],
        winner=game['winner'],
        valid_moves=[col for col, _ in board.possible_moves()] if not game['game_over'] else [],
        last_move=best_column
    )


@app.delete("/api/game/{game_id}")
async def delete_game_endpoint(game_id: str):
    """Delete a game and clean up blob storage"""
    try:
        # Remove from memory
        if game_id in games:
            del games[game_id]

        # Remove from blob storage
        if BLOB_AVAILABLE:
            delete_game(game_id)

        # Remove from dynamic cache
        if game_id in dynamic_cache:
            del dynamic_cache[game_id]

        return {"status": "deleted", "game_id": game_id}
    except Exception as e:
        print(f"Error deleting game {game_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cleanup/old-games")
async def cleanup_old_games(max_age_hours: int = 24):
    """Delete games older than max_age_hours from blob storage"""
    if not BLOB_AVAILABLE:
        return {"status": "skipped", "reason": "blob storage not available"}

    try:
        from datetime import datetime, timedelta

        # List all game blobs
        response = blob_list({"prefix": "games/"})
        if not response or 'blobs' not in response:
            return {"status": "success", "deleted": 0}

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0

        for blob in response['blobs']:
            # Parse uploadedAt timestamp
            uploaded_at = datetime.fromisoformat(blob['uploadedAt'].replace('Z', '+00:00'))

            if uploaded_at < cutoff_time:
                try:
                    blob_delete(blob['url'])
                    deleted_count += 1
                    print(f"🗑️ Deleted old game: {blob['pathname']}")
                except Exception as e:
                    print(f"Failed to delete {blob['pathname']}: {e}")

        return {"status": "success", "deleted": deleted_count, "max_age_hours": max_age_hours}
    except Exception as e:
        print(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket for AI move computation with progress updates"""
    await websocket.accept()

    try:
        if game_id not in games:
            await websocket.send_json({"type": "error", "message": "Game not found"})
            await websocket.close()
            return

        game = games[game_id]

        while not game['game_over']:
            # Wait for trigger to compute AI move
            data = await websocket.receive_json()

            if data.get('action') == 'compute_ai_move':
                if game['current_player'] != 'O':
                    await websocket.send_json({"type": "error", "message": "Not AI's turn"})
                    continue

                if game['game_over']:
                    await websocket.send_json({"type": "error", "message": "Game is over"})
                    continue

                # Send thinking notification
                await websocket.send_json({"type": "thinking", "message": "AI is thinking..."})

                # Check opening book first
                board_hash = str(game['board'].to_hash())
                best_column = None

                if board_hash in opening_book:
                    # Opening book stores [score, column]
                    book_entry = opening_book[board_hash]
                    best_column = book_entry[1] if isinstance(book_entry, list) else book_entry
                    await websocket.send_json({
                        "type": "progress",
                        "message": "Using opening book"
                    })
                    await asyncio.sleep(0.5)  # Small delay for UX
                else:
                    # Compute AI move in background
                    search_depth = game['search_depth']
                    await websocket.send_json({
                        "type": "progress",
                        "message": f"Computing move at depth {search_depth}..."
                    })

                    # Run AI computation
                    ai_engine = game['ai_engine']
                    loop = asyncio.get_event_loop()

                    # Run in executor to avoid blocking
                    eval_score, best_column = await loop.run_in_executor(
                        None,
                        ai_engine.fixed_depth_search,
                        game['board'],
                        search_depth,
                        'O',
                        game['number_of_play'],
                        game['last_column']
                    )

                    # Send evaluation info
                    if abs(eval_score) >= 10000:
                        message = "Found forced win!" if eval_score > 0 else "Detected forced loss"
                        await websocket.send_json({"type": "progress", "message": message})

                if best_column is None:
                    await websocket.send_json({"type": "error", "message": "AI couldn't find a move"})
                    continue

                # Check if this is the first move BEFORE adding to history
                is_first_move = len(game['move_history']) == 0

                # Make AI move
                board = game['board']
                board.play_move(best_column, 'O')
                game['move_history'].append(('O', best_column))
                game['last_column'] = best_column

                # Check if AI won
                if board.is_winner('O', 4):
                    game['game_over'] = True
                    game['winner'] = 'O'
                elif board.is_end_of_game():
                    game['game_over'] = True
                    game['winner'] = None
                else:
                    # Update player turn based on consecutive moves rule
                    ai_engine = game['ai_engine']

                    # Determine next player and number of plays
                    next_player = ai_engine.next_player('O', game['number_of_play'], first_play=is_first_move)
                    next_number = ai_engine.next_number_of_play(game['number_of_play'], first_play=is_first_move)

                    game['current_player'] = next_player
                    game['number_of_play'] = next_number

                # Send move result
                await websocket.send_json({
                    "type": "move",
                    "column": best_column,
                    "board": board.board,
                    "current_player": game['current_player'],
                    "game_over": game['game_over'],
                    "winner": game['winner'],
                    "valid_moves": [col for col, _ in board.possible_moves()] if not game['game_over'] else []
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"WebSocket error: {error_msg}")
        try:
            await websocket.send_json({"type": "error", "message": error_msg})
        except:
            pass


# Serve static files and HTML
@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Serve test page"""
    return """<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
    <style>
        body { font-family: monospace; padding: 20px; }
        #log { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; background: #f5f5f5; }
        button { margin: 5px; padding: 10px; }
        .error { color: red; }
        .success { color: green; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1>Four-in-a-Row WebSocket Test</h1>
    <div>
        <button onclick="testAIStarts()">Test AI Starts Scenario</button>
        <button onclick="clearLog()">Clear Log</button>
    </div>
    <div id="log"></div>

    <script>
        function log(message, className = '') {
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.textContent = new Date().toISOString().substr(11, 12) + ' - ' + message;
            if (className) entry.className = className;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
            console.log(message);
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        async function testAIStarts() {
            clearLog();
            log('Starting test: AI goes first', 'info');

            try {
                // Step 1: Create game with AI starting
                log('Step 1: Creating game (AI starts)...', 'info');
                const response = await fetch('/api/game/new', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({player_starts: false})
                });
                const gameData = await response.json();
                const gameId = gameData.game_id;
                log('Game created: ' + gameId, 'success');
                log('Current player: ' + gameData.current_player, 'info');

                // Step 2: Connect WebSocket and trigger AI move
                log('Step 2: Connecting WebSocket...', 'info');
                const ws = new WebSocket('ws://' + window.location.host + '/ws/' + gameId);

                let moveCount = 0;

                ws.onopen = () => {
                    log('WebSocket connected!', 'success');
                    log('Sending compute_ai_move request...', 'info');
                    ws.send(JSON.stringify({action: 'compute_ai_move'}));
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    log('WS Message: type=' + data.type, 'info');

                    if (data.type === 'move') {
                        moveCount++;
                        log('AI Move #' + moveCount + ': column=' + data.column + ', next_player=' + data.current_player, 'success');

                        if (data.current_player === 'O') {
                            log('AI still has turn, sending another compute_ai_move...', 'info');
                            ws.send(JSON.stringify({action: 'compute_ai_move'}));
                        } else {
                            log('AI finished. Switched to player ' + data.current_player, 'success');

                            // Now player makes 2 moves
                            setTimeout(() => makePlayerMoves(gameId, ws), 1000);
                        }
                    } else if (data.type === 'progress') {
                        log('Progress: ' + data.message, 'info');
                    } else if (data.type === 'error') {
                        log('ERROR: ' + data.message, 'error');
                    }
                };

                ws.onerror = (error) => {
                    log('WebSocket error: ' + error, 'error');
                };

                ws.onclose = () => {
                    log('WebSocket closed', 'info');
                };

            } catch (error) {
                log('Exception: ' + error, 'error');
            }
        }

        async function makePlayerMoves(gameId, ws) {
            log('Step 3: Player makes 2 moves (column 3)...', 'info');

            // Move 1
            let response = await fetch('/api/game/' + gameId + '/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({column: 3})
            });
            let data = await response.json();
            log('Player move 1: next_player=' + data.current_player, 'success');

            // Move 2
            response = await fetch('/api/game/' + gameId + '/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({column: 3})
            });
            data = await response.json();
            log('Player move 2: next_player=' + data.current_player, 'success');

            if (data.current_player === 'O') {
                log('Step 4: Triggering AI moves again...', 'info');
                ws.send(JSON.stringify({action: 'compute_ai_move'}));
            } else {
                log('ERROR: Should be AI turn but got ' + data.current_player, 'error');
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the game UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Four in a Row</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            color: white;
        }

        h1 {
            margin: 20px 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .game-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }

        .status {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 20px;
            min-height: 40px;
            font-weight: bold;
        }

        .board {
            background: #2c5aa0;
            padding: 10px;
            border-radius: 10px;
            display: inline-block;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .row {
            display: flex;
        }

        .cell {
            width: 70px;
            height: 70px;
            margin: 5px;
            background: #1e3a5f;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }

        .cell:hover {
            background: #2a4a7f;
            transform: scale(1.05);
        }

        .cell.disabled {
            cursor: not-allowed;
            opacity: 0.5;
        }

        .cell.disabled:hover {
            transform: none;
            background: #1e3a5f;
        }

        .piece {
            width: 60px;
            height: 60px;
            border-radius: 50%;
        }

        .piece.X {
            background: radial-gradient(circle, #ff6b6b, #c92a2a);
            box-shadow: inset 0 -3px 10px rgba(0,0,0,0.3);
        }

        .piece.O {
            background: radial-gradient(circle, #ffd93d, #f5a623);
            box-shadow: inset 0 -3px 10px rgba(0,0,0,0.3);
        }

        .piece.new-piece {
            animation: drop 0.5s ease-out, blink 1.5s ease-in-out;
        }

        @keyframes drop {
            from {
                transform: translateY(-400px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            25% { opacity: 0.4; }
            50% { opacity: 1; }
            75% { opacity: 0.4; }
        }

        .controls {
            text-align: center;
            margin-top: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }

        button {
            background: white;
            color: #667eea;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        button.restart-btn {
            background: #ff6b6b;
            color: white;
        }

        button.restart-btn:hover {
            background: #ff5252;
        }

        /* Mobile Responsive */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            h1 {
                font-size: 1.8em;
                margin: 10px 0;
            }

            .game-container {
                padding: 15px;
            }

            .status {
                font-size: 1.2em;
                margin-bottom: 15px;
            }

            .board {
                padding: 5px;
            }

            .cell {
                width: 45px;
                height: 45px;
                margin: 3px;
            }

            .piece {
                width: 39px;
                height: 39px;
            }

            button {
                padding: 12px 20px;
                font-size: 0.95em;
            }

            .winner-banner {
                padding: 15px 20px;
                font-size: 1.2em;
            }
        }

        @media (max-width: 480px) {
            h1 {
                font-size: 1.5em;
            }

            .cell {
                width: 38px;
                height: 38px;
                margin: 2px;
            }

            .piece {
                width: 34px;
                height: 34px;
            }

            button {
                padding: 10px 15px;
                font-size: 0.9em;
            }

            .controls {
                gap: 5px;
            }
        }

        .progress {
            text-align: center;
            margin-top: 10px;
            min-height: 30px;
            font-style: italic;
            color: #ffd93d;
        }

        .winner-banner {
            background: rgba(255, 255, 255, 0.95);
            color: #667eea;
            padding: 20px 40px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <h1>🎮 Four in a Row</h1>

    <div class="game-container">
        <div class="status" id="status">Choose game mode to start</div>
        <div class="board" id="board"></div>
        <div class="progress" id="progress"></div>
        <div class="controls">
            <button id="btnPlayerStart">New Game (You Start)</button>
            <button id="btnAIStart">New Game (AI Starts)</button>
            <button id="btnRestart" class="restart-btn" style="display: none;">🔄 Restart Game</button>
        </div>
        <div id="winner-banner"></div>
    </div>

    <script>
        let gameId = null;
        let currentPlayer = null;
        let gameOver = false;
        let validMoves = [];
        let previousBoard = null;

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        function updateProgress(message) {
            document.getElementById('progress').textContent = message;
        }

        function renderBoard(board, isNewGame = false) {
            const boardEl = document.getElementById('board');

            // Find new pieces by comparing with previous board
            let newPieces = [];
            if (!isNewGame && previousBoard) {
                for (let row = 0; row < 6; row++) {
                    for (let col = 0; col < 7; col++) {
                        if (board[row][col] !== ' ' && previousBoard[row][col] === ' ') {
                            newPieces.push({row, col});
                        }
                    }
                }
            }

            // If it's a new game, clear everything
            if (isNewGame) {
                boardEl.innerHTML = '';
            }

            // Render board
            if (boardEl.children.length === 0) {
                // Initial render - create all cells
                for (let row = 0; row < 6; row++) {
                    const rowEl = document.createElement('div');
                    rowEl.className = 'row';
                    rowEl.dataset.row = row;

                    for (let col = 0; col < 7; col++) {
                        const cell = document.createElement('div');
                        cell.className = 'cell';
                        cell.dataset.col = col;
                        cell.dataset.row = row;

                        const piece = board[row][col];
                        if (piece !== ' ') {
                            const pieceEl = document.createElement('div');
                            const isNew = newPieces.some(p => p.row === row && p.col === col);
                            pieceEl.className = `piece ${piece}${isNew ? ' new-piece' : ''}`;
                            cell.appendChild(pieceEl);
                        }

                        if (!gameOver && currentPlayer === 'X' && validMoves.includes(col)) {
                            cell.onclick = () => makeMove(col);
                        } else {
                            cell.classList.add('disabled');
                        }

                        rowEl.appendChild(cell);
                    }

                    boardEl.appendChild(rowEl);
                }
            } else {
                // Update existing cells - only update pieces that changed
                for (let row = 0; row < 6; row++) {
                    for (let col = 0; col < 7; col++) {
                        const cell = boardEl.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                        if (!cell) continue;

                        const piece = board[row][col];
                        const existingPiece = cell.querySelector('.piece');

                        // Update piece if changed
                        if (piece !== ' ' && !existingPiece) {
                            const pieceEl = document.createElement('div');
                            const isNew = newPieces.some(p => p.row === row && p.col === col);
                            pieceEl.className = `piece ${piece}${isNew ? ' new-piece' : ''}`;
                            cell.appendChild(pieceEl);

                            // Remove new-piece class after animation completes
                            if (isNew) {
                                setTimeout(() => {
                                    pieceEl.classList.remove('new-piece');
                                }, 1500);
                            }
                        }

                        // Update cell interactivity
                        cell.onclick = null;
                        cell.classList.remove('disabled');
                        if (!gameOver && currentPlayer === 'X' && validMoves.includes(col)) {
                            cell.onclick = () => makeMove(col);
                        } else {
                            cell.classList.add('disabled');
                        }
                    }
                }
            }

            // Store current board for next comparison
            previousBoard = board.map(row => [...row]);
        }

        async function makeAIMove() {
            if (gameOver || currentPlayer !== 'O') return;

            updateStatus('AI is thinking...');
            updateProgress('Computing move...');

            try {
                const response = await fetch(`/api/game/${gameId}/ai-move`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });

                const data = await response.json();

                // Check for error response
                if (!response.ok || data.detail) {
                    updateProgress('Error: ' + (data.detail || 'AI move failed'));
                    return;
                }

                currentPlayer = data.current_player;
                gameOver = data.game_over;
                validMoves = data.valid_moves;

                renderBoard(data.board);

                if (gameOver) {
                    if (data.winner === 'O') {
                        updateStatus('😔 AI won!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">AI wins! Better luck next time!</div>';
                    } else if (data.winner === 'X') {
                        updateStatus('🎉 You won!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">🎉 Congratulations! You won! 🎉</div>';
                    } else {
                        updateStatus('🤝 Draw!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">🤝 It is a draw!</div>';
                    }
                    updateProgress('');
                } else {
                    // Check whose turn it is - AI might have another move (2-move rule)
                    if (currentPlayer === 'X') {
                        updateStatus('Your turn! (Red pieces)');
                        updateProgress('');
                    } else {
                        // AI still has a turn
                        updateProgress('AI making 2nd move...');
                        setTimeout(() => makeAIMove(), 500);
                    }
                }
            } catch (error) {
                updateProgress('Error: ' + error.message);
                updateStatus('Error during AI move');
            }
        }

        async function newGame(playerStarts) {
            console.log('newGame called with playerStarts:', playerStarts);
            updateProgress('Starting new game...');
            document.getElementById('winner-banner').innerHTML = '';
            previousBoard = null; // Reset board tracking

            // Show restart button
            document.getElementById('btnRestart').style.display = 'inline-block';

            try {
                console.log('Fetching /api/game/new...');
                const response = await fetch('/api/game/new', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({player_starts: playerStarts})
                });

                console.log('Response status:', response.status);
                const data = await response.json();
                gameId = data.game_id;
                currentPlayer = data.current_player;
                gameOver = data.game_over;
                validMoves = data.valid_moves;

                renderBoard(data.board, true); // true = new game

                if (currentPlayer === 'X') {
                    updateStatus('Your turn! (Red pieces)');
                    updateProgress('');
                } else {
                    updateStatus('AI is thinking...');
                    // Trigger AI move after short delay
                    setTimeout(() => makeAIMove(), 500);
                }
            } catch (error) {
                console.error('Error in newGame:', error);
                updateProgress('Error: ' + error.message);
                updateStatus('Error creating game');
            }
        }

        async function restartGame() {
            // Hide restart button temporarily
            document.getElementById('btnRestart').style.display = 'none';

            // Delete old game from server
            if (gameId) {
                try {
                    await fetch(`/api/game/${gameId}`, {
                        method: 'DELETE'
                    });
                } catch (error) {
                    console.error('Failed to delete game:', error);
                }
            }

            // Reset to mode selection
            gameId = null;
            gameOver = false;
            previousBoard = null;
            document.getElementById('board').innerHTML = '';
            document.getElementById('winner-banner').innerHTML = '';
            updateStatus('Click "New Game" to start');
            updateProgress('');
        }

        async function makeMove(column) {
            if (gameOver || currentPlayer !== 'X') return;

            updateProgress('Making your move...');

            try {
                const response = await fetch(`/api/game/${gameId}/move`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({column: column})
                });

                const data = await response.json();

                // Check for error response
                if (!response.ok || data.detail) {
                    updateProgress('Error: ' + (data.detail || 'Move failed'));
                    return;
                }

                currentPlayer = data.current_player;
                gameOver = data.game_over;
                validMoves = data.valid_moves;

                renderBoard(data.board);

                if (gameOver) {
                    if (data.winner === 'X') {
                        updateStatus('🎉 You won!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">🎉 Congratulations! You won! 🎉</div>';
                    } else if (data.winner === 'O') {
                        updateStatus('😔 AI won!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">AI wins! Better luck next time!</div>';
                    } else {
                        updateStatus('🤝 Draw!');
                        document.getElementById('winner-banner').innerHTML =
                            '<div class="winner-banner">🤝 It is a draw!</div>';
                    }
                    updateProgress('');
                } else {
                    // Check whose turn it is
                    if (currentPlayer === 'X') {
                        updateStatus('Your turn! (Red pieces)');
                        updateProgress('');
                    } else {
                        // AI's turn - trigger AI move
                        setTimeout(() => makeAIMove(), 500);
                    }
                }
            } catch (error) {
                updateProgress('Error: ' + error.message);
            }
        }

        // Set up event listeners - run immediately since script is at bottom
        const btnPlayerStart = document.getElementById('btnPlayerStart');
        const btnAIStart = document.getElementById('btnAIStart');
        const btnRestart = document.getElementById('btnRestart');

        if (btnPlayerStart) {
            btnPlayerStart.addEventListener('click', () => newGame(true));
        }
        if (btnAIStart) {
            btnAIStart.addEventListener('click', () => newGame(false));
        }
        if (btnRestart) {
            btnRestart.addEventListener('click', () => restartGame());
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
