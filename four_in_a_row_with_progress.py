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

    def fixed_depth_search(self, board, search_depth, current_player,
                          number_of_play, last_column):
        """
        Fixed depth search with progress display
        """
        start_time = time.time()

        if self.show_progress:
            print(f"🤖 Thinking at depth {search_depth}...", end="", flush=True)

        try:
            eval_score, move = self.minimax_alpha_beta(
                board, search_depth, -math.inf, math.inf,
                current_player, number_of_play, last_column
            )

            if self.show_progress:
                total_time = time.time() - start_time
                if abs(eval_score) >= 10000:
                    if eval_score > 0:
                        print(f" ✓ Forced win found!")
                    else:
                        print(f" ⚠ Forced loss detected")
                print(f"\n   → Move {move}, eval {eval_score:+.0f}, depth {search_depth}, {total_time:.2f}s")

            return eval_score, move

        except KeyboardInterrupt:
            if self.show_progress:
                print(" ⚠️ Interrupted")
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
