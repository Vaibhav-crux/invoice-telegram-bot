import logging
import os

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def save_uploaded_pdf(file_path):
    """
    Save the uploaded PDF to the specified file path.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # File is already downloaded by telegram_handler.py, no further action needed
    logger.info("PDF saved at %s", file_path)