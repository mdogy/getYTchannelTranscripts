#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p output

# Run flake8 and save output to file
echo "Running flake8..."
flake8 . > output/flake8.log 2>&1
flake8_status=$?

# Run black and save output to file
echo "Running black..."
black . > output/black.log 2>&1
black_status=$?

# Run mypy and save output to file
echo "Running mypy..."
mypy . > output/mypy.log 2>&1
mypy_status=$?

# Run pytest and save output to file
echo "Running pytest..."
pytest --junitxml=output/test-results.xml > output/pytest.log 2>&1
pytest_status=$?

# Print summary
echo "=== Test Summary ==="
echo "flake8: $([ $flake8_status -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "black: $([ $black_status -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "mypy: $([ $mypy_status -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "pytest: $([ $pytest_status -eq 0 ] && echo "PASS" || echo "FAIL")"

# Exit with failure if any test failed
if [ $flake8_status -ne 0 ] || [ $black_status -ne 0 ] || [ $mypy_status -ne 0 ] || [ $pytest_status -ne 0 ]; then
    exit 1
fi 