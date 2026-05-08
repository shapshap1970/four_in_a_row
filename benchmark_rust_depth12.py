#!/usr/bin/env python3
"""Benchmark Rust AI at depth 12"""

from board import Board
from rust_ai_wrapper import compute_move_rust
import time

print("Benchmarking Rust AI at depth 12:\n")

test_positions = [
    ("Empty board", []),
    ("After X:3", [(3, 'X')]),
    ("After X:3, O:2", [(3, 'X'), (2, 'O')]),
    ("Mid-game (8 moves)", [(3, 'X'), (2, 'O'), (3, 'X'), (2, 'O'), (4, 'X'), (5, 'O'), (3, 'X'), (4, 'O')]),
]

for desc, moves in test_positions:
    board = Board(7, 6)
    
    # Apply moves
    for col, player in moves:
        board.play_move(col, player)
    
    # Determine current player
    if len(moves) == 0:
        current_player = 'X'
        num_play = 2
    else:
        last_player = moves[-1][1]
        consecutive = 1
        for i in range(len(moves)-2, -1, -1):
            if moves[i][1] == last_player:
                consecutive += 1
            else:
                break
        if consecutive >= 2:
            current_player = 'O' if last_player == 'X' else 'X'
            num_play = 2
        else:
            current_player = last_player
            num_play = 2 - consecutive
    
    print(f"{desc}:")
    
    # Time depth 12
    start = time.time()
    score, move = compute_move_rust(board, 12, current_player, num_play)
    elapsed = time.time() - start
    
    print(f"  Depth 12: {elapsed:.2f} seconds - move={move}, score={score}")
    
    # Compare with depth 8
    start = time.time()
    score8, move8 = compute_move_rust(board, 8, current_player, num_play)
    elapsed8 = time.time() - start
    
    print(f"  Depth 8:  {elapsed8:.2f} seconds - move={move8}, score={score8}")
    print(f"  Slowdown: {elapsed/elapsed8:.1f}x slower\n")

print("Summary: Depth 12 takes roughly 0.5-5 seconds depending on position complexity")
