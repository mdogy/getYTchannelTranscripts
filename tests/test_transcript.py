"""Tests for transcript extraction and formatting functionality."""

import pytest
from unittest.mock import Mock, patch
import logging
import os
import sys
from typing import Dict, Any, List

from youtube_transcripts.core.transcript import (
    extract_transcript,
    format_timestamp,
    format_transcript,
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
def mock_ytdl():
    with patch("yt_dlp.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def sample_transcript() -> List[Dict[str, Any]]:
    return [
        {
            "text": "Hello, welcome to this video.",
            "start": 0.0,
            "end": 5.0,
        },
        {
            "text": "Today we'll be discussing Python programming.",
            "start": 5.0,
            "end": 10.0,
        },
        {
            "text": "Let's get started!",
            "start": 10.0,
            "end": 15.0,
        },
    ]


def test_format_timestamp():
    """Test timestamp formatting."""
    assert format_timestamp(0) == "0:00:00"
    assert format_timestamp(61) == "0:01:01"
    assert format_timestamp(3661) == "1:01:01"


def test_format_transcript_text_with_timestamps(sample_transcript):
    """Test formatting transcript as text with timestamps."""
    expected = (
        "0:00:00 Hello, welcome to this video.\n"
        "0:00:05 Today we'll be discussing Python programming.\n"
        "0:00:10 Let's get started!"
    )
    result = format_transcript(
        sample_transcript, include_timestamps=True, format="text"
    )
    assert result == expected


def test_format_transcript_text_without_timestamps(sample_transcript):
    """Test formatting transcript as text without timestamps."""
    expected = (
        "Hello, welcome to this video.\n"
        "Today we'll be discussing Python programming.\n"
        "Let's get started!"
    )
    result = format_transcript(
        sample_transcript, include_timestamps=False, format="text"
    )
    assert result == expected


def test_format_transcript_markdown_with_timestamps(sample_transcript):
    """Test formatting transcript as markdown with timestamps."""
    expected = (
        "[0:00:00] Hello, welcome to this video.\n\n"
        "[0:00:05] Today we'll be discussing Python programming.\n\n"
        "[0:00:10] Let's get started!"
    )
    result = format_transcript(
        sample_transcript, include_timestamps=True, format="markdown"
    )
    assert result == expected


def test_format_transcript_markdown_without_timestamps(sample_transcript):
    """Test formatting transcript as markdown without timestamps."""
    expected = (
        "Hello, welcome to this video.\n\n"
        "Today we'll be discussing Python programming.\n\n"
        "Let's get started!"
    )
    result = format_transcript(
        sample_transcript, include_timestamps=False, format="markdown"
    )
    assert result == expected


def test_extract_transcript(mock_ytdl):
    """Test transcript extraction."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "subtitles": {
            "en": [
                {
                    "data": [
                        {
                            "start": 0.0,
                            "end": 5.0,
                            "text": "Test transcript",
                        }
                    ]
                }
            ]
        }
    }

    result = extract_transcript("https://youtube.com/watch?v=test")
    assert result is not None
    assert len(result) == 1
    assert result[0]["text"] == "Test transcript"


def test_extract_transcript_no_captions(mock_ytdl):
    """Test transcript extraction when no captions are available."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "subtitles": {},
        "automatic_captions": {},
    }

    result = extract_transcript("https://youtube.com/watch?v=test")
    assert result is None


def test_extract_transcript_error(mock_ytdl):
    """Test transcript extraction error handling."""
    mock_instance = Mock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.side_effect = Exception("Test error")

    result = extract_transcript("https://youtube.com/watch?v=test")
    assert result is None
