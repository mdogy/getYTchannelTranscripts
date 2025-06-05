"""Core functionality for extracting and formatting YouTube video transcripts."""

import yt_dlp  # type: ignore
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import timedelta

logger = logging.getLogger("yt_channel_metadata")


def extract_transcript(video_url: str) -> Optional[List[Dict[str, Any]]]:
    """
    Extracts transcript from a YouTube video.
    Returns a list of transcript segments with timestamps and text.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "socket_timeout": 30,
        "retries": 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info:
                logger.error("No video information returned")
                return None

            # Try to get manual captions first, then automatic
            captions = info.get("subtitles", {}).get("en", [])
            if not captions:
                captions = info.get("automatic_captions", {}).get("en", [])

            if not captions:
                logger.error("No captions found for video")
                return None

            # Get the first available caption format
            caption_data = captions[0]
            if "data" in caption_data:
                return caption_data["data"]
            else:
                logger.error("No caption data found in format")
                return None

    except Exception as e:
        logger.error(f"Error extracting transcript: {e}")
        return None


def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS format."""
    return str(timedelta(seconds=int(seconds)))


def format_transcript(
    transcript: List[Dict[str, Any]],
    include_timestamps: bool = True,
    format: str = "text",
) -> str:
    """
    Formats transcript into the specified format.

    Args:
        transcript: List of transcript segments
        include_timestamps: Whether to include timestamps
        format: Output format ("text" or "markdown")
    """
    if not transcript:
        return ""

    formatted_lines = []

    for segment in transcript:
        text = segment.get("text", "").strip()
        if not text:
            continue

        if include_timestamps:
            timestamp = format_timestamp(segment.get("start", 0))
            if format == "markdown":
                line = f"[{timestamp}] {text}"
            else:
                line = f"{timestamp} {text}"
        else:
            line = text

        formatted_lines.append(line)

    if format == "markdown":
        return "\n\n".join(formatted_lines)
    else:
        return "\n".join(formatted_lines)
