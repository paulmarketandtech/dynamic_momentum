import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.analytics.list_of_tickers_generator import (
    MetricsRepository,
    find_breakouts,
    select_list_of_tickers_gt_df,
)
from app.db_storage.database import get_db
from app.dependencies import get_metrics_repo

router = APIRouter(include_in_schema=False)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _query_tickers(conn: sqlite3.Connection, mc: int, q: str, limit: int):
    df = select_list_of_tickers_gt_df(conn, mc)
    if q:
        df = df[df["ticker"].str.contains(q.strip().upper(), na=False)]
    total_count = len(df)
    rows = df.head(limit).to_dict(orient="records")
    return rows, total_count


def _query_breakouts(repo: MetricsRepository, n: int):
    df = repo.fetch_52week_extremes()
    highs_df, lows_df = find_breakouts(df, n=n)
    highs = highs_df.rename(
        columns={"fifty_two_week_high_value": "value", "date_52week_high": "date"}
    ).to_dict("records")
    lows = lows_df.rename(
        columns={"fifty_two_week_low_value": "value", "date_52week_low": "date"}
    ).to_dict("records")
    return highs, lows


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    highs, lows = _query_breakouts(repo, n=5)
    rows, total_count = _query_tickers(conn, mc=2_000_000_000, q="", limit=50)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "n_days": 5,
            "highs": highs,
            "lows": lows,
            "rows": rows,
            "total_count": total_count,
            "mc": 2_000_000_000,
            "q": "",
            "limit": 50,
        },
    )


@router.get("/partials/breakouts", response_class=HTMLResponse)
def partial_breakouts(
    request: Request,
    n: int = 5,
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    highs, lows = _query_breakouts(repo, n=n)
    return templates.TemplateResponse(
        request=request,
        name="partials/breakouts_table.html",
        context={"n_days": n, "highs": highs, "lows": lows},
    )


@router.get("/partials/tickers", response_class=HTMLResponse)
def partial_tickers(
    request: Request,
    mc: int = 2_000_000_000,
    q: str = "",
    limit: int = 50,
    conn: sqlite3.Connection = Depends(get_db),
):
    rows, total_count = _query_tickers(conn, mc=mc, q=q, limit=limit)
    return templates.TemplateResponse(
        request=request,
        name="partials/tickers_table.html",
        context={
            "rows": rows,
            "total_count": total_count,
            "mc": mc,
            "q": q,
            "limit": limit,
        },
    )
