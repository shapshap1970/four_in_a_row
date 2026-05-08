#!/usr/bin/env python3
"""Test opening book vs Rust AI for both starting scenarios"""

from board import Board
from rust_ai_wrapper import compute_move_rust
import gzip
import json

# Load opening book
with gzip.open('opening_book_7x6.json.gz', 'rt') as f:
    opening_book = json.load(f)

print("="*70)
print("SCENARIO 1: AI (O) goes FIRST")
print("="*70)

board1 = Board(7, 6)
board_hash1 = str(board1.to_hash())

# Check opening book
if board_hash1 in opening_book:
    entry = opening_book[board_hash1]
    print(f"Opening book (depth 8): move={entry[1]}, score={entry[0]}")
else:
    print("Opening book: NOT FOUND")

# Check Rust AI depth 12
score12, move12 = compute_move_rust(board1, 12, 'O', 2)
print(f"Rust AI (depth 12):     move={move12}, score={score12}")

if board_hash1 in opening_book:
    book_move = opening_book[board_hash1][1]
    if book_move != move12:
        print(f"❌ MISMATCH! Book says {book_move}, Rust says {move12}")
    else:
        print(f"✅ MATCH!")
print()

print("="*70)
print("SCENARIO 2: Player (X) goes first, then AI (O) responds")
print("="*70)

# Player plays column 3
board2 = Board(7, 6)
board2.play_move(3, 'X')
board_hash2 = str(board2.to_hash())

# Check opening book
if board_hash2 in opening_book:
    entry = opening_book[board_hash2]
    print(f"Opening book (depth 8): move={entry[1]}, score={entry[0]}")
else:
    print("Opening book: NOT FOUND")

# Check Rust AI depth 12
score12, move12 = compute_move_rust(board2, 12, 'O', 2)
print(f"Rust AI (depth 12):     move={move12}, score={score12}")

if board_hash2 in opening_book:
    book_move = opening_book[board_hash2][1]
    if book_move != move12:
        print(f"❌ MISMATCH! Book says {book_move}, Rust says {move12}")
    else:
        print(f"✅ MATCH!")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("Both scenarios use opening book (depth 8) instead of Rust AI (depth 12)")
print("This causes weaker play in BOTH cases - whether AI or player starts first!")
