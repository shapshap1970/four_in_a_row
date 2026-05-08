#!/usr/bin/env python3
"""
Test: Both AIs should be 100% deterministic
Same input should ALWAYS give same output
"""

from board import Board
from four_in_a_row_optimized import FourInARowOptimized
from rust_ai_wrapper import compute_move_rust

def test_deterministic(description, moves, depth=8):
    """Run the same position multiple times - should get identical results"""
    board = Board(7, 6)
    for col, player in moves:
        board.play_move(col, player)

    # Determine turn
    num_moves = len(moves)
    if num_moves == 0:
        current_player = 'X'
        number_of_play = 2
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
            number_of_play = 2
        else:
            current_player = last_player
            number_of_play = 2 - consecutive

    print(f"\n{description}")
    print(f"  Testing determinism with 3 runs...")

    # Run Python 3 times - should get identical results
    py_results = []
    for i in range(3):
        py_ai = FourInARowOptimized(6, 7, 4, 2)  # Fresh instance each time
        py_score, py_move = py_ai.minimax_alpha_beta(
            board, depth, -float('inf'), float('inf'),
            current_player, number_of_play, None, False
        )
        py_results.append((py_score, py_move))

    # Run Rust 3 times
    rust_results = []
    for i in range(3):
        rust_score, rust_move = compute_move_rust(board, depth, current_player, number_of_play)
        rust_results.append((rust_score, rust_move))

    # Check Python determinism
    py_deterministic = all(r == py_results[0] for r in py_results)
    print(f"  Python runs: {py_results}")
    print(f"  Python deterministic: {'✅ YES' if py_deterministic else '❌ NO'}")

    # Check Rust determinism
    rust_deterministic = all(r == rust_results[0] for r in rust_results)
    print(f"  Rust runs: {rust_results}")
    print(f"  Rust deterministic: {'✅ YES' if rust_deterministic else '❌ NO'}")

    # Check if they match each other
    match = py_results[0] == rust_results[0]
    print(f"  Python == Rust: {'✅ YES' if match else '❌ NO'}")

    return py_deterministic and rust_deterministic and match

print("="*70)
print("Testing DETERMINISM - same input should give same output")
print("="*70)

tests = [
    ("Empty board", []),
    ("X:3", [(3, 'X')]),
    ("X:3, O:2", [(3, 'X'), (2, 'O')]),
    ("X:3, O:2, X:3", [(3, 'X'), (2, 'O'), (3, 'X')]),
]

passed = 0
failed = 0

for desc, moves in tests:
    if test_deterministic(desc, moves, depth=6):  # Depth 6 for speed
        passed += 1
    else:
        failed += 1

print("\n" + "="*70)
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ Both AIs are deterministic and match perfectly!")
else:
    print("❌ Non-deterministic behavior found - BUG!")
print("="*70)
