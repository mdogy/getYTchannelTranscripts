import pytest
from unittest.mock import Mock, patch
from youtube_transcripts.core.transcript import (
    TranscriptExtractor,
    TranscriptFormatter,
)


@pytest.fixture
def mock_ytdl():
    """Mock the yt_dlp.YoutubeDL class."""
    with patch("yt_dlp.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def sample_segments():
    """Return a list of sample transcript segments."""
    return [
        {"start": 0.0, "text": "Hello world."},
        {"start": 5.0, "text": "This is a test."},
    ]


class TestTranscriptExtractor:
    """Tests for the TranscriptExtractor class."""

    @patch("subprocess.run")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open")
    def test_extract_success(
        self, mock_open, mock_exists, mock_run, mock_ytdl, sample_segments
    ):
        """Test successful transcript extraction."""
        mock_instance = mock_ytdl.return_value
        mock_instance.extract_info.return_value = {
            "id": "test_video",
            "title": "Test Video",
        }
        mock_run.return_value = Mock(returncode=0, stderr="")
        vtt_content = (
            "00:00:00.000 --> 00:00:05.000\nHello world.\n\n"
            "00:00:05.000 --> 00:00:10.000\nThis is a test."
        )
        mock_open.return_value.__enter__.return_value.read.return_value = vtt_content

        extractor = TranscriptExtractor()
        video_info, segments = extractor.extract("some_url")

        assert video_info["id"] == "test_video"
        assert len(segments) == 2
        assert segments[0]["text"] == "Hello world."

    def test_extract_no_info(self, mock_ytdl):
        """Test extraction when no video info is returned."""
        mock_instance = mock_ytdl.return_value
        mock_instance.extract_info.return_value = None

        extractor = TranscriptExtractor()
        video_info, segments = extractor.extract("some_url")

        assert video_info is None
        assert segments is None

    @patch("subprocess.run")
    def test_extract_no_captions(self, mock_run, mock_ytdl):
        """Test extraction when no captions are available."""
        mock_instance = mock_ytdl.return_value
        mock_instance.extract_info.return_value = {
            "id": "test_video",
            "title": "Test Video",
        }
        mock_run.return_value = Mock(
            returncode=1, stderr="no subtitles are available"
        )

        extractor = TranscriptExtractor()
        video_info, segments = extractor.extract("some_url")

        assert video_info["id"] == "test_video"
        assert segments is None


class TestTranscriptFormatter:
    """Tests for the TranscriptFormatter class."""

    def test_format_raw_with_timestamps(self, sample_segments):
        """Test formatting as raw text with timestamps."""
        formatter = TranscriptFormatter()
        result = formatter.format(sample_segments, "raw", True)
        expected = "[00:00:00] Hello world.\n[00:00:05] This is a test."
        assert result == expected

    def test_format_raw_without_timestamps(self, sample_segments):
        """Test formatting as raw text without timestamps."""
        formatter = TranscriptFormatter()
        result = formatter.format(sample_segments, "raw", False)
        expected = "Hello world.\nThis is a test."
        assert result == expected

    def test_format_markdown_with_timestamps(self, sample_segments):
        """Test formatting as markdown with timestamps."""
        formatter = TranscriptFormatter()
        result = formatter.format(sample_segments, "markdown", True)
        expected = "**00:00:00**: Hello world.\n\n**00:00:05**: This is a test."
        assert result == expected

    def test_format_markdown_without_timestamps(self, sample_segments):
        """Test formatting as markdown without timestamps."""
        formatter = TranscriptFormatter()
        result = formatter.format(sample_segments, "markdown", False)
        expected = "Hello world.\n\nThis is a test."
        assert result == expected
