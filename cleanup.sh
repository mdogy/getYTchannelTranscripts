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
rm -f .coverage.*
rm -f coverage.xml

# Remove CSV files from output
rm -f output/*.csv

# Remove cache directories
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf __pycache__/
rm -rf */__pycache__/
rm -rf src/**/__pycache__/
rm -rf tests/**/__pycache__/

# Remove build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf src/*.egg-info/
rm -rf youtube_channel_metadata.egg-info/

# Remove IDE-specific files
rm -rf .idea/
rm -rf .vscode/
rm -rf *.swp
rm -rf *.swo

# Remove Python virtual environment (if exists)
if [ -d "venv" ]; then
    rm -rf venv/
fi

# Remove any .DS_Store files (macOS)
find . -name ".DS_Store" -delete

# Remove pip cache if present
rm -rf ~/.cache/pip

# Remove any pip wheelhouse
rm -rf wheelhouse/

# Remove any pip log files
rm -f pip-log.txt

# Remove any pyc files
find . -name "*.pyc" -delete

# Remove any pyo files
find . -name "*.pyo" -delete

# Remove any .pyd files
find . -name "*.pyd" -delete

echo "Cleanup completed!" 