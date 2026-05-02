#!/usr/bin/env python3
"""
Beautiful CLI version with colors and formatting
"""

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress
import time
import os
import gzip
import json
import sys

# Enable ANSI colors on Windows
if os.name == 'nt':  # Windows
    try:
        # Enable ANSI escape sequences in Windows 10+ Console
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass
    # Set UTF-8 encoding for unicode characters
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Print game header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}    🎮  F O U R - I N - A - R O W  🎮{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")


def print_board(board):
    """Print beautiful polished board with colors"""
    # Top border
    print(f"\n{Colors.BOLD}{Colors.BLUE}      ╔{'═══════╤' * (board.cols - 1)}═══════╗{Colors.RESET}")

    for row in range(board.rows):
        # Empty line above pieces for spacing
        print(f"{Colors.BOLD}{Colors.BLUE}      ║{Colors.RESET}", end="")
        for col in range(board.cols):
            print(f"       ", end="")
            if col < board.cols - 1:
                print(f"{Colors.BLUE}│{Colors.RESET}", end="")
        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}")

        # Main line with pieces and row number
        print(f"{Colors.BOLD}{Colors.CYAN}   {board.rows - row}  {Colors.BLUE}║{Colors.RESET}", end="")

        for col in range(board.cols):
            cell = board.board[row][col]

            if cell == 'X':
                # Red piece with nice spacing
                piece = f"{Colors.RED}{Colors.BOLD}   ⬤   {Colors.RESET}"
            elif cell == 'O':
                # Yellow piece with nice spacing
                piece = f"{Colors.YELLOW}{Colors.BOLD}   ⬤   {Colors.RESET}"
            else:
                # Empty cell with subtle dot
                piece = f"{Colors.WHITE}   ·   {Colors.RESET}"

            print(piece, end="")

            if col < board.cols - 1:
                print(f"{Colors.BLUE}│{Colors.RESET}", end="")

        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}")

        # Empty line below pieces for spacing
        print(f"{Colors.BOLD}{Colors.BLUE}      ║{Colors.RESET}", end="")
        for col in range(board.cols):
            print(f"       ", end="")
            if col < board.cols - 1:
                print(f"{Colors.BLUE}│{Colors.RESET}", end="")
        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}")

        # Row separator (between rows)
        if row < board.rows - 1:
            print(f"{Colors.BOLD}{Colors.BLUE}      ╟{'═══════╪' * (board.cols - 1)}═══════╢{Colors.RESET}")

    # Bottom border
    print(f"{Colors.BOLD}{Colors.BLUE}      ╚{'═══════╧' * (board.cols - 1)}═══════╝{Colors.RESET}")

    # Column numbers
    print(f"{Colors.BOLD}{Colors.CYAN}         ", end="")
    for col in range(board.cols):
        print(f"   {col}    ", end="")
    print(f"{Colors.RESET}\n")


def print_status(move_num, current_player, coins_this_turn, coins_played, human_player):
    """Print game status"""
    player_name = f"{Colors.GREEN}YOU{Colors.RESET}" if current_player == human_player else f"{Colors.MAGENTA}AI{Colors.RESET}"
    player_symbol = f"{Colors.RED}●{Colors.RESET}" if current_player == 'X' else f"{Colors.YELLOW}●{Colors.RESET}"

    print(f"{Colors.BOLD}┌{'─' * 68}┐{Colors.RESET}")
    print(f"{Colors.BOLD}│{Colors.RESET} Turn: {player_name} {player_symbol}  │  Move: {Colors.CYAN}{move_num}{Colors.RESET}  │  Coins: {Colors.YELLOW}{coins_played}/{coins_this_turn}{Colors.RESET}" + " " * 30 + f"{Colors.BOLD}│{Colors.RESET}")
    print(f"{Colors.BOLD}└{'─' * 68}┘{Colors.RESET}\n")


