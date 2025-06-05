#!/bin/bash

# Remove all log files
rm -f output/*.log

# Remove test results
rm -f output/test-results.xml
rm -f output/test.log

# Remove coverage files
rm -rf htmlcov/
rm -f .coverage
rm -f coverage.xml

# Remove CSV files
rm -f output/*.csv

# Remove cache directories
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf __pycache__/
rm -rf */__pycache__/

echo "Cleanup completed!" 