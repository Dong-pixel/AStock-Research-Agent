import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

load_dotenv()


class Settings(BaseModel):
    """Application configuration loaded from environment variables."""

    deepseek_api_key: SecretStr
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"


@lru_cache
def get_settings() -> Settings:
    """Load and validate application settings once."""

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError("DEEPSEEK_API_KEY is missing. Please configure it in the .env file.")

    return Settings(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv(
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com",
        ),
        deepseek_model=os.getenv(
            "DEEPSEEK_MODEL",
            "deepseek-v4-flash",
        ),
    )
