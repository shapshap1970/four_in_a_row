#!/usr/bin/env python3
"""Compare Rust vs Python AI on the exact game sequence where AI lost"""

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress

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

def test_move_sequence():
    """Test both AI engines on the losing sequence"""

    # The move sequence that led to AI loss
    # O = AI, X = human
    moves = [
        ('O', 3),   # AI move 1
        ('X', 3),   # Human move 1
        ('X', 1),   # Human move 2
        ('O', 4),   # AI move 1
        ('O', 5),   # AI move 2 - CRITICAL: Should have blocked!
        ('X', 2),   # Human move 1
        ('X', 6),   # Human move 2
        ('O', 1),   # AI move 1
        ('O', 1),   # AI move 2
        ('X', 1),   # Human move 1
        ('X', 3),   # Human move 2
        ('O', 3),   # AI move 1
        ('O', 3),   # AI move 2
        ('X', 4),   # Human move 1
        ('X', 4),   # Human move 2
        ('O', 3),   # AI move 1
        ('O', 2),   # AI move 2 - CRITICAL: Should have blocked 5 or 6!
        ('X', 5),   # Human move 1
        ('X', 6),   # Human wins!
    ]

    print("="*60)
    print("REPLAY WITH PYTHON AI")
    print("="*60)

    board = Board(7, 6)
    ai = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4, consec_moves=2, show_progress=False)

    current_player = 'O'
    number_of_play = 1
    move_history = []

    for i, (expected_player, col) in enumerate(moves):
        if current_player != expected_player:
            print(f"ERROR: Expected {expected_player} but got {current_player}")
            break

        if current_player == 'O':
            # AI move - compute what Python AI would do
            eval_score, best_col = ai.fixed_depth_search(
                board, 12, 'O', number_of_play,
                move_history[-1][1] if move_history else None
            )

            print(f"\nMove {i+1}: AI (O) - number_of_play={number_of_play}")
            print(f"  Python AI suggests: column {best_col}, score {eval_score}")
            print(f"  Human played: column {col}")

            if best_col != col:
                print(f"  ⚠️  MISMATCH! Python would play {best_col}, but human game had {col}")

            # Play the actual move from the game
            board.play_move(col, 'O')
        else:
            # Human move
            print(f"\nMove {i+1}: Human (X) plays column {col} - number_of_play={number_of_play}")
            board.play_move(col, 'X')

        move_history.append((current_player, col))

        # Check win
        if board.is_winner('X', 4):
            print_board(board, "\n🎉 X WINS!")
            print("\n❌ AI FAILED TO BLOCK!")
            break
        if board.is_winner('O', 4):
            print_board(board, "\n😔 O WINS!")
            break

        # Update turn
        if number_of_play == 1:
            current_player = 'X' if current_player == 'O' else 'O'
            number_of_play = 2
        else:
            number_of_play -= 1

    print("\n" + "="*60)
    print("TESTING RUST AI ON CRITICAL POSITIONS")
    print("="*60)

    # Test Rust AI at the critical moments
    try:
        from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move

        # Position after move 4 (before AI's critical move 5)
        board1 = Board(7, 6)
        board1.play_move(3, 'O')  # Move 1
        board1.play_move(3, 'X')  # Move 2
        board1.play_move(1, 'X')  # Move 3
        board1.play_move(4, 'O')  # Move 4

        print_board(board1, "\nCRITICAL POSITION 1 (after move 4):")
        print("AI's turn, number_of_play=1")

        board_str = '\n'.join(''.join(row) for row in board1.board)
        rust_score, rust_col = rust_get_best_move(board_str, 12, 2, 1)
        python_score, python_col = ai.fixed_depth_search(board1, 12, 'O', 1, 4)

        print(f"  Rust AI:   column {rust_col}, score {rust_score}")
        print(f"  Python AI: column {python_col}, score {python_score}")
        print(f"  Actual:    column 5")
        print(f"  Should block: column 2 to prevent X's horizontal threat")

        # Position before move 17 (AI's last chance to block)
        board2 = Board(7, 6)
        for player, col in moves[:16]:
            board2.play_move(col, player)

        print_board(board2, "\nCRITICAL POSITION 2 (before move 17):")
        print("AI's turn, number_of_play=1")

        board_str2 = '\n'.join(''.join(row) for row in board2.board)
        rust_score2, rust_col2 = rust_get_best_move(board_str2, 12, 2, 1)
        python_score2, python_col2 = ai.fixed_depth_search(board2, 12, 'O', 1, 3)

        print(f"  Rust AI:   column {rust_col2}, score {rust_score2}")
        print(f"  Python AI: column {python_col2}, score {python_score2}")
        print(f"  Actual:    column 2")
        print(f"  Should block: column 5 or 6 to prevent X's horizontal threat!")

    except ImportError:
        print("⚠️  Rust extension not available for comparison")

if __name__ == "__main__":
    test_move_sequence()
