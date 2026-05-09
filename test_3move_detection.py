#!/usr/bin/env python3
"""Test 3-move threat detection"""

from board import Board
from threat_detector import detect_three_move_win, detect_must_block_moves

def test_3move():
    """Test 3-move detection on a complex position"""

    board = Board(7, 6)

    # Setup: X has pieces that can build a winning sequence in 3 moves
    board.board[5] = [' ', ' ', 'X', ' ', 'X', ' ', ' ']
    board.board[4] = [' ', ' ', 'O', ' ', 'O', ' ', ' ']
    board.board[3] = [' ', ' ', ' ', ' ', ' ', ' ', ' ']

    # Update max_hight
    for col in range(7):
        for row in range(6):
            if board.board[row][col] != ' ':
                board.max_hight[col] = row - 1
                break
        else:
            board.max_hight[col] = 5

    print("Board (X can build winning sequence in 3 moves):")
    print("╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for row in board.board:
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")

    # Check 3-move detection
    three_move_wins = detect_three_move_win(board, 'X', consec_to_win=4)
    print(f"\n3-move winning sequences for X: {len(three_move_wins)} found")
    if len(three_move_wins) <= 10:
        for seq in three_move_wins:
            print(f"  {seq}")
    else:
        print(f"  (showing first 10)")
        for seq in three_move_wins[:10]:
            print(f"  {seq}")

    # Check what AI detects
    forced_type, forced_moves = detect_must_block_moves(
        board, 'O', consec_to_win=4,
        check_two_moves=True,
        check_three_moves=True
    )
    print(f"\nAI threat detection:")
    print(f"  Type: {forced_type}")
    print(f"  Blocking moves: {forced_moves}")

    if forced_type == 'block_3move':
        print(f"\n✓ AI detected 3-move threat and would block: {forced_moves[0]}")
    else:
        print(f"\n⚠️  Detection result: {forced_type}")

if __name__ == "__main__":
    test_3move()
