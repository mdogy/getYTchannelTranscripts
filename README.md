# YouTube Channel Video Metadata and Transcript Extractor

A Python tool to extract video metadata from YouTube channels and auto-generated transcripts from individual videos, designed for data analysis workflows.

## Features

- Extract comprehensive video metadata from entire YouTube channels.
- Extract auto-generated English transcripts from any YouTube video.
- Filter a channel's videos by a specified date range.
- Limit the number of recent videos to process from a channel.
- Save channel metadata to a CSV file.
- Save individual transcripts to clean text or markdown files.
- Command-line option to include or exclude timestamps in transcripts.
- Robust logging for troubleshooting.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/getYTchannelTranscripts.git
    cd getYTchannelTranscripts
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the package in editable mode:**

    This command uses the `setup.py` file to install the project and its dependencies, making the command-line scripts available in your environment. The `-e` flag means changes you make to the source code will take effect immediately without reinstalling.

    ```bash
    pip install -e .
    ```

4.  **(Optional) Install development dependencies:**
    If you plan to run tests or contribute to the code, install the development dependencies.
    ```bash
    pip install -e ".[dev]"
    ```

## Usage

### Extracting Channel Video Metadata

The `channel-videos-to-csv` script fetches video data from a channel and saves it to a CSV file.

**Basic usage:**
*Note: The `--output` argument is required.*
```bash
channel-videos-to-csv --channel "https://www.youtube.com/@MrBeast" --output "output/mrbeast_videos.csv"
```
**Note:** Setting the `--limit` parameter to `-1` will retrieve all videos without limitation, which may result in a very long execution time.

**Limit to the 50 most recent videos:**
```bash
channel-videos-to-csv --channel "https://www.youtube.com/@MrBeast" --limit 50 --output "output/mrbeast_latest_50.csv"
```

**Get videos from a specific date range:**
```bash
channel-videos-to-csv \
  --channel "https://www.youtube.com/@lexfridman" \
  --start-date "2023-01-01" \
  --end-date "2023-03-31" \
  --output "output/lex_q1_2023.csv"
```

### Extracting a Video Transcript

The `extract-video-transcript` script downloads the auto-generated transcript for a single video.

**Basic usage:**
*This saves the transcript with timestamps to a generated filename in the `output/` directory.*
```bash
extract-video-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Save to a specific file without timestamps:**
```bash
extract-video-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-timestamps -o "output/my_transcript.txt"
```

**Save as Markdown with timestamps:**
```bash
extract-video-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format markdown -o "output/my_transcript.md"
```

## Development

The project includes a comprehensive test suite and linting configuration.

### Running Tests and Linting

To run all checks (requires development dependencies):

```bash
# Run flake8 for code style checking
flake8 src tests

# Run black to format code
black src tests

# Run mypy for static type checking
mypy src

# Run pytest for unit tests
pytest
```

## Logging

Log files are stored in the `var/logs` directory by default. You can specify a different log file with the `--log` argument in any script.

-   `var/logs/app.log`: Default application log file.

## License

MIT License
YouTube Channel Video Metadata and Transcript ExtractorA Python tool to extract video metadata from YouTube channels and auto-generated transcripts from individual videos, designed for data analysis workflows.FeaturesExtract comprehensive video metadata from entire YouTube channels.Extract auto-generated English transcripts from any YouTube video.Filter a channel's videos by a specified date range.Limit the number of recent videos to process from a channel.Save channel metadata to a CSV file.Save individual transcripts to clean text or markdown files.Command-line option to include or exclude timestamps in transcripts.Robust logging for troubleshooting.InstallationClone the repository:git clone [https://github.com/yourusername/getYTchannelTranscripts.git](https://github.com/yourusername/getYTchannelTranscripts.git)
cd getYTchannelTranscripts
Create and activate a virtual environment:# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
Install the package in editable mode:This command uses the setup.py file to install the project and its dependencies, making the command-line scripts available in your environment. The -e flag means changes you make to the source code will take effect immediately without reinstalling.pip install -e .
(Optional) Install development dependencies:If you plan to run tests or contribute to the code, install the development dependencies.pip install -e ".[dev]"
UsageExtracting Channel Video MetadataThe channel-videos-to-csv script fetches video data from a channel and saves it to a CSV file.Basic usage:Note: The --output argument is required.channel-videos-to-csv --channel "[https://www.youtube.com/@MrBeast](https://www.youtube.com/@MrBeast)" --output "output/mrbeast_videos.csv"
Limit to the 50 most recent videos:channel-videos-to-csv --channel "[https://www.youtube.com/@MrBeast](https://www.youtube.com/@MrBeast)" --limit 50 --output "output/mrbeast_latest_50.csv"
Get videos from a specific date range:channel-videos-to-csv \
  --channel "[https://www.youtube.com/@lexfridman](https://www.youtube.com/@lexfridman)" \
  --start-date "2023-01-01" \
  --end-date "2023-03-31" \
  --output "output/lex_q1_2023.csv"
Extracting a Video TranscriptThe extract-video-transcript script downloads the auto-generated transcript for a single video.Basic usage:This saves the transcript with timestamps to a generated filename in the output/ directory.extract-video-transcript "[https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
Save to a specific file without timestamps:extract-video-transcript "[https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=dQw4w9WgXcQ)" --no-timestamps -o "output/my_transcript.txt"
Save as Markdown with timestamps:extract-video-transcript "[https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=dQw4w9WgXcQ)" --format markdown -o "output/my_transcript.md"
DevelopmentThe project includes a comprehensive test suite and linting configuration.Running Tests and LintingTo run all checks (requires development dependencies):# Run flake8 for code style checking
flake8 src tests

# Run black to format code
black src tests

# Run mypy for static type checking
mypy src

# Run pytest for unit tests
pytest
LoggingLog files are stored in the var/logs directory by default. You can specify a different log file with the --log argument in any script.var/logs/app.log: Default application log file.LicenseMIT License
