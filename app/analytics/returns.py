import pandas as pd
from pandas import DataFrame


def compute_period_returns(prices: DataFrame) -> DataFrame:
    """Pure function: (ticker,date,close) already filtered -> returns."""
    if prices.empty:
        return DataFrame(
            columns=[
                "ticker",
                "start_date",
                "end_date",
                "start_price",
                "end_price",
                "return_pct",
            ]
        )

    df = prices.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["close"])
    df = df[df["close"] > 0]

    idx_first = df.groupby("ticker")["date"].idxmin()
    idx_last = df.groupby("ticker")["date"].idxmax()

    first = df.loc[idx_first, ["ticker", "date", "open"]].set_index("ticker")
    last = df.loc[idx_last, ["ticker", "date", "close"]].set_index("ticker")

    out = pd.DataFrame(
        {
            "start_date": first["date"],
            "end_date": last["date"],
            "start_price": first["open"],
            "end_price": last["close"],
        }
    )
    out["return_pct"] = out["end_price"] / out["start_price"] - 1.0
    out = out.reset_index().sort_values("return_pct", ascending=False)
    return out
