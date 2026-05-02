#!/usr/bin/env python3
"""
Fast interactive game with progress display and opening book
"""

from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress
import time
import os
import gzip
import json


def load_opening_book(filename='opening_book_7x6.json.gz'):
    """Load opening book if available (secure JSON format)"""
    # Try .json.gz first, then .pkl.gz for backwards compatibility
    json_filename = filename.replace('.pkl.gz', '.json.gz')

    try:
        with gzip.open(json_filename, 'rt', encoding='utf-8') as f:
            book = json.load(f)
        print(f"✓ Loaded opening book: {len(book):,} positions")
        return book
    except FileNotFoundError:
        # Try old .pkl.gz filename
        if filename.endswith('.pkl.gz') and filename != json_filename:
            try:
                with gzip.open(filename, 'rt', encoding='utf-8') as f:
                    book = json.load(f)
                print(f"✓ Loaded opening book: {len(book):,} positions")
                return book
            except:
                pass
        print(f"ℹ️  No opening book found ({json_filename})")
        print(f"   Generate one with: python3 generate_opening_book.py")
        return {}


def print_board(board):
    """Print board with column numbers"""
    print("\n" + "="*50)
    print("   ", end="")
    for i in range(board.cols):
        print(f" {i} ", end="")
    print()
    print("   " + "---" * board.cols)

    for row in range(board.rows):
        print(f"{board.rows - row} |", end="")
        for col in range(board.cols):
            cell = board.board[row][col]
            if cell == 'X':
                print(" X", end=" ")
            elif cell == 'O':
                print(" O", end=" ")
            else:
                print(" .", end=" ")
        print("|")
    print("   " + "---" * board.cols)
    print()


def get_human_move(board):
    """Get valid move from human"""
    while True:
        try:
            col = int(input(f"Your move (column 0-{board.cols-1}): "))
            if 0 <= col < board.cols and board.is_possible_move(col):
                return col
            else:
                print("❌ Invalid move. Try again.")
        except ValueError:
            print("❌ Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Game interrupted. Goodbye!")
            exit(0)


def play_game():
    """Main game loop with opening book and progress"""
    print("="*60)
    print("🎮 FOUR-IN-A-ROW: FAST MODE")
    print("="*60)

    # Game configuration
    print("\nGame Setup:")
    print("1. Quick game (5x5 board)")
    print("2. Standard game (7x6 board) ⭐ Recommended")
    print("3. Custom size")

    choice = input("\nSelect (1-3, default=2): ").strip() or "2"

    if choice == "1":
        cols, rows = 5, 5
        book_file = "opening_book_5x5.json.gz"
    elif choice == "3":
        try:
            cols = int(input("Columns (4-9): "))
            rows = int(input("Rows (4-8): "))
            book_file = f"opening_book_{cols}x{rows}.json.gz"
        except:
            cols, rows = 7, 6
            book_file = "opening_book_7x6.json.gz"
            print("Using default: 7x6")
    else:
        cols, rows = 7, 6
        book_file = "opening_book_7x6.json.gz"

    consec_to_win = 4
    consec_moves = 2

    print(f"\n📊 Configuration:")
    print(f"   Board: {cols} columns × {rows} rows")
    print(f"   Win condition: {consec_to_win} in a row")
    print(f"   Moves per turn: {consec_moves} (except first move = 1)")

    # Load opening book
    opening_book = load_opening_book(book_file)

    # Who goes first?
    first = input("\nWho goes first? (1=You, 2=AI, default=1): ").strip() or "1"
    human_first = (first == "1")

    # AI thinking time
    time_choice = input("\nAI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): ").strip() or "2"
    if time_choice == "1":
        ai_time = 2.0
    elif time_choice == "3":
        ai_time = 10.0
    else:
        ai_time = 5.0

    print(f"   AI thinking time: {ai_time} seconds (with progress display)")

    # Initialize with progress display
    game = FourInARowWithProgress(
        rows=rows, cols=cols,
        consec_to_win=consec_to_win,
        consec_moves=consec_moves,
        show_progress=True
    )
    board = Board(cols, rows)

    if human_first:
        human_player, ai_player = 'X', 'O'
        print("\n🎮 You are X (play first with 1 coin)")
        print("🤖 AI is O (plays with 2 coins per turn)")
    else:
        human_player, ai_player = 'O', 'X'
        print("\n🤖 AI is X (plays first with 1 coin)")
        print("🎮 You are O (play with 2 coins per turn)")

    if opening_book:
        print(f"📚 Opening book active - early moves will be instant!")

    print("\n" + "="*60)
    print("🎯 GAME START!")
    print("="*60)

    move_num = 0
    current_player = 'X'
    first_turn = True

    # Game loop
    while True:
        move_num += 1
        num_coins = 1 if first_turn else consec_moves

        print(f"\n{'='*60}")
        print(f"📍 MOVE {move_num}: {current_player}'s turn ({num_coins} coin{'s' if num_coins > 1 else ''})")
        print(f"{'='*60}")

        print_board(board)

        # Play coins for this turn
        for coin in range(num_coins):
            if num_coins > 1:
                print(f"\n--- Coin {coin+1}/{num_coins} ---")

            if current_player == human_player:
                # Human move
                col = get_human_move(board)
                board.play_move(col, current_player)
                print(f"✓ You played column {col}")

            else:
                # AI move - check opening book first
                board_hash = board.to_hash()
                # Convert to string for JSON compatibility
                key = str(board_hash)
                if key in opening_book:
                    # Use opening book (instant)
                    result = opening_book[key]
                    # Handle both tuple and list from JSON
                    if isinstance(result, list):
                        eval_score, col = result[0], result[1]
                    else:
                        eval_score, col = result
                    print(f"📚 Using opening book (instant)")
                    print(f"   → Move {col}, eval {eval_score:+.0f}")
                else:
                    # Regular search with progress
                    start = time.time()
                    eval_score, col = game.get_best_move(
                        board, current_player, num_coins - coin, None, max_time=ai_time
                    )

                board.play_move(col, current_player)

            # Check for win after each coin
            if board.is_winner(current_player, consec_to_win):
                print_board(board)
                print("\n" + "="*60)
                if current_player == human_player:
                    print("🎉 YOU WIN! Congratulations!")
                else:
                    print("🤖 AI WINS!")
                print("="*60)
                return

            # Check for draw
            if board.is_end_of_game():
                print_board(board)
                print("\n" + "="*60)
                print("🤝 DRAW! Board is full.")
                print("="*60)
                return

        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'
        first_turn = False


if __name__ == "__main__":
    try:
        play_game()

        # Ask to play again
        print("\n" + "="*60)
        again = input("Play again? (y/n): ").strip().lower()
        if again == 'y':
            play_game()
        else:
            print("\n👋 Thanks for playing!")

    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
