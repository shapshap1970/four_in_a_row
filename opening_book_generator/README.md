# Rust Opening Book Generator

Ultra-fast opening book generator written in Rust for Four-in-a-Row game.

## Why Rust?

- **10-50x faster** than Python
- True parallelism (no GIL)
- Compiled to native machine code
- Memory efficient

## Installation

### Install Rust (if not already installed)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

Verify installation:
```bash
rustc --version
cargo --version
```

## Build & Run

### Quick Start (one command)

```bash
cd opening_book_generator
cargo run --release
```

This will:
1. Download dependencies
2. Compile with optimizations
3. Run the generator
4. Output: `opening_book_7x6.json.gz` in parent directory

### Manual Build (optional)

```bash
# Build optimized binary
cargo build --release

# Run it
./target/release/opening_book_generator
```

## Performance

**Expected time:** 5-15 minutes for 67,351 positions

**Configuration:**
- Book depth: 8 moves
- Search depth: 8 plies
- Board: 7x6
- Parallelism: All CPU cores

## Output

Generates `opening_book_7x6.json.gz` compatible with the Python web server.

Format:
```json
{
  "board_hash": [score, best_move],
  ...
}
```

## How It Works

1. **BFS Generation**: Creates all possible board positions up to 8 moves
2. **Parallel Evaluation**: Uses Rayon for multi-threaded minimax evaluation
3. **Alpha-Beta Pruning**: Efficient tree search with move ordering
4. **Compression**: Gzip compression for small file size

## Comparison

| Implementation | Time | Speed |
|---------------|------|-------|
| Python (multiprocessing) | 60+ min | ~20 pos/s |
| **Rust (rayon)** | **5-15 min** | **100-300 pos/s** |

## Dependencies

- `serde` + `serde_json`: JSON serialization
- `flate2`: Gzip compression
- `rayon`: Data parallelism

All dependencies are automatically downloaded by Cargo.
