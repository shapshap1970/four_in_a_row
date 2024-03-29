import math
from board import Board


class FourInARow:
    def __init__(self, rows=3, cols=3, consecutive=3, max_play=2):
        self.rows = rows
        self.cols = cols
        self.consecutive = consecutive
        self.max_play = max_play
        self.memoization = {}

    def is_winner(self, player, board):
        return board.is_winner(player, self.consecutive)

    def possible_moves(self, board):
        return board.possible_moves()

    def switch_player(self, current_player):
        return 'O' if current_player == 'X' else 'X'

    def play_move(self, col, current_player):
        self.board.play_move(col, current_player)

    ''' 2 X win
        1 draw
        None no win 
        -2 O wins
    '''

    def evaluate(self, board):
        if self.is_winner('X', board):
            return 2
        elif self.is_winner('O', board):
            return -2
        # case full board
        if board.is_end_of_game():
            return 1
        else:
            return None

    def next_player(self, current_player, number_of_play, first_play=False):
        if number_of_play == 1 or first_play:
            return self.switch_player(current_player)
        else:
            return current_player

    def next_number_of_play(self, number_of_play, first_play=False):
        if number_of_play == 1 or first_play:
            return self.max_play
        else:
            return number_of_play-1

    def minimax(self, board, depth, current_player, number_of_play, last_column, first_play=False):
        """
        Minimax algorithm implementation.
        """
        # Check if the game is over or depth limit reached
        if board.to_string() in self.memoization:
            return self.memoization[board.to_string()]
        result = self.evaluate(board)
        if result is not None or depth == 0:
            return result, last_column

        moves = board.possible_moves()
        if current_player == 'X':
            max_eval = -math.inf

            move = None
            max_move = None
            for move in moves:
                move_board = Board(board)
                move_board.play_move(move[0], current_player)
                eval, _ = self.minimax(
                    move_board,
                    depth-1,
                    self.next_player(
                        current_player, number_of_play, first_play),
                    self.next_number_of_play(number_of_play, first_play),
                    move[0]
                )
                if eval > max_eval:
                    max_eval = eval
                    max_move = move[0]
                if max_eval == 2:
                    break
            self.memoization[board.to_string()] = max_eval, max_move
            print(len(self.memoization))
            return max_eval, max_move
        else:
            min_eval = math.inf
            move = None
            min_move = None
            for move in moves:
                move_board = Board(board)
                move_board.play_move(move[0], current_player)
                eval, _ = self.minimax(
                    move_board,
                    depth-1,
                    self.next_player(current_player, number_of_play),
                    self.next_number_of_play(number_of_play),
                    move[0]
                )
                if eval < min_eval:
                    min_eval = eval
                    min_move = move[0]
                if min_eval == -2:
                    break
            print(len(self.memoization))
            self.memoization[board.to_string()] = min_eval, min_move
            return min_eval, min_move
