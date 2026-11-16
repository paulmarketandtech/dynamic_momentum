import sqlite3

import pandas as pd


def select_list_of_tickers_gt_df(
    conn: sqlite3.Connection, mc: int = 2_000_000_000
) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT ticker, market_cap FROM extra_stock_metrics WHERE market_cap > ?",
        conn,
        params=(mc,),
    )


class MetricsRepository:
    def __init__(self, conn):
        self.conn = conn

    def fetch_52week_extremes(self) -> pd.DataFrame:
        query = """
        SELECT ticker, fifty_two_week_high_value, date_52week_high,
               fifty_two_week_low_value, date_52week_low
        FROM extra_stock_metrics
        """
        return pd.read_sql_query(query, self.conn)


def _filter_last_n_dates(df: pd.DataFrame, date_col: str, value_col: str, n: int):
    dates = pd.to_datetime(df[date_col])
    last_n = dates.drop_duplicates().sort_values().tail(n)
    mask = dates.isin(last_n)
    return df.loc[mask, ["ticker", value_col, date_col]].copy()


def find_breakouts(df: pd.DataFrame, n: int = 1):
    highs = _filter_last_n_dates(df, "date_52week_high", "fifty_two_week_high_value", n)
    lows = _filter_last_n_dates(df, "date_52week_low", "fifty_two_week_low_value", n)
    return highs, lows
