import sqlite3

from fastapi import APIRouter, Depends

from app.analytics.list_of_tickers_generator import (
    MetricsRepository,
    find_breakouts,
    select_list_of_tickers_gt_df,
)
from app.db_storage.database import get_db
from app.dependencies import get_metrics_repo
from app.schemas.breakouts import BreakoutsResponse

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/ticker-list-gt")
def get_list_of_ticker_gt_df(
    mc: int = 2_000_000_000, conn: sqlite3.Connection = Depends(get_db)
):
    df = select_list_of_tickers_gt_df(conn, mc)
    return df.to_dict(orient="records")


@router.get("/breakouts", response_model=BreakoutsResponse)
def get_breakouts(n: int = 5, repo: MetricsRepository = Depends(get_metrics_repo)):
    df = repo.fetch_52week_extremes()
    highs_df, lows_df = find_breakouts(df, n=n)

    return {
        "n_days": n,
        "highs": highs_df.rename(
            columns={"fifty_two_week_high_value": "value", "date_52week_high": "date"}
        ).to_dict("records"),
        "lows": lows_df.rename(
            columns={"fifty_two_week_low_value": "value", "date_52week_low": "date"}
        ).to_dict("records"),
    }
