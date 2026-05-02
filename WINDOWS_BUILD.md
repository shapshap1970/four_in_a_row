# Building Windows Executable

## Quick Build (Automated)

### On macOS/Linux:
```bash
python3 build_windows_exe.py
```

### On Windows:
```bash
python build_windows_exe.py
```

This will create `dist/FourInARow.exe` ready to distribute!

---

## Manual Build Steps

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the Executable

**Option A: Using the spec file (Recommended)**
```bash
pyinstaller FourInARow.spec
```

**Option B: Direct command**
```bash
pyinstaller --onefile --name=FourInARow --console \
  --add-data="opening_book_7x6.pkl.gz:." \
  play_game_beautiful.py
```

### 3. Find Your Executable

The executable will be in:
```
dist/FourInARow.exe
```

---

## Distribution

### What to Share:

**Just the executable:**
- `dist/FourInARow.exe` (~10-15 MB)

**That's it!** The opening book is embedded inside.

### Requirements for Users:
- ✅ Windows 7/8/10/11
- ✅ No Python required
- ✅ No additional installation needed
- ✅ Double-click to run!

---

## Build on Different Platforms

### Building Windows .exe from macOS (Cross-compile):

Unfortunately, PyInstaller **cannot cross-compile**. You need to build on the target platform:
- Windows .exe → Must build on Windows
- macOS app → Must build on macOS
- Linux binary → Must build on Linux

### Solutions:

**Option 1: Use a Windows VM**
- Install Windows in VirtualBox/Parallels
- Install Python on the VM
- Build inside the VM

**Option 2: Use GitHub Actions (Automated)**
- Set up CI/CD to build for multiple platforms
- GitHub Actions can build for Windows/Mac/Linux automatically

**Option 3: Ask a Windows user to build**
- Share the source code
- They run: `python build_windows_exe.py`
- They send you back the .exe

---

## File Sizes

Expected file sizes:
- **Without opening book**: ~8-10 MB
- **With opening book**: ~10-15 MB

If the file is too large (>30 MB), PyInstaller may be including unnecessary libraries. Use the spec file to exclude them.

---

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" errors
Add to `hiddenimports` in `FourInARow.spec`:
```python
hiddenimports = ['missing_module_name']
```

### Exe is too large
Exclude unnecessary packages in `FourInARow.spec`:
```python
excludes = ['matplotlib', 'numpy', 'tkinter']
```

### Colors not working in Windows
Windows 10+ supports ANSI colors by default. On older Windows:
- Run in Windows Terminal (recommended)
- Or use ConEmu / Cmder
- Or the colors will show as escape codes (still playable)

### Opening book not loading
Make sure `opening_book_7x6.pkl.gz` is included:
```bash
pyinstaller --add-data="opening_book_7x6.pkl.gz:." FourInARow.spec
```

---

## Advanced: Build for All Platforms

### Create platform-specific builds:

**1. Windows .exe:**
```bash
# On Windows machine
python build_windows_exe.py
# → dist/FourInARow.exe
```

**2. macOS app:**
```bash
# On Mac
pyinstaller --onefile --windowed --name=FourInARow \
  --add-data="opening_book_7x6.pkl.gz:." \
  play_game_beautiful.py
# → dist/FourInARow.app
```

**3. Linux binary:**
```bash
# On Linux
pyinstaller --onefile --name=FourInARow \
  --add-data="opening_book_7x6.pkl.gz:." \
  play_game_beautiful.py
# → dist/FourInARow
```

---

## Testing the Executable

### On Windows:

1. **Double-click** `FourInARow.exe`
2. Or run from Command Prompt:
   ```cmd
   FourInARow.exe
   ```

3. You should see the colored game interface

### Expected Behavior:

- ✅ Colors display correctly (Windows 10+)
- ✅ Opening book loads automatically
- ✅ First 6 moves are instant
- ✅ Game is fully playable
- ✅ No Python installation required

---

## Distribution Checklist

Before sharing your .exe:

- [ ] Test on clean Windows machine (no Python)
- [ ] Verify colors work
- [ ] Verify opening book loads
- [ ] Check file size is reasonable (<20 MB)
- [ ] Test all game modes (5×5, 7×6)
- [ ] Test AI at different speeds
- [ ] Verify "New Game" and "Quit" work

---

## GitHub Release (Recommended)

Upload the .exe to GitHub Releases:

1. Create a new release
2. Upload `FourInARow.exe`
3. Add release notes
4. Users can download directly

Example release notes:
```markdown
# Four-in-a-Row v1.0

Windows executable - no installation required!

## Features:
- 🎨 Beautiful colored CLI interface
- 🤖 Smart AI with 3 difficulty levels
- ⚡ Opening book for instant early moves
- 📊 Real-time progress display

## Download:
- [FourInARow.exe](link) - Windows 7/8/10/11

## Usage:
1. Download FourInARow.exe
2. Double-click to run
3. Follow on-screen prompts
4. Enjoy!

## Requirements:
- Windows 7 or later
- No additional software needed
```

---

## Summary

**To build Windows .exe:**
```bash
# Quick way
python3 build_windows_exe.py

# Manual way
pyinstaller FourInARow.spec
```

**Result:**
- Single file: `dist/FourInARow.exe`
- Size: ~10-15 MB
- Includes opening book
- No dependencies
- Ready to distribute!

**Share with:**
- ✅ Anyone with Windows
- ✅ No Python required
- ✅ No installation needed
- ✅ Just double-click and play!
