#!/usr/bin/env python3
"""
Debug: manually call Rust and trace what it counts
"""

from board import Board
import subprocess

# Create board: X:3
board = Board(7, 6)
board.play_move(3, 'X')

print("Board:")
board.print_board()

# Create Rust input
rust_input = "0\n"  # depth = 0 (just evaluate)
rust_input += "1\n"  # player = 1 (X)
rust_input += "2\n"  # num_play = 2

# Add board (6 rows x 7 cols)
for row in board.board:
    rust_input += ''.join(row) + '\n'

print("\nCalling Rust AI...")
print(f"Input:\n{rust_input}")

result = subprocess.run(
    ["./opening_book_generator/target/release/ai_engine"],
    input=rust_input,
    capture_output=True,
    text=True
)

print(f"\nRust output:")
print(result.stdout)

# Now manually count in Python what Rust should see
print("\nManual count in Python (what Rust should see):")

grid = [[0 if c == ' ' else (1 if c == 'X' else 2) for c in row] for row in board.board]

# Count horizontal threats with length=1
h_count = 0
for row in range(6):
    for col in range(4):  # 0..=(7-4) = 0..=3
        window = [grid[row][col+i] for i in range(4)]
        player_count = window.count(1)
        opponent_count = window.count(2)
        if player_count == 1 and opponent_count == 0:
            h_count += 1
            print(f"  Horizontal row={row}, col={col}: {window}")

print(f"Horizontal 1-threats: {h_count}")

# Count vertical threats
v_count = 0
for col in range(7):
    for row in range(3):  # 0..=(6-4) = 0..=2
        window = [grid[row+i][col] for i in range(4)]
        player_count = window.count(1)
        opponent_count = window.count(2)
        if player_count == 1 and opponent_count == 0:
            v_count += 1
            print(f"  Vertical col={col}, row={row}: {window}")

print(f"Vertical 1-threats: {v_count}")

# Count diagonals
d1_count = 0
for row in range(3):  # 0..=(6-4)
    for col in range(4):  # 0..=(7-4)
        window = [grid[row+i][col+i] for i in range(4)]
        player_count = window.count(1)
        opponent_count = window.count(2)
        if player_count == 1 and opponent_count == 0:
            d1_count += 1
            print(f"  Diag-down row={row}, col={col}: {window}")

print(f"Diagonal-down 1-threats: {d1_count}")

d2_count = 0
for row in range(3, 6):  # 3..6
    for col in range(4):  # 0..=(7-4)
        window = [grid[row-i][col+i] for i in range(4)]
        player_count = window.count(1)
        opponent_count = window.count(2)
        if player_count == 1 and opponent_count == 0:
            d2_count += 1
            print(f"  Diag-up row={row}, col={col}: {window}")

print(f"Diagonal-up 1-threats: {d2_count}")

total = h_count + v_count + d1_count + d2_count
print(f"\nTotal 1-threats: {total}")
print(f"Plus center bonus (+3): {total + 3}")
