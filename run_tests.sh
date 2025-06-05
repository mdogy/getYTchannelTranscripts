#!/bin/bash

# Create necessary directories
mkdir -p var/logs

# Run flake8
echo "Running flake8..."
flake8 . > var/logs/flake8.log 2>&1

# Run black
echo "Running black..."
black . > var/logs/black.log 2>&1

# Run mypy from within src directory
echo "Running mypy..."
(cd src && mypy --explicit-package-bases youtube_transcripts) > var/logs/mypy.log 2>&1

# Run pytest
echo "Running pytest..."
pytest --junitxml=var/logs/test-results.xml > var/logs/pytest.log 2>&1

# Print test summary
echo "=== Test Summary ==="
echo "flake8: $(grep -q "error" var/logs/flake8.log && echo "FAIL" || echo "PASS")"
echo "black: $(grep -q "error" var/logs/black.log && echo "FAIL" || echo "PASS")"
echo "mypy: $(grep -q "error" var/logs/mypy.log && echo "FAIL" || echo "PASS")"
echo "pytest: $(grep -q "FAILED" var/logs/pytest.log && echo "FAIL" || echo "PASS")"

# Exit with failure if any test failed
if grep -q "error" var/logs/flake8.log || grep -q "error" var/logs/black.log || grep -q "error" var/logs/mypy.log || grep -q "FAILED" var/logs/pytest.log; then
    exit 1
fi 