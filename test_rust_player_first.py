#!/usr/bin/env python3
"""Test Rust AI when player goes first"""

from board import Board
from rust_ai_wrapper import compute_move_rust

print("Testing Rust AI when player (X) plays column 3 first:\n")

board = Board(7, 6)
board.play_move(3, 'X')  # Player's first move

print("Board after X plays column 3:")
board.print_board()

print("\nCalling Rust AI (depth 12, player=O, num_play=2)...")
score, move = compute_move_rust(board, 12, 'O', 2)

print(f"Rust AI response: column {move}, score {score}")
print(f"\nExpected from opening book: column 2, score 137")

if move != 2:
    print(f"\n❌ MISMATCH! Rust chose {move} instead of 2")
else:
    print(f"\n✅ MATCH! Rust chose correct move")
