#!/usr/bin/env python3
"""Test what's in the opening book when player starts"""

from board import Board
import gzip
import json

# Load opening book
with gzip.open('opening_book_7x6.json.gz', 'rt') as f:
    opening_book = json.load(f)

print(f"Opening book has {len(opening_book)} positions\n")

# Test: Player (X) plays column 3 first
board = Board(7, 6)
board.play_move(3, 'X')

board_hash = str(board.to_hash())
print(f"After X plays column 3:")
print(f"  Board hash: {board_hash}")
print(f"  In opening book? {board_hash in opening_book}")

if board_hash in opening_book:
    entry = opening_book[board_hash]
    print(f"  Opening book entry: {entry}")
else:
    print(f"  ❌ NOT in opening book! AI will compute from scratch.")

# Test a few other first moves
print("\nChecking other first moves by X:")
for col in [0, 1, 2, 3, 4, 5, 6]:
    board = Board(7, 6)
    board.play_move(col, 'X')
    board_hash = str(board.to_hash())
    in_book = board_hash in opening_book
    status = "✅" if in_book else "❌"
    print(f"  X plays col {col}: {status} {'IN' if in_book else 'NOT IN'} book")
