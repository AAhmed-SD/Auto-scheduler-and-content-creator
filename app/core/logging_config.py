import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Set up specific loggers
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.INFO)

    db_logger = logging.getLogger('database')
    db_logger.setLevel(logging.INFO)

    cache_logger = logging.getLogger('cache')
    cache_logger.setLevel(logging.INFO)

    return {
        'root': root_logger,
        'api': api_logger,
        'database': db_logger,
        'cache': cache_logger
    }

# Initialize logging
loggers = setup_logging() 