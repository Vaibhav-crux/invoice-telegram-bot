import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Common log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # General logger configuration
    logging.basicConfig(level=logging.INFO, format=log_format)

    # General file handler (app.log)
    app_log_handler = RotatingFileHandler(
        os.path.join(logs_dir, "app.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    app_log_handler.setFormatter(formatter)
    app_log_handler.setLevel(logging.INFO)

    # Access log file handler (access.log)
    access_log_handler = RotatingFileHandler(
        os.path.join(logs_dir, "access.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    access_log_handler.setFormatter(formatter)
    access_log_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(app_log_handler)

    # Configure access logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_log_handler)
    access_logger.setLevel(logging.INFO)