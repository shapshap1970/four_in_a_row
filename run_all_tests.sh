#!/bin/bash
# Complete test runner - runs ALL tests including slow system tests

echo "==========================================="
echo "Complete Test Suite - All Tests"
echo "==========================================="
echo
echo "⚠️  This includes slow system tests (~60s)"
echo

# Check if pytest is available
if ! python3.11 -m pytest --version &> /dev/null; then
    echo "❌ Error: pytest not found"
    echo "Install dependencies: pip install -r tests/requirements-test.txt"
    exit 1
fi

echo "1️⃣  Running Unit Tests..."
echo "-------------------------------------------"
python3.11 -m pytest tests/unit/ -v --tb=short
UNIT_EXIT=$?

echo
echo "2️⃣  Running Integration Tests..."
echo "-------------------------------------------"
python3.11 -m pytest tests/integration/ -v --tb=short
INTEGRATION_EXIT=$?

echo
echo "3️⃣  Running System Tests (slow)..."
echo "-------------------------------------------"
echo "⏱️  This may take ~60 seconds..."
python3.11 -m pytest tests/system/ -v --tb=short
SYSTEM_EXIT=$?

echo
echo "==========================================="
echo "Test Summary"
echo "==========================================="
echo

# Summary
if [ $UNIT_EXIT -eq 0 ] && [ $INTEGRATION_EXIT -eq 0 ] && [ $SYSTEM_EXIT -eq 0 ]; then
    echo "✅ All tests PASSED!"
    echo
    python3.11 -m pytest tests/ --tb=no -q
    echo
    echo "==========================================="
    echo "Test Coverage Breakdown"
    echo "==========================================="
    echo "Unit Tests:        47 tests ✅"
    echo "Integration Tests: 15 tests ✅"
    echo "System Tests:      10+ tests ✅"
    echo "==========================================="
    exit 0
else
    echo "❌ Some tests FAILED"
    echo
    [ $UNIT_EXIT -ne 0 ] && echo "  ❌ Unit tests failed"
    [ $INTEGRATION_EXIT -ne 0 ] && echo "  ❌ Integration tests failed"
    [ $SYSTEM_EXIT -ne 0 ] && echo "  ❌ System tests failed"
    echo
    exit 1
fi
