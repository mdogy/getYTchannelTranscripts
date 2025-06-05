"""Core functionality for extracting and formatting YouTube video transcripts."""

import yt_dlp  # type: ignore
from typing import Optional, Dict, Any, List
import logging
from datetime import timedelta
import re

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

            # Try to get manual captions first
            captions = info.get("subtitles", {}).get("en", [])
            if not captions:
                # If no manual captions, try auto-generated
                captions = info.get("automatic_captions", {}).get("en", [])
                if not captions:
                    logger.error("No captions found for video")
                    return None

            # Get the first available caption format
            caption_data = captions[0]
            if "data" in caption_data:
                # Ensure we return a list of dicts
                data = caption_data["data"]
                if isinstance(data, list) and all(
                    isinstance(item, dict) for item in data
                ):
                    return data
                logger.error("Invalid caption data format")
                return None
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


def parse_vtt_file(vtt_path: str, include_timestamps: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    Parses a .vtt subtitle file and extracts transcript segments.
    Returns a list of dicts with 'start', 'end', and 'text'.
    """
    segments = []
    timestamp_re = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})")
    start = end = None
    text_lines = []
    with open(vtt_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = timestamp_re.match(line)
            if match:
                if start and text_lines:
                    # Save previous segment
                    segments.append({
                        "start": _vtt_timestamp_to_seconds(start),
                        "end": _vtt_timestamp_to_seconds(end),
                        "text": " ".join(text_lines).strip(),
                    })
                    text_lines = []
                start, end = match.groups()
            elif line and not line.startswith("WEBVTT") and not line.startswith("Kind:") and not line.startswith("Language:") and not line.startswith("NOTE"):
                text_lines.append(line)
        # Add last segment
        if start and text_lines:
            segments.append({
                "start": _vtt_timestamp_to_seconds(start),
                "end": _vtt_timestamp_to_seconds(end),
                "text": " ".join(text_lines).strip(),
            })
    if not segments:
        return None
    return segments


def _vtt_timestamp_to_seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    s, ms = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
