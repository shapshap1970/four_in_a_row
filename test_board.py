import pytest
from board import Board


class TestBoardInitialization:
    """Test Board initialization and construction"""

    def test_board_creation_with_dimensions(self):
        """Test creating a board with specific dimensions"""
        board = Board(5, 5)  # cols=5, rows=5
        assert board.cols == 5
        assert board.rows == 5
        assert len(board.board) == 5  # rows
        assert len(board.board[0]) == 5  # cols

    def test_board_empty_on_creation(self):
        """Test that all cells are empty on creation"""
        board = Board(4, 4)
        for row in board.board:
            for cell in row:
                assert cell == ' '

    def test_max_height_initialization(self):
        """Test that max_height is properly initialized"""
        board = Board(4, 5)  # cols=4, rows=5
        for col in range(4):
            assert board.max_hight[col] == 4  # rows-1

    def test_board_copy_constructor(self):
        """Test creating a board from another board"""
        original = Board(3, 3)
        original.play_move(0, 'X')
        original.play_move(1, 'O')

        copy = Board(original)

        assert copy.rows == original.rows
        assert copy.cols == original.cols
        assert copy.board == original.board
        assert copy.max_hight == original.max_hight
        # Ensure deep copy
        copy.play_move(2, 'X')
        assert copy.board != original.board


class TestBoardMoves:
    """Test board move operations"""

    def test_play_move_basic(self):
        """Test basic move playing"""
        board = Board(5, 5)
        board.play_move(0, 'X')
        assert board.board[4][0] == 'X'
        assert board.max_hight[0] == 3

    def test_play_multiple_moves_same_column(self):
        """Test stacking pieces in the same column"""
        board = Board(5, 5)
        board.play_move(0, 'X')
        board.play_move(0, 'O')
        board.play_move(0, 'X')

        assert board.board[4][0] == 'X'
        assert board.board[3][0] == 'O'
        assert board.board[2][0] == 'X'
        assert board.max_hight[0] == 1

    def test_play_moves_different_columns(self):
        """Test playing moves in different columns"""
        board = Board(4, 4)
        board.play_move(0, 'X')
        board.play_move(1, 'O')
        board.play_move(2, 'X')

        assert board.board[3][0] == 'X'
        assert board.board[3][1] == 'O'
        assert board.board[3][2] == 'X'

    def test_fill_column_completely(self):
        """Test filling a column to the top"""
        board = Board(4, 4)
        for i in range(4):
            board.play_move(0, 'X')

        assert board.max_hight[0] == -1
        assert all(board.board[i][0] == 'X' for i in range(4))


class TestPossibleMoves:
    """Test possible moves detection"""

    def test_possible_moves_empty_board(self):
        """Test all moves are possible on empty board"""
        board = Board(5, 5)
        moves = board.possible_moves()
        assert len(moves) == 5
        assert all(col < 5 for col, _ in moves)

    def test_possible_moves_partial_board(self):
        """Test possible moves with some columns filled"""
        board = Board(3, 3)
        # Fill column 1 completely
        for _ in range(3):
            board.play_move(1, 'X')

        moves = board.possible_moves()
        assert len(moves) == 2
        assert (0, 2) in moves
        assert (2, 2) in moves
        assert (1, -1) not in moves

    def test_is_possible_move_valid(self):
        """Test checking if a move is possible"""
        board = Board(4, 4)
        assert board.is_possible_move(0) == True
        assert board.is_possible_move(3) == True

    def test_is_possible_move_invalid_column(self):
        """Test invalid column numbers"""
        board = Board(4, 4)
        assert board.is_possible_move(-1) == False
        assert board.is_possible_move(4) == False
        assert board.is_possible_move(10) == False

    def test_is_possible_move_full_column(self):
        """Test move is not possible in full column"""
        board = Board(3, 3)
        for _ in range(3):
            board.play_move(1, 'X')

        assert board.is_possible_move(1) == False
        assert board.is_possible_move(0) == True


