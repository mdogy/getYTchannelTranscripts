#!/usr/bin/env python3
"""Script to extract transcripts from YouTube videos."""

import yt_dlp  # type: ignore
import argparse
import logging
import sys
import os
from typing import Optional, Dict, Any, List
import re

from youtube_transcripts.core.transcript import (
    extract_transcript,
    format_transcript,
    parse_vtt_file,
)
from youtube_transcripts.core.utils import setup_logging, get_unique_filename

# Create a module-level logger
logger = logging.getLogger("yt_transcript")


def get_video_info(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts basic video information (ID, title, upload date) from a YouTube video.
    Handles different URL formats.
    """
    # Clean up the URL
    video_url = video_url.strip()
    logger.info(f"Processing video URL: {video_url}")

    # Configure yt-dlp options for video extraction
    ydl_opts = {
        "quiet": False,  # Enable output for debugging
        "ignoreerrors": True,
        "no_warnings": False,  # Show warnings for debugging
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Attempting to extract video info...")
            info = ydl.extract_info(video_url, download=False)

            if not info:
                logger.error("No video information returned")
                return None

            logger.info(f"Video info keys: {info.keys()}")
            logger.info(f"Video title: {info.get('title', 'unknown')}")
            logger.info(f"Video ID: {info.get('id', 'unknown')}")
            logger.info(f"Upload date: {info.get('upload_date', 'unknown')}")

            return dict(info)  # Convert to dict to ensure type safety

    except Exception as e:
        logger.error(f"Error extracting video info: {str(e)}")
        return None


def save_transcript_to_file(transcript: List[Dict[str, Any]], output_file: str) -> None:
    """Save transcript to a file."""
    formatted = format_transcript(transcript, include_timestamps=False)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted)


def main() -> None:
    """Main function to process video transcripts."""
    parser = argparse.ArgumentParser(
        description="Extract transcript from a YouTube video and save to file"
    )
    parser.add_argument(
        "--video",
        required=True,
        help="YouTube video URL (e.g., https://youtube.com/watch?v=...)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. If not specified, output goes to stdout",
    )
    parser.add_argument(
        "--log",
        default="var/logs/app.log",
        help="Log file path (default: var/logs/app.log)",
    )
    args = parser.parse_args()

    # Create all required directories first
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Set up logging after directories are created
    logger = setup_logging(args.log)

    try:
        transcript = extract_transcript(args.video)
        if not transcript:
            # Try to find a .vtt file and parse it
            video_id = None
            # Try to extract video ID from URL
            match = re.search(r"v=([\w-]+)", args.video)
            if match:
                video_id = match.group(1)
            if video_id:
                vtt_path = f"output/{video_id}.en.vtt"
                if os.path.exists(vtt_path):
                    transcript = parse_vtt_file(vtt_path)
            if not transcript:
                logger.error("No transcript found")
                sys.exit(1)

        if args.output:
            # Get a unique filename if the file already exists
            output_file = get_unique_filename(args.output)
            save_transcript_to_file(transcript, output_file)
            logger.info(f"Saved transcript to {output_file}")
        else:
            # Print transcript to stdout
            formatted = format_transcript(transcript, include_timestamps=False)
            print(formatted)

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


if __name__ == "__main__":
    main()
