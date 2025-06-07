#!/usr/bin/env python3
"""Script to extract video metadata from a YouTube channel and save to a CSV file."""

import pandas as pd
import os
import sys
import argparse
import logging
from youtube_transcripts.core.video_metadata import (
    get_channel_videos,
    build_video_row,
    filter_videos_by_date,
)
from youtube_transcripts.core.utils import setup_logging

# It's standard practice to get the logger at the top level of the module.
logger = logging.getLogger(__name__)

def main() -> None:
    """Main function to process channel videos and save to CSV."""
    parser = argparse.ArgumentParser(
        description="Extract video information from a YouTube channel and save to CSV."
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="YouTube channel URL (e.g., https://www.youtube.com/@MrBeast)",
    )
    parser.add_argument(
        "--start-date", help="Filter videos published on or after this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--end-date", help="Filter videos published on or before this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True, # Making output required as per typical use case
        help="Output CSV file path (e.g., output/channel_videos.csv).",
    )
    parser.add_argument(
        "--log",
        default="var/logs/app.log",
        help="Log file path (default: var/logs/app.log).",
    )
    # FIX: Changed '-n' to '--limit' for clarity.
    parser.add_argument(
        "--limit",
        type=int,
        default=None, # Default to no limit
        help="Maximum number of recent videos to process. Processes all if not set.",
    )
    args = parser.parse_args()

    # --- Setup Directories and Logging ---
    # Create the output directory if it doesn't exist.
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    # Create the log directory if it doesn't exist.
    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Now it's safe to set up file logging.
    setup_logging(args.log)

    try:
        # --- Main Logic ---
        logger.info(f"Fetching videos from channel: {args.channel}")
        
        # 1. Get video list from the channel, applying the limit if specified.
        # The 'limit' argument is passed to yt-dlp's 'playlistend' option.
        videos = get_channel_videos(args.channel, playlist_end=args.limit)
        if not videos:
            logger.warning("No videos found for the specified channel. Exiting.")
            sys.exit(0)
        
        logger.info(f"Found {len(videos)} videos before date filtering.")

        # 2. Filter videos by the provided date range.
        filtered_videos = filter_videos_by_date(videos, args.start_date, args.end_date)
        if not filtered_videos:
            logger.warning("No videos found within the specified date range. Exiting.")
            sys.exit(0)
            
        logger.info(f"Found {len(filtered_videos)} videos after date filtering.")

        # 3. Build the data rows for the CSV file.
        rows = [build_video_row(video) for video in filtered_videos]

        # 4. Create a pandas DataFrame and save to CSV.
        df = pd.DataFrame(rows)
        
        # Reorder columns for better readability in the CSV
        column_order = [
            "channel_name", "channel_id", "upload_date", "title", "video_id", 
            "video_url", "duration_seconds", "view_count", "like_count", "comment_count",
            "thumbnail_url", "description"
        ]
        # Only include columns that actually exist in the dataframe
        df = df[[col for col in column_order if col in df.columns]]

        df.to_csv(args.output, index=False, encoding='utf-8')
        logger.info(f"Successfully saved {len(df)} video records to {args.output}")

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
