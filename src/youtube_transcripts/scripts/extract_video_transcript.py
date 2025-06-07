#!/usr/bin/env python3
"""Script to extract a transcript from a single YouTube video."""

import os
import sys
import argparse
import logging
import re
from youtube_transcripts.core.transcript import TranscriptExtractor, TranscriptFormatter
from youtube_transcripts.core.utils import setup_logging

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from a string so it can be used as a filename."""
    s = re.sub(r'[^\w\s-]', '', filename)
    s = re.sub(r'\s+', '-', s).strip()
    return s

def main() -> None:
    """Main function to process a video transcript."""
    parser = argparse.ArgumentParser(
        description="Extract a transcript from a single YouTube video."
    )
    parser.add_argument(
        "video_url",
        help="The full URL of the YouTube video."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path. If not provided, a filename is generated from the video title and saved in './output'."
    )
    parser.add_argument(
        "--format",
        choices=["raw", "markdown"],
        default="raw",
        help="Output format. 'raw' is plain text, 'markdown' adds formatting."
    )
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Do not include timestamps in the output."
    )
    # NEW: Added the deduplication flag as requested for debugging.
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Disable the experimental logic for removing duplicate/rolling captions."
    )
    parser.add_argument(
        "--log",
        default="var/logs/app.log",
        help="Log file path (default: var/logs/app.log).",
    )
    args = parser.parse_args()

    # --- Setup Directories and Logging ---
    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    setup_logging(args.log)

    include_timestamps = not args.no_timestamps
    # The --no-dedupe flag means the `deduplicate` parameter should be False.
    should_deduplicate = not args.no_dedupe

    try:
        extractor = TranscriptExtractor()
        formatter = TranscriptFormatter()

        logger.info(f"Extracting transcript for: {args.video_url}")
        # Pass the deduplication flag to the extractor.
        video_info, segments = extractor.extract(args.video_url, deduplicate=should_deduplicate)

        if not video_info:
            logger.error("Could not retrieve video information.")
            sys.exit(1)
        
        if not segments:
            logger.error("No transcript could be extracted.")
            sys.exit(1)
        
        logger.info(f"Successfully extracted {len(segments)} transcript segments.")
        
        transcript_text = formatter.format(segments, args.format, include_timestamps)
        
        if args.output:
            output_path = args.output
        else:
            video_title = video_info.get("title", "video_transcript")
            sanitized_title = sanitize_filename(video_title)
            extension = "md" if args.format == "markdown" else "txt"
            output_dir = "output"
            output_path = os.path.join(output_dir, f"{sanitized_title}.{extension}")

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {video_info.get('title', 'Video Transcript')}\n")
            f.write(f"Source URL: {video_info.get('webpage_url', args.video_url)}\n\n")
            f.write(transcript_text)

        logger.info(f"Transcript successfully saved to {output_path}")

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

