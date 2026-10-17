from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.domain.scoring import analyze_milestones
from app.models import Analysis, Milestone, Offer, Subscription
from app.security import SessionDep, UserDep

router = APIRouter(prefix="/v1/offers", tags=["offers"])
FREE_MONTHLY_ANALYSES = 5


class MilestoneInput(BaseModel):
    position: int = Field(ge=1)
    label: str = Field(min_length=1, max_length=220)
    reward: Decimal = Field(ge=0)
    estimated_hours: Decimal = Field(default=0, ge=0)
    estimated_spend: Decimal = Field(default=0, ge=0)
    completion_probability: Decimal = Field(default=Decimal("0.5"), ge=0, le=1)
    tracking_confidence: Decimal = Field(default=Decimal("0.8"), ge=0, le=1)


class OfferInput(BaseModel):
    provider: str = Field(default="freecash", max_length=80)
    title: str = Field(min_length=2, max_length=220)
    platform: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default=None, max_length=2)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    headline_reward: Decimal = Field(default=0, ge=0)
    deadline_days: int | None = Field(default=None, ge=1, le=365)
    notes: str | None = Field(default=None, max_length=5000)
    milestones: list[MilestoneInput] = Field(min_length=1, max_length=50)


def _serialize_offer(offer: Offer, milestones: list[Milestone], analysis: Analysis | None = None):
    return {
        "id": offer.id,
        "provider": offer.provider,
        "title": offer.title,
        "platform": offer.platform,
        "country": offer.country,
        "currency": offer.currency,
        "headline_reward": float(offer.headline_reward),
        "deadline_days": offer.deadline_days,
        "notes": offer.notes,
        "status": offer.status,
        "created_at": offer.created_at,
        "milestones": [
            {
                "id": m.id,
                "position": m.position,
                "label": m.label,
                "reward": float(m.reward),
                "estimated_hours": float(m.estimated_hours),
                "estimated_spend": float(m.estimated_spend),
                "completion_probability": float(m.completion_probability),
                "tracking_confidence": float(m.tracking_confidence),
            }
            for m in sorted(milestones, key=lambda x: x.position)
        ],
        "analysis": None if not analysis else {
            "id": analysis.id,
            "pd_score": analysis.pd_score,
            "verdict": analysis.verdict,
            "recommended_stop_position": analysis.recommended_stop_position,
            "expected_reward": float(analysis.expected_reward),
            "expected_spend": float(analysis.expected_spend),
            "expected_hours": float(analysis.expected_hours),
            "effective_hourly_rate": float(analysis.effective_hourly_rate),
            "explanation": analysis.explanation,
        },
    }


def _enforce_analysis_entitlement(user_id: int, session: SessionDep) -> None:
    subscription = session.scalar(select(Subscription).where(Subscription.user_id == user_id))
    if subscription and subscription.plan_id in {"pro", "max"} and subscription.status in {"active", "trialing"}:
        return
    now = datetime.now(UTC)
    month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
    used = session.scalar(
        select(func.count(Analysis.id)).where(Analysis.user_id == user_id, Analysis.created_at >= month_start)
    ) or 0
    if used >= FREE_MONTHLY_ANALYSES:
        raise HTTPException(status_code=402, detail=f"Free plan includes {FREE_MONTHLY_ANALYSES} analyses per month. Upgrade to continue.")


@router.post("")
def create_offer(payload: OfferInput, user: UserDep, session: SessionDep):
    _enforce_analysis_entitlement(user.id, session)
    offer = Offer(
        user_id=user.id,
        provider=payload.provider.strip().lower(),
        title=payload.title.strip(),
        platform=payload.platform,
        country=payload.country.upper() if payload.country else None,
        currency=payload.currency.upper(),
        headline_reward=payload.headline_reward,
        deadline_days=payload.deadline_days,
        notes=payload.notes,
        status="analyzed",
    )
    session.add(offer)
    session.flush()
    rows = []
    for item in payload.milestones:
        row = Milestone(offer_id=offer.id, **item.model_dump())
        session.add(row)
        rows.append(row)
    result = analyze_milestones([x.model_dump() for x in payload.milestones])
    analysis = Analysis(user_id=user.id, offer_id=offer.id, **result)
    session.add(analysis)
    session.commit()
    session.refresh(offer)
    session.refresh(analysis)
    return _serialize_offer(offer, rows, analysis)


@router.get("")
def list_offers(user: UserDep, session: SessionDep):
    offers = session.scalars(select(Offer).where(Offer.user_id == user.id).order_by(Offer.created_at.desc())).all()
    items = []
    for offer in offers:
        milestones = session.scalars(select(Milestone).where(Milestone.offer_id == offer.id)).all()
        analysis = session.scalar(select(Analysis).where(Analysis.offer_id == offer.id).order_by(Analysis.created_at.desc()))
        items.append(_serialize_offer(offer, milestones, analysis))
    return {"items": items}


@router.get("/{offer_id}")
def get_offer(offer_id: int, user: UserDep, session: SessionDep):
    offer = session.get(Offer, offer_id)
    if not offer or offer.user_id != user.id:
        raise HTTPException(status_code=404, detail="Offer not found")
    milestones = session.scalars(select(Milestone).where(Milestone.offer_id == offer.id)).all()
    analysis = session.scalar(select(Analysis).where(Analysis.offer_id == offer.id).order_by(Analysis.created_at.desc()))
    return _serialize_offer(offer, milestones, analysis)
