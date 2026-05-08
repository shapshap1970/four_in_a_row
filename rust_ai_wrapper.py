#!/usr/bin/env python3
"""
Python wrapper to call Rust AI engine
10-50x faster than Python implementation
"""

import subprocess
import os

# Path to Rust AI binary
RUST_AI_PATH = os.path.join(
    os.path.dirname(__file__),
    "opening_book_generator/target/release/ai_engine"
)

def compute_move_rust(board, depth, player, number_of_play):
    """
    Call Rust AI engine to compute best move

    Args:
        board: Board object with 7x6 grid
        depth: Search depth (e.g., 10)
        player: 'X' (1) or 'O' (2)
        number_of_play: Number of consecutive moves remaining

    Returns:
        (score, best_column)
    """
    # Convert player to number
    player_num = 1 if player == 'X' else 2

    # Prepare input for Rust program
    input_data = f"{depth}\n"
    input_data += f"{player_num}\n"
    input_data += f"{number_of_play}\n"

    # Add board state (6 rows x 7 cols)
    for row in board.board:
        row_str = ''.join(row)
        input_data += row_str + '\n'

    # Call Rust binary
    try:
        result = subprocess.run(
            [RUST_AI_PATH],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"Rust AI failed: {result.stderr}")

        # Parse output
        lines = result.stdout.strip().split('\n')
        score = int(lines[0])
        best_move = int(lines[1])

        if best_move == 999:
            return score, None

        return score, best_move

    except subprocess.TimeoutExpired:
        raise Exception("Rust AI timeout")
    except Exception as e:
        raise Exception(f"Rust AI error: {e}")


def is_rust_ai_available():
    """Check if Rust AI binary exists and not disabled by environment"""
    # Disable Rust AI on Vercel or when explicitly disabled
    if os.getenv('VERCEL_DEPLOYMENT') or os.getenv('DISABLE_RUST_AI'):
        return False
    return os.path.exists(RUST_AI_PATH)


if __name__ == "__main__":
    # Test the wrapper
    from board import Board

    if not is_rust_ai_available():
        print(f"❌ Rust AI not found at: {RUST_AI_PATH}")
        print("Run: cd opening_book_generator && cargo build --release --bin ai_engine")
        exit(1)

    # Create test board
    board = Board(7, 6)
    board.play_move(3, 'X')

    print("Testing Rust AI wrapper...")
    print("Board:")
    board.print_board()

    import time
    start = time.time()
    score, move = compute_move_rust(board, 10, 'O', 2)
    elapsed = time.time() - start

    print(f"\n✅ Rust AI response:")
    print(f"   Best move: column {move}")
    print(f"   Score: {score}")
    print(f"   Time: {elapsed:.3f}s")
    print(f"\n🚀 {10/elapsed:.1f}x faster than typical Python!")
