"""Core functionality for extracting and formatting YouTube video transcripts."""

import os
import shutil
import subprocess
import logging
import re
from typing import Optional, List, Dict, Any, Tuple
import yt_dlp

# It's better to get the logger at the module level
logger = logging.getLogger(__name__)

class TranscriptExtractor:
    """Class for extracting YouTube video info and transcript data."""

    def __init__(self, temp_dir: str = "temp"):
        """Initialize the transcript extractor."""
        self.temp_dir = temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)
        self._ydl = yt_dlp.YoutubeDL({"quiet": True, "skip_download": True})


    def __del__(self):
        """Clean up temporary files when object is destroyed."""
        self._cleanup_temp_files()

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files and directories."""
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

    def _get_video_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Get video metadata and ID in a single call."""
        try:
            info = self._ydl.extract_info(video_url, download=False)
            return info if info else None
        except Exception as e:
            logger.error(f"Error getting video info for {video_url}: {e}")
            return None

    def _download_auto_captions(self, video_url: str, video_id: str) -> Optional[str]:
        """
        Download auto-generated captions to a VTT file.
        Returns the path to the downloaded file.
        """
        sanitized_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', video_id)
        output_template = os.path.join(self.temp_dir, f"{sanitized_id}.%(ext)s")
        
        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "-o", output_template,
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                if "no subtitles are available" in result.stderr.lower():
                    logger.warning(f"No auto-generated English captions found for {video_id}.")
                else:
                    logger.error(f"yt-dlp failed for {video_id}: {result.stderr}")
                return None
            
            expected_vtt_path = os.path.join(self.temp_dir, f"{sanitized_id}.en.vtt")
            if os.path.exists(expected_vtt_path):
                return expected_vtt_path
            
            for filename in os.listdir(self.temp_dir):
                if sanitized_id in filename and filename.endswith(".vtt"):
                    return os.path.join(self.temp_dir, filename)
            
            logger.error(f"VTT file for {video_id} not found after download.")
            return None

        except FileNotFoundError:
            logger.error("yt-dlp command not found. Is it installed and in your PATH?")
            return None
        except Exception as e:
            logger.error(f"An error occurred while running yt-dlp for {video_id}: {e}")
            return None

    def _parse_vtt_file(self, vtt_path: str) -> List[Dict[str, Any]]:
        """Parse a VTT file into a list of transcript segments, cleaning up ASR artifacts."""
        segments = []
        pattern = re.compile(
            r"(\d*:?\d{2}:\d{2}\.\d{3})\s*-->\s*(\d*:?\d{2}:\d{2}\.\d{3}).*?\n(.*?)(?=\n\n|\Z)",
            re.DOTALL
        )
        try:
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for match in pattern.finditer(content):
                start_time, end_time, text_block = match.groups()
                clean_text = re.sub(r'<[^>]+>', '', text_block).replace('\n', ' ').strip()
                if clean_text:
                    segments.append({
                        "start": self._vtt_timestamp_to_seconds(start_time),
                        "text": clean_text
                    })

            # FIX: New, more robust logic to handle cumulative "rolling" captions from YouTube ASR.
            if not segments:
                return []
            
            # This algorithm merges consecutive captions that are continuations of each other.
            clean_segments = []
            if segments:
                # Start with the first segment
                current_segment = segments[0]
                for i in range(1, len(segments)):
                    next_segment = segments[i]
                    # If the next segment's text starts with the current one, it's a continuation.
                    # We just update the text of our current segment to the fuller version.
                    if next_segment['text'].startswith(current_segment['text']):
                        current_segment['text'] = next_segment['text']
                    # If it's not a continuation, the previous phrase is complete.
                    # Add it to our clean list and start a new phrase.
                    else:
                        clean_segments.append(current_segment)
                        current_segment = next_segment
                # Add the last processed segment
                clean_segments.append(current_segment)

            return clean_segments

        except Exception as e:
            logger.error(f"Error parsing VTT file {vtt_path}: {e}")
            return []

    def _vtt_timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert VTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
        try:
            time_parts = timestamp.split('.')
            main_time = time_parts[0]
            milliseconds = int(time_parts[1])
            
            parts = main_time.split(':')
            if len(parts) == 3:
                h, m, s = [int(p) for p in parts]
            elif len(parts) == 2:
                h = 0
                m, s = [int(p) for p in parts]
            else:
                raise ValueError(f"Invalid timestamp format: {timestamp}")

            return (h * 3600 + m * 60 + s) + (milliseconds / 1000.0)
        except Exception as e:
            logger.error(f"Error converting timestamp '{timestamp}': {e}")
            return 0.0

    def extract(self, video_url: str) -> Tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]]:
        """
        Extracts video info and transcript data.
        Returns a tuple: (video_info, transcript_segments).
        """
        logger.info(f"Starting transcript extraction for {video_url}")
        video_info = self._get_video_info(video_url)
        if not video_info or not video_info.get("id"):
            logger.error("Could not retrieve video information.")
            return None, None

        video_id = video_info["id"]
        
        vtt_path = self._download_auto_captions(video_url, video_id)
        if not vtt_path:
            return video_info, None

        segments = self._parse_vtt_file(vtt_path)
        logger.info(f"Extracted {len(segments)} clean segments for video {video_id}.")
        return video_info, segments


class TranscriptFormatter:
    """Formats transcript data into different string formats."""
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        if seconds < 0: seconds = 0
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def format(self, segments: List[Dict[str, Any]], format_type: str, include_timestamps: bool) -> str:
        """Formats the transcript segments into the specified format."""
        if not segments:
            return ""

        output_lines = []
        for segment in segments:
            text = segment.get("text", "").strip()
            if not text:
                continue
            
            if format_type == "markdown":
                if include_timestamps:
                    start_time = self._format_timestamp(segment.get("start", 0))
                    output_lines.append(f"**{start_time}**: {text}")
                else:
                    output_lines.append(text)
            else:  # Default to "raw" format
                if include_timestamps:
                    start_time = self._format_timestamp(segment.get("start", 0))
                    output_lines.append(f"[{start_time}] {text}")
                else:
                    output_lines.append(text)

        # FIX: The joiner is now determined by the format, not just timestamps.
        # Markdown looks better with double newlines, raw text with single newlines.
        joiner = "\n\n" if format_type == "markdown" else "\n"
        return joiner.join(output_lines)
