import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.models import Session as SessionRecord, User


def hash_token(token: str) -> str:
    settings = get_settings()
    return hashlib.sha256(f"{settings.auth_secret}:{token}".encode()).hexdigest()


def new_token() -> str:
    return secrets.token_urlsafe(32)


def new_referral_code() -> str:
    return secrets.token_urlsafe(7).replace("-", "").replace("_", "")[:9].upper()


def session_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(days=get_settings().session_days)


def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(db_session)]


def require_user(authorization: Annotated[str | None, Header()] = None, session: Session = Depends(db_session)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    raw = authorization.split(" ", 1)[1].strip()
    row = session.scalar(select(SessionRecord).where(SessionRecord.token_hash == hash_token(raw)))
    now = datetime.now(UTC)
    if not row or row.revoked_at or row.expires_at <= now:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    user = session.get(User, row.user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User unavailable")
    return user


UserDep = Annotated[User, Depends(require_user)]
