#!/usr/bin/env python3
"""
Build script to create Windows executable
"""

import os
import subprocess
import sys

def build_executable():
    """Build Windows executable using PyInstaller"""

    print("=" * 70)
    print("Building Windows Executable for Four-in-a-Row")
    print("=" * 70)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

    # Files to include
    data_files = [
        ('opening_book_7x6.pkl.gz', '.'),  # Include opening book
    ]

    # Build command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable
        '--name=FourInARow',  # Executable name
        '--console',  # Console application (not GUI)
        '--icon=NONE',  # No icon (can add later)
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite without asking
    ]

    # Add data files
    for src, dest in data_files:
        if os.path.exists(src):
            cmd.append(f'--add-data={src}{os.pathsep}{dest}')
            print(f"✓ Including: {src}")

    # Add the main script
    cmd.append('play_game_beautiful.py')

    print("\nBuilding executable...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 70)
        print("✅ Build successful!")
        print("=" * 70)
        print("\nExecutable location:")
        print("  → dist/FourInARow.exe")
        print("\nFile size:")
        exe_path = os.path.join('dist', 'FourInARow.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"  → {size_mb:.1f} MB")
        print("\nTo distribute:")
        print("  1. Copy dist/FourInARow.exe to Windows machine")
        print("  2. Double-click to run")
        print("  3. No Python installation required!")
        print("=" * 70)

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
