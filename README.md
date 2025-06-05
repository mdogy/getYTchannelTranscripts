# YouTube Channel Video Metadata Extractor

A Python tool to extract video metadata from YouTube channels and save it to CSV files.

## Features

- Extract video metadata from YouTube channels
- Filter videos by date range
- Save results to CSV files
- Comprehensive test suite
- Code quality checks with linting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/getYTchannelTranscripts.git
cd getYTchannelTranscripts
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

Basic usage:
```bash
python channel_videos_to_csv.py --channel "https://www.youtube.com/@ChannelName"
```

With date filtering:
```bash
python channel_videos_to_csv.py --channel "https://www.youtube.com/@ChannelName" --start-date "2023-01-01" --end-date "2023-12-31"
```

With logging:
```bash
python channel_videos_to_csv.py --channel "https://www.youtube.com/@ChannelName" --log output/run.log
```

## Development

### Running Tests and Linting

The project includes a comprehensive test suite and linting configuration. To run all checks:

```bash
./run_tests.sh
```

This will:
1. Run flake8 for code style checking
2. Run black for code formatting
3. Run mypy for type checking
4. Run pytest for unit tests

All output is saved to the `output` directory:
- `output/flake8.log`: Flake8 output
- `output/black.log`: Black formatting output
- `output/mypy.log`: Mypy type checking output
- `output/pytest.log`: Test output
- `output/test-results.xml`: Test results in JUnit XML format
- `output/test.log`: Test logging output

### Manual Testing

To run individual checks:

```bash
# Run flake8
flake8 .

# Run black
black .

# Run mypy
mypy .

# Run pytest
pytest
```

## Logging

The application uses Python's logging module with the following configuration:
- Console output: INFO level and above
- File output: DEBUG level and above
- Error log: ERROR level and above

Log files are stored in the `output` directory:
- `output/app.log`: General application logs
- `output/error.log`: Error logs
- `output/run.log`: Runtime logs (when --log is specified)

## License

MIT License
