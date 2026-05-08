#!/usr/bin/env python3
"""
Test ONLY the evaluation function (no minimax)
This isolates if the bug is in evaluation or minimax
"""

from board import Board
from four_in_a_row_optimized import FourInARowOptimized
import subprocess

def evaluate_rust(board):
    """Get Rust evaluation of a static position"""
    # We'll create a Rust program that just evaluates
    # For now, let's run depth=0 minimax which returns evaluation
    from rust_ai_wrapper import compute_move_rust
    score, _ = compute_move_rust(board, 0, 'X', 2)  # depth=0 returns evaluation
    return score

def test_evaluation(description, moves):
    """Test evaluation function only"""
    board = Board(7, 6)
    for col, player in moves:
        board.play_move(col, player)

    # Python evaluation
    ai = FourInARowOptimized(6, 7, 4, 2)
    py_eval = ai.evaluate_heuristic(board)

    # Rust evaluation
    rust_eval = evaluate_rust(board)

    match = abs(py_eval - rust_eval) < 5

    print(f"\n{description}")
    print(f"  Python eval: {py_eval}")
    print(f"  Rust eval:   {rust_eval}")
    print(f"  {'✅ MATCH' if match else '❌ DIFFER'}")

    return match

print("="*70)
print("Testing EVALUATION FUNCTION only (no minimax)")
print("="*70)

tests = [
    ("Empty board", []),
    ("X:3", [(3, 'X')]),
    ("X:3, O:2", [(3, 'X'), (2, 'O')]),
    ("X:3, O:2, X:3", [(3, 'X'), (2, 'O'), (3, 'X')]),
    ("X:3, O:2, X:3, O:2", [(3, 'X'), (2, 'O'), (3, 'X'), (2, 'O')]),
]

passed = 0
for desc, moves in tests:
    if test_evaluation(desc, moves):
        passed += 1

print(f"\n{passed}/{len(tests)} evaluation tests passed")

if passed == len(tests):
    print("\n✅ Evaluation function is correct!")
    print("❌ Bug must be in MINIMAX logic")
else:
    print("\n❌ Evaluation function has bugs - must fix first")
