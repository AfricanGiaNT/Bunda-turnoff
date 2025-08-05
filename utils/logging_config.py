"""
Logging configuration for the service station operations bot.

Handles structured logging setup and configuration.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import os

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """Setup logging configuration for the application."""
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

def log_function_call(func_name: str, **kwargs):
    """Log a function call with parameters."""
    logger = get_logger("function_calls")
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"Function call: {func_name}({params})")

def log_api_request(service: str, endpoint: str, method: str = "GET", **kwargs):
    """Log an API request."""
    logger = get_logger("api_requests")
    logger.info(f"API Request: {method} {service}/{endpoint}")

def log_api_response(service: str, endpoint: str, status_code: int, response_time: float):
    """Log an API response."""
    logger = get_logger("api_responses")
    level = logging.INFO if status_code < 400 else logging.WARNING
    logger.log(level, f"API Response: {service}/{endpoint} - {status_code} ({response_time:.2f}s)")

def log_telegram_message(chat_id: int, message_type: str, content_length: int):
    """Log a Telegram message."""
    logger = get_logger("telegram")
    logger.info(f"Telegram {message_type}: chat_id={chat_id}, length={content_length}")

def log_airtable_operation(table: str, operation: str, record_count: int = 1):
    """Log an Airtable operation."""
    logger = get_logger("airtable")
    logger.info(f"Airtable {operation}: table={table}, records={record_count}")

def log_gpt_request(prompt_length: int, model: str = "gpt-4o-mini"):
    """Log a GPT request."""
    logger = get_logger("gpt")
    logger.info(f"GPT Request: model={model}, prompt_length={prompt_length}")

def log_gpt_response(response_length: int, model: str = "gpt-4o-mini", success: bool = True):
    """Log a GPT response."""
    logger = get_logger("gpt")
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"GPT Response: model={model}, response_length={response_length}, success={success}")

def log_export_generated(export_type: str, file_size: int, file_path: str):
    """Log an export generation."""
    logger = get_logger("exports")
    logger.info(f"Export generated: type={export_type}, size={file_size} bytes, path={file_path}")

def log_error(error: Exception, context: str = "", **kwargs):
    """Log an error with context."""
    logger = get_logger("errors")
    error_msg = f"Error in {context}: {str(error)}"
    if kwargs:
        error_msg += f" - {kwargs}"
    logger.error(error_msg, exc_info=True)

# Initialize logging when module is imported
setup_logging() 