#!/usr/bin/env python3
"""Interactive game analysis - AI starts"""

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress

def print_board(board):
    """Print board in CLI format"""
    print("\n╔═══════════════╗")
    print("║ 0 1 2 3 4 5 6 ║")
    print("╠═══════════════╣")
    for i, row in enumerate(board.board):
        print(f"║ {' '.join(row)} ║")
    print("╚═══════════════╝")
    print()

def play_game():
    """AI starts, you play as X"""
    board = Board(7, 6)  # cols, rows
    ai = FourInARowWithProgress(rows=6, cols=7, consec_to_win=4, consec_moves=2, show_progress=False)

    current_player = 'O'  # AI starts
    number_of_play = 1
    move_history = []

    print("🎮 Four-in-a-Row Analysis Game")
    print("AI (O) starts first. You are X.")
    print("Enter column number (0-6) for your moves.")
    print("Enter 'q' to quit\n")

    while True:
        print_board(board)

        # Check game over
        if board.is_winner('X', 4):
            print("🎉 You (X) won!")
            break
        if board.is_winner('O', 4):
            print("😔 AI (O) won!")
            break
        if board.is_end_of_game():
            print("🤝 Draw!")
            break

        if current_player == 'O':
            # AI move
            print(f"AI (O) thinking... (depth 12, {number_of_play} move{'s' if number_of_play > 1 else ''})")

            # Check if Rust extension is available
            try:
                from four_in_a_row_rust.four_in_a_row_rust import get_best_move as rust_get_best_move
                board_str = '\n'.join(''.join(row) for row in board.board)
                eval_score, best_col = rust_get_best_move(board_str, 12, 2, number_of_play)
                print(f"✓ Using Rust AI (score: {eval_score})")
            except ImportError:
                eval_score, best_col = ai.fixed_depth_search(
                    board, 12, 'O', number_of_play,
                    move_history[-1][1] if move_history else None
                )
                print(f"⚠ Using Python AI (score: {eval_score})")

            board.play_move(best_col, 'O')
            move_history.append(('O', best_col))
            print(f"AI played column {best_col}")

            # Update turn
            if number_of_play == 1:
                current_player = 'X'
                number_of_play = 2
            else:
                number_of_play -= 1
        else:
            # Human move
            valid_moves = [col for col, _ in board.possible_moves()]
            print(f"Your turn (X), {number_of_play} move{'s' if number_of_play > 1 else ''}")
            print(f"Valid columns: {valid_moves}")

            move_input = input("Enter column (0-6): ").strip()
            if move_input == 'q':
                print("Game quit.")
                break

            try:
                col = int(move_input)
                if col not in valid_moves:
                    print(f"❌ Invalid column! Choose from {valid_moves}")
                    continue

                board.play_move(col, 'X')
                move_history.append(('X', col))

                # Update turn
                if number_of_play == 1:
                    current_player = 'O'
                    number_of_play = 2
                else:
                    number_of_play -= 1

            except ValueError:
                print("❌ Invalid input! Enter a number 0-6")
                continue

    print("\n📊 Game Analysis:")
    print(f"Total moves: {len(move_history)}")
    print("Move history:")
    for i, (player, col) in enumerate(move_history, 1):
        print(f"  {i}. {player} -> column {col}")

if __name__ == "__main__":
    play_game()
