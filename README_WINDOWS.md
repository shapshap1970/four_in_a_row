# Four-in-a-Row for Windows

## Quick Start

1. **Download** `FourInARow.exe`
2. **Double-click** to run
3. **Play!**

No installation needed. No Python required.

---

## How to Play

### Starting the Game:

When you run `FourInARow.exe`, you'll see:

1. **Board Size** - Choose 7×6 (recommended)
2. **Who goes first** - Choose "You" or "AI"
3. **AI Speed** - Choose Normal (5s)

Press Enter for defaults!

### Playing:

- You'll see a **colored board** with:
  - 🔴 **Red circles** = Player X
  - 🟡 **Yellow circles** = Player O
  - ⚪ **White dots** = Empty spaces

- **Your turn**: Type a column number (0-6) and press Enter
- **AI turn**: Watch the AI think and make its move

### Winning:

Get **4 in a row** (horizontal, vertical, or diagonal) to win!

---

## Features

✨ **Beautiful Interface**
- Colored pieces and borders
- Clear visual feedback
- Professional look

🤖 **Smart AI**
- 3 difficulty levels (Fast/Normal/Strong)
- Opening book for instant early moves
- Real-time progress display

⚡ **Performance**
- First 6 moves are INSTANT (< 0.01s)
- Later moves take 2-10 seconds depending on difficulty
- Optimized minimax algorithm with alpha-beta pruning

---

## Game Rules

### Special Rule: 2 Moves Per Turn

This is not standard Connect Four!

- **First move**: Player X plays 1 coin
- **After that**: Each player plays 2 coins per turn
- **Win condition**: 4 in a row (any direction)

This makes the game more strategic and faster-paced!

---

## Troubleshooting

### Colors not showing?

**Windows 10/11:** Colors should work automatically.

**Windows 7/8:** Use Windows Terminal or ConEmu:
- Download [Windows Terminal](https://aka.ms/terminal)
- Or use [ConEmu](https://conemu.github.io/)

### Antivirus blocking?

Some antivirus software may flag .exe files built with PyInstaller:
- This is a **false positive**
- The source code is open and safe
- Add exception in your antivirus if needed

### Game running slow?

- Choose "Fast" mode (2 seconds AI)
- Or play without opening book (still fast)

### Can't type moves?

- Make sure Command Prompt window is focused
- Click on the window if needed

---

## System Requirements

- **OS:** Windows 7/8/10/11
- **RAM:** 50 MB minimum
- **Disk:** 15 MB
- **Other:** None!

---

## Tips for Playing

### Strategy:
1. **Control the center** (column 3) - it's the strongest position
2. **Look ahead** - Think about opponent's next move
3. **Create threats** - Force opponent to respond
4. **Block 3-in-a-rows** - Immediately stop opponent's winning moves
5. **Watch vertical stacks** - Be careful, opponent controls what's on top

### Difficulty Levels:
- **Fast (2s):** Good for casual play, searches 4-6 moves ahead
- **Normal (5s):** Balanced, searches 6-10 moves ahead (Recommended)
- **Strong (10s):** Very difficult, searches 10-14 moves ahead

The AI is quite strong - don't be discouraged if you lose!

---

## What's Included

The executable includes:
- ✅ Complete game engine
- ✅ Opening book (6 pre-computed positions)
- ✅ All game modes
- ✅ Progress display
- ✅ Everything self-contained

**No additional files needed!**

---

## Source Code

This game is open source!

View the code at: [GitHub Repository URL]

**Technologies:**
- Python 3.9+
- Minimax algorithm with alpha-beta pruning
- Iterative deepening search
- Transposition tables (memoization)
- Opening book generation

---

## Support

Having issues? Questions?

1. Check this README
2. Check WINDOWS_BUILD.md (for building)
3. Open an issue on GitHub

---

## Version

**Version:** 1.0
**Build Date:** 2025-05-02
**Python Version:** 3.9+

---

## License

[Add your license here]

---

## Credits

Created with ❤️ using Python and PyInstaller

Built with assistance from Claude (Anthropic)

---

## Enjoy!

Have fun playing Four-in-a-Row! 🎮

Try to beat the AI - it's quite smart! 🤖
