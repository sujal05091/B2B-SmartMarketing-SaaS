"""
Logger Configuration Module

Provides centralized logging functionality with colored output,
file logging, and different log levels for the application.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import colorlog


def setup_logger(name: str = "smart_marketing", log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler - detailed logs
    log_file = log_dir / "activity.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler - colored output
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "smart_marketing") -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.
    
    Usage:
        class MyClass(LoggerMixin):
            def __init__(self):
                self.setup_logging("MyClass")
    """
    
    def setup_logging(self, name: str = None):
        """Set up logging for the class."""
        if name is None:
            name = self.__class__.__name__
        self.logger = get_logger(name)
    
    def log_info(self, message: str):
        """Log info message."""
        if hasattr(self, 'logger'):
            self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message."""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
    
    def log_error(self, message: str, exc_info=False):
        """Log error message."""
        if hasattr(self, 'logger'):
            self.logger.error(message, exc_info=exc_info)
    
    def log_debug(self, message: str):
        """Log debug message."""
        if hasattr(self, 'logger'):
            self.logger.debug(message)
