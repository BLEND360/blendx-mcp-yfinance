"""
Logging utilities for MCP tools.

This module provides logging setup and configuration for MCP tools.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime, UTC


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    output: str = "stdout",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration for MCP tools.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type (json, text)
        output: Output destination (stdout, stderr)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("mcp_tool")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if format_type.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create console handler
    if output.lower() == "stderr":
        console_handler = logging.StreamHandler(sys.stderr)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    This formatter converts log records to JSON format for better
    integration with log aggregation systems.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


def get_logger(name: str = "mcp_tool") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.now(UTC)
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            
            logger.info(
                f"Function {func.__name__} executed successfully",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "success"
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            
            logger.error(
                f"Function {func.__name__} failed: {str(e)}",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                }
            )
            
            raise
    
    return wrapper


def log_tool_execution(tool_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any], execution_time: float):
    """
    Log tool execution details.
    
    Args:
        tool_name: Name of the tool
        input_data: Tool input data
        output_data: Tool output data
        execution_time: Execution time in seconds
    """
    logger = get_logger()
    
    logger.info(
        f"Tool {tool_name} executed",
        extra={
            "tool_name": tool_name,
            "input_data": input_data,
            "output_data": output_data,
            "execution_time": execution_time,
            "status": "success"
        }
    ) 