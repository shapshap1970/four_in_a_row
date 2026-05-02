#!/usr/bin/env python3
"""
Generate opening book for fast gameplay
Pre-computes first N moves deeply so gameplay is instant

SECURITY: Uses JSON instead of pickle to prevent code execution vulnerabilities.
"""

import json
import gzip
import time
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


class OpeningBookGenerator:
    """Generates and manages opening book using secure JSON format"""

    def __init__(self, filename='opening_book.json.gz'):
        # Convert .pkl.gz to .json.gz if needed
        if filename.endswith('.pkl.gz'):
            filename = filename.replace('.pkl.gz', '.json.gz')
        self.filename = filename
        self.book = {}

    def generate_comprehensive(self, rows=6, cols=7, consec_to_win=4, consec_moves=2,
                               max_moves=10, search_depth=12):
        """
        Generate comprehensive opening book

        Args:
            max_moves: Generate book for first N moves (10 = ~20 turns)
            search_depth: How deep to search each position (12 = very strong)
        """
        print("="*60)
        print("🏗️  OPENING BOOK GENERATOR")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Board: {cols}x{rows}")
        print(f"  Win: {consec_to_win} in a row")
        print(f"  Moves per turn: {consec_moves}")
        print(f"  Book depth: First {max_moves} moves")
        print(f"  Search depth: {search_depth} plies")
        print(f"\n⏱️  Estimated time: 10-30 minutes")
        print(f"📁 Output: {self.filename}")
        print("="*60)

        game = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)
        start_time = time.time()
        positions_evaluated = [0]  # Use list to allow modification in nested function

        def explore_position(board, move_count, current_player, number_of_play,
                           first_play, path=""):
            """Recursively explore and cache positions"""

            if move_count > max_moves:
                return

            board_hash = board.to_hash()

            # Skip if already in book
            if board_hash in self.book:
                return

            # Compute best move for this position
            positions_evaluated[0] += 1

            if positions_evaluated[0] % 10 == 1:
                elapsed = time.time() - start_time
                rate = positions_evaluated[0] / elapsed if elapsed > 0 else 0
                print(f"\r🔍 Evaluating position {positions_evaluated[0]:,} "
                      f"(move {move_count}, {rate:.1f} pos/s, {elapsed/60:.1f}m elapsed)",
                      end="", flush=True)

            eval_score, best_move = game.minimax_alpha_beta(
                board, search_depth, -float('inf'), float('inf'),
                current_player, number_of_play, None, first_play
            )

            # Convert board_hash to string for JSON compatibility
            key = str(board_hash)
            self.book[key] = (eval_score, best_move)

            # Explore main continuation
            if best_move is not None and move_count < max_moves:
                new_board = Board(board)
                new_board.play_move(best_move, current_player)

                next_player = game.next_player(current_player, number_of_play, first_play)
                next_number = game.next_number_of_play(number_of_play, first_play)

                explore_position(new_board, move_count + 1, next_player,
                               next_number, False, path + f"-{best_move}")

        # Start from empty board
        empty_board = Board(cols, rows)
        print("\n\n🚀 Starting generation...\n")
        explore_position(empty_board, 1, 'X', 1, True, "start")

        elapsed = time.time() - start_time
        print(f"\n\n✅ Generation complete!")
        print(f"   Positions evaluated: {positions_evaluated[0]:,}")
        print(f"   Time taken: {elapsed/60:.1f} minutes")
        print(f"   Positions cached: {len(self.book):,}")

        # Save to file
        self.save()

    def save(self):
        """Save opening book to file using secure JSON format"""
        print(f"\n💾 Saving to {self.filename}...")
        with gzip.open(self.filename, 'wt', encoding='utf-8') as f:
            json.dump(self.book, f, indent=2)

        import os
        size_mb = os.path.getsize(self.filename) / (1024 * 1024)
        print(f"   ✓ Saved {len(self.book):,} positions ({size_mb:.1f} MB)")

    def load(self):
        """Load opening book from file (JSON format)"""
        try:
            with gzip.open(self.filename, 'rt', encoding='utf-8') as f:
                self.book = json.load(f)
            print(f"✓ Loaded {len(self.book):,} positions from {self.filename}")
            return True
        except FileNotFoundError:
            print(f"✗ Opening book not found: {self.filename}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Error loading opening book: {e}")
            return False


if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("🎮 FOUR-IN-A-ROW OPENING BOOK GENERATOR")
    print("="*60)

    # Configuration
    print("\nSelect configuration:")
    print("1. Standard (7x6, 10 moves, 12 depth) - Recommended")
    print("2. Quick (7x6, 6 moves, 10 depth) - Faster generation")
    print("3. Deep (7x6, 12 moves, 14 depth) - Best play, slow generation")
    print("4. Custom")

    choice = input("\nSelect (1-4, default=1): ").strip() or "1"

    if choice == "2":
        max_moves, search_depth = 6, 10
        print("\n📝 Quick opening book (6 moves, ~5 minutes)")
    elif choice == "3":
        max_moves, search_depth = 12, 14
        print("\n📝 Deep opening book (12 moves, ~60 minutes)")
    elif choice == "4":
        max_moves = int(input("Max moves to cache (6-15): "))
        search_depth = int(input("Search depth (8-16): "))
    else:
        max_moves, search_depth = 10, 12
        print("\n📝 Standard opening book (10 moves, ~15 minutes)")

    filename = input(f"\nOutput filename (default=opening_book_7x6.json.gz): ").strip()
    if not filename:
        filename = "opening_book_7x6.json.gz"
    elif filename.endswith('.pkl.gz'):
        filename = filename.replace('.pkl.gz', '.json.gz')
        print(f"   → Using JSON format: {filename}")

    # Confirm
    print(f"\n⚠️  This will generate an opening book:")
    print(f"   - First {max_moves} moves will be pre-computed")
    print(f"   - Search depth: {search_depth} plies")
    print(f"   - Estimated time: {max_moves} minutes")
    print(f"   - Output: {filename}")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Generate
    generator = OpeningBookGenerator(filename)
    generator.generate_comprehensive(
        rows=6, cols=7,
        consec_to_win=4,
        consec_moves=2,
        max_moves=max_moves,
        search_depth=search_depth
    )

    print("\n" + "="*60)
    print("✅ OPENING BOOK READY!")
    print("="*60)
    print(f"\nTo use the opening book:")
    print(f"1. Copy {filename} to your game directory")
    print(f"2. Use play_game_fast.py (it will auto-load the book)")
    print(f"3. First {max_moves} moves will be INSTANT!")
    print("="*60)
