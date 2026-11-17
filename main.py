from pathlib import Path

import fastapi_swagger_dark as fsd
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import public, web

app = FastAPI(docs_url=None)
router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent / "app" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


fsd.install(router)
app.include_router(router)
app.include_router(public.router)
app.include_router(web.router)


@app.get("/health")
def health_check():
    try:
        return {"status": "ok"}
    except Exception as e:
        return {"status": "degraded", "db": str(e)}
