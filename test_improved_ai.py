#!/usr/bin/env python3
"""Test improved AI with threat detection on the game sequence where human won"""

from board import Board
from threat_detector import detect_must_block_moves
import sys

# Check if Rust is available
try:
    from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move
    RUST_AVAILABLE = True
except ImportError:
    from four_in_a_row_with_progress import FourInARowWithProgress
    RUST_AVAILABLE = False

def print_board(board, title=""):
    """Print board"""
    if title:
        print(f"\n{title}")
    print("╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for row in board.board:
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")

def get_ai_move_with_threat_detection(board, depth, player, num_play):
    """Get AI move with threat detection (mimics web_server logic)"""

    # Check for immediate threats (if 6+ pieces)
    total_pieces = sum(1 for row in board.board for cell in row if cell != ' ')
    if total_pieces >= 6:
        forced_type, forced_moves = detect_must_block_moves(board, player, consec_to_win=4, check_two_moves=True)
        if forced_type == 'win':
            print(f"    ⚡ IMMEDIATE WIN available! Playing column {forced_moves[0]}")
            return 10000, forced_moves[0]
        elif forced_type in ['block', 'block_2move']:
            print(f"    🛡️  BLOCKING opponent {forced_type}! Playing column {forced_moves[0]}")
            return -10000, forced_moves[0]

    # Normal minimax
    if RUST_AVAILABLE:
        board_str = '\n'.join(''.join(row) for row in board.board)
        player_num = 1 if player == 'X' else 2
        score, col = rust_get_best_move(board_str, depth, player_num, num_play)
        print(f"    🚀 Rust AI (depth {depth}): column {col}, score {score}")
        return score, col
    else:
        ai = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4, consec_moves=2, show_progress=False)
        score, col = ai.fixed_depth_search(board, depth, player, num_play, None)
        print(f"    🐍 Python AI (depth {depth}): column {col}, score {score}")
        return score, col

def replay_winning_game():
    """Replay the game where human won, see if AI blocks now"""

    print("="*70)
    print("REPLAYING YOUR WINNING GAME WITH IMPROVED AI")
    print("="*70)

    # The exact sequence from your game
    moves = [
        ('O', 3, 1),    # AI move 1
        ('X', 3, 2),    # Human move 1
        ('X', 1, 1),    # Human move 2
        ('O', 4, 2),    # AI move 1
        ('O', 5, 1),    # AI move 2 - Should this be different now?
        ('X', 2, 2),    # Human move 1
        ('X', 6, 1),    # Human move 2
        ('O', 1, 2),    # AI move 1
        ('O', 1, 1),    # AI move 2
        ('X', 1, 2),    # Human move 1
        ('X', 3, 1),    # Human move 2
        ('O', 3, 2),    # AI move 1
        ('O', 3, 1),    # AI move 2
        ('X', 4, 2),    # Human move 1
        ('X', 4, 1),    # Human move 2
        ('O', 3, 2),    # AI move 1
        ('O', 2, 1),    # AI move 2 - CRITICAL: Should block 5 or 6!
        ('X', 5, 2),    # Human move 1
        ('X', 6, 1),    # Human wins!
    ]

    board = Board(7, 6)
    move_num = 0

    for i, (player, col, num_play) in enumerate(moves):
        move_num += 1

        print(f"\n{'='*70}")
        print(f"Move {move_num}: {player} plays column {col} (number_of_play={num_play})")

        if player == 'O':
            # AI move - compute what improved AI suggests
            print("  AI thinking with threat detection...")
            suggested_score, suggested_col = get_ai_move_with_threat_detection(board, 12, 'O', num_play)

            if suggested_col != col:
                print(f"  ⚠️  IMPROVED AI SUGGESTS DIFFERENT MOVE!")
                print(f"      Original game: column {col}")
                print(f"      Improved AI:    column {suggested_col}")

                # Play the improved move instead
                board.play_move(suggested_col, 'O')
                print_board(board, f"  Board after AI plays {suggested_col}:")

                # Check if this prevents human win
                print(f"\n  Continuing with improved AI move {suggested_col}...")
                continue
            else:
                print(f"  ✓ Improved AI agrees with column {col}")

        # Play the move
        board.play_move(col, player)
        print_board(board, f"  Board after {player} plays {col}:")

        # Check win
        if board.is_winner('X', 4):
            print(f"\n{'='*70}")
            print("🎉 HUMAN (X) WINS!")
            print("❌ AI failed to prevent this win")
            print("="*70)
            return False
        elif board.is_winner('O', 4):
            print(f"\n{'='*70}")
            print("🤖 AI (O) WINS!")
            print("✓ AI successfully won")
            print("="*70)
            return True

    print(f"\n{'='*70}")
    print("Game continues or draw")
    print("="*70)
    return True

if __name__ == "__main__":
    success = replay_winning_game()
    sys.exit(0 if success else 1)
