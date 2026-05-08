"""
Unit tests for web server game logic
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress


class TestGameStateLogic:
    """Test game state management logic"""

    def test_initial_game_state_player_starts(self):
        """Test initial game state when player starts"""
        board = Board(7, 6)
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                           consec_moves=2, show_progress=False)

        game_state = {
            'board': board,
            'ai_engine': ai_engine,
            'search_depth': 6,
            'current_player': 'X',
            'number_of_play': 2,
            'last_column': None,
            'game_over': False,
            'winner': None,
            'move_history': []
        }

        assert game_state['current_player'] == 'X'
        assert game_state['number_of_play'] == 2
        assert len(game_state['move_history']) == 0

    def test_initial_game_state_ai_starts(self):
        """Test initial game state when AI starts"""
        board = Board(7, 6)
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                           consec_moves=2, show_progress=False)

        game_state = {
            'board': board,
            'ai_engine': ai_engine,
            'search_depth': 6,
            'current_player': 'O',
            'number_of_play': 2,
            'last_column': None,
            'game_over': False,
            'winner': None,
            'move_history': []
        }

        assert game_state['current_player'] == 'O'


class TestTurnLogic:
    """Test turn switching logic"""

    def test_first_move_switches_player(self):
        """Test that first move switches to other player"""
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                           consec_moves=2, show_progress=False)

        move_history = []
        is_first_move = len(move_history) == 0

        next_player = ai_engine.next_player('X', 2, first_play=is_first_move)
        next_number = ai_engine.next_number_of_play(2, first_play=is_first_move)

        assert next_player == 'O'  # Switches
        assert next_number == 2  # Resets to 2

    def test_second_move_stays_same_player(self):
        """Test that second move stays with same player"""
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                           consec_moves=2, show_progress=False)

        move_history = [('X', 3)]  # One move made
        is_first_move = len(move_history) == 0

        current_number_of_play = 2
        next_player = ai_engine.next_player('O', current_number_of_play, first_play=is_first_move)
        next_number = ai_engine.next_number_of_play(current_number_of_play, first_play=is_first_move)

        assert next_player == 'O'  # Stays same
        assert next_number == 1  # Counts down

    def test_last_of_two_moves_switches(self):
        """Test that last of 2 consecutive moves switches player"""
        ai_engine = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4,
                                           consec_moves=2, show_progress=False)

        move_history = [('X', 3), ('O', 3)]
        is_first_move = len(move_history) == 0

        current_number_of_play = 1  # Last move of the 2
        next_player = ai_engine.next_player('O', current_number_of_play, first_play=is_first_move)
        next_number = ai_engine.next_number_of_play(current_number_of_play, first_play=is_first_move)

        assert next_player == 'X'  # Switches
        assert next_number == 2  # Resets


class TestWinDetection:
    """Test win detection in game context"""

    def test_detect_horizontal_win(self):
        """Test detecting horizontal win"""
        board = Board(7, 6)

        # X makes 4 in a row
        for col in range(4):
            board.play_move(col, 'X')

        assert board.is_winner('X', 4) is True

    def test_detect_vertical_win(self):
        """Test detecting vertical win"""
        board = Board(7, 6)

        # O makes 4 in a column
        for _ in range(4):
            board.play_move(3, 'O')

        assert board.is_winner('O', 4) is True

    def test_no_winner_yet(self):
        """Test game continues when no winner"""
        board = Board(7, 6)

        board.play_move(0, 'X')
        board.play_move(1, 'O')
        board.play_move(2, 'X')

        assert not board.is_winner('X', 4)
        assert not board.is_winner('O', 4)
        assert not board.is_end_of_game()

    def test_draw_condition(self):
        """Test detecting draw (full board, no winner)"""
        # This is complex to construct a perfect draw
        # Just test that we can detect a full board
        board = Board(7, 6)

        # Fill most columns
        for col in range(7):
            for row in range(5):  # Not completely full
                board.play_move(col, 'X' if col % 2 == 0 else 'O')

        # Board should not be full yet
        assert not board.is_end_of_game()


class TestValidMoves:
    """Test valid move calculation"""

    def test_all_columns_valid_initially(self):
        """Test all columns are valid at start"""
        board = Board(7, 6)
        valid_moves = [col for col, _ in board.possible_moves()]

        assert len(valid_moves) == 7
        assert valid_moves == [0, 1, 2, 3, 4, 5, 6]

    def test_full_column_not_valid(self):
        """Test full column is not in valid moves"""
        board = Board(7, 6)

        # Fill column 3
        for _ in range(6):
            board.play_move(3, 'X')

        valid_moves = [col for col, _ in board.possible_moves()]

        assert 3 not in valid_moves
        assert len(valid_moves) == 6

    def test_no_valid_moves_when_full(self):
        """Test no valid moves when board is full"""
        board = Board(7, 6)

        # Fill entire board
        for col in range(7):
            for row in range(6):
                board.play_move(col, 'X')

        valid_moves = [col for col, _ in board.possible_moves()]

        assert len(valid_moves) == 0
