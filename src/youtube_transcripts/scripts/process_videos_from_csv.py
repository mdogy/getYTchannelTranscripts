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
    s = re.sub(r"[^\w\s-]", "", filename)
    s = re.sub(r"\s+", "-", s).strip()
    return s


def generate_unique_filename(title: str, video_id: str) -> str:
    """Generates a unique filename from a video title and its ID."""
    sanitized_title = sanitize_filename(title)
    return f"{sanitized_title}-{video_id}.txt"


def process_video_row(
    row: pd.Series,
    extractor: TranscriptExtractor,
    formatter: TranscriptFormatter,
    output_dir: str,
    should_deduplicate: bool,
    include_timestamps: bool,
) -> bool:
    """
    Processes a single video row from the DataFrame.
    Returns True on success, False on failure.
    """
    video_url = row.get("video_url")
    video_id = row.get("video_id")
    title = row.get("title", "untitled")

    if not video_url or pd.isna(video_url) or not video_id:
        logger.warning("Skipping row due to missing video URL or ID.")
        return False

    logger.info(f"Processing video: {title} ({video_url})")

    try:
        logger.info(f"Extracting transcript for: {title}")
        video_info, segments = extractor.extract(
            video_url, deduplicate=should_deduplicate
        )

        if not video_info or not segments:
            logger.error(f"No transcript could be extracted for {video_url}.")
            return False

        transcript_text = formatter.format(segments, "raw", include_timestamps)
        filename = generate_unique_filename(title, video_id)
        output_path = os.path.join(output_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {video_info.get('title', 'Video Transcript')}\n")
            f.write(f"Source URL: {video_info.get('webpage_url', video_url)}\n\n")
            f.write(transcript_text)

        logger.info(f"Transcript for '{title}' saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to process video {video_url}: {e}", exc_info=True)
        return False


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract transcripts for a list of videos from a CSV file."
    )
    parser.add_argument(
        "--csv-file",
        required=True,
        help="Input CSV file path (e.g., output/channel_videos.csv).",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Directory to save transcript files. Defaults to a folder named after "
            "the CSV file in the 'output' directory."
        ),
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Include timestamps in the output. Default is to exclude them.",
    )
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Disable the experimental logic for removing duplicate/rolling captions.",
    )
    parser.add_argument(
        "--log",
        default="var/logs/app.log",
        help="Log file path (default: var/logs/app.log).",
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Restart the process from the beginning, ignoring any saved state.",
    )
    return parser.parse_args()


def _setup_environment(args: argparse.Namespace) -> str:
    """Set up directories and logging, and return the output directory."""
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
    return output_dir


def _load_processed_ids(state_file: str, restart: bool) -> set:
    """Load the set of processed video IDs from the state file."""
    if restart and os.path.exists(state_file):
        os.remove(state_file)
        logger.info("Restarting process, removed existing state file.")
        return set()

    if not restart and os.path.exists(state_file):
        with open(state_file, "r") as f:
            processed_ids = set(pd.read_json(f, typ="series").tolist())
        logger.info(f"Resuming process, found {len(processed_ids)} completed videos.")
        return processed_ids

    return set()


def main() -> None:
    """Main function to process videos from a CSV file."""
    args = _parse_args()
    output_dir = _setup_environment(args)

    try:
        df = pd.read_csv(args.csv_file)
        total_videos = len(df)
        logger.info(f"Loaded {total_videos} videos from {args.csv_file}")

        state_file = os.path.join(output_dir, ".progress.json")
        processed_ids = _load_processed_ids(state_file, args.restart)

        extractor = TranscriptExtractor()
        formatter = TranscriptFormatter()

        for index, row in df.iterrows():
            video_id = row.get("video_id")
            if video_id in processed_ids:
                logger.info(f"Skipping already processed video: {video_id}")
                continue

            if process_video_row(
                row,
                extractor,
                formatter,
                output_dir,
                not args.no_dedupe,
                args.timestamps,
            ):
                processed_ids.add(video_id)
                with open(state_file, "w") as f:
                    pd.Series(list(processed_ids)).to_json(f)

            progress = (index + 1) / total_videos * 100
            logger.info(f"Progress: {index + 1}/{total_videos} ({progress:.2f}%)")

        logger.info("Finished processing all videos.")

    except FileNotFoundError:
        logger.critical(f"CSV file not found at: {args.csv_file}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
