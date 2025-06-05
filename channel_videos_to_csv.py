import yt_dlp  # type: ignore
import pandas as pd
from datetime import datetime, date
import os
import sys
import argparse
import logging
import logging.config
from typing import Optional, Dict, Any, List

# Create a module-level logger
logger = logging.getLogger("yt_channel_metadata")


def setup_logging(log_file: str) -> logging.Logger:
    """Set up logging configuration."""
    # Configure logging without creating directories
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr),
        ],
    )
    return logging.getLogger("yt_channel_metadata")


def prompt_channel_url() -> str:
    return input("Enter YouTube channel URL: ").strip()


def get_channel_video_info(channel_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts basic video information (IDs, titles, upload dates) from a YouTube channel.
    Handles different URL formats.
    """
    # Clean up the URL
    channel_url = channel_url.strip()
    logger.info(f"Processing channel URL: {channel_url}")

    # Configure yt-dlp options for channel extraction
    ydl_opts = {
        "quiet": False,  # Enable output for debugging
        "ignoreerrors": True,
        "extract_flat": "in_playlist",  # Extract videos from playlists
        "no_warnings": False,  # Show warnings for debugging
        "skip_download": True,
        "playlistend": 10,  # Start with just 10 videos for testing
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Attempting to extract channel info...")
            info = ydl.extract_info(channel_url, download=False)
            
            if not info:
                logger.error("No channel information returned")
                return None

            logger.info(f"Channel info keys: {info.keys()}")
            
            # Process entries to flatten playlists
            all_entries = []
            entries = info.get("entries", [])
            if not entries:
                logger.error("No entries found in channel info")
                return None

            logger.info(f"Found {len(entries)} entries")
            
            # Process each entry
            for entry in entries:
                if entry.get("_type") == "playlist" and "entries" in entry:
                    logger.info(f"Processing playlist: {entry.get('title', 'unknown')} with {len(entry['entries'])} videos")
                    all_entries.extend(entry["entries"])
                else:
                    all_entries.append(entry)

            # Update info with flattened entries
            info["entries"] = all_entries
            logger.info(f"Total videos found after flattening playlists: {len(all_entries)}")
            
            # Log first entry details for debugging
            if all_entries:
                first_entry = all_entries[0]
                logger.info(f"First entry keys: {first_entry.keys()}")
                logger.info(f"First entry data: {first_entry}")

            return info

    except Exception as e:
        logger.error(f"Error extracting channel info: {str(e)}")
        return None


def get_video_details(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed information for a single video.
    """
    video_ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "force_generic_extractor": True,
        "ignoreerrors": True,
        "dump_single_json": True,
        "extract_flat": True,  # Only extract basic info
        "no_warnings": True,
        "socket_timeout": 30,  # Add timeout
        "retries": 3,  # Number of retries
        "fragment_retries": 3,  # Number of retries for fragments
    }
    try:
        with yt_dlp.YoutubeDL(video_ydl_opts) as video_ydl:
            video_details = video_ydl.extract_info(video_url, download=False)
        return video_details
    except Exception as e:
        logger.error(f"Error extracting details for {video_url}: {e}")
        return None


def parse_upload_date(upload_date_val) -> date:
    """Parses upload date from YYYYMMDD string or Unix timestamp to date object."""
    if isinstance(upload_date_val, int):
        # Assume it's a Unix timestamp
        return datetime.utcfromtimestamp(upload_date_val).date()
    if isinstance(upload_date_val, str):
        # Try YYYYMMDD
        try:
            return datetime.strptime(upload_date_val, "%Y%m%d").date()
        except ValueError:
            pass
        # Try ISO format
        try:
            return datetime.fromisoformat(upload_date_val).date()
        except ValueError:
            pass
        # Try parsing as int (timestamp in string)
        try:
            return datetime.utcfromtimestamp(int(upload_date_val)).date()
        except Exception:
            pass
    raise ValueError(f"Unrecognized upload date format: {upload_date_val}")


def get_unique_csv_filename(base_name: str, output_dir: str) -> str:
    """Generates a unique filename for the CSV to avoid overwriting."""
    base_path = os.path.join(output_dir, base_name)
    if not os.path.exists(base_path + ".csv"):
        return base_path + ".csv"
    i = 1
    while True:
        candidate = f"{base_path}_{i}.csv"
        if not os.path.exists(candidate):
            return candidate
        i += 1


