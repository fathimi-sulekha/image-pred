import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = "*****"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

settings = Settings()

if not settings.OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set. Please check your .env file or environment variables.")
