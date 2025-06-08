import pytest
from unittest.mock import patch, MagicMock
from youtube_transcripts.scripts.extract_video_transcript import main as extract_main

@pytest.fixture
def mock_extractor():
    with patch(
        "youtube_transcripts.scripts.extract_video_transcript.TranscriptExtractor"
    ) as mock:
        yield mock

@pytest.fixture
def mock_formatter():
    with patch(
        "youtube_transcripts.scripts.extract_video_transcript.TranscriptFormatter"
    ) as mock:
        yield mock

@patch("sys.exit")
def test_extract_main_success(
    mock_exit, mock_extractor, mock_formatter, tmp_path
):
    """Test the main script for extract_video_transcript."""
    output_file = tmp_path / "transcript.txt"
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
            "extract_video_transcript",
            "some_url",
            "-o",
            str(output_file),
        ],
    ):
        extract_main()

    assert output_file.exists()
    assert "Hello world" in output_file.read_text()
    mock_exit.assert_not_called()

@patch("sys.exit")
def test_extract_main_no_transcript(mock_exit, mock_extractor):
    """Test the main script when no transcript is found."""
    mock_extractor_instance = mock_extractor.return_value
    mock_extractor_instance.extract.return_value = ({"title": "Test Video"}, None)

    with patch(
        "sys.argv",
        [
            "extract_video_transcript",
            "some_url",
        ],
    ):
        extract_main()

    mock_exit.assert_called_with(1)
