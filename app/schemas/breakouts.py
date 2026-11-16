from datetime import date

from pydantic import BaseModel


class BreakoutItem(BaseModel):
    ticker: str
    value: float
    date: date


class BreakoutsResponse(BaseModel):
    n_days: int
    highs: list[BreakoutItem]
    lows: list[BreakoutItem]
