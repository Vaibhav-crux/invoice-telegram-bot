from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    TELEGRAM_BOT_TOKEN: str
    CHAT_ID: str
    GEMINI_API_KEY: str

settings = Settings()