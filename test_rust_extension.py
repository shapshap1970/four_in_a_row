#!/usr/bin/env python3
"""Test the Rust Python extension"""

import time
from four_in_a_row_rust.four_in_a_row_rust import get_best_move

# Empty board test
board_str = "       \n       \n       \n       \n       \n       "

print("Testing Rust Python extension...")
print("Board (empty):")
print(board_str.replace("\n", "\n"))

# Test at depth 12
print("\n=== Depth 12 (like current Rust AI) ===")
start = time.time()
score, best_move = get_best_move(board_str, 12, 1, 2)
elapsed = time.time() - start

print(f"Best move: {best_move}, Score: {score}")
print(f"Time: {elapsed:.3f}s")

# Test at depth 10
print("\n=== Depth 10 ===")
start = time.time()
score, best_move = get_best_move(board_str, 10, 1, 2)
elapsed = time.time() - start

print(f"Best move: {best_move}, Score: {score}")
print(f"Time: {elapsed:.3f}s")

# Test with a move already played
board_str2 = "       \n       \n       \n       \n       \n   X   "
print("\n\nBoard (X played center):")
print(board_str2.replace(" ", ".").replace("\n", ".\n.") + ".")

print("\n=== Depth 12 ===")
start = time.time()
score, best_move = get_best_move(board_str2, 12, 2, 2)
elapsed = time.time() - start

print(f"Best move: {best_move}, Score: {score}")
print(f"Time: {elapsed:.3f}s")

print("\n✅ Rust extension working!")
