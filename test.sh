#!/bin/bash
# Master test runner with options

PYTHON="python3.11"

show_help() {
    echo "Four-in-a-Row Test Runner"
    echo
    echo "Usage: ./test.sh [option]"
    echo
    echo "Options:"
    echo "  fast, f         Run fast tests only (unit + integration, ~2s)"
    echo "  all, a          Run all tests including slow system tests (~60s)"
    echo "  unit, u         Run unit tests only"
    echo "  integration, i  Run integration tests only"
    echo "  system, s       Run system tests only (slow)"
    echo "  coverage, cov   Run fast tests with coverage report"
    echo "  validate, v     Validate test suite"
    echo "  help, h         Show this help message"
    echo
    echo "Examples:"
    echo "  ./test.sh fast          # Quick feedback (recommended)"
    echo "  ./test.sh all           # Full test suite"
    echo "  ./test.sh cov           # Coverage report"
    echo
}

run_fast() {
    echo "⚡ Running Fast Tests (Unit + Integration)"
    echo "==========================================="
    $PYTHON -m pytest tests/unit/ tests/integration/ -v --tb=short
}

run_all() {
    echo "🔄 Running All Tests (Including System Tests)"
    echo "==========================================="
    echo "⏱️  This may take ~60 seconds..."
    echo
    $PYTHON -m pytest tests/ -v --tb=short
}

run_unit() {
    echo "🧪 Running Unit Tests Only"
    echo "==========================================="
    $PYTHON -m pytest tests/unit/ -v --tb=short
}

run_integration() {
    echo "🔗 Running Integration Tests Only"
    echo "==========================================="
    $PYTHON -m pytest tests/integration/ -v --tb=short
}

run_system() {
    echo "🌐 Running System Tests Only (Slow)"
    echo "==========================================="
    echo "⏱️  This may take ~60 seconds..."
    echo
    $PYTHON -m pytest tests/system/ -v --tb=short
}

run_coverage() {
    echo "📊 Running Tests with Coverage"
    echo "==========================================="
    $PYTHON -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=html --cov-report=term-missing
    echo
    echo "✅ Coverage report generated!"
    echo "   View report: open htmlcov/index.html"
}

run_validate() {
    echo "✓ Validating Test Suite"
    echo "==========================================="
    ./validate_tests.sh
}

# Main script
case "${1:-fast}" in
    fast|f)
        run_fast
        ;;
    all|a)
        run_all
        ;;
    unit|u)
        run_unit
        ;;
    integration|i)
        run_integration
        ;;
    system|s)
        run_system
        ;;
    coverage|cov)
        run_coverage
        ;;
    validate|v)
        run_validate
        ;;
    help|h|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        echo
        show_help
        exit 1
        ;;
esac
