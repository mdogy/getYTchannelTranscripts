# YouTube Channel Video Metadata and Transcript Extractor

A Python tool to extract video metadata from YouTube channels and transcripts from videos.

## Features

- Extract video metadata from YouTube channels
- Extract transcripts from YouTube videos
- Filter videos by date range
- Save results to CSV files or text/markdown
- Support for timestamps in transcripts
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

### Extracting Channel Video Metadata

Basic usage:
```bash
channel-videos-to-csv --channel "https://www.youtube.com/@ChannelName"
```

With date filtering:
```bash
channel-videos-to-csv --channel "https://www.youtube.com/@ChannelName" --start-date "2023-01-01" --end-date "2023-12-31"
```

Get videos from the past year with all metadata:
```bash
# Calculate dates for the past year
channel-videos-to-csv \
  --channel "https://www.youtube.com/@ChannelName" \
  --start-date "$(date -v-1y +%Y-%m-%d)" \
  --end-date "$(date +%Y-%m-%d)" \
  --output "output/channel_videos_past_year.csv" \
  --log "var/logs/run.log"
```

### Extracting Video Transcripts

Basic usage (outputs to stdout):
```bash
extract-video-transcript "https://www.youtube.com/watch?v=VIDEO_ID"
```

Save to file:
```bash
extract-video-transcript "https://www.youtube.com/watch?v=VIDEO_ID" -o output/transcript.txt
```

Save as markdown with timestamps:
```bash
extract-video-transcript "https://www.youtube.com/watch?v=VIDEO_ID" --format markdown -o output/transcript.md
```

Save without timestamps:
```bash
extract-video-transcript "https://www.youtube.com/watch?v=VIDEO_ID" --no-timestamps -o output/transcript.txt
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

Log files are stored in the `var/logs` directory:
- `var/logs/app.log`: General application logs
- `var/logs/error.log`: Error logs
- `var/logs/run.log`: Runtime logs (when --log is specified)

## License

MIT License
