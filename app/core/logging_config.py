"""Logging configuration module."""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict


class Loggers:
    """Loggers class for managing application loggers."""

    def __init__(self):
        """Initialize loggers."""
        self._loggers: Dict[str, logging.Logger] = {}

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name."""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            self._loggers[name] = logger
        return self._loggers[name]


def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Add file handler
    file_handler = RotatingFileHandler(
        f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(console_handler)

    return root_logger


# Initialize logging
loggers = Loggers()
