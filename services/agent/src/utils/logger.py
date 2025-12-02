"""
Structured Logger for Nyx Venatrix
Provides consistent logging configuration with Rich integration and file rotation.
"""
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Try to import rich for pretty console output
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def setup_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (default: INFO)
        log_file: Path to log file (optional)
        console_output: Whether to log to console (default: True)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    if console_output:
        if RICH_AVAILABLE:
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_path=False
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(file_formatter)

        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

    # File Handler
    if log_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with standard configuration"""
    # If logger already has handlers, assume it's configured
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Default configuration if not setup
        return setup_logger(name)
    return logger
