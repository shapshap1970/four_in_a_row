#!/usr/bin/env python3
"""Test if AI detects and blocks immediate threats"""

from board import Board

def print_board(board, title=""):
    if title:
        print(f"\n{title}")
    print("╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for row in board.board:
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")

def test_immediate_block():
    """Test AI on simple blocking scenario"""

    # Simple test: X has 3 in a row, AI must block
    board = Board(7, 6)
    board.board[5] = [' ', 'X', 'X', 'X', ' ', ' ', ' ']
    board.max_hight[0] = 4
    board.max_hight[1] = 4
    board.max_hight[2] = 4
    board.max_hight[3] = 4
    board.max_hight[4] = 5
    board.max_hight[5] = 5
    board.max_hight[6] = 5

    print_board(board, "TEST 1: X has 3 in a row (cols 1,2,3). AI MUST block column 0 or 4!")

    # Test Rust AI
    try:
        from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move
        board_str = '\n'.join(''.join(row) for row in board.board)
        rust_score, rust_col = rust_get_best_move(board_str, 12, 2, 2)
        print(f"\nRust AI: column {rust_col}, score {rust_score}")
        if rust_col in [0, 4]:
            print("✓ CORRECT: Rust AI blocks!")
        else:
            print(f"❌ WRONG: Rust AI should block 0 or 4, but played {rust_col}")
    except ImportError:
        print("⚠️  Rust extension not available")

    # Test Python AI
    from four_in_a_row_with_progress import FourInARowWithProgress
    ai = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4, consec_moves=2, show_progress=False)
    python_score, python_col = ai.fixed_depth_search(board, 12, 'O', 2, None)
    print(f"\nPython AI: column {python_col}, score {python_score}")
    if python_col in [0, 4]:
        print("✓ CORRECT: Python AI blocks!")
    else:
        print(f"❌ WRONG: Python AI should block 0 or 4, but played {python_col}")

    # Test 2: More complex - X has 3-in-a-row with gaps
    print("\n" + "="*60)
    board2 = Board(7, 6)
    # X has pieces at columns 2, 4, 5 in row 5 (3 out of 4 in span of 4)
    board2.board[5] = [' ', ' ', 'X', ' ', 'X', 'X', ' ']
    board2.board[4] = [' ', ' ', ' ', 'O', ' ', ' ', ' ']
    for col in [0, 1, 2, 4, 5, 6]:
        if col == 3:
            board2.max_hight[col] = 3
        else:
            board2.max_hight[col] = 4

    print_board(board2, "TEST 2: X has pieces at 2,4,5 in row 5. AI should block column 3!")

    try:
        from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move
        board_str = '\n'.join(''.join(row) for row in board2.board)
        rust_score, rust_col = rust_get_best_move(board_str, 12, 2, 2)
        print(f"\nRust AI: column {rust_col}, score {rust_score}")
        if rust_col == 3:
            print("✓ CORRECT: Rust AI blocks!")
        else:
            print(f"❌ WRONG: Rust AI should block 3, but played {rust_col}")
    except ImportError:
        pass

    python_score, python_col = ai.fixed_depth_search(board2, 12, 'O', 2, None)
    print(f"\nPython AI: column {python_col}, score {python_score}")
    if python_col == 3:
        print("✓ CORRECT: Python AI blocks!")
    else:
        print(f"❌ WRONG: Python AI should block 3, but played {python_col}")

if __name__ == "__main__":
    test_immediate_block()
