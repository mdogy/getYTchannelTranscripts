import pytest
import logging
import os
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock, call
import sys
from typing import Dict, Any, Generator, Optional, List
import shutil
import pandas as pd
import argparse

from channel_videos_to_csv import (
    get_channel_video_info,
    get_video_details,
    parse_upload_date,
    get_unique_csv_filename,
    filter_video_by_date,
    build_video_row,
    filter_and_build_rows,
    main,
    setup_logging,
)


@pytest.fixture(autouse=True)
def setup_logging_fixture():
    os.makedirs("var/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("var/logs/test.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    yield
    for handler in logging.getLogger().handlers[:]:
        handler.close()
        logging.getLogger().removeHandler(handler)


@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir
    shutil.rmtree(output_dir)


@pytest.fixture
def mock_ytdl():
    with patch("yt_dlp.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def sample_channel_info():
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
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    test_urls = [
        "https://youtube.com/channel/UC123",
        "https://youtube.com/c/TestChannel",
        "https://youtube.com/@TestChannel",
    ]

    for url in test_urls:
        result = get_channel_video_info(url)
        assert result == sample_channel_info
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
    os.makedirs(tmp_path / "output", exist_ok=True)

    filename = get_unique_csv_filename("test", str(tmp_path / "output"))
    assert filename == str(tmp_path / "output" / "test.csv")

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

    assert "title" in result
    assert "entries" in result
    assert isinstance(result["entries"], list)

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

    output_file = str(temp_output_dir / "test_output.csv")
    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "-o",
            output_file,
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                # Expect two calls: one for output, one for log
                assert mock_makedirs.call_count == 2
                expected_calls = [
                    call(os.path.dirname(output_file), exist_ok=True),
                    call(os.path.dirname("var/logs/test.log"), exist_ok=True),
                ]
                for c in expected_calls:
                    assert c in mock_makedirs.call_args_list
                mock_to_csv.assert_called_once()


def test_main_with_date_filters(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any], temp_output_dir
) -> None:
    """Test main function with date filters."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    output_file = str(temp_output_dir / "test_output.csv")
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
            "-o",
            output_file,
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                assert mock_makedirs.call_count == 2
                expected_calls = [
                    call(os.path.dirname(output_file), exist_ok=True),
                    call(os.path.dirname("var/logs/test.log"), exist_ok=True),
                ]
                for c in expected_calls:
                    assert c in mock_makedirs.call_args_list
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
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            assert mock_exit.called
            assert mock_exit.call_count >= 1
            mock_exit.assert_any_call(1)


def test_main_with_log_file(
    mock_ytdl: Mock, sample_channel_info: Dict[str, Any], temp_output_dir
) -> None:
    """Test main function with log file."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = sample_channel_info

    output_file = str(temp_output_dir / "test_output.csv")
    log_file = str(temp_output_dir / "test.log")
    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "-o",
            output_file,
            "--log",
            log_file,
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                main()
                assert mock_makedirs.call_count == 2
                expected_calls = [
                    call(os.path.dirname(output_file), exist_ok=True),
                    call(os.path.dirname(log_file), exist_ok=True),
                ]
                for c in expected_calls:
                    assert c in mock_makedirs.call_args_list
                mock_to_csv.assert_called_once()


def test_main_with_no_channel_info(mock_ytdl: Mock, temp_output_dir) -> None:
    """Test main function when no channel info is returned."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = None

    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            assert mock_exit.called
            assert mock_exit.call_count >= 1
            mock_exit.assert_any_call(1)


def test_main_with_invalid_entries(mock_ytdl: Mock, temp_output_dir) -> None:
    """Test main function with invalid entries in channel info."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "title": "Test Channel",
        "entries": None,  # Invalid entries
    }

    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("sys.exit") as mock_exit:
            main()
            assert mock_exit.called
            assert mock_exit.call_count >= 1
            mock_exit.assert_any_call(1)


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

    with patch(
        "sys.argv",
        [
            "script.py",
            "--channel",
            "https://youtube.com/channel/UC123",
            "--log",
            "var/logs/test.log",
        ],
    ):
        with patch("os.makedirs") as mock_makedirs:
            with patch("pandas.DataFrame") as mock_df:
                mock_df_instance = Mock()
                mock_df.return_value = mock_df_instance
                main()
                mock_makedirs.assert_called_once()


def test_filter_video_by_date() -> None:
    """Test filtering videos by date."""
    video_date = date(2023, 1, 15)
    args = argparse.Namespace(start_date="2023-01-01", end_date="2023-01-31")
    assert filter_video_by_date(video_date, args)


def test_build_video_row() -> None:
    """Test building a video row."""
    entry = {
        "id": "video1",
        "title": "Test Video",
        "upload_date": "20230101",
        "uploader": "Test Uploader",
        "duration": 3600,
        "view_count": 1000,
        "description": "Test Description",
        "webpage_url": "https://youtube.com/watch?v=video1",
        "automatic_captions": {"en": [{"ext": "vtt"}]},
    }
    row = build_video_row(entry, None)
    assert row["video_id"] == "video1"
    assert row["title"] == "Test Video"
    assert row["has_captions"] is True


def test_filter_and_build_rows() -> None:
    """Test filtering and building rows."""
    entries = [
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
        }
    ]
    args = argparse.Namespace(
        start_date="2023-01-01", end_date="2023-01-31", row_limit=5
    )
    logger = logging.getLogger("test")
    rows = filter_and_build_rows(entries, args, logger)
    assert len(rows) == 1
    assert rows[0]["video_id"] == "video1"


def test_real_gregisenberg_extraction():
    """
    Integration test: Extract at least 5 videos from GregIsenberg channel and output to CSV.
    """
    output_file = "output/GregIsenberg.csv"
    # Remove file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    # Run the script as a subprocess to simulate real CLI usage
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "channel_videos_to_csv.py",
            "--channel",
            "https://www.youtube.com/@GregIsenberg",
            "-o",
            output_file,
            "--log",
            "var/logs/gregisenberg_test.log",
            "-n",
            "5",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if not os.path.exists(output_file):
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert os.path.exists(output_file), "CSV file was not created!"
    df = pd.read_csv(output_file)
    assert len(df) >= 5, f"Expected at least 5 rows, got {len(df)}"
    # Check for required columns
    for col in ["video_id", "title", "upload_date", "url"]:
        assert col in df.columns
    print("\nFirst row of extracted data:")
    print(df.head(1))
