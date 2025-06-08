import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from youtube_transcripts.core.video_metadata import (
    get_channel_videos,
    build_video_row,
    filter_videos_by_date,
)
from youtube_transcripts.scripts.channel_videos_to_csv import main as channel_main
from youtube_transcripts.core.utils import setup_logging


@pytest.fixture(autouse=True)
def setup_logging_fixture(tmp_path):
    """Set up logging for tests."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "test.log"
    setup_logging(str(log_file))


@pytest.fixture
def sample_video_entries():
    """Return a list of sample video entries."""
    return [
        {
            "id": "dQw4w9WgXcQ",
            "videoId": "dQw4w9WgXcQ",
            "title": "Test Video 1",
            "upload_date": "20230101",
            "channel_id": "channel1",
            "uploader": "Test Channel",
            "duration": 60,
            "view_count": 100,
            "like_count": 10,
            "comment_count": 5,
            "description": "Description 1",
            "webpage_url": "http://example.com/video1",
            "thumbnail": "http://example.com/thumb1.jpg",
        },
        {
            "id": "abcdefghijk",
            "videoId": "abcdefghijk",
            "title": "Test Video 2",
            "upload_date": "20230201",
            "channel_id": "channel1",
            "uploader": "Test Channel",
            "duration": 120,
            "view_count": 200,
            "like_count": 20,
            "comment_count": 10,
            "description": "Description 2",
            "webpage_url": "http://example.com/video2",
            "thumbnail": "http://example.com/thumb2.jpg",
        },
    ]


def test_get_channel_videos(sample_video_entries):
    """Test fetching channel videos."""
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"entries": sample_video_entries}
    videos = get_channel_videos("some_url", ydl=mock_ydl)
    assert len(videos) == 2
    assert videos[0]["id"] == "dQw4w9WgXcQ"
    mock_ydl.extract_info.assert_called_once()


def test_get_channel_videos_no_entries():
    """Test fetching channel with no video entries."""
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"entries": []}
    videos = get_channel_videos("some_url", ydl=mock_ydl)
    assert len(videos) == 0


def test_build_video_row(sample_video_entries):
    """Test building a video row from video info."""
    video_info = sample_video_entries[0]
    row = build_video_row(video_info)
    assert row["video_id"] == "dQw4w9WgXcQ"
    assert row["title"] == "Test Video 1"
    assert row["upload_date"] == "2023-01-01"


def test_filter_videos_by_date(sample_video_entries):
    """Test filtering videos by date."""
    filtered = filter_videos_by_date(sample_video_entries, "2023-01-15", None)
    assert len(filtered) == 1
    assert filtered[0]["id"] == "abcdefghijk"

    filtered = filter_videos_by_date(sample_video_entries, None, "2023-01-15")
    assert len(filtered) == 1
    assert filtered[0]["id"] == "dQw4w9WgXcQ"

    filtered = filter_videos_by_date(sample_video_entries, "2023-01-01", "2023-02-01")
    assert len(filtered) == 2


@patch("sys.exit")
@patch("youtube_transcripts.core.video_metadata.yt_dlp.YoutubeDL")
def test_channel_videos_to_csv_main(
    mock_ytdl_class, mock_exit, tmp_path, sample_video_entries
):
    """Test the main script for channel_videos_to_csv."""
    output_csv = tmp_path / "videos.csv"
    mock_instance = mock_ytdl_class.return_value
    mock_instance.extract_info.return_value = {"entries": sample_video_entries}

    with patch(
        "sys.argv",
        [
            "channel_videos_to_csv",
            "--channel",
            "some_channel",
            "--output",
            str(output_csv),
        ],
    ):
        with patch(
            "youtube_transcripts.scripts.channel_videos_to_csv.get_channel_videos"
        ) as mock_get_videos:
            mock_get_videos.return_value = sample_video_entries
            channel_main()

    assert output_csv.exists()
    df = pd.read_csv(output_csv)
    assert len(df) == 2
    assert df["video_id"][0] == "dQw4w9WgXcQ"
    mock_exit.assert_not_called()
