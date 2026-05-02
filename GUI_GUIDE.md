# 🎮 GUI Mode - Modern Visual Interface

## Quick Start

```bash
python3 play_game_gui.py
```

That's it! A window will open with a modern graphical interface.

---

## Features

### 🎨 Visual Board
- **Colorful pieces**: Red (X) and Yellow (O)
- **Animated board**: Clean, modern design
- **Hover highlights**: Column highlights when you hover
- **Click to play**: Simply click the column to drop your piece

### 🤖 Smart AI Display
- **Progress indicators**: See AI thinking in real-time
- **Opening book status**: Shows when AI uses pre-computed moves
- **Evaluation scores**: Displays AI's confidence
- **Smooth animations**: Visual feedback for all moves

### ⚙️ Easy Configuration
- **Interactive dialog**: Configure game before starting
- **Board sizes**: 5×5, 7×6, 8×7
- **Who goes first**: You or AI
- **AI speed**: Fast (2s), Normal (5s), Strong (10s)
- **New Game button**: Restart anytime

---

## Screenshots (Text Description)

```
┌─────────────────────────────────────────┐
│  🎮 Four-in-a-Row                       │
├─────────────────────────────────────────┤
│                                         │
│    🎮 Your turn (X)                     │
│    Move 3 • 2 coins per turn • Coin 1/2│
│                                         │
│    0   1   2   3   4   5   6            │
│  ┌───┬───┬───┬───┬───┬───┬───┐         │
│  │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ ⚪ │ ⚪ │ ⚪ │ 🔴 │ ⚪ │ ⚪ │ ⚪ │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ ⚪ │ ⚪ │ 🟡 │ 🔴 │ ⚪ │ ⚪ │ ⚪ │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ ⚪ │ ⚪ │ 🟡 │ 🔴 │ 🟡 │ ⚪ │ ⚪ │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ 🟡 │ 🟡 │ 🔴 │ 🟡 │ 🔴 │ 🔴 │ ⚪ │         │
│  └───┴───┴───┴───┴───┴───┴───┘         │
│                                         │
│  [ New Game ]  [ Quit ]                 │
└─────────────────────────────────────────┘
```

---

## How to Play

### 1. Launch the Game
```bash
python3 play_game_gui.py
```

### 2. Configure
A dialog appears:
- **Board Size**: Choose 7×6 (recommended)
- **Who Goes First**: Choose "You (X)" or "AI (X)"
- **AI Speed**: Choose Normal (5s) for balanced play
- Click **Start Game**

### 3. Play
- **Your turn**: Click any column to drop a piece
- **AI turn**: Watch the progress bar and AI thinking
- **Win/Draw**: Dialog appears with "Play again?" option

### 4. New Game
Click **New Game** button anytime to reconfigure and restart

---

## Configuration Options

### Board Sizes

**5×5 (Quick)**
- Fast games
- Good for testing
- AI responds quickly

**7×6 (Standard) ⭐ Recommended**
- Official Connect Four size
- Balanced gameplay
- Best experience

**8×7 (Large)**
- Longer games
- More strategic
- Requires more thinking time

### AI Speed

**Fast (2s)**
- Quick responses
- Searches 4-6 moves ahead
- Good for casual play

**Normal (5s) ⭐ Recommended**
- Balanced speed/strength
- Searches 6-10 moves ahead
- Strong gameplay

**Strong (10s)**
- Deep thinking
- Searches 10-14 moves ahead
- Maximum difficulty

---

## Visual Elements

### Colors

- **Red (🔴)**: Player X
- **Yellow (🟡)**: Player O
- **White**: Empty spaces
- **Blue**: Board background
- **Green**: Column highlight on hover

### Status Display

**Top Section:**
```
🎮 Your turn (X)
Move 3 • 2 coins per turn • Coin 1/2
```

**During AI thinking:**
```
🤖 AI thinking...
🤖 Depth 4, eval +15, 2.3s
[Progress bar animating]
```

**Using opening book:**
```
📚 Opening book: eval +10
```

---

## Comparison: CLI vs GUI

| Feature | CLI (`play_game_fast.py`) | GUI (`play_game_gui.py`) |
|---------|---------------------------|--------------------------|
| **Interface** | Text-based terminal | Visual window |
| **Board** | ASCII characters | Graphical circles |
| **Input** | Type column number | Click column |
| **AI Progress** | Text updates | Progress bar + text |
| **Configuration** | Prompts | Dialog box |
| **User Experience** | Fast, minimal | Modern, intuitive |
| **Dependencies** | None | tkinter (built-in) |

