import pandas as pd

from app.analytics.returns import compute_period_returns


def test_compute():
    df = pd.DataFrame(
        [
            {"ticker": "AAPL", "date": "2026-01-02", "open": 100, "close": 104},
            {"ticker": "AAPL", "date": "2026-11-17", "open": 110, "close": 120},
        ]
    )
    res = compute_period_returns(df)
    assert round(res.loc[0, "return_pct"], 1) == 0.2
