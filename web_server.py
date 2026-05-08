"""
FastAPI web server for Four-in-a-Row game
Lightweight server with WebSocket support for AI progress updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import json
import asyncio
from contextlib import asynccontextmanager

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress

# Game session storage
games: Dict[str, dict] = {}

# Opening book - loaded on startup
opening_book = None


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load opening book on startup"""
    global opening_book
    try:
        import gzip
        with gzip.open('opening_book_7x6.json.gz', 'rt') as f:
            opening_book = json.load(f)
        print(f"✓ Loaded opening book with {len(opening_book)} positions")
    except FileNotFoundError:
        print("⚠ Opening book not found, AI will calculate from scratch")
        opening_book = {}
    except Exception as e:
        print(f"⚠ Error loading opening book: {e}")
        opening_book = {}

    yield

    # Cleanup
    games.clear()


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
    ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                       consec_moves=2, show_progress=False)
    search_depth = 6  # AI search depth

    # Human is always 'X', AI is always 'O'
    current_player = 'X' if request.player_starts else 'O'

    games[game_id] = {
        'board': board,
        'ai_engine': ai_engine,
        'search_depth': search_depth,
        'current_player': current_player,
        'number_of_play': 2,
        'last_column': None,
        'game_over': False,
        'winner': None,
        'move_history': []
    }

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
    if game_id not in games:
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

        # Determine next player and number of plays
        next_player = ai_engine.next_player('X', game['number_of_play'], first_play=is_first_move)
        next_number = ai_engine.next_number_of_play(game['number_of_play'], first_play=is_first_move)

        game['current_player'] = next_player
        game['number_of_play'] = next_number

    return GameState(
        game_id=game_id,
        board=board.board,
        current_player=game['current_player'],
        game_over=game['game_over'],
        winner=game['winner'],
        valid_moves=[col for col, _ in board.possible_moves()] if not game['game_over'] else [],
        last_move=move.column
    )


@app.get("/api/game/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: str):
    """Get current game state"""
    if game_id not in games:
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
            animation: drop 0.3s ease-out;
        }

        .piece.X {
            background: radial-gradient(circle, #ff6b6b, #c92a2a);
            box-shadow: inset 0 -3px 10px rgba(0,0,0,0.3);
        }

        .piece.O {
            background: radial-gradient(circle, #ffd93d, #f5a623);
            box-shadow: inset 0 -3px 10px rgba(0,0,0,0.3);
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

        .controls {
            text-align: center;
            margin-top: 20px;
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
        <div class="status" id="status">Click "New Game" to start</div>
        <div class="board" id="board"></div>
        <div class="progress" id="progress"></div>
        <div class="controls">
            <button id="btnPlayerStart">New Game (You Start)</button>
            <button id="btnAIStart" style="margin-left: 10px;">New Game (AI Starts)</button>
        </div>
        <div id="winner-banner"></div>
    </div>

    <script>
        let gameId = null;
        let ws = null;
        let currentPlayer = null;
        let gameOver = false;
        let validMoves = [];

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        function updateProgress(message) {
            document.getElementById('progress').textContent = message;
        }

        function renderBoard(board) {
            const boardEl = document.getElementById('board');
            boardEl.innerHTML = '';

            for (let row = 0; row < 6; row++) {
                const rowEl = document.createElement('div');
                rowEl.className = 'row';

                for (let col = 0; col < 7; col++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.dataset.col = col;

                    const piece = board[row][col];
                    if (piece !== ' ') {
                        const pieceEl = document.createElement('div');
                        pieceEl.className = `piece ${piece}`;
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
        }

        async function newGame(playerStarts) {
            console.log('newGame called with playerStarts:', playerStarts);
            updateProgress('Starting new game...');
            document.getElementById('winner-banner').innerHTML = '';

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

                renderBoard(data.board);

                // Setup WebSocket
                if (ws) ws.close();
                ws = new WebSocket(`ws://${window.location.host}/ws/${gameId}`);

                ws.onopen = () => {
                    if (currentPlayer === 'O') {
                        ws.send(JSON.stringify({action: 'compute_ai_move'}));
                    }
                };

                ws.onmessage = handleWebSocketMessage;

                ws.onerror = (error) => {
                    updateProgress('Connection error');
                    console.error('WebSocket error:', error);
                };

                if (currentPlayer === 'X') {
                    updateStatus('Your turn! (Red pieces)');
                    updateProgress('');
                } else {
                    updateStatus('AI is thinking...');
                }
            } catch (error) {
                console.error('Error in newGame:', error);
                updateProgress('Error: ' + error.message);
                updateStatus('Error creating game');
            }
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
                        updateStatus('AI is thinking...');
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({action: 'compute_ai_move'}));
                        } else {
                            updateProgress('Error: Connection lost');
                        }
                    }
                }
            } catch (error) {
                updateProgress('Error: ' + error.message);
            }
        }

        function handleWebSocketMessage(event) {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'thinking':
                    updateProgress(data.message);
                    break;

                case 'progress':
                    updateProgress(data.message);
                    break;

                case 'move':
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
                        // Check whose turn it is - AI might have another move!
                        if (currentPlayer === 'X') {
                            updateStatus('Your turn! (Red pieces)');
                            updateProgress('');
                        } else {
                            // AI still has a turn (2-move rule)
                            updateStatus('AI is thinking...');
                            updateProgress('AI making 2nd move...');
                            if (ws && ws.readyState === WebSocket.OPEN) {
                                ws.send(JSON.stringify({action: 'compute_ai_move'}));
                            } else {
                                updateProgress('Error: Connection lost');
                            }
                        }
                    }
                    break;

                case 'error':
                    updateProgress('Error: ' + data.message);
                    break;
            }
        }

        // Set up event listeners - run immediately since script is at bottom
        const btnPlayerStart = document.getElementById('btnPlayerStart');
        const btnAIStart = document.getElementById('btnAIStart');

        if (btnPlayerStart && btnAIStart) {
            btnPlayerStart.addEventListener('click', () => newGame(true));
            btnAIStart.addEventListener('click', () => newGame(false));
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
