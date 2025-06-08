"""Core functionality for extracting YouTube channel and video metadata."""

import yt_dlp
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def get_channel_videos(
    channel_url: str, playlist_end: Optional[int] = 5
) -> List[Dict[str, Any]]:
    """
    Extracts all video entries from a YouTube channel.
    
    Args:
        channel_url: The URL of the YouTube channel.
        playlist_end: Optional limit on the number of videos to retrieve.
    
    Returns:
        A list of video information dictionaries.
    """
    logger.info(f"Attempting to extract video info from channel: {channel_url}")

    # FIX: Removed the hardcoded 'playlistend' limit from the options.
    # The script should control this, not the core library function.
    ydl_opts = {
        "quiet": True,
        "ignoreerrors": True,
        "extract_flat": False,  # Change to False to get detailed video info
        "skip_download": True,
    }

    if playlist_end and playlist_end > 0:
        ydl_opts['playlistend'] = playlist_end
    if channel_url.startswith("https://www.youtube.com/@") and "/videos" not in channel_url:
        channel_url = channel_url.rstrip("/") + "/videos"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # yt-dlp handles various channel URL formats automatically
            info = ydl.extract_info(channel_url, download=False)

            if not info or "entries" not in info:
                logger.error(f"Could not retrieve video entries for channel {channel_url}.")
                return []
            
            # The 'entries' key contains a list of videos
            import re
            video_id_pattern = re.compile(r'^[A-Za-z0-9_-]{11}$')
            raw_videos = info.get("entries", [])
            filtered_videos = []
            for v in raw_videos:
                vid = v.get("id") or v.get("videoId")
                if vid and video_id_pattern.match(vid):
                    v["id"] = vid
                    filtered_videos.append(v)
            return filtered_videos

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching channel videos: {e}")
        return []


def build_video_row(video_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a structured dictionary (row) for a single video.
    This is useful for creating DataFrames.
    """
    upload_date_str = video_info.get("upload_date")
    upload_date = None
    if upload_date_str:
        try:
            upload_date = (
                datetime.strptime(upload_date_str, "%Y%m%d").date().isoformat()
            )
        except (ValueError, TypeError):
            logger.warning(
                f"Could not parse upload date '{upload_date_str}' for video {video_info.get('id')}"
            )
            upload_date = upload_date_str  # Keep original if parsing fails

    # Simplified row construction
    row = {
        "channel_id": video_info.get("channel_id"),
        "channel_name": video_info.get("uploader"),
        "video_id": video_info.get("id"),
        "title": video_info.get("title"),
        "upload_date": upload_date,
        "duration_seconds": video_info.get("duration"),
        "view_count": video_info.get("view_count"),
        "like_count": video_info.get("like_count"),
        "comment_count": video_info.get("comment_count"),
        "description": video_info.get("description"),
        "video_url": video_info.get("webpage_url"),
        "thumbnail_url": video_info.get("thumbnail"),
    }
    return row


def filter_videos_by_date(
    videos: List[Dict[str, Any]], start_date: Optional[str], end_date: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Filters a list of videos to be within a specified date range.
    
    Args:
        videos: A list of video info dictionaries.
        start_date: The start date in 'YYYY-MM-DD' format.
        end_date: The end date in 'YYYY-MM-DD' format.
        
    Returns:
        A list of filtered video info dictionaries.
    """
    if not start_date and not end_date:
        return videos

    filtered_videos = []
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    for video in videos:
        upload_date_str = video.get("upload_date")
        if not upload_date_str:
            continue

        try:
            video_date = datetime.strptime(upload_date_str, "%Y%m%d").date()
            if start and video_date < start:
                continue
            if end and video_date > end:
                continue
            filtered_videos.append(video)
        except (ValueError, TypeError):
            logger.warning(
                f"Could not parse date '{upload_date_str}' for video {video.get('id')}. "
                "Skipping date filter for this item."
            )
            # Decide if you want to include items with unparseable dates
            # For now, we skip them if a date filter is active.
            continue
            
    return filtered_videos
