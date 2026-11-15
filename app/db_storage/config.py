import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # model_config = {"env_file": ".env"}


settings = Settings()
conn = sqlite3.connect(settings.DATABASE_URL)
cur = conn.cursor()
