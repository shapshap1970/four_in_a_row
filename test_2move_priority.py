#!/usr/bin/env python3
"""Test 2-move threat detection with multiple paths"""

from board import Board
from threat_detector import detect_two_move_win, detect_must_block_moves

def test_2move():
    """Test board from move 22 - where X won"""

    # After move 21 (before X's winning move 22 at column 4)
    # This is a simplified version - X has 3 in row 4 at columns 3,4,5
    # and can extend to win
    board = Board(7, 6)

    # Simulate a position where X can win in 2 moves
    board.board[5] = ['O', 'X', 'X', 'O', 'O', 'O', 'X']
    board.board[4] = ['O', 'O', 'O', 'X', 'X', 'X', ' ']
    board.board[3] = [' ', 'O', ' ', 'X', ' ', ' ', ' ']
    board.board[2] = [' ', 'X', ' ', 'O', ' ', ' ', ' ']
    board.board[1] = [' ', ' ', ' ', 'O', ' ', ' ', ' ']
    board.board[0] = [' ', ' ', ' ', 'O', ' ', ' ', ' ']

    # Update max_hight
    for col in range(7):
        for row in range(6):
            if board.board[row][col] != ' ':
                board.max_hight[col] = row - 1
                break
        else:
            board.max_hight[col] = 5

    print("Board (X to play, can win in 2 moves):")
    print("╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for row in board.board:
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")

    # Check what 2-move detector finds
    two_move_wins = detect_two_move_win(board, 'X', consec_to_win=4)
    print(f"\n2-move winning sequences for X: {two_move_wins}")

    # Check what AI would do
    forced_type, forced_moves = detect_must_block_moves(board, 'O', consec_to_win=4, check_two_moves=True)
    print(f"\nAI threat detection:")
    print(f"  Type: {forced_type}")
    print(f"  Blocking moves: {forced_moves}")

    if forced_type in ['block', 'block_2move']:
        print(f"\n✓ AI detected threat and would block: {forced_moves[0]}")
    else:
        print(f"\n❌ AI did NOT detect threat!")

if __name__ == "__main__":
    test_2move()
