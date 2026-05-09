#!/usr/bin/env python3
"""Test that 2-move detection prioritizes the right blocking moves"""

from board import Board
from threat_detector import detect_must_block_moves

def test_prioritization():
    """Test that we block the move that prevents the most threats"""

    # Setup: X has pieces at columns 2, 4, 5 in row 5
    # X can win by: (3, None), (3, 1), (3, 6), (1, 6)
    # Column 3 appears in 3 sequences, so it should be priority #1
    board = Board(7, 6)
    board.board[5] = [' ', ' ', 'X', ' ', 'X', 'X', ' ']
    board.board[4] = [' ', ' ', ' ', 'O', ' ', ' ', ' ']

    for col in [0, 1, 2, 4, 5, 6]:
        if col == 3:
            board.max_hight[col] = 3
        else:
            board.max_hight[col] = 4

    print("Board:")
    print("╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for row in board.board:
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")

    forced_type, forced_moves = detect_must_block_moves(board, 'O', consec_to_win=4, check_two_moves=True)

    print(f"\nThreat type: {forced_type}")
    print(f"Blocking moves (priority order): {forced_moves}")

    if forced_type in ['block', 'block_2move']:
        print(f"\n✓ Correctly detected threat")
        print(f"  Priority #1: column {forced_moves[0]}")
        if forced_moves[0] == 3:
            print("  ✓ CORRECT: Column 3 blocks the most threats!")
        else:
            print(f"  ❌ WRONG: Should prioritize column 3, got {forced_moves[0]}")
    else:
        print(f"❌ Failed to detect threat! Got: {forced_type}")

if __name__ == "__main__":
    test_prioritization()
