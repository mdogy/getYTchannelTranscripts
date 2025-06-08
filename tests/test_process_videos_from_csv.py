import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from youtube_transcripts.scripts.process_videos_from_csv import (
    main as process_main,
    process_video_row,
)

@pytest.fixture
def mock_extractor():
    with patch(
        "youtube_transcripts.scripts.process_videos_from_csv.TranscriptExtractor"
    ) as mock:
        yield mock

@pytest.fixture
def mock_formatter():
    with patch(
        "youtube_transcripts.scripts.process_videos_from_csv.TranscriptFormatter"
    ) as mock:
        yield mock

@patch("sys.exit")
def test_process_main_success(
    mock_exit, mock_extractor, mock_formatter, tmp_path
):
    """Test the main script for process_videos_from_csv."""
    csv_file = tmp_path / "videos.csv"
    df = pd.DataFrame(
        {
            "video_url": ["http://example.com/video1"],
            "video_id": ["video1"],
            "title": ["Test Video 1"],
        }
    )
    df.to_csv(csv_file, index=False)

    mock_extractor_instance = mock_extractor.return_value
    mock_extractor_instance.extract.return_value = (
        {"title": "Test Video"},
        [{"text": "Hello world"}],
    )
    mock_formatter_instance = mock_formatter.return_value
    mock_formatter_instance.format.return_value = "Hello world"

    with patch(
        "sys.argv",
        [
            "process_videos_from_csv",
            "--csv-file",
            str(csv_file),
        ],
    ):
        process_main()

    output_dir = tmp_path / "videos_transcripts"
    assert (output_dir / "Test-Video-1-video1.txt").exists()
    mock_exit.assert_not_called()

def test_process_video_row(mock_extractor, mock_formatter, tmp_path):
    """Test processing a single video row."""
    row = pd.Series(
        {
            "video_url": "http://example.com/video1",
            "video_id": "video1",
            "title": "Test Video 1",
        }
    )
    output_dir = tmp_path
    mock_extractor_instance = mock_extractor.return_value
    mock_extractor_instance.extract.return_value = (
        {"title": "Test Video"},
        [{"text": "Hello world"}],
    )
    mock_formatter_instance = mock_formatter.return_value
    mock_formatter_instance.format.return_value = "Hello world"

    process_video_row(
        row,
        mock_extractor_instance,
        mock_formatter_instance,
        str(output_dir),
        True,
        False,
    )

    assert (output_dir / "Test-Video-1-video1.txt").exists()
