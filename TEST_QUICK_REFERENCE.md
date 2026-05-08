# Test Quick Reference Card

## 🚀 Quick Commands

```bash
# Fast tests (recommended)
./test.sh fast                    # 62 tests, ~2s

# All tests
./test.sh all                     # 72+ tests, ~60s

# Coverage report
./test.sh coverage                # HTML report + terminal

# Help
./test.sh help                    # Show all options
```

## 📊 Test Scripts

| Script | Purpose | Speed | Tests |
|--------|---------|-------|-------|
| `./test.sh fast` | Fast tests | 2s | 62 ✅ |
| `./test.sh all` | All tests | 60s | 72+ ✅ |
| `./run_tests_fast.sh` | Fast only | 2s | 62 ✅ |
| `./run_all_tests.sh` | Complete | 60s | 72+ ✅ |

## 🎯 Common Tasks

### Development (Fast Feedback)
```bash
./test.sh fast
```

### Before Commit (Complete Check)
```bash
./test.sh all
```

### Check Coverage
```bash
./test.sh coverage
open htmlcov/index.html
```

### Specific Test Type
```bash
./test.sh unit          # Unit tests only
./test.sh integration   # Integration only
./test.sh system        # System tests (slow)
```

## 📝 Direct pytest Commands

```bash
# Fast tests
python3.11 -m pytest tests/unit/ tests/integration/

# All tests
python3.11 -m pytest tests/

# Specific file
python3.11 -m pytest tests/unit/test_board.py

# Single test
python3.11 -m pytest tests/unit/test_board.py::TestBoardMoves::test_play_move

# With coverage
python3.11 -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=html
```

## 🏆 Test Status

✅ **62/62 fast tests passing**
✅ **1.1 second execution**
✅ **All optimized**

## 📚 Documentation

- `RUNNING_TESTS.md` - Complete guide
- `TEST_STATUS.md` - Current status
- `TESTS_OPTIMIZED.md` - Optimization details
- `tests/README.md` - Test structure

## 🔧 Options Summary

```bash
./test.sh fast         # ⚡ Fast tests (1-2s)
./test.sh all          # 🔄 All tests (~60s)
./test.sh unit         # 🧪 Unit only
./test.sh integration  # 🔗 Integration only
./test.sh system       # 🌐 System only (slow)
./test.sh coverage     # 📊 With coverage
./test.sh validate     # ✓ Validate suite
./test.sh help         # ❓ Show help
```

## 💡 Pro Tips

- Use `./test.sh fast` for quick development
- Use `./test.sh all` before pushing
- Check coverage with `./test.sh coverage`
- Skip slow tests: `python3.11 -m pytest tests/ -m "not slow"`

---
**All 62 fast tests passing in 1.1s!** ⚡✅
