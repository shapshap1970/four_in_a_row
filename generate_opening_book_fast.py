#!/usr/bin/env python3
"""
Ultra-Fast Parallelized Opening Book Generator
Optimized for maximum CPU utilization
"""

import gzip
import json
import time
import multiprocessing as mp
from multiprocessing import Pool, Manager
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


def worker_generate_position(args):
    """
    Worker: Generate one position (board state)
    Returns: (board_hash, [eval_score, best_move])
    """
    board_state, current_player, number_of_play, last_column, first_play, search_depth = args

    # Recreate board from state
    board = Board(7, 6)
    board.board = [row[:] for row in board_state]

    # Recalculate max_hight (note: typo in original Board class)
    from collections import defaultdict
    board.max_hight = defaultdict(lambda: board.rows-1)
    for col in range(board.cols):
        for row in range(board.rows):
            if board.board[row][col] != ' ':
                board.max_hight[col] = row - 1
                break

    # Create engine
    engine = FourInARowOptimized(6, 7, 4, 2)

    # Calculate best move
    eval_score, best_move = engine.minimax_alpha_beta(
        board, search_depth, -float('inf'), float('inf'),
        current_player, number_of_play, last_column, first_play
    )

    board_hash = str(board.to_hash())
    return board_hash, [eval_score, best_move]


def generate_all_positions(book_depth, search_depth):
    """
    Generate all positions up to book_depth in BFS manner
    Returns list of position arguments for parallel processing
    """
    positions_to_evaluate = []

    # BFS queue: (board, current_player, number_of_play, last_column, depth, first_play)
    queue = []

    # Start with empty board - player X to move
    initial_board = Board(7, 6)
    queue.append((initial_board, 'X', 2, None, 0, False))

    visited = set()

    while queue:
        board, player, num_play, last_col, depth, first_play = queue.pop(0)

        if depth >= book_depth:
            continue

        board_hash = str(board.to_hash())
        if board_hash in visited:
            continue
        visited.add(board_hash)

        # Add this position for evaluation
        board_state = [row[:] for row in board.board]
        positions_to_evaluate.append(
            (board_state, player, num_play, last_col, first_play, search_depth)
        )

        # Generate all next positions
        for col, _ in board.possible_moves():
            next_board = Board(board)
            next_board.play_move(col, player)

            # Skip if game ended
            if next_board.is_winner(player, 4) or next_board.is_end_of_game():
                continue

            # Determine next player
            is_first = (depth == 0)
            if num_play == 1 or is_first:
                next_player = 'O' if player == 'X' else 'X'
                next_num = 2
            else:
                next_player = player
                next_num = num_play - 1

            queue.append((next_board, next_player, next_num, col, depth + 1, is_first))

    return positions_to_evaluate


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🚀 ULTRA-FAST PARALLEL OPENING BOOK GENERATOR")
    print("="*70)

    # Configuration
    book_depth = 8
    search_depth = 8
    filename = "opening_book_7x6.json.gz"

    # Get CPU count
    cpu_count = mp.cpu_count()

    print(f"\nConfiguration:")
    print(f"  Board: 7x6")
    print(f"  Book depth: First {book_depth} moves")
    print(f"  Search depth: {search_depth} plies")
    print(f"  CPU cores: {cpu_count} (will use all)")
    print(f"  Strategy: BFS + parallel evaluation")
    print(f"\n⏱️  Estimated time: 10-30 minutes")
    print(f"📁 Output: {filename}")
    print("="*70)
    print("\n🚀 Starting generation...\n")

    print("📋 Phase 1: Generating position list (BFS)...")
    start_time = time.time()

    positions = generate_all_positions(book_depth, search_depth)

    gen_time = time.time() - start_time
    print(f"   ✓ Generated {len(positions)} positions to evaluate ({gen_time:.1f}s)")

    print(f"\n🚀 Phase 2: Parallel evaluation using {cpu_count} cores...")
    eval_start = time.time()

    # Process in parallel with progress tracking
    book = {}
    chunk_size = max(1, len(positions) // (cpu_count * 4))

    with Pool(processes=cpu_count) as pool:
        completed = 0
        for result in pool.imap_unordered(worker_generate_position, positions, chunksize=chunk_size):
            board_hash, value = result
            book[board_hash] = value
            completed += 1

            if completed % 100 == 0 or completed == len(positions):
                elapsed = time.time() - eval_start
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (len(positions) - completed) / rate if rate > 0 else 0
                print(f"   Progress: {completed}/{len(positions)} "
                      f"({completed*100/len(positions):.1f}%) - "
                      f"{rate:.1f} pos/s - "
                      f"ETA: {remaining/60:.1f}m", end='\r')

    print()  # New line after progress
    eval_time = time.time() - eval_start
    total_time = time.time() - start_time

    print(f"\n✅ Evaluation complete!")
    print(f"   Positions evaluated: {len(positions)}")
    print(f"   Unique board states: {len(book)}")
    print(f"   Evaluation time: {eval_time/60:.1f} minutes")
    print(f"   Total time: {total_time/60:.1f} minutes")
    print(f"   Speed: {len(positions)/eval_time:.1f} positions/second")

    # Save
    print(f"\n💾 Saving to {filename}...")
    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(book, f)

    import os
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"   ✓ Saved {len(book)} positions ({size_mb:.2f} MB)")

    print("\n" + "="*70)
    print("✅ OPENING BOOK READY!")
    print("="*70)
    print(f"\nThe web server will now use instant moves for first {book_depth} moves!")
    print("="*70 + "\n")


if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)
    main()
