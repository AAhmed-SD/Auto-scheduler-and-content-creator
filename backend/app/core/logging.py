import logging
import logging.handlers
import os
from pathlib import Path
import json
from datetime import datetime
import sys
import traceback
from typing import Any, Dict, Optional
import socket
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

class EnhancedStructuredLogFormatter(logging.Formatter):
    """Enhanced structured JSON logging with additional context"""
    
    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.pid = os.getpid()
    
    def format(self, record):
        # Create a structured log entry with enhanced context
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "logger": record.name,
            "hostname": self.hostname,
            "pid": self.pid,
            "thread": record.thread,
            "thread_name": record.threadName
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
            
        # Add correlation ID if present in request context
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
            
        return json.dumps(log_entry)

class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def filter(self, record):
        # Add correlation ID from request context if available
        if hasattr(record, "request"):
            record.correlation_id = getattr(record.request.state, "correlation_id", None)
        return True

def setup_logging():
    """Configure enhanced logging with rotation and structured format"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(EnhancedStructuredLogFormatter())
    console_handler.addFilter(CorrelationFilter())
    root_logger.addHandler(console_handler)
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(EnhancedStructuredLogFormatter())
    file_handler.addFilter(CorrelationFilter())
    root_logger.addHandler(file_handler)
    
    # Create error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(EnhancedStructuredLogFormatter())
    error_handler.addFilter(CorrelationFilter())
    root_logger.addHandler(error_handler)
    
    # Create audit log handler
    audit_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "audit.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(EnhancedStructuredLogFormatter())
    audit_handler.addFilter(CorrelationFilter())
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    
    # Set up logging for specific modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    return root_logger

# Initialize logging
logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    json_formatter = JSONFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # JSON handler for structured logging
    json_handler = RotatingFileHandler(
        'logs/app.json',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    json_handler.setFormatter(json_formatter)
    logger.addHandler(json_handler)
    
    return logger

def get_audit_logger() -> logging.Logger:
    """Get the audit logger instance"""
    return logging.getLogger("audit")

def log_api_call(
    logger: logging.Logger,
    request_id: str,
    path: str,
    method: str,
    user_id: Optional[str] = None,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    error: Optional[str] = None,
    stack_trace: Optional[str] = None
) -> None:
    """Log an API call with structured data"""
    extra = {
        'request_id': request_id,
        'path': path,
        'method': method,
        'user_id': user_id,
        'status_code': status_code,
        'duration': duration,
        'error': error,
        'stack_trace': stack_trace
    }
    
    if error:
        logger.error(f"API call failed: {error}", extra=extra)
    else:
        logger.info("API call completed", extra=extra)

class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', None),
            'user_id': getattr(record, 'user_id', None),
            'path': getattr(record, 'path', None),
            'method': getattr(record, 'method', None),
            'status_code': getattr(record, 'status_code', None),
            'duration': getattr(record, 'duration', None),
            'error': getattr(record, 'error', None),
            'stack_trace': getattr(record, 'stack_trace', None)
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data) 