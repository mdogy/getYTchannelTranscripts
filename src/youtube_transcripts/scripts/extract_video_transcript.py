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
    # Remove non-alphanumeric characters, except for spaces, hyphens, and underscores
    s = re.sub(r'[^\w\s-]', '', filename)
    # Replace whitespace with a single hyphen
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
    # FIX: Changed flag to match README. This is a common pattern for boolean flags.
    # The default is to include timestamps. This flag turns them off.
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Do not include timestamps in the output."
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

    # The --no-timestamps flag means include_timestamps should be False
    include_timestamps = not args.no_timestamps

    try:
        # --- Main Logic ---
        extractor = TranscriptExtractor()
        formatter = TranscriptFormatter()

        # 1. Extract the video info and transcript data in one step.
        logger.info(f"Extracting transcript for: {args.video_url}")
        video_info, segments = extractor.extract(args.video_url)

        if not video_info:
            logger.error("Could not retrieve video information. The URL may be invalid or the video unavailable.")
            sys.exit(1)
        
        if not segments:
            logger.error("No transcript could be extracted. The video may not have auto-captions available.")
            sys.exit(1)
        
        logger.info(f"Successfully extracted {len(segments)} transcript segments.")
        
        # 2. Format the transcript into a string.
        transcript_text = formatter.format(segments, args.format, include_timestamps)
        
        # 3. Determine the output path.
        if args.output:
            output_path = args.output
        else:
            # If no output path is given, create one from the video title.
            video_title = video_info.get("title", "video_transcript")
            sanitized_title = sanitize_filename(video_title)
            extension = "md" if args.format == "markdown" else "txt"
            # Save to an 'output' directory by default.
            output_dir = "output"
            output_path = os.path.join(output_dir, f"{sanitized_title}.{extension}")

        # Ensure the final output directory exists.
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 4. Write the final content to the file.
        with open(output_path, 'w', encoding='utf-8') as f:
            # Add a simple header to the file
            f.write(f"# {video_info.get('title', 'Video Transcript')}\n")
            f.write(f"Source URL: {video_info.get('webpage_url', args.video_url)}\n\n")
            f.write(transcript_text)

        logger.info(f"Transcript successfully saved to {output_path}")

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
