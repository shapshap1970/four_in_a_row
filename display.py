
from rich.table import Table
from rich.console import Console
console = Console()

def print_board(board_obj):
    #console.clear()
    table = Table(show_header=True, show_lines=True, header_style="white")
    table.add_column("#")
    for i in range(board_obj.cols):
            table.add_column(str(i))

    row_size = board_obj.rows
    for i, row in enumerate(board_obj.board):
        styled_row = [f"[bold]{row_size-i}[/bold]"]
        for cell in row:
            if cell == 'X':
                styled_row.append('[bold red]X[/bold red]')
            elif cell == 'O':
                styled_row.append('[bold green]O[/bold green]')
            else:
                styled_row.append(cell)
        table.add_row(*styled_row)
    console.print(table, "")

def print_message(msg):
    console.print(msg)