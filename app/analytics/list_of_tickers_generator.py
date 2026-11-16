import os
import sqlite3
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# cur = conn.cursor()


"""
def select_list_of_tickers_gt(mc: int = 2000000000):
    res = cur.execute(
        f"SELECT ticker, market_cap FROM 'extra_stock_metrics' WHERE market_cap > '{mc}';"
    )
    query_result = res.fetchall()
    return query_result
"""


def select_list_of_tickers_gt(mc: int = 2_000_000_000):
    conn = sqlite3.connect(DATABASE_URL)
    try:
        cur = conn.cursor()
        res = cur.execute(
            "SELECT ticker, market_cap FROM extra_stock_metrics WHERE market_cap > ?",
            (mc,),
        )
        return res.fetchall()
    finally:
        conn.close()


def get_52week_extremes() -> DataFrame:
    query = """
    SELECT ticker, fifty_two_week_high_value, date_52week_high,
    fifty_two_week_low_value, date_52week_low
    FROM extra_stock_metrics
    """
    df = pd.read_sql_query(
        query,
        conn,
    )
    return df


def select_new_52week_extremes(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    latest_high_date = df["date_52week_high"].max()
    latest_low_date = df["date_52week_low"].max()

    latest_high_df = df[df["date_52week_high"] == latest_high_date].copy()
    latest_low_df = df[df["date_52week_low"] == latest_low_date].copy()

    return latest_high_df, latest_low_df


def select_number_of_last_days(df: DataFrame, n: int = 5):
    """DF wiht new highs from last 5 days"""
    latest_n_high_dates = (
        df["date_52week_high"].drop_duplicates().sort_values().tail(n).tolist()
    )
    latest_high_df = df[df["date_52week_high"].isin(latest_n_high_dates)]
    latest_high_df = latest_high_df[
        ["ticker", "fifty_two_week_high_value", "date_52week_high"]
    ]

    """DF wiht new lows from last 5 days"""
    latest_n_low_dates = (
        df["date_52week_low"].drop_duplicates().sort_values().tail(n).tolist()
    )
    latest_low_df = df[df["date_52week_low"].isin(latest_n_low_dates)]
    latest_low_df = latest_low_df[
        ["ticker", "fifty_two_week_low_value", "date_52week_low"]
    ]

    return latest_high_df, latest_low_df


# one_bill = select_list_of_tickers_gt()
# print(yesterdays_highs)
# df_extremes = get_52week_extremes()
# yesterdays_highs, yesterdays_lows = select_new_52week_extremes(df=df_extremes)
# print(yesterdays_highs)
# last_week_highs, last_week_lows = select_number_of_last_days(df=df_extremes)
# print(last_week_highs)
