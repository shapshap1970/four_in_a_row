# Four in a Row - Rust AI Engine

Fast Rust-based AI engine for Four-in-a-Row (Connect Four) game, with Python bindings.

## Features

- **Blazing fast**: Depth 12 search in under 1 second
- **Small size**: ~170KB wheel (1000x smaller than Numba+NumPy)
- **Minimax algorithm** with alpha-beta pruning
- **Python bindings** via PyO3

## Installation

```bash
pip install four-in-a-row-rust
```

## Usage

```python
from four_in_a_row_rust.four_in_a_row_rust import get_best_move

# Board is a string of 6 lines, 7 characters each
# 'X' = player 1, 'O' = player 2, ' ' = empty
board = "       \n       \n       \n       \n       \n       "

# Get best move at depth 12
score, best_move = get_best_move(
    board,      # Board string
    12,         # Search depth
    1,          # Current player (1=X, 2=O)
    2           # Number of moves before switching player
)

print(f"Best move: column {best_move}, score: {score}")
```

## Performance

Typical performance on Apple M1:
- Depth 10: 0.3s
- Depth 12: 0.8-2.3s

Compare to Python-only (depth 9):  3-8s

## Building from Source

Requires Rust and maturin:

```bash
pip install maturin
cd four_in_a_row_rust
maturin build --release
pip install target/wheels/*.whl
```

## License

MIT
