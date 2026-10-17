from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app import research_models  # noqa: F401 - registers research tables with metadata
from app.routes import auth, billing, offers, referrals, research


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.public_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(offers.router)
app.include_router(referrals.router)
app.include_router(billing.router)
app.include_router(research.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "playdirective-rewards-api"}


@app.get("/ready")
def ready():
    session = SessionLocal()
    try:
        session.execute(text("select 1"))
        return {"status": "ready", "database": "ok"}
    finally:
        session.close()
