from collections import defaultdict
import copy
import display 


class Board:
    def __init__(self, *args):
        if len(args) == 2:
            self.cols = args[0]
            self.rows = args[1]
            self.board = [[' ' for _ in range(self.cols)]
                          for _ in range(self.rows)]
            self.max_hight = defaultdict(lambda: self.rows-1)
        else:
            board_obj = args[0]
            self.board = copy.deepcopy(board_obj.board)
            self.cols = board_obj.cols
            self.rows = board_obj.rows
            self.max_hight = copy.deepcopy(board_obj.max_hight)

    def to_string(self):
        value = str(self.board)
        return value

    def print_board(self):
        display.print_board(self)

    def possible_moves(self):
        return [(i, self.max_hight[i]) for i in range(self.cols) if self.max_hight[i] != -1]

    def play_move(self, col, current_player, to_print=False):
        col_max_hight = self.max_hight[col]
        self.board[col_max_hight][col] = current_player
        self.max_hight[col] -= 1
        if (to_print):
            self.print_board()
    
    def is_possible_move(self, col):
        return True if self.max_hight[col] != -1 else False

    def is_end_of_game(self):
        return len(self.possible_moves()) == 0

    def is_winner(self, player, consecutive):
        for row in range(self.rows):
            for col in range(self.cols - consecutive + 1):
                if all(self.board[row][col + i] == player for i in range(consecutive)):
                    return True

        for col in range(self.cols):
            for row in range(self.rows - consecutive + 1):
                if all(self.board[row + i][col] == player for i in range(consecutive)):
                    return True

        for row in range(self.rows - consecutive + 1):
            for col in range(self.cols - consecutive + 1):
                if all(self.board[row + i][col + i] == player for i in range(consecutive)):
                    return True

        for row in range(consecutive - 1, self.rows):
            for col in range(self.cols - consecutive + 1):
                if all(self.board[row - i][col + i] == player for i in range(consecutive)):
                    return True
