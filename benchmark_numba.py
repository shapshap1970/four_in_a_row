#!/usr/bin/env python3
"""
Benchmark: Python AI vs Numba AI
Compare speed at different depths
"""

from board import Board
from four_in_a_row_optimized import FourInARowOptimized
from four_in_a_row_numba import FourInARowNumba
import time

print("="*70)
print("Benchmarking: Python AI vs Numba AI")
print("="*70)

# Test positions
positions = [
    ("Empty board", []),
    ("After X:3", [(3, 'X')]),
    ("After X:3, O:2", [(3, 'X'), (2, 'O')]),
    ("Mid-game", [(3, 'X'), (2, 'O'), (3, 'X'), (4, 'O')]),
]

for desc, moves in positions:
    print(f"\n{desc}:")
    board = Board(7, 6)
    for col, player in moves:
        board.play_move(col, player)

    # Determine current player
    if len(moves) == 0:
        current_player = 'X'
        num_play = 2
    else:
        last_player = moves[-1][1]
        current_player = 'O' if last_player == 'X' else 'X'
        num_play = 2

    # Test different depths
    for depth in [6, 8, 10]:
        print(f"\n  Depth {depth}:")

        # Python AI
        py_ai = FourInARowOptimized(6, 7, 4, 2)
        start = time.time()
        py_score, py_move = py_ai.minimax_alpha_beta(
            board, depth, -float('inf'), float('inf'),
            current_player, num_play, None, False
        )
        py_time = time.time() - start

        # Numba AI
        numba_ai = FourInARowNumba(6, 7, 4, 2)
        start = time.time()
        numba_score, numba_move = numba_ai.minimax_alpha_beta(
            board, depth, -float('inf'), float('inf'),
            current_player, num_play, None, False
        )
        numba_time = time.time() - start

        # Calculate speedup
        speedup = py_time / numba_time if numba_time > 0 else 0

        print(f"    Python: {py_time:.3f}s - move={py_move}, score={py_score}")
        print(f"    Numba:  {numba_time:.3f}s - move={numba_move}, score={numba_score}")
        print(f"    Speedup: {speedup:.1f}x faster")

        # Verify same result
        if py_move != numba_move:
            print(f"    ⚠️  WARNING: Different moves! Python={py_move}, Numba={numba_move}")

print("\n" + "="*70)
print("Benchmark complete!")
print("="*70)
