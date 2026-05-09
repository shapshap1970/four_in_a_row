#!/usr/bin/env python3
"""Quick test for threat detector"""

from board import Board
from threat_detector import detect_must_block_moves

def test_immediate_threats():
    """Test threat detection"""

    # Test 1: X can win horizontally
    board1 = Board(7, 6)
    board1.board[5] = [' ', 'X', 'X', 'X', ' ', ' ', ' ']
    for i in range(7):
        if i in [1, 2, 3]:
            board1.max_hight[i] = 4
        else:
            board1.max_hight[i] = 5

    forced_type, forced_moves = detect_must_block_moves(board1, 'O')
    print(f"Test 1 - X has 3 in row:")
    print(f"  Type: {forced_type}, Moves: {forced_moves}")
    assert forced_type == 'block', f"Should detect block, got {forced_type}"
    assert set(forced_moves) == {0, 4}, f"Should block 0 or 4, got {forced_moves}"
    print("  ✓ PASS")

    # Test 2: O can win
    board2 = Board(7, 6)
    board2.board[5] = [' ', 'O', 'O', 'O', ' ', ' ', ' ']
    for i in range(7):
        if i in [1, 2, 3]:
            board2.max_hight[i] = 4
        else:
            board2.max_hight[i] = 5

    forced_type, forced_moves = detect_must_block_moves(board2, 'O')
    print(f"\nTest 2 - O can win:")
    print(f"  Type: {forced_type}, Moves: {forced_moves}")
    assert forced_type == 'win', f"Should detect win, got {forced_type}"
    assert set(forced_moves) == {0, 4}, f"Should win at 0 or 4, got {forced_moves}"
    print("  ✓ PASS")

    # Test 3: No immediate threats
    board3 = Board(7, 6)
    board3.board[5] = [' ', 'X', ' ', 'O', ' ', 'X', ' ']
    board3.board[4] = [' ', 'O', ' ', 'X', ' ', 'O', ' ']

    forced_type, forced_moves = detect_must_block_moves(board3, 'O')
    print(f"\nTest 3 - No threats:")
    print(f"  Type: {forced_type}, Moves: {forced_moves}")
    assert forced_type == 'none', f"Should detect none, got {forced_type}"
    assert forced_moves == [], f"Should have no forced moves, got {forced_moves}"
    print("  ✓ PASS")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_immediate_threats()
