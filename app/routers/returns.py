from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.analytics.list_of_tickers_generator import MetricsRepository
from app.analytics.returns import compute_period_returns
from app.dependencies import get_metrics_repo
from app.schemas.returns import ReturnsResponse

router = APIRouter(prefix="/returns", tags=["returns"])


def _get_returns(repo: MetricsRepository, start: date, end: date, mc: int) -> dict:
    prices_df = repo.fetch_prices(start, end, mc)
    ret_df = compute_period_returns(prices_df)
    """there are issues with delisted stocks and if MC was not updated for a while - had to exclude those stocks"""
    ret_df = ret_df.loc[ret_df["end_date"].dt.date == end]
    return {
        "start": start,
        "end": end,
        "as_of": repo.get_max_trading_date(),
        "mc_threshold": mc,
        "count": len(ret_df),
        "data": ret_df.to_dict(orient="records"),
    }


@router.get("/ytd", response_model=ReturnsResponse)
def get_ytd_returns(
    mc: int = Query(2_000_000_000, ge=0),
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    max_date = repo.get_max_trading_date()
    start = date(max_date.year, 1, 1)
    return _get_returns(repo, start, max_date, mc)


@router.get("/custom", response_model=ReturnsResponse)
def get_custom_returns(
    start: date,
    end: date,
    mc: int = Query(2_000_000_000, ge=0),
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    if start > end:
        raise HTTPException(400, "start must be <= end")
    return _get_returns(repo, start, end, mc)
