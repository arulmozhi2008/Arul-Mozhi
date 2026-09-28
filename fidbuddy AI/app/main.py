from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    version="1.0.0",
    description=(
        "AI fitness planning with Gemini, "
        "FastAPI, Jinja2 and SQLite."
    ),
    lifespan=lifespan
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.admin_session_secret,
    session_cookie="fitbuddy_session",
    same_site="lax",
    https_only=False
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


app.include_router(router)