"""Logging utilities for AI agent."""

import logging
from typing import Optional
import uuid

class RequestIdFilter(logging.Filter):
    """Filter to add request ID to log records."""
    
    def filter(self, record):
        """Add request ID to log record."""
        if not hasattr(record, 'request_id'):
            record.request_id = str(uuid.uuid4())
        return True

def setup_logging(app_name: str = "ai_agent", log_level: Optional[str] = None):
    """
    Set up logging for the application.
    
    Args:
        app_name: Name of the application
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level = getattr(logging, log_level.upper()) if log_level else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Add request ID filter
    request_id_filter = RequestIdFilter()
    root_logger.addFilter(request_id_filter)
    
    # Create application logger
    logger = logging.getLogger(app_name)
    logger.setLevel(level)
    
    return logger
