import logging
from telegram import Bot, BotCommand
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def register_bot_commands():
    """
    Register Telegram bot commands using the setMyCommands method.
    """
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    commands = [
        BotCommand(command="invoices", description="Start the invoice process"),
        BotCommand(command="help", description="Get help with the bot"),
        BotCommand(command="status", description="Check processing status"),
    ]

    try:
        await bot.set_my_commands(commands=commands)
        logger.info("Bot commands registered successfully: %s", [cmd.command for cmd in commands])
    except Exception as e:
        logger.error("Failed to register bot commands: %s", str(e))
        raise