from fastapi import FastAPI
from app.middleware.cors import add_cors_middleware
from app.routes.invoice import router as invoice_router
from app.routes.pdf import router as pdf_router
from app.services.bot_commands import register_bot_commands
from app.services.telegram_handler import setup_telegram_handlers
from app.core.db_config import init_db
from telegram.ext import Application
from app.core.config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import time

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)

# Include routes
app.include_router(invoice_router)
app.include_router(pdf_router)

# Initialize Telegram bot application
telegram_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

# Store the polling task to prevent garbage collection
polling_task = None

# Executor for running polling in a separate thread
executor = ThreadPoolExecutor(max_workers=1)

def run_polling():
    """Run Telegram bot polling in a separate event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Initialize and set up handlers
        loop.run_until_complete(telegram_app.initialize())
        setup_telegram_handlers(telegram_app)
        loop.run_until_complete(register_bot_commands())
        # Start polling
        loop.run_until_complete(telegram_app.run_polling())
    except Exception as e:
        logger.error("Polling error: %s", str(e))
    finally:
        # Ensure clean shutdown
        loop.run_until_complete(telegram_app.stop())
        loop.run_until_complete(telegram_app.updater.shutdown())
        loop.close()

# Register bot commands and handlers on startup
@app.on_event("startup")
async def startup_event():
    global polling_task
    # Initialize database
    init_db()
    # Start polling in a separate thread
    polling_task = executor.submit(run_polling)
    logger.info("Application startup complete")

# Stop executor on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    start_time = time.time()
    # Shut down the executor
    logger.info("Shutting down executor")
    executor_shutdown_start = time.time()
    executor.shutdown(wait=False, cancel_futures=True)
    executor_shutdown_duration = time.time() - executor_shutdown_start
    logger.info("Executor shutdown completed in %.2f seconds", executor_shutdown_duration)
    
    total_shutdown_duration = time.time() - start_time
    logger.info("Total application shutdown completed in %.2f seconds", total_shutdown_duration)