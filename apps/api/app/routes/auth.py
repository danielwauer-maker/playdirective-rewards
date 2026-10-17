from datetime import UTC, datetime, timedelta
from html import escape

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select

from app.config import get_settings
from app.email import send_email
from app.models import MagicLink, Referral, Session as SessionRecord, Subscription, User
from app.security import SessionDep, UserDep, hash_token, new_referral_code, new_token, session_expiry

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class MagicLinkRequest(BaseModel):
    email: EmailStr
    referral_code: str | None = Field(default=None, max_length=32)


class RedeemRequest(BaseModel):
    token: str = Field(min_length=20, max_length=256)


def _unique_referral_code(session: SessionDep) -> str:
    while True:
        code = new_referral_code()
        if not session.scalar(select(User.id).where(User.referral_code == code)):
            return code


@router.post("/magic-link")
async def request_magic_link(payload: MagicLinkRequest, session: SessionDep):
    settings = get_settings()
    email = str(payload.email).strip().lower()
    raw = new_token()
    row = MagicLink(
        email=email,
        token_hash=hash_token(raw),
        referral_code=(payload.referral_code or "").strip().upper() or None,
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.magic_link_minutes),
    )
    session.add(row)
    session.commit()
    url = f"{settings.public_origin}/auth/verify?token={raw}"
    await send_email(
        email,
        "Your PlayDirective Rewards sign-in link",
        f"<p>Use this secure link to sign in:</p><p><a href=\"{escape(url)}\">Sign in to PlayDirective Rewards</a></p><p>This link expires in {settings.magic_link_minutes} minutes and can only be used once.</p>",
    )
    return {"status": "accepted", "message": "Check your email for your secure sign-in link."}


@router.post("/redeem")
def redeem_magic_link(payload: RedeemRequest, session: SessionDep):
    now = datetime.now(UTC)
    link = session.scalar(select(MagicLink).where(MagicLink.token_hash == hash_token(payload.token)))
    if not link or link.used_at or link.expires_at <= now:
        raise HTTPException(status_code=401, detail="Magic link expired or invalid")

    user = session.scalar(select(User).where(func.lower(User.email) == link.email.lower()))
    created = False
    if not user:
        user = User(email=link.email, referral_code=_unique_referral_code(session))
        session.add(user)
        session.flush()
        session.add(Subscription(user_id=user.id, plan_id="free", status="free"))
        created = True

        if link.referral_code:
            referrer = session.scalar(select(User).where(User.referral_code == link.referral_code.upper()))
            if referrer and referrer.id != user.id:
                user.referred_by_user_id = referrer.id
                session.add(Referral(
                    referrer_user_id=referrer.id,
                    referred_user_id=user.id,
                    referral_code=referrer.referral_code,
                    status="pending",
                ))

    raw_session = new_token()
    session.add(SessionRecord(
        user_id=user.id,
        token_hash=hash_token(raw_session),
        expires_at=session_expiry(),
    ))
    link.used_at = now
    session.commit()
    return {
        "access_token": raw_session,
        "token_type": "bearer",
        "created": created,
        "user": {"id": user.id, "email": user.email, "display_name": user.display_name, "referral_code": user.referral_code},
    }


@router.get("/me")
def me(user: UserDep, session: SessionDep):
    subscription = session.scalar(select(Subscription).where(Subscription.user_id == user.id))
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "referral_code": user.referral_code,
        "plan": subscription.plan_id if subscription else "free",
        "subscription_status": subscription.status if subscription else "free",
    }


@router.post("/logout")
def logout(user: UserDep):
    return {"status": "ok"}
