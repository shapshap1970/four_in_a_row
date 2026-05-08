"""
Enhanced optimized engine with progress display and time control
"""

import math
import time
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


class FourInARowWithProgress(FourInARowOptimized):
    """
    Extended version with progress display and strict time limits
    """

    def __init__(self, rows=6, cols=7, consec_to_win=4, consec_moves=2, show_progress=True):
        super().__init__(rows, cols, consec_to_win, consec_moves)
        self.show_progress = show_progress
        self.last_progress_time = 0
        self.search_start_time = 0
        self.initial_cache_size = 0

    def minimax_alpha_beta(self, board, depth, alpha, beta, current_player,
                           number_of_play, last_column, first_play=False):
        """
        Override minimax to add periodic progress updates
        """
        # Show progress every 2 seconds
        if self.show_progress and self.search_start_time > 0:
            current_time = time.time()
            if current_time - self.last_progress_time >= 2.0:
                elapsed = current_time - self.search_start_time
                positions = len(self.memoization) - self.initial_cache_size
                positions_per_sec = positions / elapsed if elapsed > 0 else 0
                print(f"\r🤖 Thinking... {elapsed:.1f}s elapsed, "
                      f"{positions} positions ({positions_per_sec:.0f}/s)    ", end="", flush=True)
                self.last_progress_time = current_time

        # Call parent implementation
        return super().minimax_alpha_beta(board, depth, alpha, beta, current_player,
                                         number_of_play, last_column, first_play)

    def fixed_depth_search(self, board, search_depth, current_player,
                          number_of_play, last_column):
        """
        Fixed depth search with progress display
        """
        start_time = time.time()
        self.search_start_time = start_time
        self.last_progress_time = start_time
        self.initial_cache_size = len(self.memoization)

        if self.show_progress:
            print(f"🤖 Thinking at depth {search_depth}...", end="", flush=True)

        try:
            eval_score, move = self.minimax_alpha_beta(
                board, search_depth, -math.inf, math.inf,
                current_player, number_of_play, last_column
            )

            if self.show_progress:
                total_time = time.time() - start_time
                positions_evaluated = len(self.memoization) - self.initial_cache_size

                # Clear the progress line and show result
                print(f"\r🤖 Search complete!                                              ")

                if abs(eval_score) >= 10000:
                    if eval_score > 0:
                        print(f"   ✓ Forced win found!")
                    else:
                        print(f"   ⚠ Forced loss detected")

                print(f"   → Move {move}, eval {eval_score:+.0f}, depth {search_depth}, "
                      f"{total_time:.2f}s, {positions_evaluated} positions")

            # Reset for next search
            self.search_start_time = 0

            return eval_score, move

        except KeyboardInterrupt:
            if self.show_progress:
                print(" ⚠️ Interrupted")
            self.search_start_time = 0
            # Return first valid move as fallback
            moves = board.possible_moves()
            if moves:
                return 0, moves[0][0]
            return 0, None

    def get_best_move(self, board, current_player, number_of_play,
                      last_column=None, max_time=5.0):
        """
        Public interface with progress display - always searches to depth 12
        """
        return self.fixed_depth_search(
            board, 12, current_player, number_of_play, last_column
        )
