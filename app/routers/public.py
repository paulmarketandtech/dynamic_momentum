from fastapi import APIRouter

from app.analytics.list_of_tickers_generator import select_list_of_tickers_gt

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/")
def get_list_of_ticker_gt():
    list_of_ticker = select_list_of_tickers_gt()
    return list_of_ticker
