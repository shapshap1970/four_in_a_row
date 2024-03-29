from four_in_a_row import FourInARow
from board import Board
import pickle
import os
from display import print_message


def print_huristic_message(max_eval):
    if max_eval == 2:
        huristic = 'X is the winner if plays optimal'
    elif max_eval == -2:
        huristic = 'O is the winner if plays optimal'
    else:
        huristic = 'No winner if both players play smart!'
    print_message(huristic)


def train_model(game: FourInARow, play_board, rows, cols, consec_moves):
    file = f'memoization_cache.pkl-{rows}-{cols}-{consec_moves}'
    if os.path.exists(file):
        return
    game.minimax(play_board, 25, 'X', consec_moves, None, consec_moves == 2)
    with open(f'memoization_cache.pkl-{rows}-{cols}-{consec_moves}', 'wb') as fp:
        pickle.dump(game.memoization, fp)
    print_message('model saved successfully to file')


def load_model(game: FourInARow, rows, cols, consec_moves):
    print_message('loading model....')
    with open(f'memoization_cache.pkl-{rows}-{cols}-{consec_moves}', 'rb') as fp:
        game.memoization = pickle.load(fp)
    print_message('dictionary successfully loaded')


def main():
    CONSEC_TO_WIN = 4
    CONSEC_MOVES = 2
    ROWS = 5
    COLS = 5
    game = FourInARow(ROWS, COLS, CONSEC_TO_WIN, CONSEC_MOVES)
    play_board = Board(ROWS, COLS)
    train_model(game, play_board, ROWS, COLS, CONSEC_MOVES)
    load_model(game, ROWS, COLS, CONSEC_MOVES)
    play_board.print_board()
    game_run = True
    col = int(input("Enter the column number to drop: "))
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
            while True:
                col = int(input("Enter the column number to drop: "))
                if not play_board.is_possible_move(col):
                    print_message('Not a valid move, please try again...')
                else:
                    break
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
