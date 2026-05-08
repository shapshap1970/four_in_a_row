#!/usr/bin/env python3
"""
Comprehensive test: Rust AI must match Python AI exactly
"""

from board import Board
from four_in_a_row_optimized import FourInARowOptimized
from rust_ai_wrapper import compute_move_rust, is_rust_ai_available
import sys

if not is_rust_ai_available():
    print("❌ Rust AI not found")
    sys.exit(1)

def test_position(description, moves, depth=8):
    """Test a specific board position"""
    # Create FRESH Python AI for each test (no accumulated state!)
    py_ai = FourInARowOptimized(6, 7, 4, 2)

    board = Board(7, 6)

    # Apply moves
    for col, player in moves:
        board.play_move(col, player)

    # Determine whose turn it is
    num_moves = len(moves)
    if num_moves == 0:
        current_player = 'X'
        number_of_play = 2
    else:
        last_player = moves[-1][1]
        # Count consecutive moves by last player
        consecutive = 1
        for i in range(len(moves)-2, -1, -1):
            if moves[i][1] == last_player:
                consecutive += 1
            else:
                break

        # Determine next player
        if consecutive >= 2:
            current_player = 'O' if last_player == 'X' else 'X'
            number_of_play = 2
        else:
            current_player = last_player
            number_of_play = 2 - consecutive

    # Python AI
    py_score, py_move = py_ai.minimax_alpha_beta(
        board, depth, -float('inf'), float('inf'),
        current_player, number_of_play, None, False
    )

    # Rust AI
    rust_score, rust_move = compute_move_rust(board, depth, current_player, number_of_play)

    # Compare
    move_match = (py_move == rust_move)
    score_close = abs(py_score - rust_score) < 5  # Allow small score differences

    print(f"\n{description}")
    print(f"  Board: {moves}")
    print(f"  Turn: {current_player}, num_play={number_of_play}")
    print(f"  Python: move={py_move}, score={py_score}")
    print(f"  Rust:   move={rust_move}, score={rust_score}")

    if move_match and score_close:
        print(f"  ✅ MATCH")
        return True
    else:
        print(f"  ❌ MISMATCH! {'Move differs' if not move_match else 'Score differs'}")
        if not move_match:
            print(f"\n  Debugging: Board state:")
            board.print_board()
        return False

print("="*70)
print("Testing Rust AI vs Python AI")
print("="*70)

tests = [
    ("Empty board", []),
    ("X plays center", [(3, 'X')]),
    ("X:3, O:3", [(3, 'X'), (3, 'O')]),
    ("X:3, O:2", [(3, 'X'), (2, 'O')]),
    ("X:3, O:2, X:3", [(3, 'X'), (2, 'O'), (3, 'X')]),
    ("X:3, O:2, X:3, O:2", [(3, 'X'), (2, 'O'), (3, 'X'), (2, 'O')]),
    ("X:3, O:2, X:3, O:2, X:3", [(3, 'X'), (2, 'O'), (3, 'X'), (2, 'O'), (3, 'X')]),
    ("X:3, O:3, X:4, O:2", [(3, 'X'), (3, 'O'), (4, 'X'), (2, 'O')]),
    ("X:0, O:6, X:1, O:5", [(0, 'X'), (6, 'O'), (1, 'X'), (5, 'O')]),
    ("X:3, O:3, X:3, O:2, X:2, O:4", [(3, 'X'), (3, 'O'), (3, 'X'), (2, 'O'), (2, 'X'), (4, 'O')]),
]

passed = 0
failed = 0

for desc, moves in tests:
    if test_position(desc, moves, depth=8):
        passed += 1
    else:
        failed += 1

print("\n" + "="*70)
print(f"Results: {passed} passed, {failed} failed")
print("="*70)

if failed == 0:
    print("✅ Rust AI matches Python AI perfectly!")
    sys.exit(0)
else:
    print("❌ Rust AI has bugs - needs fixing")
    sys.exit(1)
