# Windows Executable Build - Quick Reference

## For You (macOS user):

**You cannot build Windows .exe on macOS directly.**

PyInstaller requires building on the target platform.

### Your Options:

#### Option 1: Use a Windows VM ⭐ Recommended
```bash
# On Windows VM:
1. Install Python 3.9+
2. Copy this project folder
3. Run: build_windows.bat
4. Get: dist/FourInARow.exe
```

#### Option 2: GitHub Actions (Automated)
Set up CI/CD to build automatically for Windows/Mac/Linux

#### Option 3: Ask someone with Windows
Share the project, they run `build_windows.bat`

---

## For Windows Users:

### Easy Build (Double-click):
```
build_windows.bat
```

### Manual Build:
```bash
pip install pyinstaller
python build_windows_exe.py
```

### Result:
- `dist/FourInARow.exe` (~10-15 MB)
- Includes opening book
- No dependencies
- Ready to distribute!

---

## Files Created:

| File | Purpose |
|------|---------|
| `build_windows_exe.py` | Automated build script (Python) |
| `build_windows.bat` | Easy build for Windows (batch file) |
| `FourInARow.spec` | PyInstaller configuration |
| `WINDOWS_BUILD.md` | Complete build documentation |
| `README_WINDOWS.md` | User guide for .exe users |

---

## Distribution:

**What to share:**
- Just `FourInARow.exe` (everything embedded)

**Users need:**
- Windows 7+
- Nothing else!

---

## Quick Commands:

```bash
# Install dependencies
pip install pyinstaller

# Build (any of these):
python build_windows_exe.py          # Automated
pyinstaller FourInARow.spec          # Using spec file
build_windows.bat                    # Windows batch (double-click)

# Result
dist/FourInARow.exe
```

---

## File Sizes:

- **Executable:** ~10-15 MB
- **Opening book (embedded):** ~0.1 MB
- **Python runtime:** ~8-10 MB

Total: ~15 MB single file

---

## Current Status:

✅ Build scripts ready
✅ Documentation complete
✅ Spec file configured
⏳ **Needs Windows machine to actually build**

The code is ready. Just needs Windows to execute the build!
