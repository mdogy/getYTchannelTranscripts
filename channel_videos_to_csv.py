import yt_dlp  # type: ignore
import pandas as pd
from datetime import datetime, date
import os
import sys
import argparse
import logging
import logging.config
from typing import Optional, Dict, Any, List

# Configure logging
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("yt_channel_metadata")


def prompt_channel_url() -> str:
    return input("Enter YouTube channel URL: ").strip()


def get_channel_video_info(channel_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts basic video information (IDs, titles, upload dates) from a YouTube channel.
    Handles different URL formats.
    """
    # Clean up the URL
    channel_url = channel_url.strip()

    # yt-dlp options for initial channel extraction to get full metadata
    ydl_opts = {
        "quiet": True,  # Suppress console output
        "force_generic_extractor": True,  # Ensure generic extractor is used for channels
        "ignoreerrors": True,  # Ignore errors for individual videos during initial scan
    }

    # Handle different URL formats
    if "/channel/" in channel_url:
        pass
    elif "/c/" in channel_url:
        channel_url = channel_url.replace("/c/", "/channel/")
    elif "/@" in channel_url:
        pass
    else:
        pass

    logger.info(f"Attempting to extract basic video info from: {channel_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if not info:
                logger.warning("No channel information found.")
                return None
            if "entries" not in info or not isinstance(info["entries"], list):
                logger.warning(
                    "No video entries found in channel or unexpected info structure."
                )
                return None
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
    }
    try:
        with yt_dlp.YoutubeDL(video_ydl_opts) as video_ydl:
            video_details = video_ydl.extract_info(video_url, download=False)
        return video_details
    except Exception as e:
        logger.error(f"Error extracting details for {video_url}: {e}")
        return None


def parse_upload_date(upload_date_str: str) -> date:
    """Parses upload date from YYYYMMDD string to date object."""
    return datetime.strptime(upload_date_str, "%Y%m%d").date()


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
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
            if video_date < start_date:
                return False
        except ValueError:
            logger.error(
                f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD"
            )
            sys.exit(1)
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
            if video_date > end_date:
                return False
        except ValueError:
            logger.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            sys.exit(1)
    return True


def build_video_row(
    entry: Dict[str, Any], video_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "upload_date": entry.get("upload_date"),
        "uploader": entry.get("uploader"),
        "duration": entry.get("duration"),
        "view_count": entry.get("view_count"),
        "description": entry.get("description"),
        "url": entry.get("webpage_url"),
        "has_captions": bool(entry.get("automatic_captions", {}).get("en")),
    }


def filter_and_build_rows(
    entries: List[Dict[str, Any]], args: argparse.Namespace, logger: logging.Logger
) -> List[Dict[str, Any]]:
    rows = []
    for entry in entries:
        if entry.get("_type") != "video":
            continue
        upload_date = entry.get("upload_date")
        if not upload_date:
            logger.warning("Skipping video %s - no upload date", entry.get("id"))
            continue
        try:
            video_date = parse_upload_date(upload_date)
        except ValueError as e:
            logger.warning("Skipping video %s - invalid date: %s", entry.get("id"), e)
            continue
        if not filter_video_by_date(video_date, args):
            continue
        video_url = entry.get("webpage_url")
        if not video_url:
            logger.warning("Skipping video %s - no URL", entry.get("id"))
            continue
        video_info = get_video_details(video_url)
        if not video_info:
            logger.warning(
                "Skipping video %s - could not get video details", entry.get("id")
            )
            continue
        rows.append(build_video_row(entry, video_info))
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
        "--output-dir",
        default="output",
        help="Directory to save the CSV file (default: output)",
    )
    parser.add_argument("--log", help="Log file path (default: var/logs/app.log)")
    args = parser.parse_args()

    # Create necessary directories
    os.makedirs("var/logs", exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    log_file = args.log or os.path.join("var/logs", "app.log")
    # If --output-dir is not specified (i.e., is 'output') and --log is specified, use log dir for output
    if args.log and args.output_dir == "output":
        output_dir = os.path.dirname(log_file)
    else:
        output_dir = args.output_dir
    log_dir = os.path.dirname(log_file)

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger(__name__)

    try:
        info = get_channel_video_info(args.channel)
        if not info:
            logger.error("No channel information returned")
            sys.exit(1)
        channel_name = info.get("title", "channel")
        logger.info(f"Processing channel: {channel_name}")
        entries = info.get("entries", [])
        if not entries:
            logger.error("No video entries found in channel")
            sys.exit(1)
        rows = filter_and_build_rows(entries, args, logger)
        df = pd.DataFrame(rows)
        output_file = get_unique_csv_filename(channel_name, output_dir)
        output_file_dir = os.path.dirname(output_file)
        # Create log and output directories if needed, but only once each
        if log_dir != output_file_dir:
            os.makedirs(log_dir, exist_ok=True)
            os.makedirs(output_file_dir, exist_ok=True)
        else:
            os.makedirs(output_file_dir, exist_ok=True)
        df.to_csv(output_file, index=False)
        if rows:
            logger.info(f"Saved {len(rows)} videos to {output_file}")
        else:
            logger.warning("No videos found matching criteria")
    except Exception as e:
        logger.error(f"Error processing channel: {e}")
        sys.exit(1)
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


if __name__ == "__main__":
    main()
