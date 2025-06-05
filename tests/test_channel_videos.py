import pytest
import logging
import os
from datetime import date
from unittest.mock import Mock, patch
import sys
from typing import Dict, Any, Generator
import shutil
import pandas as pd

# Import the functions we want to test
from channel_videos_to_csv import (
    get_channel_video_info,
    get_video_details,
    parse_upload_date,
    get_unique_csv_filename,
    main,
)


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("output/test.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    yield
    # Cleanup logging handlers
    for handler in logging.getLogger().handlers[:]:
        handler.close()
        logging.getLogger().removeHandler(handler)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir
    # Cleanup
    shutil.rmtree(output_dir)


@pytest.fixture
def mock_ytdl() -> Generator[Mock, None, None]:
    """Fixture to provide a mocked yt-dlp instance."""
    with patch("yt_dlp.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def sample_channel_info() -> Dict[str, Any]:
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


def test_get_channel_video_info(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any]
) -> None:
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
        # The URL should be converted to channel format for /c/ URLs
        expected_url = url.replace("/c/", "/channel/") if "/c/" in url else url
        mock_instance.extract_info.assert_called_with(expected_url, download=False)


def test_get_channel_video_info_error(mock_ytdl: Mock) -> None:
    """Test error handling in get_channel_video_info."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.side_effect = Exception("Test error")

    result = get_channel_video_info("https://youtube.com/channel/UC123")
    assert result is None


def test_get_video_details(mock_ytdl: Mock) -> None:
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


def test_parse_upload_date() -> None:
    """Test parsing upload date."""
    date_str = "20230101"
    result = parse_upload_date(date_str)
    assert isinstance(result, date)
    assert result.year == 2023
    assert result.month == 1
    assert result.day == 1


def test_get_unique_csv_filename(tmp_path: Any) -> None:
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


def test_youtube_dl_output_format(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any]
) -> None:
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


def test_main_with_channel_url(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any], temp_output_dir
) -> None:
    """Test main function with channel URL argument."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    # Test with channel URL
    with patch(
        "sys.argv",
        ["script.py", "--channel", "https://youtube.com/channel/UC123"],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                mock_makedirs.assert_called_once()
                mock_to_csv.assert_called_once()


def test_main_with_date_filters(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any], temp_output_dir
) -> None:
    """Test main function with date filters."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    # Test with date filters
    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--start-date",
            "2023-01-01",
            "--end-date",
            "2023-01-02",
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                mock_makedirs.assert_called_once()
                mock_to_csv.assert_called_once()


def test_main_with_invalid_date(mock_ytdl: Mock) -> None:
    """Test main function with invalid date format."""
    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--start-date",
            "invalid-date",
        ],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)


def test_main_with_log_file(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any], temp_output_dir
) -> None:
    """Test main function with log file output."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    log_file = temp_output_dir / "test.log"

    # Test with log file
    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--log",
            str(log_file),
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                mock_makedirs.assert_called_once()
                mock_to_csv.assert_called_once()
                assert log_file.exists()


def test_main_with_no_channel_info(mock_ytdl: Mock, temp_output_dir) -> None:
    """Test main function when no channel info is returned."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = None

    # Test with no channel info
    with patch(
        "sys.argv",
        ["script.py", "--channel", "https://youtube.com/channel/UC123"],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)


def test_main_with_invalid_entries(mock_ytdl: Mock, temp_output_dir) -> None:
    """Test main function with invalid entries in channel info."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "title": "Test Channel",
        "entries": None,  # Invalid entries
    }

    # Test with invalid entries
    with patch(
        "sys.argv",
        ["script.py", "--channel", "https://youtube.com/channel/UC123"],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)


def test_main_with_missing_video_data(mock_ytdl: Mock, temp_output_dir) -> None:
    """Test main function with missing video data."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "title": "Test Channel",
        "entries": [
            {
                "_type": "video",
                "id": "video1",
                # Missing upload_date to test skipping
            }
        ],
    }

    # Test with missing video data
    with patch(
        "sys.argv",
        ["script.py", "--channel", "https://youtube.com/channel/UC123"],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame") as mock_df:
                mock_df_instance = Mock()
                mock_df.return_value = mock_df_instance
                main()
                mock_makedirs.assert_called_once()
                mock_df.assert_called_once()
                # The DataFrame should be created with an empty list of rows
                args, kwargs = mock_df.call_args
                rows_arg = args[0]
                assert isinstance(rows_arg, list)
                assert len(rows_arg) == 0


def test_channel_without_date_filters():
    """Test that channel extraction without date filters returns non-empty results."""
    channel_url = "https://www.youtube.com/@GregIsenberg"
    info = get_channel_video_info(channel_url)
    assert info is not None
    assert "entries" in info
    assert len(info["entries"]) > 0


def test_channel_with_date_filters():
    """Test that channel extraction with date filters returns correct results."""
    channel_url = "https://www.youtube.com/@GregIsenberg"
    start_date = "2024-05-01"
    end_date = "2024-06-30"

    # Get all videos
    info = get_channel_video_info(channel_url)
    assert info is not None
    assert "entries" in info

    # Filter videos by date range
    filtered_videos = []
    for entry in info["entries"]:
        if entry.get("_type") != "video":
            continue
        upload_date = entry.get("upload_date")
        if not upload_date:
            continue
        try:
            video_date = datetime.strptime(upload_date, "%Y%m%d").date()
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if start <= video_date <= end:
                filtered_videos.append(entry)
        except ValueError:
            continue

    # Verify that all filtered videos are within the date range
    for video in filtered_videos:
        upload_date = video.get("upload_date")
        video_date = datetime.strptime(upload_date, "%Y%m%d").date()
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        assert start <= video_date <= end


def test_channel_csv_generation():
    """Test that CSV file is generated with correct content."""
    channel_url = "https://www.youtube.com/@GregIsenberg"
    output_file = "output/Greg_Isenberg_videos.csv"

    # Run the main function
    sys.argv = [
        "channel_videos_to_csv.py",
        "--channel",
        channel_url,
        "--output-dir",
        "output",
    ]
    main()

    # Verify CSV file exists and is not empty
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0

    # Read CSV and verify content
    df = pd.read_csv(output_file)
    assert len(df) > 0
    assert all(
        col in df.columns
        for col in [
            "id",
            "title",
            "upload_date",
            "uploader",
            "duration",
            "view_count",
            "description",
            "url",
            "has_captions",
        ]
    )