---

## Requirements

### Python Version
- Python 3.7+

### Dependencies
- **tkinter**: Built-in with Python (no installation needed)
- **All game files**: board.py, four_in_a_row_with_progress.py

### Optional
- **Opening book**: `opening_book_7x6.pkl.gz` for instant early moves

---

## Advanced Features

### Opening Book Integration

The GUI automatically loads opening books if available:

```bash
# Generate opening book (one-time, 15 minutes)
python3 generate_opening_book.py

# Then play with GUI - first 10 moves are instant!
python3 play_game_gui.py
```

When opening book is active:
- Shows "📚 Opening book: eval +X" instead of progress bar
- Moves are instant (< 0.01s)
- No searching required

### Multi-Threading

The GUI uses threading to keep the interface responsive:
- AI calculations run in background thread
- Board remains interactive during AI thinking
- Progress updates in real-time
- No freezing or lag

---

## Tips for Playing

### Strategy
1. **Center columns** (especially column 3) are strongest
2. **Look ahead**: Think about opponent's next move
3. **Create threats**: Build multiple winning opportunities
4. **Block threats**: Stop opponent's 3-in-a-rows immediately
5. **Vertical traps**: Be careful stacking - opponent controls what's on top

### UI Tips
1. **Hover first**: See which column before clicking
2. **Watch progress**: Understand AI's thinking depth
3. **Use opening book**: Generate once for permanent speedup
4. **Try different speeds**: Fast for fun, Strong for challenge

---

## Troubleshooting

### "No module named 'tkinter'"

On some Linux systems, install tkinter:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS and Windows: Already included
```

### Window doesn't appear

Check if Python has GUI access:
```bash
python3 -c "import tkinter; tkinter.Tk()"
```

If error, you may need to:
- Run in terminal (not SSH)
- Enable GUI permissions (macOS Security)
- Use CLI version instead: `python3 play_game_fast.py`

### AI moves too slow

Reduce AI speed in configuration:
- Choose "Fast (2s)" option
- Or generate opening book for instant early moves

### Board looks weird

Adjust window size:
- Board auto-sizes based on configuration
- 7×6 board: ~600×500 pixels
- If too large/small, try different board size

---

## Command Summary

```bash
# Play with GUI (MODERN!)
python3 play_game_gui.py

# Play with CLI (original fast mode)
python3 play_game_fast.py

# Generate opening book (one-time setup)
python3 generate_opening_book.py

# Compare both interfaces
python3 play_game_fast.py    # CLI version
python3 play_game_gui.py     # GUI version
```

---

## Keyboard Shortcuts

Currently the GUI uses mouse input. Future versions may add:
- Number keys (0-6) for column selection
- Space bar to confirm
- Escape to quit
- R for new game

*For now: use mouse clicks*

---

## What's Next?

### Already Implemented ✅
- Modern graphical board
- Click-to-play interface
- Real-time progress display
- Opening book support
- Configuration dialog
- Win/draw detection
- Play again option

### Possible Future Enhancements
- Undo move button
- Move history display
- Save/load game
- Hints feature
- Piece animations (dropping effect)
- Sound effects
- Two-player mode (no AI)
- Network multiplayer

---

## Quick Comparison

**Use GUI (`play_game_gui.py`) when:**
- ✅ You want modern visual interface
- ✅ You prefer clicking to typing
- ✅ You want to see the board clearly
- ✅ You have a graphical environment

**Use CLI (`play_game_fast.py`) when:**
- ✅ You're in a terminal/SSH
- ✅ You prefer keyboard input
- ✅ You want minimal interface
- ✅ You're running on a server

**Both versions:**
- Use the same optimized engine
- Support opening books
- Show AI progress
- Have configurable settings
- Play at same strength

---

## Summary

The GUI version provides a modern, visual experience while maintaining all the features of the CLI version:

**Key Benefits:**
- 🎨 Beautiful visual board
- 🖱️ Click-to-play interface
- 📊 Real-time AI progress
- ⚙️ Easy configuration
- 🚀 Fast performance
- 📚 Opening book support

**Get Started:**
```bash
python3 play_game_gui.py
```

Enjoy your modern Four-in-a-Row experience! 🎮
