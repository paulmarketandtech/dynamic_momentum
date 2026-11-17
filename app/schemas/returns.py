from pydantic import BaseModel
from datetime import date


class TickerReturn(BaseModel):
    ticker: str
    return_pct: float
    start_price: float
    end_price: float
    start_date: date
    end_date: date


class ReturnsResponse(BaseModel):
    start: date
    end: date
    as_of: date
    mc_threshold: int
    count: int
    data: list[TickerReturn]