class TestWinnerDetection:
    """Test winner detection in all directions"""

    def test_horizontal_win(self):
        """Test horizontal 4-in-a-row detection"""
        board = Board(5, 5)
        # Create horizontal line at bottom
        for col in range(4):
            board.play_move(col, 'X')

        assert board.is_winner('X', 4) == True
        assert board.is_winner('O', 4) != True  # Returns None, not False

    def test_vertical_win(self):
        """Test vertical 4-in-a-row detection"""
        board = Board(5, 5)
        # Create vertical line in column 0
        for _ in range(4):
            board.play_move(0, 'X')

        assert board.is_winner('X', 4) == True
        assert board.is_winner('O', 4) != True  # Returns None, not False

    def test_diagonal_down_right_win(self):
        """Test diagonal (top-left to bottom-right) win"""
        board = Board(5, 5)
        # Create diagonal: (4,0), (3,1), (2,2), (1,3)
        board.play_move(0, 'X')  # row 4, col 0

        board.play_move(1, 'O')  # row 4, col 1
        board.play_move(1, 'X')  # row 3, col 1

        board.play_move(2, 'O')  # row 4, col 2
        board.play_move(2, 'O')  # row 3, col 2
        board.play_move(2, 'X')  # row 2, col 2

        board.play_move(3, 'O')  # row 4, col 3
        board.play_move(3, 'O')  # row 3, col 3
        board.play_move(3, 'O')  # row 2, col 3
        board.play_move(3, 'X')  # row 1, col 3

        assert board.is_winner('X', 4) == True

    def test_diagonal_up_right_win(self):
        """Test diagonal (bottom-left to top-right) win"""
        board = Board(5, 5)
        # Create diagonal: (4,0), (3,1), (2,2), (1,3)
        board.play_move(0, 'O')  # row 4, col 0
        board.play_move(0, 'O')  # row 3, col 0
        board.play_move(0, 'O')  # row 2, col 0
        board.play_move(0, 'X')  # row 1, col 0

        board.play_move(1, 'O')  # row 4, col 1
        board.play_move(1, 'O')  # row 3, col 1
        board.play_move(1, 'X')  # row 2, col 1

        board.play_move(2, 'O')  # row 4, col 2
        board.play_move(2, 'X')  # row 3, col 2

        board.play_move(3, 'X')  # row 4, col 3

        assert board.is_winner('X', 4) == True

    def test_no_winner(self):
        """Test no winner detected"""
        board = Board(5, 5)
        board.play_move(0, 'X')
        board.play_move(1, 'O')
        board.play_move(2, 'X')

        assert board.is_winner('X', 4) != True  # Returns None when no winner
        assert board.is_winner('O', 4) != True  # Returns None when no winner

    def test_winner_with_more_than_4(self):
        """Test winner detection with more than 4 in a row"""
        board = Board(5, 5)
        for col in range(5):
            board.play_move(col, 'X')

        assert board.is_winner('X', 4) == True


class TestGameEnd:
    """Test end game detection"""

    def test_empty_board_not_end(self):
        """Test empty board is not end of game"""
        board = Board(5, 5)
        assert board.is_end_of_game() == False

    def test_full_board_is_end(self):
        """Test full board is end of game"""
        board = Board(3, 3)
        # Fill the entire board
        for col in range(3):
            for _ in range(3):
                board.play_move(col, 'X')

        assert board.is_end_of_game() == True

    def test_partial_board_not_end(self):
        """Test partially filled board is not end"""
        board = Board(4, 4)
        for col in range(2):
            for _ in range(4):
                board.play_move(col, 'X')

        assert board.is_end_of_game() == False


class TestBoardHashing:
    """Test board hashing functionality"""

    def test_empty_board_hash(self):
        """Test hashing of empty board"""
        board1 = Board(3, 3)
        board2 = Board(3, 3)
        assert board1.to_hash() == board2.to_hash()

    def test_different_boards_different_hash(self):
        """Test different board states have different hashes"""
        board1 = Board(3, 3)
        board2 = Board(3, 3)

        board1.play_move(0, 'X')
        board2.play_move(1, 'X')

        assert board1.to_hash() != board2.to_hash()

    def test_same_board_state_same_hash(self):
        """Test identical board states have same hash"""
        board1 = Board(3, 3)
        board2 = Board(3, 3)

        board1.play_move(0, 'X')
        board1.play_move(1, 'O')

        board2.play_move(0, 'X')
        board2.play_move(1, 'O')

        assert board1.to_hash() == board2.to_hash()

    def test_hash_consistency(self):
        """Test hash is consistent across multiple calls"""
        board = Board(3, 3)
        board.play_move(0, 'X')

        hash1 = board.to_hash()
        hash2 = board.to_hash()

        assert hash1 == hash2

    def test_hash_different_players(self):
        """Test X and O in same position produce different hashes"""
        board1 = Board(3, 3)
        board2 = Board(3, 3)

        board1.play_move(0, 'X')
        board2.play_move(0, 'O')

        assert board1.to_hash() != board2.to_hash()


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_minimum_board_size(self):
        """Test smallest possible board"""
        board = Board(1, 1)
        assert board.rows == 1
        assert board.cols == 1
        board.play_move(0, 'X')
        assert board.is_end_of_game() == True

    def test_rectangular_board(self):
        """Test non-square board dimensions"""
        board = Board(5, 3)  # cols=5, rows=3
        assert board.cols == 5
        assert board.rows == 3
        assert len(board.possible_moves()) == 5

    def test_winner_with_consecutive_3(self):
        """Test winner detection with consecutive=3"""
        board = Board(4, 4)
        board.play_move(0, 'X')
        board.play_move(1, 'X')
        board.play_move(2, 'X')

        assert board.is_winner('X', 3) == True
        assert board.is_winner('X', 4) != True  # Returns None when not enough consecutive
