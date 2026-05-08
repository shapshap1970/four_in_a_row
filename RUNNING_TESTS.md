# Running Tests - Four-in-a-Row

Complete guide for running all tests in the project.

## Quick Start

### Recommended: Fast Tests (1-2 seconds)
```bash
./test.sh fast
# or
./run_tests_fast.sh
```

### All Tests (including slow system tests)
```bash
./test.sh all
# or
./run_all_tests.sh
```

## Test Scripts Overview

### 1. `test.sh` - Master Test Runner ⭐ (Recommended)
Universal test runner with multiple options:

```bash
./test.sh [option]

Options:
  fast         Quick tests (unit + integration, ~2s)
  all          All tests including system tests (~60s)
  unit         Unit tests only
  integration  Integration tests only
  system       System tests only (slow)
  coverage     Tests with coverage report
  validate     Validate test suite
  help         Show help
```

**Examples:**
```bash
./test.sh fast          # Quick feedback
./test.sh all           # Complete test suite
./test.sh unit          # Only unit tests
./test.sh coverage      # Generate coverage report
```

### 2. `run_tests_fast.sh` - Fast Tests Only
Runs unit and integration tests (excludes slow system tests):
```bash
./run_tests_fast.sh
# 62 tests in ~2 seconds
```

### 3. `run_all_tests.sh` - Complete Test Suite
Runs ALL tests including slow system tests:
```bash
./run_all_tests.sh
# 72+ tests in ~60 seconds
```

### 4. `run_tests.sh` - Original Runner
Original test runner with all test types:
```bash
./run_tests.sh
```

### 5. `validate_tests.sh` - Test Validation
Validates each test suite separately:
```bash
./validate_tests.sh
```

## Direct pytest Commands

### Fast Tests (Recommended for Development)
```bash
# All fast tests
python3.11 -m pytest tests/unit/ tests/integration/

# Quiet mode
python3.11 -m pytest tests/unit/ tests/integration/ -q

# Verbose mode
python3.11 -m pytest tests/unit/ tests/integration/ -v
```

### All Tests
```bash
# Complete test suite
python3.11 -m pytest tests/

# Skip slow tests
python3.11 -m pytest tests/ -m "not slow"

# Only slow tests
python3.11 -m pytest tests/ -m slow
```

### Specific Test Suites
```bash
# Unit tests only
python3.11 -m pytest tests/unit/

# Integration tests only
python3.11 -m pytest tests/integration/

# System tests only
python3.11 -m pytest tests/system/
```

### Specific Test Files
```bash
# Board tests
python3.11 -m pytest tests/unit/test_board.py

# AI engine tests
python3.11 -m pytest tests/unit/test_ai_engine.py

# API tests
python3.11 -m pytest tests/integration/test_api.py
```

### Specific Test Cases
```bash
# Single test
python3.11 -m pytest tests/unit/test_board.py::TestBoardMoves::test_play_move

# Test class
python3.11 -m pytest tests/unit/test_board.py::TestBoardMoves
```

## Coverage Reports

### Generate HTML Coverage Report
```bash
# Fast tests with coverage
python3.11 -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

### Generate Terminal Coverage Report
```bash
python3.11 -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=term-missing
```

### All Tests with Coverage
```bash
python3.11 -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

## Test Performance

### Fast Tests ⚡
- **Unit Tests**: 47 tests, ~0.7s
- **Integration Tests**: 15 tests, ~0.4s
- **Total**: 62 tests, ~1.1s

### Slow Tests 🐢
- **System Tests**: 10+ tests, ~60s
- **Full Suite**: 72+ tests, ~60s

## Filtering Tests

### By Marker
```bash
# Skip slow tests (default for fast development)
python3.11 -m pytest tests/ -m "not slow"

# Only slow tests
python3.11 -m pytest tests/ -m slow

# Only unit tests (if marked)
python3.11 -m pytest tests/ -m unit
```

### By Keyword
```bash
# Tests with "board" in name
python3.11 -m pytest tests/ -k "board"

# Tests with "AI" or "engine"
python3.11 -m pytest tests/ -k "ai or engine"

# Exclude certain tests
python3.11 -m pytest tests/ -k "not slow"
```

## Test Output Options

### Verbosity
```bash
# Quiet (minimal output)
python3.11 -m pytest tests/unit/ -q

# Normal (default)
python3.11 -m pytest tests/unit/

# Verbose
python3.11 -m pytest tests/unit/ -v

# Very verbose
python3.11 -m pytest tests/unit/ -vv
```

### Traceback
```bash
# Short traceback
python3.11 -m pytest tests/unit/ --tb=short

# Line traceback
python3.11 -m pytest tests/unit/ --tb=line

# No traceback
python3.11 -m pytest tests/unit/ --tb=no

# Full traceback
python3.11 -m pytest tests/unit/ --tb=long
```

### Show Output
```bash
# Show print statements
python3.11 -m pytest tests/unit/ -s

# Show captured output on failure
python3.11 -m pytest tests/unit/ --capture=no
```

## Debugging Tests

### Stop on First Failure
```bash
python3.11 -m pytest tests/unit/ -x
```

### Stop After N Failures
```bash
python3.11 -m pytest tests/unit/ --maxfail=3
```

### Run Last Failed Tests
```bash
python3.11 -m pytest tests/unit/ --lf
```

### Run Failed First, Then Others
```bash
python3.11 -m pytest tests/unit/ --ff
```

### Show Durations (Slowest Tests)
```bash
python3.11 -m pytest tests/unit/ --durations=10
```

### Enter Debugger on Failure
```bash
python3.11 -m pytest tests/unit/ --pdb
```

## CI/CD Usage

### Fast CI (Every Commit)
```bash
# Quick validation
python3.11 -m pytest tests/unit/ tests/integration/ --tb=short
```

### Nightly/Full CI
```bash
# Complete test suite
python3.11 -m pytest tests/ --tb=short --maxfail=5
```

### With Coverage for CI
```bash
python3.11 -m pytest tests/unit/ tests/integration/ \
  --cov=. \
  --cov-report=xml \
  --cov-report=term-missing
```

## Troubleshooting

### pytest Not Found
```bash
# Install dependencies
pip install -r tests/requirements-test.txt
```

### Wrong Python Version
```bash
# Use python3.11 explicitly
python3.11 -m pytest tests/

# Or check version
python3.11 --version
```

### Tests Running Slow
```bash
# Run only fast tests
./test.sh fast

# Skip system tests
python3.11 -m pytest tests/ -m "not slow"
```

### Import Errors
```bash
# Run from project root
cd /Users/ashapira/private/internal_development/4inArow
python3.11 -m pytest tests/
```

## Summary

### For Quick Development
```bash
./test.sh fast              # Fastest option (1-2s)
```

### Before Committing
```bash
./test.sh all               # Full validation (~60s)
```

### For Coverage Check
```bash
./test.sh coverage          # With HTML report
```

### For Specific Testing
```bash
python3.11 -m pytest tests/unit/test_board.py -v
```

## Test Files Reference

```
tests/
├── unit/
│   ├── test_board.py              # 18 tests, Board logic
│   ├── test_ai_engine.py          # 17 tests, AI engine
│   └── test_web_server_logic.py   # 12 tests, Game state
├── integration/
│   └── test_api.py                # 15 tests, API endpoints
└── system/
    └── test_full_game.py          # 10+ tests, E2E scenarios (slow)
```

**Total: 72+ tests, all passing ✅**
