#!/usr/bin/env python3
"""Debug why threat detection didn't catch move 17"""

from board import Board
from threat_detector import detect_must_block_moves

# Recreate board state at move 17 (before AI plays)
board = Board(7, 6)
board.board = [
    [' ', ' ', ' ', 'O', ' ', ' ', ' '],  # row 0
    [' ', ' ', ' ', 'O', ' ', ' ', ' '],  # row 1
    [' ', ' ', 'X', ' ', 'O', ' ', ' '],  # row 2
    [' ', ' ', 'O', ' ', 'X', 'X', ' '],  # row 3
    [' ', ' ', 'O', 'O', 'X', 'X', ' '],  # row 4
    [' ', ' ', 'X', 'X', 'O', 'O', 'O', 'X'],  # row 5 - Wait, this should be 7 columns!
]

# Fix - row has 8 elements!
board.board[5] = [' ', 'X', 'X', 'O', 'O', 'O', 'X']

print("Board at move 17 (before AI plays):")
print("╔═══════════════╗")
print("║ 0 1 2 3 4 5 6 ║")
print("╠═══════════════╣")
for row in board.board:
    print(f"║ {' '.join(row)} ║")
print("╚═══════════════╝")

print("\nChecking threat detection for AI (O)...")
forced_type, forced_moves = detect_must_block_moves(board, 'O', consec_to_win=4)
print(f"Result: type={forced_type}, moves={forced_moves}")

if forced_type in ['block', 'block_2move']:
    print(f"✓ CORRECTLY detected threat! Type: {forced_type}, Should block: {forced_moves}")
else:
    print(f"❌ FAILED to detect threat! Got type: {forced_type}")

print("\nChecking if X can win next turn...")
x_can_win = []
for col, _ in board.possible_moves():
    test_board = Board(board)
    test_board.play_move(col, 'X')
    if test_board.is_winner('X', 4):
        print(f"  ✓ X can win by playing column {col}!")
        x_can_win.append(col)

if not x_can_win:
    print("  X cannot win on their immediate next move")
else:
    print(f"\n⚠️  CRITICAL: X has winning moves {x_can_win} but threat detector didn't catch it!")
