"""Common utility functions for the project."""

import sys
import logging
import re


def setup_logging(log_file_path: str) -> None:
    """
    Sets up logging to both a file and the console (stderr).

    Args:
        log_file_path: The full path to the log file.
    """
    # Get the root logger. Configuring the root logger is often simpler
    # than managing individual loggers when the configuration is shared.
    root_logger = logging.getLogger()

    # Set the minimum level of messages to be processed.
    # If set to INFO, DEBUG messages will be ignored.
    root_logger.setLevel(logging.INFO)

    # Clear any existing handlers to avoid duplicate logging messages
    # if this function is ever called more than once.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Define the format for log messages.
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # --- File Handler ---
    # This handler writes log messages to a file.
    try:
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)  # Set the level for the file handler.
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, log the error to the console and continue.
        logging.basicConfig()  # Basic config to ensure the next line is visible.
        logging.error(f"Failed to set up file handler at {log_file_path}: {e}")

    # --- Console (Stream) Handler ---
    # This handler writes log messages to the console (standard error).
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(
        logging.INFO
    )  # You could use logging.WARNING for less verbose console output
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    logging.info("Logging configured successfully.")


def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from a string so it can be used as a filename."""
    s = re.sub(r"[^\w\s-]", "", filename)
    s = re.sub(r"\s+", "-", s).strip()
    return s


def generate_unique_filename(title: str, video_id: str) -> str:
    """Generates a unique filename from a video title and its ID."""
    sanitized_title = sanitize_filename(title)
    return f"{sanitized_title}-{video_id}.txt"
