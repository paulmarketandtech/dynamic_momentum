import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_PATH = os.getenv("DATABASE_URL")


def get_db():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # so you get dict-like rows, not just tuples
    try:
        yield conn
    finally:
        conn.close()
