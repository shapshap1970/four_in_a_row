#!/usr/bin/env python3
"""Test AI's response when player starts"""

from board import Board
import gzip
import json

# Load opening book
with gzip.open('opening_book_7x6.json.gz', 'rt') as f:
    opening_book = json.load(f)

print("Testing AI responses when player (X) goes first:\n")

# Player plays column 3, then AI (O) needs to respond
board = Board(7, 6)
board.play_move(3, 'X')  # Player's first move
print("After X plays column 3:")
board.print_board()

# Now check if AI's response position is in the book
# AI would play as 'O' with number_of_play=2
# Let's check what the book recommends
board_hash = str(board.to_hash())
entry = opening_book.get(board_hash)
print(f"Opening book says: score={entry[0]}, best_move={entry[1]}")
print(f"AI should play column {entry[1]}\n")

# Now simulate AI playing that move and check if next position is in book
board.play_move(entry[1], 'O')
print(f"After O plays column {entry[1]}:")
board.print_board()

board_hash = str(board.to_hash())
in_book = board_hash in opening_book
print(f"Next position in book? {in_book}")
if in_book:
    entry = opening_book[board_hash]
    print(f"  Book entry: {entry}")
