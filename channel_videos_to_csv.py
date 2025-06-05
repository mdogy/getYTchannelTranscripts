import yt_dlp
import pandas as pd
from datetime import datetime, date
import re
import os
import sys
import argparse
import logging
import logging.config

# Configure logging
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("yt_channel_metadata")


def prompt_channel_url():
    return input("Enter YouTube channel URL: ").strip()


def get_channel_video_info(channel_url):
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


def get_video_details(video_url):
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


def parse_upload_date(upload_date_str):
    """Parses upload date from YYYYMMDD string to date object."""
    return datetime.strptime(upload_date_str, "%Y%m%d").date()


def get_unique_csv_filename(base_name, output_dir):
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


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube channel video metadata to CSV."
    )
    parser.add_argument("--channel", type=str, help="YouTube channel URL")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument(
        "--end-date", type=str, help="End date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument("--log", type=str, help="Log file to write stdout and stderr")
    args = parser.parse_args()

    # Gather required and optional input
    channel_url = args.channel
    if not channel_url:
        channel_url = prompt_channel_url()

    # Parse dates or use defaults
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(
                f"Invalid start date format: {args.start_date}. Please use YYYY-MM-DD."
            )
            sys.exit(1)
    else:
        start_date = None

    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(
                f"Invalid end date format: {args.end_date}. Please use YYYY-MM-DD."
            )
            sys.exit(1)
    else:
        end_date = date.today()

    # Redirect stdout/stderr if requested
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    log_file = None
    if args.log:
        try:
            log_file = open(args.log, "w", encoding="utf-8")
            sys.stdout = log_file
            sys.stderr = log_file
            logger.info(f"Logging output to {args.log}")
        except IOError as e:
            logger.error(f"Error opening log file {args.log}: {e}")
            sys.exit(1)

    info = get_channel_video_info(channel_url)
    if not info:
        logger.error("Failed to get channel information. Exiting.")
        if log_file:
            log_file.close()
        sys.exit(1)

    channel_name = info.get("title", "Unknown Channel")
    entries = info.get("entries", [])
    logger.info(f"Found {len(entries)} entries in channel playlist for initial scan.")

    rows = []
    processed_count = 0
    skipped_count = 0

    for entry in entries:
        if not entry or entry.get("_type") != "video" or not entry.get("id"):
            skipped_count += 1
            continue

        video_id = entry.get("id", "")
        upload_date_str = entry.get("upload_date")

        if not upload_date_str:
            logger.warning(f"No upload_date for video ID {video_id}, skipping.")
            skipped_count += 1
            continue

        upload_date = parse_upload_date(upload_date_str)

        if start_date and upload_date < start_date:
            logger.info(
                f"Video ID {video_id} upload date {upload_date} before start date {start_date}, skipping."
            )
            skipped_count += 1
            continue
        if end_date and upload_date > end_date:
            logger.info(
                f"Video ID {video_id} upload date {upload_date} after end date {end_date}, skipping."
            )
            skipped_count += 1
            continue

        title = entry.get("title", "N/A")
        uploader = entry.get("uploader", "N/A")
        duration = entry.get("duration")
        view_count = entry.get("view_count", "N/A")
        description = entry.get("description", "N/A")
        webpage_url = entry.get(
            "webpage_url", f"https://www.youtube.com/watch?v={video_id}"
        )

        length_str = "N/A"
        if duration is not None:
            try:
                hours = int(duration) // 3600
                minutes = (int(duration) % 3600) // 60
                seconds = int(duration) % 60
                length_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            except (ValueError, TypeError):
                pass

        has_auto_captions = False
        if "automatic_captions" in entry and entry["automatic_captions"]:
            if "en" in entry["automatic_captions"]:
                has_auto_captions = True

        logger.info(
            f"Adding video: {title} ({webpage_url}) - Uploaded: {upload_date_str}"
        )
        rows.append(
            {
                "video_id": video_id,
                "channel_name": channel_name,
                "channel_url": channel_url,
                "video_url": webpage_url,
                "title": title,
                "length": length_str,
                "upload_date": upload_date.strftime("%Y-%m-%d"),
                "uploader": uploader,
                "view_count": view_count,
                "description": description,
                "has_auto_captions_en": has_auto_captions,
            }
        )
        processed_count += 1

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    safe_channel_name = (
        re.sub(r"[^\w\s-]", "", channel_name).strip().replace(" ", "_") or "channel"
    )
    csv_filename = get_unique_csv_filename(safe_channel_name + "_videos", output_dir)

    columns = [
        "video_id",
        "channel_name",
        "channel_url",
        "video_url",
        "title",
        "length",
        "upload_date",
        "uploader",
        "view_count",
        "description",
        "has_auto_captions_en",
    ]

    df = pd.DataFrame(rows, columns=columns)

    try:
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        logger.info(
            f"\nSuccessfully saved {processed_count} video(s) information to {csv_filename}"
        )
        if skipped_count > 0:
            logger.info(
                f"Skipped {skipped_count} entries due to missing data or date filters."
            )
    except Exception as e:
        logger.error(f"Error writing CSV file {csv_filename}: {e}")

    if log_file:
        log_file.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        logger.info(
            f"Script execution completed. Check {args.log} for detailed output."
        )


if __name__ == "__main__":
    main()
