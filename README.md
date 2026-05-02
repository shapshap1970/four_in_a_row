# 4 in a Row (Connect Four) with AI

A Python implementation of the classic Connect Four game with an AI opponent powered by the minimax algorithm with alpha-beta pruning optimization.

## Overview

This project implements a customizable Connect Four game where you can play against an intelligent AI opponent. The AI uses the minimax algorithm to calculate optimal moves and pre-trains on the game space to provide fast, strategic gameplay.

## Features

- **Configurable Game Board**: Choose board dimensions (4x4, 4x5, 5x4, or 5x5)
- **Variable Moves Per Turn**: Play with 1 or 2 consecutive moves per turn
- **Intelligent AI Opponent**: Uses minimax algorithm with memoization for optimal play
- **Pre-trained Models**: AI pre-trains on game configurations and saves them for instant loading
- **Beautiful Terminal Display**: Rich color-coded board visualization using the `rich` library
- **Replay Option**: Play multiple games in a row
- **Choose Starting Player**: Select whether you or the AI goes first

## Project Structure

- **game.py**: Main game orchestrator - handles game flow, user input, model training/loading, and game loop
- **board.py**: Board representation with move validation, winner detection, and efficient hashing for memoization
- **four_in_a_row.py**: Core game logic implementing the minimax algorithm for AI decision-making
- **display.py**: Terminal UI using the `rich` library for colorful board display
- **file_util.py**: Utilities for saving/loading compressed game state caches

## How It Works

### Game Logic

The game follows Connect Four rules: players alternate dropping pieces into columns, trying to get 4 in a row horizontally, vertically, or diagonally.

### AI Strategy

The AI uses the **minimax algorithm** with the following features:
- Evaluates all possible game states to determine optimal moves
- Uses memoization to cache previously evaluated positions
- Pre-trains on empty boards before the game starts
- Provides heuristic messages indicating the game outcome if both players play optimally

### Evaluation System

- **+2**: X (AI) wins
- **-2**: O (Player) wins
- **+1**: Draw (board full, no winner)
- **None**: Game still in progress

## Requirements

```
python 3.x
rich
bitarray
```

## Usage

Run the game:

```bash
python game.py
```

You'll be prompted to configure the game:
1. Number of columns (4-5)
2. Number of rows (4-5)
3. Moves per turn (1 or 2)
4. Who starts (Player or AI)

The AI will pre-train on the first run for each configuration (saved to cache files like `memoization_cache.pkl-5-5-4-1.zip`).

## Game Flow

1. Game initializes and loads/trains the AI model
2. Board displays in the terminal
3. Players alternate turns (making 1 or 2 moves per turn depending on configuration)
4. After each move, the AI provides a heuristic message about the game state
5. Game ends when someone gets 4 in a row or the board is full
6. Option to replay with the same configuration

## Technical Details

### Board Hashing

The board state is efficiently hashed using a bit array representation:
- Each cell uses 2 bits: `00` (empty), `01` (X), `10` (O)
- Enables fast memoization lookup for previously evaluated positions

### Minimax Implementation

- Recursive depth-limited search (depth 25 for gameplay, depth 50 for training)
- Alpha-beta pruning for optimization (early termination when definitive outcome found)
- Handles variable consecutive moves per turn
- Memoizes all evaluated states for instant replay

## Cache Files

Pre-trained models are saved as compressed pickle files with naming convention:
```
memoization_cache.pkl-{ROWS}-{COLS}-{CONSEC_TO_WIN}-{CONSEC_MOVES}.zip
```

These files can be large but significantly speed up gameplay after initial training.
