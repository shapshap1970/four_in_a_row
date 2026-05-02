#!/usr/bin/env python3
"""
Opening Book Generator for Four-in-a-Row
Generates pre-computed moves for the opening phase
"""

import gzip
import json
import time
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


class OpeningBookGenerator:
    """Generate opening book with optimal moves"""

    def __init__(self, rows=6, cols=7, consec_to_win=4, consec_moves=2,
                 book_depth=8, search_depth=8, filename='opening_book_7x6.json.gz'):
        self.rows = rows
        self.cols = cols
        self.consec_to_win = consec_to_win
        self.consec_moves = consec_moves
        self.book_depth = book_depth  # First N moves
        self.search_depth = search_depth  # Search depth
        self.filename = filename
        self.book = {}
        self.engine = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)
        self.positions_evaluated = 0
        self.start_time = None

    def generate_position(self, board, current_player, number_of_play,
                         move_count, first_play=False):
        """Recursively generate book positions"""

        if move_count >= self.book_depth:
            return

        # Evaluate this position
        board_hash = board.to_hash()
        key = str(board_hash)

        if key not in self.book:
            # Calculate best move for this position
            eval_score, best_move = self.engine.minimax_alpha_beta(
                board, self.search_depth, -float('inf'), float('inf'),
                current_player, number_of_play, None, first_play
            )

            self.book[key] = [eval_score, best_move]
            self.positions_evaluated += 1

            # Progress indicator
            elapsed = time.time() - self.start_time
            positions_per_sec = self.positions_evaluated / elapsed if elapsed > 0 else 0
            print(f"\r🔍 Evaluating position {self.positions_evaluated} "
                  f"(move {move_count + 1}, {positions_per_sec:.1f} pos/s, "
                  f"{elapsed/60:.1f}m elapsed)", end="", flush=True)
        else:
            # Already evaluated, use cached result
            eval_score, best_move = self.book[key]

        # Generate all possible next positions
        for move in board.possible_moves():
            col = move[0]
            next_board = Board(board)
            next_board.play_move(col, current_player)

            # Check if game ended
            if next_board.is_winner(current_player, self.consec_to_win):
                continue
            if next_board.is_end_of_game():
                continue

            # Determine next player and number of plays
            if number_of_play == 1 or first_play:
                next_player = 'O' if current_player == 'X' else 'X'
                next_number_of_play = self.consec_moves
            else:
                next_player = current_player
                next_number_of_play = number_of_play - 1

            # Recursively generate
            self.generate_position(
                next_board, next_player, next_number_of_play,
                move_count + 1, first_play=False
            )

    def generate(self):
        """Generate complete opening book"""
        print("\n" + "="*60)
        print("🏗️  OPENING BOOK GENERATOR")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Board: {self.cols}x{self.rows}")
        print(f"  Win: {self.consec_to_win} in a row")
        print(f"  Moves per turn: {self.consec_moves}")
        print(f"  Book depth: First {self.book_depth} moves")
        print(f"  Search depth: {self.search_depth} plies")
        print(f"\n⏱️  Estimated time: 15-30 minutes")
        print(f"📁 Output: {self.filename}")
        print("="*60)
        print("\n\n🚀 Starting generation...\n")

        self.start_time = time.time()

        # Start from initial position
        board = Board(self.cols, self.rows)
        self.generate_position(board, 'X', 1, 0, first_play=True)

        elapsed = time.time() - self.start_time
        print(f"\n\n✅ Generation complete!")
        print(f"   Positions evaluated: {self.positions_evaluated}")
        print(f"   Time taken: {elapsed/60:.1f} minutes")
        print(f"   Positions cached: {len(self.book)}")

    def save(self):
        """Save opening book to compressed JSON file"""
        print(f"\n💾 Saving to {self.filename}...")

        with gzip.open(self.filename, 'wt', encoding='utf-8') as f:
            json.dump(self.book, f, indent=2)

        import os
        size_mb = os.path.getsize(self.filename) / (1024 * 1024)
        print(f"   ✓ Saved {len(self.book)} positions ({size_mb:.1f} MB)")

    def load(self):
        """Load existing opening book"""
        try:
            with gzip.open(self.filename, 'rt', encoding='utf-8') as f:
                self.book = json.load(f)
            return True
        except FileNotFoundError:
            return False


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎮 FOUR-IN-A-ROW OPENING BOOK GENERATOR")
    print("="*60)

    print("\nSelect configuration:")
    print("1. Recommended (8 moves, 8 depth) - ~15 minutes")
    print("2. Deep (10 moves, 8 depth) - ~30-60 minutes")
    print("3. Custom")

    choice = input("\nSelect (1-3, default=1): ").strip() or "1"

    if choice == "1":
        book_depth = 8
        search_depth = 8
        desc = "Recommended opening book (8 moves, ~15 minutes)"
    elif choice == "2":
        book_depth = 10
        search_depth = 8
        desc = "Deep opening book (10 moves, ~30-60 minutes)"
    else:
        try:
            book_depth = int(input("Book depth (moves to pre-compute, default=8): ").strip() or "8")
            search_depth = int(input("Search depth (plies per move, default=8): ").strip() or "8")
            desc = f"Custom opening book ({book_depth} moves, depth {search_depth})"
        except:
            book_depth = 8
            search_depth = 8
            desc = "Default opening book"

    print(f"\n📝 {desc}")

    filename = input("\nOutput filename (default=opening_book_7x6.json.gz): ").strip()
    if not filename:
        filename = "opening_book_7x6.json.gz"

    # Confirmation
    print(f"\n⚠️  This will generate an opening book:")
    print(f"   - First {book_depth} moves will be pre-computed")
    print(f"   - Search depth: {search_depth} plies")
    print(f"   - Estimated time: {15 * (book_depth/8):.0f} minutes")
    print(f"   - Output: {filename}")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Generate
    generator = OpeningBookGenerator(
        rows=6, cols=7,
        consec_to_win=4, consec_moves=2,
        book_depth=book_depth,
        search_depth=search_depth,
        filename=filename
    )

    generator.generate()
    generator.save()

    print("\n" + "="*60)
    print("✅ OPENING BOOK READY!")
    print("="*60)
    print("\nTo use the opening book:")
    print("1. Copy the file to your game directory")
    print("2. Run play_game_beautiful.py")
    print(f"3. First {book_depth} moves will be INSTANT!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
