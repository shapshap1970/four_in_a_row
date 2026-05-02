"""
Performance comparison between original and optimized implementations.
"""

import time
from board import Board
from four_in_a_row import FourInARow
from four_in_a_row_optimized import FourInARowOptimized


def test_original(rows, cols, consec_to_win, consec_moves, depth):
    """Test original implementation"""
    print(f"\n{'='*60}")
    print(f"Testing ORIGINAL implementation")
    print(f"Board: {cols}x{rows}, depth: {depth}")
    print(f"{'='*60}")

    game = FourInARow(rows, cols, consec_to_win, consec_moves)
    board = Board(cols, rows)

    # Make a few moves to test mid-game performance
    board.play_move(3, 'X')  # Center column

    start_time = time.time()
    try:
        eval_score, best_move = game.minimax(board, depth, 'O', consec_moves, None)
        elapsed = time.time() - start_time

        print(f"✓ Completed in {elapsed:.2f}s")
        print(f"  Eval: {eval_score}, Best move: {best_move}")
        print(f"  Cache size: {len(game.memoization)}")
        return elapsed, True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Failed after {elapsed:.2f}s: {e}")
        return elapsed, False


def test_optimized(rows, cols, consec_to_win, consec_moves, max_time):
    """Test optimized implementation"""
    print(f"\n{'='*60}")
    print(f"Testing OPTIMIZED implementation")
    print(f"Board: {cols}x{rows}, time limit: {max_time}s")
    print(f"{'='*60}")

    game = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)
    board = Board(cols, rows)

    # Make a few moves to test mid-game performance
    board.play_move(3, 'X')  # Center column

    start_time = time.time()
    eval_score, best_move = game.get_best_move(
        board, 'O', consec_moves, None, max_time
    )
    elapsed = time.time() - start_time

    print(f"✓ Completed in {elapsed:.2f}s")
    print(f"  Final eval: {eval_score}, Best move: {best_move}")
    print(f"  Cache size: {len(game.memoization)}")
    return elapsed


def compare_heuristic_evaluation():
    """Compare evaluation functions"""
    print(f"\n{'='*60}")
    print("COMPARING EVALUATION FUNCTIONS")
    print(f"{'='*60}")

    game_opt = FourInARowOptimized(6, 7, 4, 2)
    board = Board(7, 6)

    # Create some test positions
    positions = [
        ("Empty board", []),
        ("Center control", [(3, 'X')]),
        ("Two in a row", [(3, 'X'), (4, 'X')]),
        ("Three in a row", [(2, 'X'), (3, 'X'), (4, 'X')]),
        ("Opponent two", [(3, 'O'), (3, 'O')]),
    ]

    for desc, moves in positions:
        test_board = Board(7, 6)
        for col, player in moves:
            test_board.play_move(col, player)

        eval_score = game_opt.evaluate_heuristic(test_board)
        print(f"{desc:20s}: {eval_score:6.0f}")


def test_move_ordering():
    """Test that move ordering improves pruning"""
    print(f"\n{'='*60}")
    print("TESTING MOVE ORDERING EFFECTIVENESS")
    print(f"{'='*60}")

    game = FourInARowOptimized(6, 7, 4, 2)
    board = Board(7, 6)

    # Test position
    board.play_move(3, 'X')
    board.play_move(2, 'O')
    board.play_move(4, 'X')

    # Without move ordering (just use original order)
    start = time.time()
    game_no_order = FourInARowOptimized(6, 7, 4, 2)
    eval1, move1 = game_no_order.minimax_alpha_beta(
        board, 4, -float('inf'), float('inf'), 'O', 2, None
    )
    time_no_order = time.time() - start
    states_no_order = len(game_no_order.memoization)

    # With move ordering
    start = time.time()
    game_with_order = FourInARowOptimized(6, 7, 4, 2)
    # Pre-populate history heuristic to favor center
    for col in range(7):
        game_with_order.history_heuristic[col] = (3 - abs(col - 3)) * 100
    eval2, move2 = game_with_order.minimax_alpha_beta(
        board, 4, -float('inf'), float('inf'), 'O', 2, None
    )
    time_with_order = time.time() - start
    states_with_order = len(game_with_order.memoization)

    print(f"Without ordering: {time_no_order:.3f}s, {states_no_order} states")
    print(f"With ordering:    {time_with_order:.3f}s, {states_with_order} states")
    print(f"Speedup:          {time_no_order/time_with_order:.2f}x")


def run_full_comparison():
    """Run complete comparison suite"""
    print("\n" + "="*60)
    print("FOUR-IN-A-ROW PERFORMANCE COMPARISON")
    print("="*60)

    # Test 1: Small board (should work for both)
    print("\n\n### TEST 1: Small Board (5x5) ###")
    test_original(5, 5, 4, 2, 8)
    test_optimized(5, 5, 4, 2, 5.0)

    # Test 2: Standard board with low depth (original might struggle)
    print("\n\n### TEST 2: Standard Board (7x6), Limited Depth ###")
    test_original(6, 7, 4, 2, 4)
    test_optimized(6, 7, 4, 2, 3.0)

    # Test 3: Standard board with realistic time (optimized only)
    print("\n\n### TEST 3: Standard Board (7x6), Realistic Play ###")
    print("(Original would be too slow, testing optimized only)")
    test_optimized(6, 7, 4, 2, 5.0)

    # Test 4: Evaluation function comparison
    compare_heuristic_evaluation()

    # Test 5: Move ordering effectiveness
    test_move_ordering()

    print("\n\n" + "="*60)
    print("COMPARISON COMPLETE")
    print("="*60)


if __name__ == "__main__":
    run_full_comparison()
