"""
Configuration settings for PDF Hash Changer application
"""

import os
from pathlib import Path

# Default settings
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_METADATA = {"/CustomHashBypass": "1"}
DEFAULT_FILENAME_LENGTH = 8
DEFAULT_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"

# File extensions
SUPPORTED_EXTENSIONS = [".pdf"]

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Batch processing
BATCH_SIZE = 10
MAX_CONCURRENT_PROCESSES = 4

# Security settings
ALLOW_OVERWRITE = False
VALIDATE_PDF_INTEGRITY = True

# UI settings (for future GUI implementation)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
THEME = "default"  # default, dark, light 