from sqlalchemy import func, select

from fastapi import APIRouter

from app.models import CreditLedgerEntry, Referral, User
from app.security import SessionDep, UserDep

router = APIRouter(prefix="/v1/referrals", tags=["referrals"])


@router.get("")
def referral_dashboard(user: UserDep, session: SessionDep):
    referrals = session.scalars(
        select(Referral).where(Referral.referrer_user_id == user.id).order_by(Referral.created_at.desc())
    ).all()
    balance = session.scalar(
        select(func.coalesce(func.sum(CreditLedgerEntry.amount_cents), 0)).where(CreditLedgerEntry.user_id == user.id)
    ) or 0
    referred_users = {u.id: u for u in session.scalars(
        select(User).where(User.id.in_([r.referred_user_id for r in referrals] or [-1]))
    ).all()}
    return {
        "referral_code": user.referral_code,
        "referral_path": f"/login?ref={user.referral_code}",
        "credit_balance_cents": int(balance),
        "referrals": [
            {
                "id": r.id,
                "email": referred_users.get(r.referred_user_id).email if referred_users.get(r.referred_user_id) else None,
                "status": r.status,
                "created_at": r.created_at,
                "qualified_at": r.qualified_at,
                "rewarded_at": r.rewarded_at,
            }
            for r in referrals
        ],
    }


@router.get("/ledger")
def credit_ledger(user: UserDep, session: SessionDep):
    entries = session.scalars(
        select(CreditLedgerEntry).where(CreditLedgerEntry.user_id == user.id).order_by(CreditLedgerEntry.created_at.desc())
    ).all()
    return {
        "items": [
            {
                "id": e.id,
                "amount_cents": e.amount_cents,
                "currency": e.currency,
                "entry_type": e.entry_type,
                "source_type": e.source_type,
                "source_id": e.source_id,
                "description": e.description,
                "created_at": e.created_at,
            }
            for e in entries
        ]
    }
