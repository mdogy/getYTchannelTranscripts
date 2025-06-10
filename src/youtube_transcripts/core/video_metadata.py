"""Core functionality for extracting YouTube channel and video metadata."""

import yt_dlp
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def _create_ydl_opts(
    playlist_end: Optional[int], start_date: Optional[str], end_date: Optional[str]
) -> Dict[str, Any]:
    """Create yt-dlp options dictionary."""
    ydl_opts: Dict[str, Any] = {
        "quiet": True,
        "ignoreerrors": True,
        "extract_flat": False,
        "skip_download": True,
        "sleep_interval": 2,
        "playlistreverse": True,
    }
    if playlist_end and playlist_end > 0:
        ydl_opts["playlistend"] = playlist_end
    if start_date:
        ydl_opts["dateafter"] = datetime.strptime(start_date, "%Y-%m-%d").strftime(
            "%Y%m%d"
        )
    if end_date:
        ydl_opts["datebefore"] = datetime.strptime(end_date, "%Y-%m-%d").strftime(
            "%Y%m%d"
        )
    return ydl_opts


def _prepare_channel_url(channel_url: str) -> str:
    """Prepare channel URL for yt-dlp."""
    if (
        channel_url.startswith("https://www.youtube.com/@")
        and "/videos" not in channel_url
    ):
        return channel_url.rstrip("/") + "/videos"
    return channel_url


def get_channel_videos(
    channel_url: str,
    playlist_end: Optional[int] = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ydl: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Extracts all video entries from a YouTube channel.

    Args:
        channel_url: The URL of the YouTube channel.
        playlist_end: Optional limit on the number of videos to retrieve.
        start_date: Optional start date in 'YYYY-MM-DD' format.
        end_date: Optional end date in 'YYYY-MM-DD' format.

    Returns:
        A list of video information dictionaries.
    """
    logger.info(f"Attempting to extract video info from channel: {channel_url}")
    ydl_opts = _create_ydl_opts(playlist_end, start_date, end_date)
    channel_url = _prepare_channel_url(channel_url)

    if ydl is None:
        ydl = yt_dlp.YoutubeDL(ydl_opts)

    with ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if info and "entries" in info:
                for video in info["entries"]:
                    if video:
                        yield video
        except Exception as e:
            logger.error(f"An error occurred during video extraction: {e}")


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
            upload_date = upload_date_str

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
