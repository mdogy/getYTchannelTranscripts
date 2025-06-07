"""Core functionality for extracting and formatting YouTube video transcripts."""

import os
import subprocess
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import yt_dlp
from .utils import sanitize_filename

class TranscriptExtractor:
    """Class for extracting and formatting YouTube video transcripts."""
    
    def __init__(self, temp_dir: str = "temp"):
        """Initialize the transcript extractor."""
        self.temp_dir = temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)

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

    def _get_video_id(self, video_url: str) -> str:
        """Extract video ID from URL."""
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get("id", "")
        except Exception as e:
            self.logger.error(f"Error getting video ID: {e}")
            raise

    def _get_video_info(self, video_url: str) -> Dict[str, Any]:
        """Get video metadata."""
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    "title": info.get("title", ""),
                    "upload_date": info.get("upload_date", ""),
                    "id": info.get("id", "")
                }
        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            raise

    def _download_auto_captions(self, video_url: str, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """Download and parse auto-generated captions."""
        try:
            # Use subprocess to run yt-dlp
            output_file = f"{self.temp_dir}/{video_id}.vtt"
            
            # Download auto-generated captions
            cmd = [
                "yt-dlp",
                "--write-auto-sub",
                "--sub-lang", "en",
                "--skip-download",
                "--sub-format", "vtt/best",
                "--output", output_file,
                video_url
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"yt-dlp error: {result.stderr}")
                    return None
                    
                if os.path.exists(output_file):
                    return self._parse_vtt_file(output_file)
                else:
                    self.logger.error("VTT file not found after download")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Error running yt-dlp: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading auto-captions: {e}")
            return None

    def _parse_vtt_file(self, vtt_path: str, include_timestamps: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Parse VTT file into transcript segments."""
        try:
            segments = []
            with open(vtt_path, encoding="utf-8") as f:
                # Skip header lines
                while True:
                    line = f.readline().strip()
                    if not line or line == "WEBVTT":
                        continue
                    if line == "":
                        break
                
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    
                    # Skip notes
                    if line.startswith("NOTE"):
                        while True:
                            line = f.readline().strip()
                            if not line:
                                break
                        continue
                    
                    # Get timestamp
                    start, end = line.split("-->")
                    start = start.strip()
                    end = end.strip()
                    
                    # Get text
                    text_lines = []
                    while True:
                        line = f.readline().strip()
                        if not line:
                            break
                        text_lines.append(line)
                    
                    if text_lines:
                        segments.append({
                            "start": self._vtt_timestamp_to_seconds(start),
                            "end": self._vtt_timestamp_to_seconds(end),
                            "text": " ".join(text_lines).strip(),
                        })
            
            if not segments:
                return None
            
            # Remove duplicates
            unique_segments = []
            last_text = ""
            for segment in segments:
                text = segment["text"]
                if text != last_text:
                    unique_segments.append(segment)
                last_text = text
            
            return unique_segments
            
        except Exception as e:
            self.logger.error(f"Error parsing VTT file: {e}")
            return None

    def _vtt_timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert VTT timestamp (HH:MM:SS.mmm) to seconds."""
        try:
            parts = timestamp.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2].replace(",", "."))
            return hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            self.logger.error(f"Error converting timestamp {timestamp}: {e}")
            return 0.0

    def _format_transcript(self, transcript_data: List[Dict[str, Any]], format_type: str = "raw", include_timestamps: bool = True) -> str:
        """Format transcript data into string."""
        if not transcript_data:
            return ""
            
        if format_type == "markdown":
            formatted = []
            for segment in transcript_data:
                text = segment.get("text", "").strip()
                if not text:
                    continue
                if include_timestamps:
                    start = segment.get("start", 0)
                    formatted.append(f"{self._format_timestamp(start)}: {text}")
                else:
                    formatted.append(text)
            return "\n".join(formatted).strip()
        
        # Default to raw format
        formatted = []
        previous_text = ""
        for segment in transcript_data:
            text = segment.get("text", "").strip()
            if not text:
                continue
            if text == previous_text:
                continue
            formatted.append(text)
            previous_text = text
        return "\n".join(formatted).strip()

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def extract_transcript(self, video_url: str, format_type: str = "raw", include_timestamps: bool = True) -> str:
        """Extract transcript from YouTube video."""
        try:
            video_id = self._get_video_id(video_url)
            video_info = self._get_video_info(video_url)
            
            # Try to download auto-generated captions
            transcript_data = self._download_auto_captions(video_url, video_id)
            
            if transcript_data:
                transcript = self._format_transcript(transcript_data, format_type, include_timestamps)
                return transcript
            else:
                return "No transcript available"
                
        except Exception as e:
            return f"Error: {str(e)}"

def extract_transcript(video_url: str,
                      format_type: str = "raw",
                      include_timestamps: bool = True) -> str:
    """Extract and format transcript from YouTube video.
    
    Args:
        video_url: URL of the YouTube video
        format_type: Format type ("raw" or "markdown")
        include_timestamps: Whether to include timestamps
        
    Returns:
        Formatted transcript string
    """
    extractor = TranscriptExtractor()
    return extractor.extract_transcript(video_url, format_type, include_timestamps)
