#!/bin/bash
# Validate test suite

echo "========================================"
echo "Test Suite Validation"
echo "========================================"
echo

echo "1. Running Board Tests..."
python3.11 -m pytest tests/unit/test_board.py -q
if [ $? -eq 0 ]; then
    echo "   ✅ Board tests: PASS"
else
    echo "   ❌ Board tests: FAIL"
    exit 1
fi

echo
echo "2. Running AI Engine Tests..."
python3.11 -m pytest tests/unit/test_ai_engine.py -q
if [ $? -eq 0 ]; then
    echo "   ✅ AI Engine tests: PASS"
else
    echo "   ❌ AI Engine tests: FAIL"
    exit 1
fi

echo
echo "3. Running Game Logic Tests..."
python3.11 -m pytest tests/unit/test_web_server_logic.py -q
if [ $? -eq 0 ]; then
    echo "   ✅ Game Logic tests: PASS"
else
    echo "   ❌ Game Logic tests: FAIL"
    exit 1
fi

echo
echo "4. Running Integration Tests..."
python3.11 -m pytest tests/integration/ -q
if [ $? -eq 0 ]; then
    echo "   ✅ Integration tests: PASS"
else
    echo "   ❌ Integration tests: FAIL"
    exit 1
fi

echo
echo "========================================"
echo "✅ All Fast Tests Passing!"
echo "========================================"
echo
echo "Test counts:"
python3.11 -m pytest tests/unit/ tests/integration/ --collect-only -q | tail -1
echo
echo "To run with coverage:"
echo "  pytest tests/unit/ tests/integration/ --cov=. --cov-report=html"
echo
echo "To run slow system tests:"
echo "  pytest tests/system/ -v"
