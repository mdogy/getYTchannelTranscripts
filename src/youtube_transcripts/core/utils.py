"""Common utility functions for YouTube video processing."""

import os
import sys
import logging
from typing import Optional


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


def get_unique_filename(
    base_name: str, output_dir: str, extension: str = ".csv"
) -> str:
    """Generates a unique filename to avoid overwriting."""
    base_path = os.path.join(output_dir, base_name)
    if not os.path.exists(base_path + extension):
        return base_path + extension
    i = 1
    while True:
        candidate = f"{base_path}_{i}{extension}"
        if not os.path.exists(candidate):
            return candidate
        i += 1
