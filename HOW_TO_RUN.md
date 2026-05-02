# How to Run Your Four-in-a-Row Game

## Quick Start (Easiest Way) ⭐

### Play Against the Optimized AI

```bash
python3 play_game.py
```

That's it! The game will:
1. Ask you to choose board size (default: 7x6)
2. Ask who goes first (default: you)
3. Ask AI speed (default: 5 seconds)
4. Start the game!

**Example interaction:**
```
Game Setup:
1. Quick game (5x5 board)
2. Standard game (7x6 board) ⭐ Recommended
3. Custom size
Select (1-3, default=2): [press Enter for default]

Who goes first? (1=You, 2=AI, default=1): [press Enter]

AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): [press Enter]

Game starts...
```

---

## Alternative Ways to Run

### 1. Using Your Original Game Loop

If you want to integrate into your existing `game.py`:

**Edit `game.py` and change these 3 lines:**

```python
# OLD:
from four_in_a_row import FourInARow
game = FourInARow(rows=6, cols=7, consec_to_win=4, consec_moves=2)
eval, move = game.minimax(board, 25, player, num_moves, col)

# NEW:
from four_in_a_row_optimized import FourInARowOptimized
game = FourInARowOptimized(rows=6, cols=7, consec_to_win=4, consec_moves=2)
eval, move = game.get_best_move(board, player, num_moves, col, max_time=5.0)
```

Then run:
```bash
python3 game.py
```

### 2. Interactive Game with Analysis

For detailed move analysis and commentary:

```bash
python3 play_with_analysis.py
```

This version shows:
- Evaluation scores for all moves
- Threat analysis
- AI's thinking process
- Strategic commentary

### 3. Compare Performance (Original vs Optimized)

To see benchmarks and speedup measurements:

```bash
python3 compare_performance.py
```

This will:
- Test both implementations
- Show timing comparisons
- Demonstrate the speedup
- Test evaluation functions

---

## Configuration Options

### Board Sizes

**Quick game (5x5):**
- Good for testing
- Fast games (~5-10 moves)
- AI responds in 1-2 seconds

**Standard game (7x6):** ⭐ **Recommended**
- Official Connect Four size
- Balanced gameplay
- AI responds in 2-5 seconds

**Large board (8x8 or 9x9):**
- Longer games
- More strategic depth
- AI responds in 5-10 seconds

### AI Speed Settings

**Fast (2 seconds):**
- Quick responses
- Searches depth 4-6
- Good for casual play

**Normal (5 seconds):** ⭐ **Recommended**
- Balanced
- Searches depth 6-10
- Strong play quality

**Strong (10 seconds):**
- Deep thinking
- Searches depth 10-14
- Best moves possible
- Use for serious games

---

## Files Reference

### Ready-to-Run Games

| File | Description | When to Use |
|------|-------------|-------------|
| `play_game.py` | Simple interactive game | **Start here!** |
| `play_with_analysis.py` | Game with move analysis | Learning/analyzing |
| `game.py` | Original game (update it) | Your existing code |

### Engines

| File | Description | Speed |
|------|-------------|-------|
| `four_in_a_row_optimized.py` | New optimized engine | 100-1000x faster |
| `four_in_a_row.py` | Original engine | Too slow for 7x6 |

### Utilities

| File | Description |
|------|-------------|
| `opening_book.py` | Opening book system (optional) |
| `compare_performance.py` | Benchmark script |
| `board.py` | Board representation (unchanged) |
| `display.py` | Display utilities (unchanged) |

---

## Advanced: Generate Opening Book (Optional)

For instant opening moves, generate an opening book:

```python
python3 -c "
from opening_book import OpeningBook

book = OpeningBook('my_opening_book.pkl.gz')
book.generate_book(
    rows=6, cols=7,
    consec_to_win=4,
    consec_moves=2,
    max_moves=6,      # First 6 moves
    search_depth=10   # Search deeply
)
"
```

**This takes 10-20 minutes but only needs to be done once.**

Then use it:

