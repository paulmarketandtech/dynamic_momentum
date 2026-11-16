import sqlite3

from fastapi import Depends

from app.analytics.list_of_tickers_generator import MetricsRepository
from app.db_storage.database import get_db


def get_metrics_repo(conn: sqlite3.Connection = Depends(get_db)):
    return MetricsRepository(conn)
