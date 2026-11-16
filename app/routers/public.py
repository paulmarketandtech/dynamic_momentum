import sqlite3

from fastapi import APIRouter, Depends

from app.analytics.list_of_tickers_generator import (
    get_52week_extremes,
    select_list_of_tickers_gt,
    select_list_of_tickers_gt_df,
    select_new_52week_extremes,
)
from app.db_storage.database import get_db

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/")
def get_list_of_ticker_gt(
    mc: int = 2_000_000_000, conn: sqlite3.Connection = Depends(get_db)
):
    return select_list_of_tickers_gt(conn, mc)


@router.get("/df")
def get_list_of_ticker_gt_df(
    mc: int = 2_000_000_000, conn: sqlite3.Connection = Depends(get_db)
):
    df = select_list_of_tickers_gt_df(conn, mc)
    # do your pandas calculations here, e.g. df['weight'] = ...
    return df.to_dict(orient="records")


@router.get("/high")
def get_new_52week_highs(conn: sqlite3.Connection = Depends(get_db)):
    df_extremes = get_52week_extremes(conn)
    yesterdays_highs, yesterdays_lows = select_new_52week_extremes(df=df_extremes)
    return yesterdays_lows.to_dict(orient="records")
