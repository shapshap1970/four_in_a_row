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

    def iterative_deepening_search(self, board, max_time_seconds, current_player,
                                    number_of_play, last_column):
        """
        Iterative deepening with progress display and strict time control
        """
        start_time = time.time()
        best_move = None
        best_eval = None
        depth = 1

        if self.show_progress:
            print("🤖 Thinking: ", end="", flush=True)

        # Always search at least depth 1
        while True:
            elapsed = time.time() - start_time

            # Strict time check - leave 0.5s buffer for cleanup
            if elapsed >= max_time_seconds - 0.5 and depth > 1:
                if self.show_progress:
                    print(f" ⏱️ Time limit reached")
                break

            try:
                depth_start = time.time()
                eval_score, move = self.minimax_alpha_beta(
                    board, depth, -math.inf, math.inf,
                    current_player, number_of_play, last_column
                )

                best_eval = eval_score
                best_move = move

                # Progress indicator
                if self.show_progress:
                    depth_time = time.time() - depth_start
                    print(f"[D{depth}={eval_score:+.0f}({depth_time:.1f}s)] ", end="", flush=True)

                # If found definite win/loss, stop early
                if abs(eval_score) >= 10000:
                    if self.show_progress:
                        if eval_score > 0:
                            print("✓ Found forced win!")
                        else:
                            print("⚠ Detected forced loss")
                    break

                depth += 1

                # Safety limit on depth
                if depth > 20:
                    if self.show_progress:
                        print(" 🎯 Max depth reached")
                    break

                # Check time again before starting next depth
                if time.time() - start_time >= max_time_seconds - 0.5:
                    if self.show_progress:
                        print(" ⏱️ Time limit")
                    break

            except KeyboardInterrupt:
                if self.show_progress:
                    print(" ⚠️ Interrupted")
                break

        if self.show_progress:
            total_time = time.time() - start_time
            print(f"\n   → Move {best_move}, eval {best_eval:+.0f}, depth {depth-1}, {total_time:.2f}s")

        return best_eval, best_move

    def get_best_move(self, board, current_player, number_of_play,
                      last_column=None, max_time=5.0):
        """
        Public interface with progress display
        """
        return self.iterative_deepening_search(
            board, max_time, current_player, number_of_play, last_column
        )
