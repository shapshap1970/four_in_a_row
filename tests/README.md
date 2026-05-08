# Four-in-a-Row Test Suite

Comprehensive test suite covering unit, integration, and system tests.

## Test Structure

```
tests/
├── unit/                      # Unit tests (fast, isolated)
│   ├── test_board.py         # Board class tests
│   ├── test_ai_engine.py     # AI engine logic tests
│   └── test_web_server_logic.py  # Server logic tests
├── integration/               # Integration tests (API)
│   └── test_api.py           # FastAPI endpoint tests
└── system/                    # System/E2E tests (full game)
    └── test_full_game.py     # Complete game scenarios
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
pytest tests/unit/

# Integration tests
pytest tests/integration/

# System tests (requires server start)
pytest tests/system/

# Run by marker
pytest -m unit
pytest -m integration
pytest -m system
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Test File

```bash
pytest tests/unit/test_board.py
pytest tests/integration/test_api.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_board.py::TestBoardMoves::test_play_move
```

## Test Coverage

### Unit Tests (tests/unit/)

**test_board.py** - 100% Board class coverage
- Initialization (empty, copy, max_height)
- Move operations (play, possible moves, column filling)
- Win conditions (horizontal, vertical, diagonal)
- Game end detection (full board, draw)
- Board hashing

**test_ai_engine.py** - AI engine coverage
- Player switching logic
- Position evaluation (terminal, heuristic)
- Threat detection (horizontal, vertical)
- AI move generation
- Immediate win/block detection
- Memoization/caching

**test_web_server_logic.py** - Game state management
- Initial game state
- Turn logic (2-move rule)
- Win detection
- Valid moves calculation

### Integration Tests (tests/integration/)

**test_api.py** - FastAPI endpoints
- Game creation (player/AI starts)
- Player moves (valid/invalid)
- Game state retrieval
- Win condition detection through API
- Error handling (404, 400)
- HTML page serving

### System Tests (tests/system/)

**test_full_game.py** - Complete game scenarios
- Player wins (horizontal 4-in-a-row)
- AI wins
- Draw (full board, no winner)
- 2-move rule enforcement
- WebSocket communication
- Edge cases (full columns, invalid moves)

## Test Scenarios

### Player Wins
Tests complete game where player creates 4-in-a-row horizontally, vertically, or diagonally.

### AI Wins
Tests AI's ability to win the game through strategic play.

### Draw Game
Tests game ending in draw when board is full with no winner.

### Edge Cases
- Full column rejection
- Invalid column numbers (-1, 7+)
- WebSocket connection/disconnection
- Game state after moves

## Coverage Goals

- **Unit Tests**: 100% code coverage of core logic
- **Integration Tests**: All API endpoints covered
- **System Tests**: All game outcomes covered (win/lose/draw)

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```bash
# CI command
pytest --cov=. --cov-report=xml --cov-report=term-missing
```

## Notes

- **System tests** start an actual web server on localhost:8000
- Tests use `pytest-cov` for coverage reporting
- WebSocket tests use `websocket-client` library
- Integration tests use FastAPI `TestClient` (no server needed)
- All tests are independent and can run in any order

## Debugging Tests

```bash
# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Run and stop at first failure
pytest -x

# Run and open debugger on failure
pytest --pdb
```

## Performance

- Unit tests: ~1-2 seconds
- Integration tests: ~2-5 seconds  
- System tests: ~30-60 seconds (includes AI moves)

Total test suite: ~1 minute
