import sqlite3

import pandas as pd

from app.db_storage.config import settings

db_path = settings.DATABASE_URL
conn = sqlite3.connect(db_path)
cur = conn.cursor()

all_tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(all_tables.fetchall())

tickers = ["QQQ", "SPY", "NVDA", "AAPL"]
start_date = "2026-01-01"
placeholders = ",".join(["?"] * len(tickers))
query_benchmark = f"""
SELECT date, ticker, close
FROM stock_data
WHERE ticker IN ({placeholders})
  AND date >= ?
ORDER BY date ASC;
"""

raw_df = pd.read_sql_query(query_benchmark, conn, params=(*tickers, start_date))
raw_df["date"] = pd.to_datetime(raw_df["date"])

dupes = raw_df[raw_df.duplicated(subset=["date", "ticker"], keep=False)]
print(f"Found {len(dupes)} duplicate rows")

# Keep the latest entry for each (date, ticker) pair
clean_df = raw_df.drop_duplicates(subset=["date", "ticker"], keep="last")
