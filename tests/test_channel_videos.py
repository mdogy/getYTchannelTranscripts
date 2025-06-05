import pytest
import logging
import os
from datetime import datetime, date
from unittest.mock import Mock, patch
import yt_dlp
import pandas as pd
import sys
from io import StringIO

# Import the functions we want to test
from channel_videos_to_csv import (
    get_channel_video_info,
    get_video_details,
    parse_upload_date,
    get_unique_csv_filename,
)

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("output/test.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_ytdl():
    """Fixture to provide a mocked yt-dlp instance."""
    with patch("yt_dlp.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def sample_channel_info():
    """Fixture to provide sample channel information."""
    return {
        "title": "Test Channel",
        "entries": [
            {
                "_type": "video",
                "id": "video1",
                "title": "Test Video 1",
                "upload_date": "20230101",
                "uploader": "Test Uploader",
                "duration": 3600,
                "view_count": 1000,
                "description": "Test Description",
                "webpage_url": "https://youtube.com/watch?v=video1",
                "automatic_captions": {"en": [{"ext": "vtt"}]},
            },
            {
                "_type": "video",
                "id": "video2",
                "title": "Test Video 2",
                "upload_date": "20230102",
                "uploader": "Test Uploader",
                "duration": 1800,
                "view_count": 500,
                "description": "Test Description 2",
                "webpage_url": "https://youtube.com/watch?v=video2",
                "automatic_captions": {},
            },
        ],
    }


def test_get_channel_video_info(mock_ytdl, sample_channel_info):
    """Test getting channel video information."""
    # Setup mock
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    # Test with different URL formats
    test_urls = [
        "https://youtube.com/channel/UC123",
        "https://youtube.com/c/TestChannel",
        "https://youtube.com/@TestChannel",
    ]

    for url in test_urls:
        result = get_channel_video_info(url)
        assert result == sample_channel_info
        mock_instance.extract_info.assert_called_with(url, download=False)


def test_get_channel_video_info_error(mock_ytdl):
    """Test error handling in get_channel_video_info."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.side_effect = Exception("Test error")

    result = get_channel_video_info("https://youtube.com/channel/UC123")
    assert result is None


def test_get_video_details(mock_ytdl):
    """Test getting video details."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "id": "video1",
        "title": "Test Video",
        "upload_date": "20230101",
    }

    result = get_video_details("https://youtube.com/watch?v=video1")
    assert result["id"] == "video1"
    assert result["title"] == "Test Video"
    assert result["upload_date"] == "20230101"


def test_parse_upload_date():
    """Test parsing upload date."""
    date_str = "20230101"
    result = parse_upload_date(date_str)
    assert isinstance(result, date)
    assert result.year == 2023
    assert result.month == 1
    assert result.day == 1


def test_get_unique_csv_filename(tmp_path):
    """Test generating unique CSV filenames."""
    # Create a temporary directory for testing
    os.makedirs(tmp_path / "output", exist_ok=True)

    # Test with non-existent file
    filename = get_unique_csv_filename("test", str(tmp_path / "output"))
    assert filename == str(tmp_path / "output" / "test.csv")

    # Create a file and test again
    with open(str(tmp_path / "output" / "test.csv"), "w") as f:
        f.write("test")

    filename = get_unique_csv_filename("test", str(tmp_path / "output"))
    assert filename == str(tmp_path / "output" / "test_1.csv")


def test_youtube_dl_output_format(mock_ytdl, sample_channel_info):
    """Test that yt-dlp produces expected output format."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    result = get_channel_video_info("https://youtube.com/channel/UC123")

    # Verify the structure of the returned data
    assert "title" in result
    assert "entries" in result
    assert isinstance(result["entries"], list)

    # Verify the structure of each video entry
    for entry in result["entries"]:
        assert "_type" in entry
        assert "id" in entry
        assert "title" in entry
        assert "upload_date" in entry
        assert "uploader" in entry
        assert "duration" in entry
        assert "view_count" in entry
        assert "description" in entry
        assert "webpage_url" in entry
        assert "automatic_captions" in entry
