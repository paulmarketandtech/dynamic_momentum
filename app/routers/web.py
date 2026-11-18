import sqlite3
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.analytics.list_of_tickers_generator import (
    MetricsRepository,
    find_breakouts,
    select_list_of_tickers_gt_df,
)
from app.analytics.ytd_chart import build_ytd_chart_json
from app.db_storage.database import get_db
from app.dependencies import get_metrics_repo
from app.routers.returns import _get_returns

router = APIRouter(prefix="/web")  # , include_in_schema=False)

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


def _build_custom_returns_context(
    repo: MetricsRepository,
    start_date: date,
    end_date: date,
    mc: int,
    top_n: int,
) -> dict:
    returns_dict = _get_returns(repo, start_date, end_date, mc=mc)
    # Adjust below if returns_dict already splits best/worst or returns a DataFrame/list
    records = returns_dict["data"]
    sorted_desc = sorted(records, key=lambda x: x["return_pct"], reverse=True)
    sorted_asc = sorted(records, key=lambda x: x["return_pct"], reverse=False)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "mc": mc,
        "top_n": top_n,
        "best_rows": sorted_desc[:top_n],
        "worst_rows": sorted_asc[:top_n],
    }


# 1. EMPTY SHELL ROUTE (Zero DB queries, zero giant context!)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="base.html")


# 2. TAB VIEWS (Each tab loads only what it needs)
@router.get("/views/overview", response_class=HTMLResponse)
def view_overview(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    chart_json = build_ytd_chart_json(conn)
    highs, lows = _query_breakouts(repo, n=5)
    return templates.TemplateResponse(
        request=request,
        name="views/overview.html",
        context={"chart_json": chart_json, "n_days": 5, "highs": highs, "lows": lows},
    )


@router.get("/views/standard-returns", response_class=HTMLResponse)
def view_standard_returns(
    request: Request,
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    max_date = repo.get_max_trading_date()
    start = date(max_date.year, 1, 1)
    returns_dict = _get_returns(repo, start, max_date, mc=2_000_000_000)
    return templates.TemplateResponse(
        request=request,
        name="views/standard_returns.html",
        context={
            "end_date": returns_dict["data"],
            "data_returns": returns_dict["data"],
        },
    )


@router.get("/views/custom-returns", response_class=HTMLResponse)
def view_custom_returns(
    request: Request,
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    max_date = repo.get_max_trading_date()
    default_start = max_date - timedelta(days=30)
    context = _build_custom_returns_context(
        repo=repo,
        start_date=default_start,
        end_date=max_date,
        mc=2_000_000_000,
        top_n=25,
    )
    return templates.TemplateResponse(
        request=request,
        name="views/custom_returns.html",
        context=context,
    )


@router.get("/views/universe", response_class=HTMLResponse)
def view_universe(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    rows, total_count = _query_tickers(conn, mc=2_000_000_000, q="", limit=50)
    return templates.TemplateResponse(
        request=request,
        name="views/universe.html",
        context={
            "rows": rows,
            "total_count": total_count,
            "mc": 2_000_000_000,
            "q": "",
            "limit": 50,
        },
    )


@router.get("/views/charts", response_class=HTMLResponse)
def view_charts(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    chart_json = build_ytd_chart_json(conn)
    return templates.TemplateResponse(
        request=request,
        name="views/charts.html",
        context={"chart_json": chart_json},
    )


"""
all to be deleted?
@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    chart_json = build_ytd_chart_json(conn)
    highs, lows = _query_breakouts(repo, n=5)
    rows, total_count = _query_tickers(conn, mc=2_000_000_000, q="", limit=50)

    max_date = repo.get_max_trading_date()
    start = date(max_date.year, 1, 1)
    returns_dict = _get_returns(repo, start, max_date, mc=2_000_000_000)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "chart_json": chart_json,
            "extra_tickers": "",
            "n_days": 5,
            "highs": highs,
            "lows": lows,
            "rows": rows,
            "total_count": total_count,
            "mc": 2_000_000_000,
            "q": "",
            "limit": 50,
            "end_date": returns_dict["data"],
            "data_returns": returns_dict["data"],
        },
    )
"""


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


@router.get("/partials/ytd-returns", response_class=HTMLResponse)
def partial_ytd_returs(
    request: Request,
    repo: MetricsRepository = Depends(get_metrics_repo),
    mc: int = 2_000_000_000,
    limit: int = 50,
):
    max_date = repo.get_max_trading_date()
    start = date(max_date.year, 1, 1)
    return templates.TemplateResponse(
        request=request,
        name="partials/ytd_table.html",
        context=_get_returns(repo, start, max_date, mc),
    )


@router.get("/partials/custom-returns", response_class=HTMLResponse)
def partial_custom_returns(
    request: Request,
    start_date: date,
    end_date: date,
    mc: int = 2_000_000_000,
    top_n: int = 25,
    repo: MetricsRepository = Depends(get_metrics_repo),
):
    context = _build_custom_returns_context(
        repo=repo,
        start_date=start_date,
        end_date=end_date,
        mc=mc,
        top_n=top_n,
    )
    return templates.TemplateResponse(
        request=request,
        name="partials/custom_returns_table.html",
        context=context,
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


@router.get("/partials/ytd-chart", response_class=HTMLResponse)
def partial_ytd_chart(
    request: Request,
    tickers: str = "",
    conn: sqlite3.Connection = Depends(get_db),
):
    extra_list = [t.strip() for t in tickers.split(",") if t.strip()]
    chart_json = build_ytd_chart_json(conn, extra_tickers=extra_list)
    return templates.TemplateResponse(
        request=request,
        name="partials/ytd_chart.html",
        context={"chart_json": chart_json},
    )
