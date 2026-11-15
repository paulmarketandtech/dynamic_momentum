import sqlite3

import pandas as pd

from app.db_storage.config import settings

db_path = settings.DATABASE_URL
conn = sqlite3.connect(db_path)
cur = conn.cursor()

all_tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(all_tables.fetchall())

query_ohlc = """
SELECT ticker, date, open, high, low, close
FROM stock_data
"""

return_periods = {
    "ret_week": 5,
    "ret_month": 21,
    "ret_3months": 63,
    "ret_12months": 126,
}

df = pd.read_sql_query(
    query_ohlc,
    conn,
)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

grouped_close = df.groupby("ticker")["close"]

for col_name, days in return_periods.items():
    df[col_name] = grouped_close.pct_change(periods=days)

latest_date = df["date"].max()
latest_momentum = df[df["date"] == latest_date].sort_values(
    "ret_3months", ascending=False
)
latest_momentum[
    ["ticker", "close", "ret_week", "ret_month", "ret_3months", "ret_12months"]
].head(15)
print(latest_momentum)
