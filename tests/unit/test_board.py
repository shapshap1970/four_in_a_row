"""
Unit tests for Board class
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from board import Board


class TestBoardInitialization:
    """Test board initialization"""

    def test_create_empty_board(self):
        """Test creating an empty board"""
        board = Board(7, 6)
        assert board.cols == 7
        assert board.rows == 6
        assert len(board.board) == 6
        assert len(board.board[0]) == 7
        assert all(cell == ' ' for row in board.board for cell in row)

    def test_create_board_copy(self):
        """Test creating a board copy"""
        original = Board(7, 6)
        original.play_move(3, 'X')
        copy = Board(original)

        assert copy.cols == original.cols
        assert copy.rows == original.rows
        assert copy.board == original.board
        assert copy.board is not original.board  # Different object
        assert copy.max_hight == original.max_hight

    def test_max_height_initialization(self):
        """Test max_height is initialized correctly"""
        board = Board(7, 6)
        for col in range(7):
            assert board.max_hight[col] == 5  # Bottom row


class TestBoardMoves:
    """Test board move operations"""

    def test_possible_moves_empty_board(self):
        """Test possible moves on empty board"""
        board = Board(7, 6)
        moves = board.possible_moves()
        assert len(moves) == 7
        assert moves == [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5)]

    def test_is_possible_move(self):
        """Test checking if move is possible"""
        board = Board(7, 6)
        assert board.is_possible_move(0) is True
        assert board.is_possible_move(6) is True
        assert board.is_possible_move(-1) is False
        assert board.is_possible_move(7) is False

    def test_play_move(self):
        """Test playing a move"""
        board = Board(7, 6)
        board.play_move(3, 'X')

        assert board.board[5][3] == 'X'
        assert board.max_hight[3] == 4

    def test_column_fills_up(self):
        """Test that column becomes unavailable when full"""
        board = Board(7, 6)

        # Fill column 3
        for i in range(6):
            board.play_move(3, 'X')

        assert board.max_hight[3] == -1
        assert not board.is_possible_move(3)
        assert (3, 5) not in board.possible_moves()

    def test_stacking_pieces(self):
        """Test pieces stack correctly"""
        board = Board(7, 6)
        board.play_move(2, 'X')
        board.play_move(2, 'O')
        board.play_move(2, 'X')

        assert board.board[5][2] == 'X'
        assert board.board[4][2] == 'O'
        assert board.board[3][2] == 'X'
        assert board.max_hight[2] == 2


class TestBoardWinConditions:
    """Test win detection"""

    def test_horizontal_win(self):
        """Test horizontal 4-in-a-row detection"""
        board = Board(7, 6)
        # Place 4 in a row horizontally
        for col in range(4):
            board.play_move(col, 'X')

        assert board.is_winner('X', 4) is True
        assert not board.is_winner('O', 4)

    def test_vertical_win(self):
        """Test vertical 4-in-a-row detection"""
        board = Board(7, 6)
        # Place 4 in a column vertically
        for _ in range(4):
            board.play_move(3, 'O')

        assert board.is_winner('O', 4) is True
        assert not board.is_winner('X', 4)

    def test_diagonal_down_right_win(self):
        """Test diagonal (down-right) win"""
        board = Board(7, 6)

        # Create diagonal: (5,0), (4,1), (3,2), (2,3)
        board.play_move(0, 'X')

        board.play_move(1, 'O')
        board.play_move(1, 'X')

        board.play_move(2, 'O')
        board.play_move(2, 'O')
        board.play_move(2, 'X')

        board.play_move(3, 'O')
        board.play_move(3, 'O')
        board.play_move(3, 'O')
        board.play_move(3, 'X')

        assert board.is_winner('X', 4) is True

    def test_diagonal_up_right_win(self):
        """Test diagonal (up-right) win"""
        board = Board(7, 6)

        # Create diagonal going up-right
        board.play_move(0, 'O')
        board.play_move(0, 'O')
        board.play_move(0, 'O')
        board.play_move(0, 'X')

        board.play_move(1, 'O')
        board.play_move(1, 'O')
        board.play_move(1, 'X')

        board.play_move(2, 'O')
        board.play_move(2, 'X')

        board.play_move(3, 'X')

        assert board.is_winner('X', 4) is True

    def test_no_winner_yet(self):
        """Test when no winner exists"""
        board = Board(7, 6)
        board.play_move(0, 'X')
        board.play_move(1, 'O')
        board.play_move(2, 'X')

        assert not board.is_winner('X', 4)
        assert not board.is_winner('O', 4)


class TestBoardGameEnd:
    """Test game end conditions"""

    def test_board_not_full(self):
        """Test board is not considered full initially"""
        board = Board(7, 6)
        assert board.is_end_of_game() is False

    def test_board_full(self):
        """Test board becomes full"""
        board = Board(7, 6)

        # Fill entire board
        for col in range(7):
            for row in range(6):
                board.play_move(col, 'X' if (col + row) % 2 == 0 else 'O')

        assert board.is_end_of_game() is True
        assert len(board.possible_moves()) == 0


class TestBoardHash:
    """Test board hashing"""

    def test_empty_board_hash(self):
        """Test hashing empty board"""
        board = Board(7, 6)
        hash_val = board.to_hash()
        assert isinstance(hash_val, int)
        assert hash_val >= 0

    def test_different_boards_different_hash(self):
        """Test different boards have different hashes"""
        board1 = Board(7, 6)
        board2 = Board(7, 6)

        board1.play_move(3, 'X')
        board2.play_move(4, 'X')

        assert board1.to_hash() != board2.to_hash()

    def test_same_boards_same_hash(self):
        """Test identical boards have same hash"""
        board1 = Board(7, 6)
        board2 = Board(7, 6)

        board1.play_move(3, 'X')
        board1.play_move(4, 'O')

        board2.play_move(3, 'X')
        board2.play_move(4, 'O')

        assert board1.to_hash() == board2.to_hash()
