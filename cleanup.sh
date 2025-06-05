#!/bin/bash

# Remove all log files from var/logs
rm -f var/logs/*.log

# Remove all test results
rm -f var/test-results/*.xml

# Remove all temporary files
rm -f var/tmp/*

# Remove all test-results.xml files in subdirectories of var
find var -name "test-results.xml" -type f -delete

# Remove coverage files
rm -rf htmlcov/
rm -f .coverage
rm -f coverage.xml

# Remove CSV files from output
rm -f output/*.csv

# Remove cache directories
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf __pycache__/
rm -rf */__pycache__/

echo "Cleanup completed!" 