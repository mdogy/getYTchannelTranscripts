#!/usr/bin/env python3
"""Script to get YouTube auto-generated captions using yt-dlp."""

import argparse
import subprocess
import sys
import os
import logging
from typing import Optional

# Module-level logger
logger = logging.getLogger("yt_captions")
logger.setLevel(logging.INFO)

def setup_logging(log_file: str) -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr),
        ],
    )
    return logger

def get_yt_captions(video_url: str, output_file: Optional[str] = None) -> str:
    """
    Get YouTube auto-generated captions using yt-dlp.
    Returns the transcript text.
    """
    # Create temp directory for VTT file
    os.makedirs("temp", exist_ok=True)
    
    try:
        # Use yt-dlp to download auto-generated captions
        cmd = [
            "yt-dlp",
            "--write-automatic-sub",
            "--sub-langs", "en",
            "--skip-download",
            "--output", "temp/%(id)s.%(ext)s",
            video_url
        ]
        
        # Run yt-dlp and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"yt-dlp failed: {result.stderr}")
            raise Exception(f"yt-dlp failed: {result.stderr}")
        
        # Get video ID from URL
        video_id = video_url.split("v=")[1].split("&")[0]
        vtt_file = f"temp/{video_id}.en.vtt"
        
        if not os.path.exists(vtt_file):
            logger.error(f"VTT file not found: {vtt_file}")
            raise Exception(f"VTT file not found: {vtt_file}")
        
        # Read and format the VTT file
        with open(vtt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse VTT file to get transcript text
        transcript = []
        in_text = False
        for line in lines:
            if line.strip() == "WEBVTT":
                continue
            if "--" in line:
                in_text = True
                continue
            if in_text and line.strip():
                transcript.append(line.strip())
            if not line.strip():
                in_text = False
        
        # Join transcript lines
        transcript_text = "\n".join(transcript)
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            logger.info(f"Saved transcript to {output_file}")
        
        return transcript_text
        
    except Exception as e:
        logger.error(f"Error getting captions: {e}")
        raise
    finally:
        # Clean up temp directory
        if os.path.exists("temp"):
            try:
                os.rmdir("temp")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Get YouTube auto-generated captions")
    parser.add_argument("--video", required=True, help="YouTube video URL")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--log", default="var/logs/app.log", help="Log file path")
    args = parser.parse_args()
    
    # Create output directory if needed
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Set up logging
    logger = setup_logging(args.log)
    
    try:
        transcript = get_yt_captions(args.video, args.output)
        if not args.output:
            print(transcript)
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
