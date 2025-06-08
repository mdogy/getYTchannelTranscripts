import pytest
from unittest.mock import MagicMock
from youtube_transcripts.core.video_metadata import get_channel_videos

def test_get_channel_videos_simple():
    """A simplified test for fetching channel videos."""
    sample_entries = [{"id": "dQw4w9WgXcQ", "videoId": "dQw4w9WgXcQ"}]
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"entries": sample_entries}

    videos = get_channel_videos("some_url", ydl=mock_ydl)
    assert len(videos) == 1
