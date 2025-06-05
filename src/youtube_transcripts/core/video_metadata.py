"""Core functionality for extracting and processing YouTube video metadata."""

import yt_dlp  # type: ignore
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import logging
import argparse

logger = logging.getLogger("yt_channel_metadata")


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

    # Add has_captions field robustly
    ac = entry.get("automatic_captions", {})
    has_captions = False
    if isinstance(ac, dict):
        has_captions = bool(ac.get("en"))
    row["has_captions"] = has_captions
    if "has_captions" not in row:
        row["has_captions"] = False

    return row


def filter_and_build_rows(
    entries: List[Dict[str, Any]],
    args: argparse.Namespace,
    logger: Optional[logging.Logger] = None,
) -> List[Dict[str, Any]]:
    """Filter entries and build rows for CSV output."""
    if logger is None:
        logger = logging.getLogger("yt_channel_metadata")

    logger.info(f"Starting to process {len(entries)} entries")
    rows = []

    for entry in entries:
        logger.info(
            f"Processing entry type: {entry.get('_type', 'unknown')}, id: {entry.get('id', 'unknown')}"
        )

        # Skip non-video entries
        if entry.get("_type") != "url" or entry.get("ie_key") != "Youtube":
            logger.info(f"Skipping non-video entry: {entry.get('_type', 'unknown')}")
            continue

        # Build row for video entry
        row = build_video_row(entry, None)
        if row:
            rows.append(row)
            logger.info(f"Successfully added video: {row.get('title', 'unknown')}")

    logger.info(f"Successfully processed {len(rows)} videos")
    return rows


def get_channel_video_info(channel_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts basic video information (IDs, titles, upload dates) from a YouTube channel.
    Handles different URL formats.
    """
    # Clean up the URL
    channel_url = channel_url.strip()
    logger.info(f"Processing channel URL: {channel_url}")

    # Convert custom URL formats to channel format (replace all occurrences)
    channel_url = channel_url.replace("/c/", "/channel/").replace("/@", "/channel/")

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
                    logger.info(
                        f"Processing playlist: {entry.get('title', 'unknown')} with {len(entry['entries'])} videos"
                    )
                    all_entries.extend(entry["entries"])
                else:
                    all_entries.append(entry)

            # Update info with flattened entries
            info["entries"] = all_entries
            logger.info(
                f"Total videos found after flattening playlists: {len(all_entries)}"
            )

            # Log first entry details for debugging
            if all_entries:
                first_entry = all_entries[0]
                logger.info(f"First entry keys: {first_entry.keys()}")
                logger.info(f"First entry data: {first_entry}")

            return info

    except Exception as e:
        logger.error(f"Error extracting channel info: {str(e)}")
        return None


def filter_video_by_date(video_date: date, args: argparse.Namespace) -> bool:
    """Filter videos by date range."""
    if hasattr(args, "start_date") and args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
            if video_date < start_date:
                return False
        except ValueError:
            logger.error(
                f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD"
            )
            return False
    if hasattr(args, "end_date") and args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
            if video_date > end_date:
                return False
        except ValueError:
            logger.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            return False
    return True
