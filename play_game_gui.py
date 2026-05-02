#!/usr/bin/env python3
"""
Modern GUI version of Four-in-a-Row game using tkinter
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import gzip
import pickle
from board import Board
from four_in_a_row_with_progress import FourInARowWithProgress


class FourInARowGUI:
    """Modern GUI for Four-in-a-Row game"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Four-in-a-Row")
        self.root.configure(bg='#2c3e50')

        # Set minimum window size
        self.root.minsize(600, 600)

        # Center window on screen
        window_width = 700
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Game state
        self.board = None
        self.game = None
        self.opening_book = {}
        self.current_player = 'X'
        self.human_player = 'X'
        self.ai_player = 'O'
        self.move_num = 0
        self.first_turn = True
        self.coins_this_turn = 1
        self.coins_played = 0
        self.ai_thinking = False

        # Configuration
        self.cols = 7
        self.rows = 6
        self.consec_to_win = 4
        self.consec_moves = 2
        self.ai_time = 5.0

        # GUI settings
        self.cell_size = 80
        self.piece_padding = 5
        self.piece_radius = self.cell_size // 2 - self.piece_padding

        # Colors
        self.bg_color = '#3498db'
        self.empty_color = '#ecf0f1'
        self.player_x_color = '#e74c3c'
        self.player_o_color = '#f1c40f'
        self.highlight_color = '#2ecc71'

        self.setup_ui()

        # Force window to appear and update
        self.root.update_idletasks()
        self.root.deiconify()

        self.show_config_dialog()

    def setup_ui(self):
        """Setup the main UI"""
        # Top frame for status
        self.top_frame = tk.Frame(self.root, bg='#2c3e50', pady=10)
        self.top_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            self.top_frame,
            text="Configure game to start",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.status_label.pack()

        self.move_label = tk.Label(
            self.top_frame,
            text="",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        self.move_label.pack()

        # Progress bar for AI thinking
        self.progress_frame = tk.Frame(self.root, bg='#2c3e50')
        self.progress_frame.pack(fill=tk.X, padx=20)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=400
        )

        # Canvas for board with border to make it visible
        self.canvas_frame = tk.Frame(
            self.root,
            bg='#2c3e50',
            relief=tk.SUNKEN,
            borderwidth=3
        )
        self.canvas_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Buttons
        self.button_frame = tk.Frame(self.root, bg='#2c3e50', pady=10)
        self.button_frame.pack()

        tk.Button(
            self.button_frame,
            text="New Game",
            command=self.show_config_dialog,
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            self.button_frame,
            text="Quit",
            command=self.root.quit,
            font=('Arial', 12),
            bg='#c0392b',
            fg='white',
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

    def show_config_dialog(self):
        """Show configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Game Configuration")
        dialog.configure(bg='#34495e')
        dialog.geometry("400x400")

        tk.Label(
            dialog,
            text="🎮 Four-in-a-Row Setup",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=20)

        # Board size
        tk.Label(
            dialog,
            text="Board Size:",
            font=('Arial', 12),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack()

        board_var = tk.StringVar(value="7x6")
        board_frame = tk.Frame(dialog, bg='#34495e')
        board_frame.pack(pady=10)

        for text, value in [("5×5", "5x5"), ("7×6 ⭐", "7x6"), ("8×7", "8x7")]:
            tk.Radiobutton(
                board_frame,
                text=text,
                variable=board_var,
                value=value,
                font=('Arial', 11),
                bg='#34495e',
                fg='#ecf0f1',
                selectcolor='#2c3e50'
            ).pack(anchor=tk.W)

        # Who goes first
        tk.Label(
            dialog,
            text="Who Goes First:",
            font=('Arial', 12),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(20, 5))

        first_var = tk.StringVar(value="human")
        first_frame = tk.Frame(dialog, bg='#34495e')
        first_frame.pack()

        tk.Radiobutton(
            first_frame,
            text="You (X)",
            variable=first_var,
            value="human",
            font=('Arial', 11),
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50'
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            first_frame,
            text="AI (X)",
            variable=first_var,
            value="ai",
            font=('Arial', 11),
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50'
        ).pack(anchor=tk.W)

        # AI speed
        tk.Label(
            dialog,
            text="AI Speed:",
            font=('Arial', 12),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(20, 5))

        speed_var = tk.StringVar(value="5")
        speed_frame = tk.Frame(dialog, bg='#34495e')
        speed_frame.pack()

        for text, value in [("Fast (2s)", "2"), ("Normal (5s) ⭐", "5"), ("Strong (10s)", "10")]:
            tk.Radiobutton(
                speed_frame,
                text=text,
                variable=speed_var,
                value=value,
                font=('Arial', 11),
                bg='#34495e',
                fg='#ecf0f1',
                selectcolor='#2c3e50'
            ).pack(anchor=tk.W)

        # Start button
        def start_game():
            board_size = board_var.get()
            self.cols, self.rows = map(int, board_size.split('x'))

            human_first = first_var.get() == "human"
            self.ai_time = float(speed_var.get())

            if human_first:
                self.human_player = 'X'
                self.ai_player = 'O'
            else:
                self.human_player = 'O'
                self.ai_player = 'X'

            dialog.destroy()
            self.root.update_idletasks()  # Force update
            self.start_new_game()

        button_frame = tk.Frame(dialog, bg='#34495e')
        button_frame.pack(pady=30)

        tk.Button(
            button_frame,
            text="Start Game",
            command=start_game,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=40,
            pady=12,
            relief=tk.RAISED,
            cursor='hand2'
        ).pack()

        # Make dialog modal and centered
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        dialog_width = 400
        dialog_height = 450
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def start_new_game(self):
        """Initialize a new game"""
        print(f"\n🎮 Starting new game: {self.cols}x{self.rows} board")

        # Load opening book
        book_file = f"opening_book_{self.cols}x{self.rows}.pkl.gz"
        try:
            with gzip.open(book_file, 'rb') as f:
                self.opening_book = pickle.load(f)
            print(f"✓ Loaded opening book: {len(self.opening_book):,} positions")
        except FileNotFoundError:
            self.opening_book = {}
            print(f"ℹ️  No opening book found")

        # Initialize game
        self.board = Board(self.cols, self.rows)
        self.game = FourInARowWithProgress(
            rows=self.rows,
            cols=self.cols,
            consec_to_win=self.consec_to_win,
            consec_moves=self.consec_moves,
            show_progress=False  # We'll show progress in GUI
        )

        self.current_player = 'X'
        self.move_num = 0
        self.first_turn = True
        self.coins_this_turn = 1
        self.coins_played = 0
        self.ai_thinking = False

        # Create board canvas
        if hasattr(self, 'canvas'):
            self.canvas.destroy()

        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size + 30  # Extra space for column numbers

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=canvas_width,
            height=canvas_height,
            bg='#2c3e50',  # Dark background
            highlightthickness=3,
            highlightbackground='#ecf0f1'
        )
        self.canvas.pack()
        print(f"✓ Canvas created: {canvas_width}x{canvas_height}")

        # Bind click events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_canvas_hover)

        self.draw_board()
        print(f"✓ Board drawn")
        self.update_status()
        print(f"✓ Status updated")

        # Update window size to fit board - ensure it's visible
        self.root.update_idletasks()
        window_width = max(canvas_width + 40, 600)
        window_height = canvas_height + 300

        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.update()

        # If AI goes first, make AI move
        if self.current_player == self.ai_player:
            self.root.after(500, self.make_ai_move)

    def draw_board(self):
        """Draw the game board"""
        self.canvas.delete('all')

        # Draw cells and pieces
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size

                # Draw cell background
                self.canvas.create_rectangle(
                    x, y, x + self.cell_size, y + self.cell_size,
                    fill=self.bg_color,
                    outline='#2980b9',
                    width=2
                )

                # Draw piece or empty slot
                cx = x + self.cell_size // 2
                cy = y + self.cell_size // 2

                cell_value = self.board.board[row][col]

                if cell_value == 'X':
                    color = self.player_x_color
                elif cell_value == 'O':
                    color = self.player_o_color
                else:
                    color = self.empty_color

                self.canvas.create_oval(
                    cx - self.piece_radius,
                    cy - self.piece_radius,
                    cx + self.piece_radius,
                    cy + self.piece_radius,
                    fill=color,
                    outline='#2c3e50',
                    width=2,
                    tags='piece'
                )

        # Draw column numbers at bottom
        for col in range(self.cols):
            x = col * self.cell_size + self.cell_size // 2
            y = self.rows * self.cell_size + 15
            self.canvas.create_text(
                x, y,
                text=str(col),
                font=('Arial', 14, 'bold'),
                fill='#ecf0f1',
                tags='colnum'
            )

    def on_canvas_hover(self, event):
        """Highlight column on hover"""
        if self.ai_thinking or self.current_player != self.human_player:
            return

        col = event.x // self.cell_size
        if 0 <= col < self.cols and self.board.is_possible_move(col):
            self.canvas.delete('highlight')

            x = col * self.cell_size
            self.canvas.create_rectangle(
                x, 0,
                x + self.cell_size,
                self.rows * self.cell_size,
                fill=self.highlight_color,
                stipple='gray50',
                tags='highlight'
            )
            self.canvas.tag_lower('highlight')

    def on_canvas_click(self, event):
        """Handle column click"""
        if self.ai_thinking or self.current_player != self.human_player:
            return

        col = event.x // self.cell_size
        if 0 <= col < self.cols and self.board.is_possible_move(col):
            self.make_move(col)

    def make_move(self, col):
        """Make a move in the given column"""
        self.board.play_move(col, self.current_player)
        self.coins_played += 1

        self.draw_board()

        # Check for win
        if self.board.is_winner(self.current_player, self.consec_to_win):
            self.game_over(f"{'You' if self.current_player == self.human_player else 'AI'} Win!")
            return

        # Check for draw
        if self.board.is_end_of_game():
            self.game_over("Draw!")
            return

        # Check if turn is complete
        if self.coins_played >= self.coins_this_turn:
            # Switch player
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            self.first_turn = False
            self.move_num += 1
            self.coins_this_turn = self.consec_moves
            self.coins_played = 0

            self.update_status()

            # If AI's turn, make AI move
            if self.current_player == self.ai_player:
                self.root.after(300, self.make_ai_move)
        else:
            self.update_status()

    def make_ai_move(self):
        """Make AI move in separate thread"""
        if self.ai_thinking:
            return

        self.ai_thinking = True
        self.update_status()
        self.progress_bar.pack(pady=5)
        self.progress_bar.start(10)

        # Run AI in separate thread
        thread = threading.Thread(target=self.ai_move_thread, daemon=True)
        thread.start()

    def ai_move_thread(self):
        """AI move calculation in separate thread"""
        num_coins_remaining = self.coins_this_turn - self.coins_played

        # Check opening book
        board_hash = self.board.to_hash()
        if board_hash in self.opening_book:
            eval_score, col = self.opening_book[board_hash]
            time.sleep(0.2)  # Small delay for visual effect
            self.progress_label.config(text=f"📚 Opening book: eval {eval_score:+.0f}")
        else:
            # Regular search
            self.progress_label.config(text=f"🤖 AI thinking (depth 1)...")

            # Custom progress callback
            def update_progress(depth, eval_score, elapsed):
                self.root.after(0, lambda: self.progress_label.config(
                    text=f"🤖 Depth {depth}, eval {eval_score:+.0f}, {elapsed:.1f}s"
                ))

            eval_score, col = self.game.get_best_move(
                self.board,
                self.current_player,
                num_coins_remaining,
                None,
                max_time=self.ai_time
            )

        # Schedule move on main thread
        self.root.after(0, lambda: self.finish_ai_move(col))

    def finish_ai_move(self, col):
        """Complete AI move on main thread"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")

        self.make_move(col)
        self.ai_thinking = False

    def update_status(self):
        """Update status labels"""
        turn_info = "First move" if self.first_turn else f"{self.coins_this_turn} coins per turn"
        coin_info = f"Coin {self.coins_played + 1}/{self.coins_this_turn}"

        if self.ai_thinking:
            player_text = "🤖 AI thinking..."
        elif self.current_player == self.human_player:
            player_text = f"🎮 Your turn ({self.human_player})"
        else:
            player_text = f"🤖 AI turn ({self.ai_player})"

        self.status_label.config(text=player_text)
        self.move_label.config(text=f"Move {self.move_num + 1} • {turn_info} • {coin_info}")

    def game_over(self, message):
        """Handle game over"""
        self.draw_board()

        result = messagebox.askyesno(
            "Game Over",
            f"{message}\n\nPlay again?",
            icon='info'
        )

        if result:
            self.show_config_dialog()
        else:
            self.root.quit()


def main():
    root = tk.Tk()
    app = FourInARowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