def filter_video_by_date(video_date: date, args: argparse.Namespace) -> bool:
    """Filter videos by date range."""
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
            if video_date < start_date:
                return False
        except ValueError:
            logger.error(
                f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD"
            )
            return False
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
            if video_date > end_date:
                return False
        except ValueError:
            logger.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            return False
    return True


def build_video_row(
    entry: Dict[str, Any], video_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Build a row of video information."""
    logger.info(f"Building row for video: {entry.get('id', 'unknown')}")
    
    # Basic required fields
    row = {
        "video_id": entry.get("id"),
        "title": entry.get("title"),
        "upload_date": entry.get("upload_date"),
        "url": entry.get("webpage_url") or entry.get("url"),
    }
    
    # Log what we have
    logger.info(f"Basic fields: {row}")
    
    # Add optional fields if they exist
    optional_fields = {
        "uploader": entry.get("uploader"),
        "channel_id": entry.get("channel_id"),
        "channel_url": entry.get("channel_url"),
        "duration_seconds": entry.get("duration"),
        "view_count": entry.get("view_count"),
        "description": entry.get("description"),
        "thumbnail_url": entry.get("thumbnail"),
    }
    
    # Only add non-None optional fields
    for key, value in optional_fields.items():
        if value is not None:
            row[key] = value
            logger.info(f"Added optional field {key}: {value}")
    
    return row


def filter_and_build_rows(entries, channel_info):
    """Filter entries and build rows for CSV output."""
    logger.info(f"Starting to process {len(entries)} entries")
    rows = []
    
    for entry in entries:
        logger.info(f"Processing entry type: {entry.get('_type', 'unknown')}, id: {entry.get('id', 'unknown')}")
        
        # Skip non-video entries
        if entry.get('_type') != 'url' or entry.get('ie_key') != 'Youtube':
            logger.info(f"Skipping non-video entry: {entry.get('_type', 'unknown')}")
            continue
            
        # Build row for video entry
        row = build_video_row(entry, channel_info)
        if row:
            rows.append(row)
            logger.info(f"Successfully added video: {row.get('title', 'unknown')}")
    
    logger.info(f"Successfully processed {len(rows)} videos")
    return rows


def main() -> None:
    """Main function to process channel videos and save to CSV."""
    parser = argparse.ArgumentParser(
        description="Extract video information from a YouTube channel and save to CSV"
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="YouTube channel URL (e.g., https://youtube.com/channel/UC...)",
    )
    parser.add_argument(
        "--start-date", help="Start date for filtering videos (YYYY-MM-DD)"
    )
    parser.add_argument("--end-date", help="End date for filtering videos (YYYY-MM-DD)")
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
    parser.add_argument(
        "-n",
        "--row-limit",
        type=int,
        default=5,
        help="Maximum number of videos to process (default: 5)",
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
        # Validate date formats before proceeding
        if args.start_date:
            try:
                datetime.strptime(args.start_date, "%Y-%m-%d")
            except ValueError:
                logger.error(
                    f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD"
                )
                sys.exit(1)
        if args.end_date:
            try:
                datetime.strptime(args.end_date, "%Y-%m-%d")
            except ValueError:
                logger.error(
                    f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD"
                )
                sys.exit(1)

        info = get_channel_video_info(args.channel)
        if not info:
            logger.error("No channel information returned")
            sys.exit(1)

        channel_name = info.get("title", "channel")
        logger.info(f"Processing channel: {channel_name}")
        entries = info.get("entries", [])
        logger.info(f"Number of entries returned: {len(entries)}")
        if entries:
            logger.info(f"First entry: {entries[0]}")
            if len(entries) > 1:
                logger.info(f"Second entry: {entries[1]}")
        if not entries:
            logger.error("No video entries found in channel")
            sys.exit(1)

        rows = filter_and_build_rows(entries, info)
        if not rows:
            logger.warning("No videos found matching criteria")
            return

        df = pd.DataFrame(rows)

        if args.output:
            df.to_csv(args.output, index=False)
            logger.info(f"Saved {len(rows)} videos to {args.output}")
        else:
            df.to_csv(sys.stdout, index=False)

    except Exception as e:
        logger.error(f"Error processing channel: {e}")
        sys.exit(1)
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


if __name__ == "__main__":
    main()
