import pandas as pd
from pandas import DataFrame

from app.db_storage.config import conn, cur


def select_list_of_tickers_gt(mc: int = 2000000000):
    res = cur.execute(
        f"SELECT ticker, market_cap FROM 'extra_stock_metrics' WHERE market_cap > '{mc}';"
    )
    query_result = res.fetchall()
    return query_result


def select_new_52week_extremes() -> tuple[DataFrame, DataFrame]:
    query = """
    SELECT ticker, fifty_two_week_high_value, date_52week_high,
    fifty_two_week_low_value, date_52week_low
    FROM extra_stock_metrics
    """
    df = pd.read_sql_query(
        query,
        conn,
    )
    latest_high_date = df["date_52week_high"].max()
    latest_low_date = df["date_52week_low"].max()

    latest_high_df = df[df["date_52week_high"] == latest_high_date].copy()
    latest_low_df = df[df["date_52week_low"] == latest_low_date].copy()

    return latest_high_df, latest_low_df


def select_number_of_last_days(n: int = 5):
    query = """
    SELECT ticker, fifty_two_week_high_value, date_52week_high,
    fifty_two_week_low_value, date_52week_low
    FROM extra_stock_metrics
    """
    df = pd.read_sql_query(
        query,
        conn,
    )
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
yesterdays_highs, yesterdays_lows = select_new_52week_extremes()
# print(yesterdays_highs)
select_number_of_last_days()
