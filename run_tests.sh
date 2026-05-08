#!/bin/bash
# Test runner script

echo "=================================="
echo "Four-in-a-Row Test Suite"
echo "=================================="
echo

echo "Running Unit Tests..."
python3.11 -m pytest tests/unit/ -v --tb=short --maxfail=5

echo
echo "Running Integration Tests..."
python3.11 -m pytest tests/integration/ -v --tb=short --maxfail=5

echo
echo "=================================="
echo "Test Summary"
echo "=================================="
python3.11 -m pytest tests/ --tb=no -q

echo
echo "To run with coverage:"
echo "  pytest --cov=. --cov-report=html"
echo
echo "To run system tests (requires server):"
echo "  pytest tests/system/ -v"
