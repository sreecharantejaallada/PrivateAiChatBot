# app/config.py
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load .env file if present (useful for local dev)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    # Telegram
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@mybot")
    ALLOWED_USER_IDS: List[int] = [
        int(uid) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid
    ]

    # Ollama
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    MODEL_NAME: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    MAX_CHARS: int = int(os.getenv("MAX_CHARS", "500"))
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Optional webhook mode
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")

    # Rate limiting (placeholder – integrate with redis/ratelimit lib)
    MESSAGE_RATE_LIMIT: int = int(os.getenv("MESSAGE_RATE_LIMIT", "0"))  # 0 = disabled

settings = Settings()
