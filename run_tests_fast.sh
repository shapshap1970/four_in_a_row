#!/bin/bash
# Fast test runner - excludes slow system tests

echo "========================================"
echo "Fast Test Suite (Unit + Integration)"
echo "========================================"
echo

echo "Running Fast Tests (excluding slow system tests)..."
echo

# Run unit and integration tests only
python3.11 -m pytest tests/unit/ tests/integration/ -v --tb=short

echo
echo "========================================"
echo "Test Summary"
echo "========================================"
python3.11 -m pytest tests/unit/ tests/integration/ --tb=no -q

echo
echo "✅ Fast tests complete!"
echo
echo "To run ALL tests including slow system tests:"
echo "  pytest tests/ -v"
echo
echo "To run ONLY slow system tests:"
echo "  pytest tests/system/ -v"
echo
echo "To generate coverage report:"
echo "  pytest tests/unit/ tests/integration/ --cov=. --cov-report=html"