def load_opening_book(filename='opening_book_7x6.json.gz'):
    """Load opening book if available (secure JSON format)"""
    # Try .json.gz first, then .pkl.gz for backwards compatibility
    json_filename = filename.replace('.pkl.gz', '.json.gz')

    try:
        with gzip.open(json_filename, 'rt', encoding='utf-8') as f:
            book = json.load(f)
        print(f"{Colors.GREEN}✓ Loaded opening book: {len(book):,} positions{Colors.RESET}")
        return book
    except FileNotFoundError:
        # Try old .pkl.gz filename
        if filename.endswith('.pkl.gz') and filename != json_filename:
            try:
                with gzip.open(filename, 'rt', encoding='utf-8') as f:
                    book = json.load(f)
                print(f"{Colors.GREEN}✓ Loaded opening book: {len(book):,} positions{Colors.RESET}")
                return book
            except:
                pass
        print(f"{Colors.YELLOW}ℹ️  No opening book found (moves will take ~{5}s){Colors.RESET}")
        return {}


def get_human_move(board):
    """Get valid move from human"""
    while True:
        try:
            prompt = f"{Colors.BOLD}{Colors.GREEN}Your move (column 0-{board.cols-1}): {Colors.RESET}"
            col = int(input(prompt))
            if 0 <= col < board.cols and board.is_possible_move(col):
                return col
            else:
                print(f"{Colors.RED}❌ Invalid move. Try again.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}❌ Please enter a number.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Game interrupted. Goodbye!{Colors.RESET}")
            exit(0)


