import json
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.utils


def build_ytd_chart_json(
    conn: sqlite3.Connection, extra_tickers: list[str] | None = None
) -> str:
    base_tickers = ["SPY", "QQQ"]
    cleaned_extras = [
        t.strip().upper()
        for t in (extra_tickers or [])
        if t.strip() and t.strip().upper() not in base_tickers
    ]
    tickers = base_tickers + cleaned_extras

    placeholders = ",".join(["?"] * len(tickers))
    # Dynamically grab the latest calendar year present in stock_data
    query = f"""
    SELECT date, ticker, open, close
    FROM stock_data
    WHERE ticker IN ({placeholders})
      AND strftime('%Y', date) = (SELECT MAX(strftime('%Y', date)) FROM stock_data)
    ORDER BY date ASC;
    """
    df = pd.read_sql_query(query, conn, params=tickers)
    if df.empty:
        return "{}"

    df = df.drop_duplicates(subset=["date", "ticker"], keep="last").copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])

    # Calculate YTD % from the first trading session's OPEN of that year
    first_open = df.groupby("ticker")["open"].transform("first")
    df["ytd_pct"] = ((df["close"] / first_open) - 1) * 100

    ytd_wide = df.pivot(index="date", columns="ticker", values="ytd_pct")
    # Keep column order: SPY, QQQ, then user's extra tickers
    ordered_cols = [c for c in tickers if c in ytd_wide.columns]
    ytd_wide = ytd_wide[ordered_cols]

    fig = px.line(
        ytd_wide,
        labels={"value": "YTD Return (%)", "date": "Date", "ticker": "Ticker"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
