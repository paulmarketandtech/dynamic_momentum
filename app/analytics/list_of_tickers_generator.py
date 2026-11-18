import sqlite3
from datetime import date

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

    def get_max_trading_date(self) -> date:
        row = self.conn.execute(
            "SELECT MAX(date) as max_date FROM stock_data"
        ).fetchone()
        return pd.to_datetime(row[0]).date()

    def fetch_prices(self, start: date, end: date, mc: int) -> pd.DataFrame:
        query = """
        SELECT s.ticker, s.date, s.close, s.open
        FROM stock_data s
        JOIN extra_stock_metrics m ON m.ticker = s.ticker
        WHERE m.market_cap > ?
          AND s.date >= ?
          AND s.date <= ?
        ORDER BY s.ticker, s.date
        """
        return pd.read_sql_query(
            query, self.conn, params=(mc, start.isoformat(), end.isoformat())
        )

    # TODO: delete
    def clearing_df(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.drop_duplicates(subset=["date", "ticker"], keep="last").copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
        return df

    # TODO: delete
    def fetch_open_close_for_current_year(
        self, df_list_of_tickers: pd.DataFrame
    ) -> pd.DataFrame:
        tickers = df_list_of_tickers["ticker"].to_list()
        placeholders = ",".join(["?"] * len(tickers[:10]))

        query = f"""
        SELECT date, ticker, open, close
        FROM stock_data
        WHERE ticker IN ({placeholders})
        AND strftime('%Y', date) = (SELECT MAX(strftime('%Y', date)) FROM stock_data)
        ORDER BY date ASC;
        """
        df_raw = pd.read_sql_query(query, self.conn, params=tickers[:10])
        # df = self.clearing_df(df_raw)

        return df_raw


def _filter_last_n_dates(df: pd.DataFrame, date_col: str, value_col: str, n: int):
    dates = pd.to_datetime(df[date_col])
    last_n = dates.drop_duplicates().sort_values().tail(n)
    mask = dates.isin(last_n)
    return df.loc[mask, ["ticker", value_col, date_col]].copy()


def find_breakouts(df: pd.DataFrame, n: int = 1):
    highs = _filter_last_n_dates(df, "date_52week_high", "fifty_two_week_high_value", n)
    lows = _filter_last_n_dates(df, "date_52week_low", "fifty_two_week_low_value", n)
    return highs, lows


def find_ytd_returns(df: pd.DataFrame):
    df["year"] = df["date"].dt.year
    first_open_of_year = df.groupby(["ticker", "year"])["open"].transform("first")
    df["ytd_calc"] = ((df["close"] / first_open_of_year) - 1) * 100

    latest_day_returns = df.groupby("ticker").last()
    # ytd_returns = latest_day_returns.sort_values("ytd_calc", ascending=False)
    return latest_day_returns
