@echo off
REM Build script for Windows users
REM Double-click this file to build FourInARow.exe

echo ===============================================
echo Building Four-in-a-Row Windows Executable
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python...
python --version
echo.

REM Install PyInstaller if needed
echo [2/3] Installing PyInstaller...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo PyInstaller installed.
echo.

REM Build the executable
echo [3/3] Building executable...
echo This may take 1-2 minutes...
echo.

python build_windows_exe.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ===============================================
echo BUILD COMPLETE!
echo ===============================================
echo.
echo Your executable is ready:
echo   dist\FourInARow.exe
echo.
echo You can now:
echo   1. Run it: dist\FourInARow.exe
echo   2. Share it with others
echo   3. No Python needed to run!
echo.
pause
