import logging
import os
import aiofiles.os

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

async def delete_file(file_path: str):
    """
    Asynchronously delete a file at the specified path.
    
    Args:
        file_path (str): Path to the file to delete.
    
    Raises:
        Exception: If file deletion fails.
    """
    try:
        await aiofiles.os.remove(file_path)
        logger.info("File deleted: %s", file_path)
    except Exception as e:
        logger.error("Failed to delete file %s: %s", file_path, str(e))
        raise