def print_ai_thinking():
    """Print AI thinking message"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}🤖 AI is thinking...{Colors.RESET}")


def print_ai_move(col, eval_score, time_taken, from_book=False):
    """Print AI move information"""
    if from_book:
        print(f"{Colors.CYAN}📚 Opening book: {Colors.RESET}Column {Colors.BOLD}{col}{Colors.RESET}, eval {Colors.CYAN}{eval_score:+.0f}{Colors.RESET}")
    else:
        print(f"{Colors.MAGENTA}🤖 AI played: {Colors.RESET}Column {Colors.BOLD}{col}{Colors.RESET}, eval {Colors.CYAN}{eval_score:+.0f}{Colors.RESET}, time {Colors.YELLOW}{time_taken:.2f}s{Colors.RESET}")


def print_winner(winner, human_player):
    """Print winner announcement"""
    clear_screen()
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")

    if winner == human_player:
        print(f"{Colors.BOLD}{Colors.GREEN}")
        print("    🎉  🎊  🎉  🎊  🎉  🎊  🎉  🎊  🎉  🎊  🎉")
        print("                  Y O U   W I N !")
        print("    🎉  🎊  🎉  🎊  🎉  🎊  🎉  🎊  🎉  🎊  🎉")
        print(f"{Colors.RESET}")
    else:
        print(f"{Colors.BOLD}{Colors.MAGENTA}")
        print("                    A I   W I N S !")
        print(f"{Colors.RESET}")

    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")


def print_draw():
    """Print draw announcement"""
    clear_screen()
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}")
    print("                      D R A W !")
    print(f"{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")


def play_game():
    """Main game loop"""
    clear_screen()
    print_header()

    # Game configuration
    print(f"{Colors.BOLD}Game Setup:{Colors.RESET}")
    print(f"  {Colors.CYAN}1.{Colors.RESET} Quick game (5×5 board)")
    print(f"  {Colors.CYAN}2.{Colors.RESET} Standard game (7×6 board) {Colors.YELLOW}⭐ Recommended{Colors.RESET}")
    print(f"  {Colors.CYAN}3.{Colors.RESET} Custom size")

    choice = input(f"\n{Colors.BOLD}Select (1-3, default=2): {Colors.RESET}").strip() or "2"

    if choice == "1":
        cols, rows = 5, 5
        book_file = "opening_book_5x5.json.gz"
    elif choice == "3":
        try:
            cols = int(input(f"{Colors.BOLD}Columns (4-9): {Colors.RESET}"))
            rows = int(input(f"{Colors.BOLD}Rows (4-8): {Colors.RESET}"))
            book_file = f"opening_book_{cols}x{rows}.json.gz"
        except:
            cols, rows = 7, 6
            book_file = "opening_book_7x6.json.gz"
            print(f"{Colors.YELLOW}Using default: 7×6{Colors.RESET}")
    else:
        cols, rows = 7, 6
        book_file = "opening_book_7x6.json.gz"

    consec_to_win = 4
    consec_moves = 2

    print(f"\n{Colors.BOLD}📊 Configuration:{Colors.RESET}")
    print(f"   Board: {Colors.CYAN}{cols} columns × {rows} rows{Colors.RESET}")
    print(f"   Win: {Colors.GREEN}{consec_to_win} in a row{Colors.RESET}")
    print(f"   Moves per turn: {Colors.YELLOW}{consec_moves}{Colors.RESET} (except first move = 1)")

    # Load opening book
    print()
    opening_book = load_opening_book(book_file)

    # Who goes first?
    first = input(f"\n{Colors.BOLD}Who goes first? (1=You, 2=AI, default=1): {Colors.RESET}").strip() or "1"
    human_first = (first == "1")

    # AI thinking time
    time_choice = input(f"{Colors.BOLD}AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): {Colors.RESET}").strip() or "2"
    if time_choice == "1":
        ai_time = 2.0
    elif time_choice == "3":
        ai_time = 10.0
    else:
        ai_time = 5.0

    print(f"   AI thinking time: {Colors.YELLOW}{ai_time}s{Colors.RESET}")

    # Initialize game
    game = FourInARowWithProgress(
        rows=rows, cols=cols,
        consec_to_win=consec_to_win,
        consec_moves=consec_moves,
        show_progress=True
    )
    board = Board(cols, rows)

    if human_first:
        human_player, ai_player = 'X', 'O'
        print(f"\n{Colors.GREEN}🎮 You are {Colors.RED}● X{Colors.RESET} {Colors.GREEN}(play first with 1 coin){Colors.RESET}")
        print(f"{Colors.MAGENTA}🤖 AI is {Colors.YELLOW}● O{Colors.RESET} {Colors.MAGENTA}(plays with 2 coins per turn){Colors.RESET}")
    else:
        human_player, ai_player = 'O', 'X'
        print(f"\n{Colors.MAGENTA}🤖 AI is {Colors.RED}● X{Colors.RESET} {Colors.MAGENTA}(plays first with 1 coin){Colors.RESET}")
        print(f"{Colors.GREEN}🎮 You are {Colors.YELLOW}● O{Colors.RESET} {Colors.GREEN}(play with 2 coins per turn){Colors.RESET}")

    input(f"\n{Colors.BOLD}Press Enter to start...{Colors.RESET}")

    move_num = 0
    current_player = 'X'
    first_turn = True

    # Game loop
    while True:
        move_num += 1
        num_coins = 1 if first_turn else consec_moves
        coins_played = 0

        clear_screen()
        print_header()
        print_board(board)
        print_status(move_num, current_player, num_coins, coins_played + 1, human_player)

        # Play coins for this turn
        for coin in range(num_coins):
            if coin > 0:
                clear_screen()
                print_header()
                print_board(board)
                print_status(move_num, current_player, num_coins, coin + 1, human_player)

            if current_player == human_player:
                # Human move
                col = get_human_move(board)
                board.play_move(col, current_player)
                print(f"{Colors.GREEN}✓ You played column {col}{Colors.RESET}\n")
            else:
                # AI move
                board_hash = board.to_hash()
                # Convert to string for JSON compatibility
                key = str(board_hash)
                if key in opening_book:
                    # Opening book
                    result = opening_book[key]
                    # Handle both tuple and list from JSON
                    if isinstance(result, list):
                        eval_score, col = result[0], result[1]
                    else:
                        eval_score, col = result
                    print_ai_move(col, eval_score, 0.0, from_book=True)
                    board.play_move(col, current_player)
                else:
                    # Regular search
                    print_ai_thinking()
                    start = time.time()
                    eval_score, col = game.get_best_move(
                        board, current_player, num_coins - coin, None, max_time=ai_time
                    )
                    time_taken = time.time() - start
                    print_ai_move(col, eval_score, time_taken, from_book=False)
                    board.play_move(col, current_player)

                time.sleep(0.5)  # Brief pause to see AI move

            # Check for win
            if board.is_winner(current_player, consec_to_win):
                clear_screen()
                print_header()
                print_board(board)
                print_winner(current_player, human_player)
                return

            # Check for draw
            if board.is_end_of_game():
                clear_screen()
                print_header()
                print_board(board)
                print_draw()
                return

        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'
        first_turn = False


if __name__ == "__main__":
    try:
        while True:
            play_game()

            # Play again?
            again = input(f"\n{Colors.BOLD}Play again? (y/n): {Colors.RESET}").strip().lower()
            if again != 'y':
                print(f"\n{Colors.CYAN}👋 Thanks for playing!{Colors.RESET}\n")
                break

    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}👋 Game interrupted. Thanks for playing!{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
