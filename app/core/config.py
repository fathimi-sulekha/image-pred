import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    #OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "*****")  # Replace with actual API key
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  # Default to localhost
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  # Convert to integer

# Create a global settings instance
settings = Settings()