```python
from opening_book import GameWithOpeningBook

game = GameWithOpeningBook(
    rows=6, cols=7,
    consec_to_win=4,
    consec_moves=2,
    opening_book_file='my_opening_book.pkl.gz'
)

# First 6 moves will be instant!
eval, move = game.get_best_move(board, player, num_moves, max_time=5.0)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'rich'"

Install dependencies:
```bash
pip install rich bitarray
```

### "Game is too slow"

Reduce AI thinking time:
- In `play_game.py`: Choose option 1 (Fast/2s)
- Or edit the code: `max_time=2.0` instead of `5.0`

### "AI plays poorly"

Increase AI thinking time:
- In `play_game.py`: Choose option 3 (Strong/10s)
- Or edit the code: `max_time=10.0`

### "Import error: four_in_a_row_optimized"

Make sure you're in the correct directory:
```bash
cd /Users/ashapira/private/internal_development/4inArow
python3 play_game.py
```

---

## Quick Command Reference

```bash
# Play against AI (simplest)
python3 play_game.py

# Play with analysis/commentary
python3 play_with_analysis.py

# Run your original game (after updating it)
python3 game.py

# Benchmark performance
python3 compare_performance.py

# Run tests
python3 -m pytest test_*.py -v

# Generate opening book (optional, takes 10-20 min)
python3 -c "from opening_book import OpeningBook; ..."
```

---

## What Each File Does

```
your_project/
├── play_game.py              ⭐ START HERE - Simple interactive game
├── play_with_analysis.py     📊 Game with detailed analysis
├── game.py                    🎮 Your original game loop
│
├── four_in_a_row_optimized.py  ⚡ New fast engine (USE THIS)
├── four_in_a_row.py            🐌 Old slow engine (keep for reference)
├── board.py                     📋 Board class (no changes needed)
├── display.py                   🖥️  Display utilities
├── file_util.py                 💾 File operations
├── opening_book.py              📚 Optional opening book
│
├── compare_performance.py       📈 Benchmarking
├── test_*.py                    ✅ Unit tests
│
└── Documentation:
    ├── README.md                📖 Project overview
    ├── HOW_TO_RUN.md           ⭐ This file
    ├── CODE_CHANGES.md         🔧 What changed
    ├── OPTIMIZATION_GUIDE.md   📚 Technical details
    ├── PERFORMANCE_COMPARISON.md 📊 Benchmarks
    ├── RECOMMENDATIONS.md      💡 Best practices
    └── TEST_RESULTS.md         ✅ Test documentation
```

---

## Examples

### Example 1: Quick Standard Game

```bash
$ python3 play_game.py
Select (1-3, default=2): [Enter]      # 7x6 board
Who goes first? (1=You, 2=AI, default=1): [Enter]  # You first
AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): [Enter]  # 5s

# Game starts, you play column by column
Your move (column 0-6): 3
✓ You played column 3

🤖 AI thinking...
🤖 AI played column 3 (4.2s, eval: -15)
...
```

### Example 2: Quick Game Against Fast AI

```bash
$ python3 play_game.py
Select (1-3, default=2): 1             # 5x5 board
Who goes first? (1=You, 2=AI, default=1): [Enter]
AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): 1  # Fast

# Quick 5-10 minute game
```

### Example 3: Let AI Go First

```bash
$ python3 play_game.py
Select (1-3, default=2): [Enter]
Who goes first? (1=You, 2=AI, default=1): 2  # AI goes first
AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): [Enter]

# AI makes first move
```

---

## Tips for Playing

1. **Center columns are strongest** (3 in a 7-column board)
2. **Watch for opponent's 2-in-a-rows** - they become 3-in-a-rows next turn
3. **Build your own threats** while blocking opponent
4. **Vertical stacking** can be dangerous - opponent controls what's on top
5. **The AI is strong** - don't feel bad if you lose! It searches 6-10 moves ahead

---

## Summary

**To play right now:**

1. Open terminal
2. Navigate to project directory:
   ```bash
   cd /Users/ashapira/private/internal_development/4inArow
   ```
3. Run:
   ```bash
   python3 play_game.py
   ```
4. Press Enter for all defaults
5. Play!

**That's it!** 🎮

Enjoy your optimized Four-in-a-Row game!
