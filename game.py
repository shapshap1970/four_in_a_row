from four_in_a_row import FourInARow
from board import Board
import pickle
import os
from display import print_message
import file_util

def print_huristic_message(max_eval):
    if max_eval == 2:
        huristic = 'X is the winner if plays optimal'
    elif max_eval == -2:
        huristic = 'O is the winner if plays optimal'
    else:
        huristic = 'No winner if both players play smart!'
    print_message(huristic)


def train_model(game: FourInARow, play_board, file):
    if os.path.exists(file):
        return
    game.minimax(play_board, 25, 'X', game.consec_moves, None, game.consec_moves == 2)
    file_util.save(game.memoization, file)
    print_message('model saved successfully to file')


def load_model(game: FourInARow, file):
    print_message('loading model....')
    game.memoization = file_util.load(file)
    print_message('dictionary successfully loaded')

def get_person_input(play_board):
    while True:
        try:
            col = int(input("Enter the column number to drop: "))
        except ValueError:
            print_message('Not a valid input, please try again...')
            continue
        if not play_board.is_possible_move(col):
            print_message('Not a valid move, please try again...')
        else:
            break
    return col

def main():
    CONSEC_TO_WIN = 4
    CONSEC_MOVES = 1
    ROWS = 4
    COLS = 4
    game = FourInARow(ROWS, COLS, CONSEC_TO_WIN, CONSEC_MOVES)
    play_board = Board(ROWS, COLS)
    file = f'memoization_cache.pkl-{ROWS}-{COLS}-{CONSEC_TO_WIN}-{CONSEC_MOVES}.zip'
    train_model(game, play_board, file)
    load_model(game, file)
    play_board.print_board()
    game_run = True
    col = get_person_input(play_board)
    play_board.play_move(col, 'X', True)
    while game_run:
        for i in range(CONSEC_MOVES):
            max_eval, best_move = game.minimax(
                play_board, 25, 'O', CONSEC_MOVES, col)
            print_huristic_message(max_eval)
            play_board.play_move(best_move, 'O', True)
            if game.evaluate(play_board) in [2, -2]:
                print_message("Game Over O wins")
                game_run = False
                break
            if play_board.is_end_of_game():
                print_message("Game Ended")
                game_run = False
                break
        if not game_run:
            break

        for _ in range(CONSEC_MOVES):
            col = get_person_input(play_board)
            play_board.play_move(col, 'X', True)
            if play_board.is_end_of_game():
                print_message("Game Ended")
                game_run = False
                break
            if game.evaluate(play_board) in [2, -2]:
                print_message("Game Over, X wins")
                game_run = False
                break


if __name__ == "__main__":
    main()
