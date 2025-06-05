#!/bin/bash

# Create necessary directories
mkdir -p var/logs

# Run flake8
echo "Running flake8..."
flake8 . > var/logs/flake8.log 2>&1

# Run black
echo "Running black..."
black . > var/logs/black.log 2>&1

# Run mypy
echo "Running mypy..."
mypy --explicit-package-bases src/youtube_transcripts > var/logs/mypy.log 2>&1

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
if [ $(grep -q "error" var/logs/flake8.log) -ne 0 ] || [ $(grep -q "error" var/logs/black.log) -ne 0 ] || [ $(grep -q "error" var/logs/mypy.log) -ne 0 ] || [ $(grep -q "FAILED" var/logs/pytest.log) -ne 0 ]; then
    exit 1
fi 