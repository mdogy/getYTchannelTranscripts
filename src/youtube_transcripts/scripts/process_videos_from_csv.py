#!/usr/bin/env python3
"""
Script to process a CSV file of YouTube videos, extract their transcripts,
and save them to individual text files.
"""

import os
import sys
import argparse
import logging
import pandas as pd
import re
from youtube_transcripts.core.transcript import TranscriptExtractor, TranscriptFormatter
from youtube_transcripts.core.utils import setup_logging

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from a string so it can be used as a filename."""
    s = re.sub(r'[^\w\s-]', '', filename)
    s = re.sub(r'\s+', '-', s).strip()
    return s


def generate_unique_filename(title: str, video_id: str) -> str:
    """Generates a unique filename from a video title and its ID."""
    sanitized_title = sanitize_filename(title)
    return f"{sanitized_title}-{video_id}.txt"


def main() -> None:
    """Main function to process videos from a CSV file."""
    parser = argparse.ArgumentParser(
        description="Extract transcripts for a list of videos from a CSV file."
    )
    parser.add_argument(
        "--csv-file",
        required=True,
        help="Input CSV file path (e.g., output/channel_videos.csv)."
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save transcript files. Defaults to a folder named after the CSV file in the 'output' directory."
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Include timestamps in the output. Default is to exclude them."
    )
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
    if args.output_dir:
        output_dir = args.output_dir
    else:
        csv_filename = os.path.splitext(os.path.basename(args.csv_file))[0]
        output_dir = os.path.join("output", f"{csv_filename}_transcripts")

    os.makedirs(output_dir, exist_ok=True)
    
    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    setup_logging(args.log)

    should_deduplicate = not args.no_dedupe
    include_timestamps = args.timestamps

    try:
        df = pd.read_csv(args.csv_file)
        logger.info(f"Loaded {len(df)} videos from {args.csv_file}")

        extractor = TranscriptExtractor()
        formatter = TranscriptFormatter()

        for index, row in df.iterrows():
            video_url = row.get("video_url")
            video_id = row.get("video_id")
            title = row.get("title", "untitled")

            if not video_url or pd.isna(video_url) or not video_id:
                logger.warning(f"Skipping row {index} due to missing video URL or ID.")
                continue

            logger.info(f"Processing video: {title} ({video_url})")

            try:
                video_info, segments = extractor.extract(video_url, deduplicate=should_deduplicate)

                if not segments:
                    logger.error(f"No transcript could be extracted for {video_url}.")
                    continue

                transcript_text = formatter.format(segments, "raw", include_timestamps)
                filename = generate_unique_filename(title, video_id)
                output_path = os.path.join(output_dir, filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {video_info.get('title', 'Video Transcript')}\n")
                    f.write(f"Source URL: {video_info.get('webpage_url', video_url)}\n\n")
                    f.write(transcript_text)

                logger.info(f"Transcript for '{title}' saved to {output_path}")

            except Exception as e:
                logger.error(f"Failed to process video {video_url}: {e}", exc_info=True)

        logger.info("Finished processing all videos.")

    except FileNotFoundError:
        logger.critical(f"CSV file not found at: {args.csv_file}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
