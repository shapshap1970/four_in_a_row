"""
Opening book for Four-in-a-Row.
Pre-computed optimal opening moves to avoid expensive computation early in the game.
"""

import pickle
import gzip
from board import Board
from four_in_a_row_optimized import FourInARowOptimized


class OpeningBook:
    """
    Stores and retrieves optimal moves for early game positions.
    """

    def __init__(self, filename='opening_book.pkl.gz'):
        self.filename = filename
        self.book = {}  # board_hash -> (eval, best_move)

    def add_position(self, board_hash, eval_score, best_move):
        """Add a position to the opening book"""
        self.book[board_hash] = (eval_score, best_move)

    def lookup(self, board):
        """Look up a position in the opening book"""
        board_hash = board.to_hash()
        return self.book.get(board_hash)

    def save(self):
        """Save opening book to file"""
        with gzip.open(self.filename, 'wb') as f:
            pickle.dump(self.book, f)
        print(f"Opening book saved with {len(self.book)} positions")

    def load(self):
        """Load opening book from file"""
        try:
            with gzip.open(self.filename, 'rb') as f:
                self.book = pickle.load(f)
            print(f"Opening book loaded with {len(self.book)} positions")
            return True
        except FileNotFoundError:
            print("No opening book found")
            return False

    def generate_book(self, rows=6, cols=7, consec_to_win=4, consec_moves=2,
                      max_moves=6, search_depth=8):
        """
        Generate opening book by computing optimal moves for first few moves.

        Args:
            max_moves: Generate book for first N moves
            search_depth: How deep to search for each position
        """
        print(f"Generating opening book for first {max_moves} moves...")
        game = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)

        def explore_position(board, move_count, current_player, number_of_play, first_play):
            """Recursively explore positions"""
            if move_count > max_moves:
                return

            board_hash = board.to_hash()

            # Skip if already in book
            if board_hash in self.book:
                return

            # Compute best move for this position
            print(f"Computing move {move_count}, player={current_player}, "
                  f"number_of_play={number_of_play}...")

            eval_score, best_move = game.minimax_alpha_beta(
                board, search_depth, -math.inf, math.inf,
                current_player, number_of_play, None, first_play
            )

            self.add_position(board_hash, eval_score, best_move)
            print(f"  Added: eval={eval_score}, move={best_move}")

            # Explore child positions
            if best_move is not None and move_count < max_moves:
                new_board = Board(board)
                new_board.play_move(best_move, current_player)

                next_player = game.next_player(current_player, number_of_play, first_play)
                next_number = game.next_number_of_play(number_of_play, first_play)

                explore_position(new_board, move_count + 1, next_player,
                               next_number, False)

        # Start with empty board, X goes first with 1 move
        import math
        empty_board = Board(cols, rows)
        explore_position(empty_board, 1, 'X', 1, True)

        self.save()
        print(f"Opening book generation complete!")


class GameWithOpeningBook:
    """
    Wrapper that uses opening book for early game, then switches to full search.
    """

    def __init__(self, rows=6, cols=7, consec_to_win=4, consec_moves=2,
                 opening_book_file='opening_book.pkl.gz'):
        self.game = FourInARowOptimized(rows, cols, consec_to_win, consec_moves)
        self.opening_book = OpeningBook(opening_book_file)
        self.opening_book.load()  # Load if exists
        self.move_count = 0

    def get_best_move(self, board, current_player, number_of_play,
                      last_column=None, max_time=5.0):
        """
        Get best move, using opening book if available, otherwise search.
        """
        self.move_count += 1

        # Try opening book first (for early game)
        if self.move_count <= 8:  # Use book for first 8 moves
            result = self.opening_book.lookup(board)
            if result is not None:
                eval_score, best_move = result
                print(f"Move {self.move_count}: Using opening book "
                      f"(eval={eval_score}, move={best_move})")
                return eval_score, best_move

        # Fall back to regular search
        print(f"Move {self.move_count}: Computing move...")
        return self.game.get_best_move(board, current_player, number_of_play,
                                       last_column, max_time)

    def reset_move_count(self):
        """Reset move counter for new game"""
        self.move_count = 0
