#!/usr/bin/env python3
"""
Simple test to verify GUI board displays correctly
"""

import tkinter as tk
from board import Board

def test_board_display():
    root = tk.Tk()
    root.title("Board Display Test")
    root.geometry("600x600")
    root.configure(bg='#2c3e50')

    # Create a label
    label = tk.Label(
        root,
        text="Four-in-a-Row Board Test",
        font=('Arial', 16, 'bold'),
        bg='#2c3e50',
        fg='#ecf0f1'
    )
    label.pack(pady=20)

    # Create canvas
    canvas = tk.Canvas(
        root,
        width=560,
        height=510,
        bg='#2c3e50',
        highlightthickness=3,
        highlightbackground='#ecf0f1'
    )
    canvas.pack(pady=10)

    # Draw board
    board = Board(7, 6)
    cell_size = 80
    bg_color = '#3498db'
    empty_color = '#ecf0f1'
    x_color = '#e74c3c'
    o_color = '#f1c40f'
    piece_radius = 35

    # Add some test pieces
    board.play_move(3, 'X')
    board.play_move(3, 'O')
    board.play_move(2, 'X')
    board.play_move(4, 'O')

    for row in range(6):
        for col in range(7):
            x = col * cell_size
            y = row * cell_size

            # Draw cell
            canvas.create_rectangle(
                x, y, x + cell_size, y + cell_size,
                fill=bg_color,
                outline='#2980b9',
                width=2
            )

            # Draw piece
            cx = x + cell_size // 2
            cy = y + cell_size // 2

            cell_value = board.board[row][col]
            if cell_value == 'X':
                color = x_color
            elif cell_value == 'O':
                color = o_color
            else:
                color = empty_color

            canvas.create_oval(
                cx - piece_radius,
                cy - piece_radius,
                cx + piece_radius,
                cy + piece_radius,
                fill=color,
                outline='#2c3e50',
                width=2
            )

    # Draw column numbers
    for col in range(7):
        x = col * cell_size + cell_size // 2
        y = 6 * cell_size + 15
        canvas.create_text(
            x, y,
            text=str(col),
            font=('Arial', 14, 'bold'),
            fill='#ecf0f1'
        )

    status = tk.Label(
        root,
        text="✓ If you see a blue board with white circles, the GUI is working!",
        font=('Arial', 12),
        bg='#2c3e50',
        fg='#27ae60'
    )
    status.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    test_board_display()
