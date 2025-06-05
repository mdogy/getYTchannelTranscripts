#!/usr/bin/env python3
"""Script to extract transcripts from YouTube videos."""

import yt_dlp  # type: ignore
import argparse
import sys
import logging
import os
from typing import Optional, Dict, Any, List

from youtube_transcripts.core.transcript import extract_transcript, format_transcript
from youtube_transcripts.core.utils import setup_logging, get_unique_filename

# Create a module-level logger
logger = logging.getLogger("yt_transcript")


def main() -> None:
    """Main function to extract and format video transcripts."""
    parser = argparse.ArgumentParser(
        description="Extract transcript from a YouTube video"
    )
    parser.add_argument(
        "url",
        help="YouTube video URL (e.g., https://youtube.com/watch?v=...)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. If not specified, output goes to stdout",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Exclude timestamps from output",
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
        transcript = extract_transcript(args.url)
        if not transcript:
            logger.error("No transcript found")
            sys.exit(1)

        formatted = format_transcript(
            transcript,
            format=args.format,
            include_timestamps=not args.no_timestamps,
        )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(formatted)
            logger.info(f"Transcript saved to {args.output}")
        else:
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
