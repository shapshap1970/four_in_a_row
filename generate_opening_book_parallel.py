#!/usr/bin/env python3
"""
Parallelized Opening Book Generator for Four-in-a-Row
Generates pre-computed moves by parallelizing across first moves (7 processes)
"""

import gzip
import json
import time
import multiprocessing as mp
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


def generate_positions_from_first_move(args):
    """
    Worker function: Generate all positions starting from a specific first move
    """
    first_col, rows, cols, consec_to_win, consec_moves, book_depth, search_depth = args

    print(f"[Worker {first_col}] Starting generation for first move: column {first_col}")

    # Create engine for this worker
    engine = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)
    book = {}
    positions_evaluated = 0
    start_time = time.time()

    # Create initial board with first move
    board = Board(cols, rows)
    board.play_move(first_col, 'X')

    # Add this first position to book
    board_hash = board.to_hash()
    key = str(board_hash)
    eval_score, best_move = engine.minimax_alpha_beta(
        board, search_depth, -float('inf'), float('inf'),
        'O', consec_moves, first_col, first_play=True
    )
    book[key] = [eval_score, best_move]
    positions_evaluated += 1

    def generate_recursive(board, current_player, number_of_play, move_count, first_play=False):
        nonlocal positions_evaluated

        if move_count >= book_depth:
            return

        # Evaluate this position
        board_hash = board.to_hash()
        key = str(board_hash)

        if key not in book:
            # Calculate best move for this position
            eval_score, best_move = engine.minimax_alpha_beta(
                board, search_depth, -float('inf'), float('inf'),
                current_player, number_of_play, None, first_play
            )

            book[key] = [eval_score, best_move]
            positions_evaluated += 1

            # Progress indicator
            if positions_evaluated % 100 == 0:
                elapsed = time.time() - start_time
                positions_per_sec = positions_evaluated / elapsed if elapsed > 0 else 0
                print(f"[Worker {first_col}] Position {positions_evaluated} "
                      f"(move {move_count + 1}, {positions_per_sec:.1f} pos/s, "
                      f"{elapsed/60:.1f}m elapsed)")
        else:
            # Already evaluated, use cached result
            eval_score, best_move = book[key]

        # Generate all possible next positions
        for move in board.possible_moves():
            col = move[0]
            next_board = Board(board)
            next_board.play_move(col, current_player)

            # Check if game ended
            if next_board.is_winner(current_player, consec_to_win):
                continue
            if next_board.is_end_of_game():
                continue

            # Determine next player and number of plays
            if number_of_play == 1 or first_play:
                next_player = 'O' if current_player == 'X' else 'X'
                next_number_of_play = consec_moves
            else:
                next_player = current_player
                next_number_of_play = number_of_play - 1

            # Recursively generate
            generate_recursive(
                next_board, next_player, next_number_of_play,
                move_count + 1, first_play=False
            )

    # Start recursive generation from this first move
    generate_recursive(board, 'O', consec_moves, 1, first_play=True)

    elapsed = time.time() - start_time
    print(f"[Worker {first_col}] Complete! {positions_evaluated} positions in {elapsed/60:.1f}m")

    return first_col, book, positions_evaluated


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎮 PARALLELIZED OPENING BOOK GENERATOR")
    print("="*60)

    # Configuration
    rows = 6
    cols = 7
    consec_to_win = 4
    consec_moves = 2
    book_depth = 8
    search_depth = 8
    filename = "opening_book_7x6.json.gz"

    print(f"\nConfiguration:")
    print(f"  Board: {cols}x{rows}")
    print(f"  Win: {consec_to_win} in a row")
    print(f"  Moves per turn: {consec_moves}")
    print(f"  Book depth: First {book_depth} moves")
    print(f"  Search depth: {search_depth} plies")
    print(f"  Parallelization: {cols} workers (one per first move)")
    print(f"\n⏱️  Estimated time: 2-3 hours (with {cols} CPU cores)")
    print(f"📁 Output: {filename}")
    print("="*60)

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    print("\n🚀 Starting parallel generation...\n")
    overall_start = time.time()

    # Prepare worker arguments
    worker_args = [
        (first_col, rows, cols, consec_to_win, consec_moves, book_depth, search_depth)
        for first_col in range(cols)
    ]

    # Create process pool and run workers in parallel
    with mp.Pool(processes=cols) as pool:
        results = pool.map(generate_positions_from_first_move, worker_args)

    # Merge all results
    print("\n" + "="*60)
    print("📦 Merging results from all workers...")
    print("="*60)

    merged_book = {}
    total_positions = 0

    for first_col, book, positions_evaluated in results:
        print(f"  Worker {first_col}: {positions_evaluated} positions")
        merged_book.update(book)
        total_positions += positions_evaluated

    # Note: merged_book may have fewer total positions due to overlapping board states
    unique_positions = len(merged_book)

    overall_elapsed = time.time() - overall_start

    print(f"\n✅ Generation complete!")
    print(f"   Total positions evaluated: {total_positions}")
    print(f"   Unique board states: {unique_positions}")
    print(f"   Time taken: {overall_elapsed/60:.1f} minutes ({overall_elapsed/3600:.1f} hours)")

    # Save merged book
    print(f"\n💾 Saving to {filename}...")
    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(merged_book, f, indent=2)

    import os
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"   ✓ Saved {unique_positions} positions ({size_mb:.1f} MB)")

    print("\n" + "="*60)
    print("✅ OPENING BOOK READY!")
    print("="*60)
    print(f"\nTo use the opening book:")
    print(f"1. File is already in place: {filename}")
    print(f"2. Run play_game_beautiful.py")
    print(f"3. First {book_depth} moves will be INSTANT!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Required for multiprocessing on macOS/Windows
    mp.set_start_method('spawn', force=True)
    main()
