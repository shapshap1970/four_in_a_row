# Four-in-a-Row Web Version

A lightweight web interface for playing Four-in-a-Row against AI.

## Features

- 🎮 Clean, modern web UI with animations
- 🤖 Real-time AI thinking progress via WebSocket
- ⚡ Server-side AI computation (depth 12)
- 📖 Opening book support for faster opening moves
- 🎨 Beautiful gradient design with piece drop animations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-web.txt
```

### 2. Run the Server

```bash
python web_server.py
```

Or with uvicorn directly:

```bash
uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open in Browser

Visit: http://localhost:8000

## How to Play

1. Click "New Game (You Start)" to play first as Red (X)
2. Click "New Game (AI Starts)" to let AI play first as Yellow (O)
3. Click on any column to drop your piece
4. Watch the AI think in real-time with progress updates
5. First to connect 4 pieces (horizontally, vertically, or diagonally) wins!

## Architecture

### Backend (FastAPI)
- **REST API**: Game creation and human moves
- **WebSocket**: AI move computation with live progress updates
- **Async**: Non-blocking AI computation
- **In-memory sessions**: Fast game state management

### Frontend (Vanilla JS)
- **Zero dependencies**: Pure HTML/CSS/JavaScript
- **Responsive design**: Works on desktop and mobile
- **Real-time updates**: WebSocket for AI progress
- **Smooth animations**: CSS transitions and keyframes

### AI Engine
- **Minimax with alpha-beta pruning** at depth 12
- **Opening book**: Precomputed moves for first 8 moves
- **Heuristic evaluation**: Smart move ordering
- **10-30 seconds per move** (depending on position complexity)

## API Endpoints

### REST API
- `POST /api/game/new` - Create new game
- `POST /api/game/{game_id}/move` - Make player move
- `GET /api/game/{game_id}/state` - Get current game state

### WebSocket
- `WS /ws/{game_id}` - Connect for AI moves and progress updates

## Performance

- **Opening moves**: < 1 second (using opening book)
- **Mid-game**: 10-30 seconds (depth 12 search)
- **End-game**: 5-15 seconds (fewer positions to evaluate)

## Technical Details

- **Player pieces**: X (Red, Human)
- **AI pieces**: O (Yellow, Computer)
- **Board size**: 7 columns × 6 rows
- **Win condition**: 4 consecutive pieces
- **Search depth**: Fixed at 12 (no time-based iteration)

## Development

Run in development mode with auto-reload:

```bash
uvicorn web_server:app --reload --log-level debug
```

## Notes

- Opening book (`opening_book_7x6.json.gz`) is optional but recommended
- Each game session is stored in memory (cleared on server restart)
- WebSocket handles AI progress updates in real-time
- AI computation runs in executor to avoid blocking the event loop
