#!/usr/bin/env python3
"""
Simplified GUI with guaranteed visible board
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import gzip
import pickle
from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress


def main():
    # Configuration
    cols, rows = 7, 6
    consec_to_win = 4
    consec_moves = 2
    human_player = 'X'
    ai_player = 'O'
    ai_time = 5.0

    # Ask configuration
    root = tk.Tk()
    root.withdraw()

    # Simple dialogs for configuration
    board_choice = messagebox.askquestion(
        "Board Size",
        "Use standard 7×6 board?\n\n(No = use 5×5)"
    )
    if board_choice == 'no':
        cols, rows = 5, 5

    first_choice = messagebox.askquestion(
        "Who Goes First?",
        "Do you want to go first (play X)?"
    )
    if first_choice == 'no':
        human_player = 'O'
        ai_player = 'X'

    speed_choice = messagebox.askyesnocancel(
        "AI Speed",
        "AI Speed:\n\nYes = Fast (2s)\nNo = Normal (5s)\nCancel = Strong (10s)"
    )
    if speed_choice == True:
        ai_time = 2.0
    elif speed_choice == False:
        ai_time = 5.0
    else:
        ai_time = 10.0

    root.destroy()

    # Create main window
    root = tk.Tk()
    root.title("🎮 Four-in-a-Row")

    # Set window size
    cell_size = 80
    window_width = cols * cell_size + 100
    window_height = rows * cell_size + 250

    # Center on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg='#2c3e50')

    # Game state
    board = Board(cols, rows)
    game = FourInARowWithProgress(
        rows=rows, cols=cols,
        consec_to_win=consec_to_win,
        consec_moves=consec_moves,
        show_progress=False
    )

    current_player = ['X']
    move_num = [0]
    first_turn = [True]
    coins_this_turn = [1]
    coins_played = [0]
    ai_thinking = [False]

    # Load opening book
    try:
        book_file = f"opening_book_{cols}x{rows}.pkl.gz"
        with gzip.open(book_file, 'rb') as f:
            opening_book = pickle.load(f)
        print(f"✓ Loaded opening book: {len(opening_book):,} positions")
    except:
        opening_book = {}

    # Top label
    status_label = tk.Label(
        root,
        text=f"{'Your' if current_player[0] == human_player else 'AI'} turn",
        font=('Arial', 18, 'bold'),
        bg='#2c3e50',
        fg='#ecf0f1',
        pady=15
    )
    status_label.pack()

    # Canvas - EXPLICITLY visible
    canvas_frame = tk.Frame(root, bg='#34495e', relief=tk.RAISED, borderwidth=5)
    canvas_frame.pack(pady=20, padx=20)

    canvas_width = cols * cell_size
    canvas_height = rows * cell_size + 30

    canvas = tk.Canvas(
        canvas_frame,
        width=canvas_width,
        height=canvas_height,
        bg='#2c3e50',
        highlightthickness=0
    )
    canvas.pack(padx=5, pady=5)

    # Draw board function
    def draw_board():
        canvas.delete('all')

        # Draw grid and pieces
        for row in range(rows):
            for col in range(cols):
                x = col * cell_size
                y = row * cell_size

                # Cell background
                canvas.create_rectangle(
                    x, y, x + cell_size, y + cell_size,
                    fill='#3498db',
                    outline='#2980b9',
                    width=3
                )

                # Piece
                cx = x + cell_size // 2
                cy = y + cell_size // 2
                radius = cell_size // 2 - 5

                cell_value = board.board[row][col]
                if cell_value == 'X':
                    color = '#e74c3c'  # Red
                elif cell_value == 'O':
                    color = '#f1c40f'  # Yellow
                else:
                    color = '#ecf0f1'  # White/empty

                canvas.create_oval(
                    cx - radius, cy - radius,
                    cx + radius, cy + radius,
                    fill=color,
                    outline='#2c3e50',
                    width=3
                )

        # Column numbers
        for col in range(cols):
            x = col * cell_size + cell_size // 2
            y = rows * cell_size + 15
            canvas.create_text(
                x, y,
                text=str(col),
                font=('Arial', 16, 'bold'),
                fill='#ecf0f1'
            )

    # Update status
    def update_status():
        turn_text = "Your turn" if current_player[0] == human_player else "AI thinking..."
        coin_text = f"Move {move_num[0] + 1} • Coin {coins_played[0] + 1}/{coins_this_turn[0]}"
        status_label.config(text=f"{turn_text} ({current_player[0]})\n{coin_text}")

    # Make move
    def make_move(col):
        board.play_move(col, current_player[0])
        coins_played[0] += 1
        draw_board()

        # Check win
        if board.is_winner(current_player[0], consec_to_win):
            winner = "You" if current_player[0] == human_player else "AI"
            if messagebox.askyesno("Game Over", f"{winner} won!\n\nPlay again?"):
                root.destroy()
                main()
            else:
                root.quit()
            return

        # Check draw
        if board.is_end_of_game():
            if messagebox.askyesno("Game Over", "Draw!\n\nPlay again?"):
                root.destroy()
                main()
            else:
                root.quit()
            return

        # Next coin or next player
        if coins_played[0] >= coins_this_turn[0]:
            current_player[0] = 'O' if current_player[0] == 'X' else 'X'
            first_turn[0] = False
            move_num[0] += 1
            coins_this_turn[0] = consec_moves
            coins_played[0] = 0

            update_status()

            if current_player[0] == ai_player:
                root.after(300, make_ai_move)
        else:
            update_status()

    # AI move
    def make_ai_move():
        if ai_thinking[0]:
            return

        ai_thinking[0] = True
        update_status()

        def ai_thread():
            num_coins_remaining = coins_this_turn[0] - coins_played[0]

            # Check opening book
            board_hash = board.to_hash()
            if board_hash in opening_book:
                eval_score, col = opening_book[board_hash]
                time.sleep(0.2)
            else:
                eval_score, col = game.get_best_move(
                    board, current_player[0], num_coins_remaining, None, max_time=ai_time
                )

            root.after(0, lambda: finish_ai_move(col))

        threading.Thread(target=ai_thread, daemon=True).start()

    def finish_ai_move(col):
        ai_thinking[0] = False
        make_move(col)

    # Human click
    def on_click(event):
        if ai_thinking[0] or current_player[0] != human_player:
            return

        col = event.x // cell_size
        if 0 <= col < cols and board.is_possible_move(col):
            make_move(col)

    canvas.bind('<Button-1>', on_click)

    # Buttons
    button_frame = tk.Frame(root, bg='#2c3e50')
    button_frame.pack(pady=15)

    tk.Button(
        button_frame,
        text="New Game",
        command=lambda: (root.destroy(), main()),
        font=('Arial', 12, 'bold'),
        bg='#27ae60',
        fg='white',
        padx=20,
        pady=8
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        button_frame,
        text="Quit",
        command=root.quit,
        font=('Arial', 12, 'bold'),
        bg='#c0392b',
        fg='white',
        padx=20,
        pady=8
    ).pack(side=tk.LEFT, padx=10)

    # Initial draw
    draw_board()
    update_status()

    # AI first move
    if current_player[0] == ai_player:
        root.after(500, make_ai_move)

    root.mainloop()


if __name__ == "__main__":
    main()
