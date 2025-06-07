#!/usr/bin/env python3
"""Script to extract transcripts from YouTube videos."""
import sys
import os
import argparse
import logging
from typing import Optional, Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from youtube_transcripts.core.transcript import TranscriptExtractor, TranscriptFormatter
from youtube_transcripts.core.utils import setup_logging

# Create a module-level logger
logger = None


def get_video_info(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts basic video information (ID, title, upload date) from a YouTube video.
    Handles different URL formats.
    """
    # Clean up the URL
    video_url = video_url.strip()
    
    # Initialize yt-dlp
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "subtitleslangs": ["en"],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info:
                logger.error("No video information returned")
                return None
                
            video_id = info.get("id")
            if not video_id:
                logger.error("Could not get video ID")
                return None
                
            # Get video title and upload date
            title = info.get("title", "")
            upload_date = info.get("upload_date", "")
            
            return {
                "id": video_id,
                "title": title,
                "upload_date": upload_date
            }
            
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None



def main() -> None:
    """Main function to process video transcripts."""
    parser = argparse.ArgumentParser(
        description="Extract transcript from a YouTube video"
    )
    parser.add_argument(
        "--video",
        required=True,
        help="YouTube video URL"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path. If not specified, output goes to stdout"
    )
    parser.add_argument(
        "--format",
        choices=["raw", "markdown"],
        default="raw",
        help="Output format (raw or markdown)"
    )
    parser.add_argument(
        "--include-timestamps",
        action="store_true",
        help="Include timestamps in output"
    )
    parser.add_argument(
        "--log",
        default="var/logs/app.log",
        help="Log file path (default: var/logs/app.log)"
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
    if logger is None:
        print("Failed to set up logging", file=sys.stderr)
        sys.exit(1)

    try:
        # Extract video info and transcript
        extractor = TranscriptExtractor()
        video_info = extractor._get_video_info(args.video)
        if not video_info:
            logger.error("Could not get video information")
            sys.exit(1)
            
        logger.info(f"Video info: {video_info}")
        
        segments = extractor.extract(args.video)
        
        if segments:
            logger.info(f"Extracted {len(segments)} transcript segments")
            
            # Format transcript using TranscriptFormatter
            formatter = TranscriptFormatter()
            transcript = formatter.format(
                segments,
                format_type=args.format,
                include_timestamps=args.include_timestamps
            )
            
            # Create output filename with video title
            title = video_info.get('title', 'Untitled')
            logger.info(f"Video title: {title}")
            
            # Clean title for filename
            clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
            clean_title = re.sub(r'\s+', '-', clean_title)
            output_filename = f"{clean_title}.md"
            
            logger.info(f"Output filename: {output_filename}")
            
            # Create output directory if specified
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)
            else:
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)
            
            logger.info(f"Output path: {output_path}")
            
            # Write transcript with title header
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {video_info.get('title', 'Untitled')}\n")
                f.write(f"Date: {video_info.get('upload_date', '')}\n\n")
                f.write(transcript)
            
            logger.info(f"Saved transcript to {output_path}")
        else:
            logger.error("No transcript segments extracted")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


if __name__ == "__main__":
    main()
