import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.admin import AdminUserDep
from app.config import get_settings
from app.research_models import OfferSnapshot, OfferSnapshotMilestone, ResearchScreenshot
from app.security import SessionDep

router = APIRouter(prefix="/v1/research", tags=["research"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


class SnapshotMilestoneInput(BaseModel):
    position: int = Field(ge=1)
    label: str = Field(min_length=1, max_length=260)
    reward: Decimal = Field(default=0, ge=0)
    milestone_type: str = Field(default="progress", max_length=32)
    purchase_amount: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class SnapshotCreate(BaseModel):
    screenshot_id: int | None = None
    provider: str = Field(default="freecash", min_length=2, max_length=80)
    game_name: str = Field(min_length=2, max_length=220)
    platform: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default="DE", min_length=2, max_length=2)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    headline_reward: Decimal = Field(default=0, ge=0)
    deadline_days: int | None = Field(default=None, ge=1, le=365)
    observed_at: datetime | None = None
    source_note: str | None = Field(default=None, max_length=4000)
    milestones: list[SnapshotMilestoneInput] = Field(min_length=1, max_length=80)


def _serialize_screenshot(row: ResearchScreenshot) -> dict:
    return {
        "id": row.id,
        "original_filename": row.original_filename,
        "content_type": row.content_type,
        "byte_size": row.byte_size,
        "sha256": row.sha256,
        "extraction_status": row.extraction_status,
        "created_at": row.created_at,
    }


def _serialize_snapshot(row: OfferSnapshot, milestones: list[OfferSnapshotMilestone]) -> dict:
    return {
        "id": row.id,
        "screenshot_id": row.screenshot_id,
        "provider": row.provider,
        "game_name": row.game_name,
        "platform": row.platform,
        "country": row.country,
        "currency": row.currency,
        "headline_reward": float(row.headline_reward),
        "deadline_days": row.deadline_days,
        "observed_at": row.observed_at,
        "source_kind": row.source_kind,
        "source_note": row.source_note,
        "review_status": row.review_status,
        "created_at": row.created_at,
        "milestones": [
            {
                "id": m.id,
                "position": m.position,
                "label": m.label,
                "reward": float(m.reward),
                "milestone_type": m.milestone_type,
                "purchase_amount": float(m.purchase_amount) if m.purchase_amount is not None else None,
                "notes": m.notes,
            }
            for m in sorted(milestones, key=lambda x: x.position)
        ],
    }


@router.post("/screenshots")
async def upload_screenshot(
    admin: AdminUserDep,
    session: SessionDep,
    file: UploadFile = File(...),
):
    settings = get_settings()
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only PNG, JPEG and WebP screenshots are supported")

    data = await file.read()
    max_bytes = settings.research_max_upload_mb * 1024 * 1024
    if not data:
        raise HTTPException(status_code=422, detail="Screenshot is empty")
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Screenshot exceeds {settings.research_max_upload_mb} MB")

    digest = hashlib.sha256(data).hexdigest()
    existing = session.scalar(select(ResearchScreenshot).where(ResearchScreenshot.sha256 == digest))
    if existing:
        return {"duplicate": True, "screenshot": _serialize_screenshot(existing)}

    suffix = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}[content_type]
    storage_dir = Path(settings.research_upload_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{digest}{suffix}"
    storage_path.write_bytes(data)

    row = ResearchScreenshot(
        uploaded_by_user_id=admin.id,
        original_filename=(file.filename or "screenshot")[:255],
        content_type=content_type,
        byte_size=len(data),
        sha256=digest,
        storage_path=str(storage_path),
        extraction_status="manual_review_required",
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return {"duplicate": False, "screenshot": _serialize_screenshot(row)}


@router.get("/screenshots")
def list_screenshots(admin: AdminUserDep, session: SessionDep):
    rows = session.scalars(select(ResearchScreenshot).order_by(ResearchScreenshot.created_at.desc()).limit(200)).all()
    return {"items": [_serialize_screenshot(x) for x in rows]}


@router.post("/snapshots")
def create_snapshot(payload: SnapshotCreate, admin: AdminUserDep, session: SessionDep):
    if payload.screenshot_id is not None and not session.get(ResearchScreenshot, payload.screenshot_id):
        raise HTTPException(status_code=404, detail="Screenshot not found")

    observed_at = payload.observed_at or datetime.now(UTC)
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=UTC)

    row = OfferSnapshot(
        imported_by_user_id=admin.id,
        screenshot_id=payload.screenshot_id,
        provider=payload.provider.strip().lower(),
        game_name=payload.game_name.strip(),
        platform=(payload.platform or "").strip().lower() or None,
        country=(payload.country or "").strip().upper() or None,
        currency=payload.currency.strip().upper(),
        headline_reward=payload.headline_reward,
        deadline_days=payload.deadline_days,
        observed_at=observed_at,
        source_kind="first_party_app_observation",
        source_note=(payload.source_note or "").strip() or None,
        review_status="verified_manual",
    )
    session.add(row)
    session.flush()

    milestone_rows: list[OfferSnapshotMilestone] = []
    for item in payload.milestones:
        milestone = OfferSnapshotMilestone(snapshot_id=row.id, **item.model_dump())
        session.add(milestone)
        milestone_rows.append(milestone)

    if payload.screenshot_id is not None:
        screenshot = session.get(ResearchScreenshot, payload.screenshot_id)
        if screenshot:
            screenshot.extraction_status = "verified_manual"

    session.commit()
    session.refresh(row)
    for milestone in milestone_rows:
        session.refresh(milestone)
    return _serialize_snapshot(row, milestone_rows)


@router.get("/snapshots")
def list_snapshots(admin: AdminUserDep, session: SessionDep):
    rows = session.scalars(select(OfferSnapshot).order_by(OfferSnapshot.observed_at.desc()).limit(300)).all()
    items = []
    for row in rows:
        milestones = session.scalars(
            select(OfferSnapshotMilestone).where(OfferSnapshotMilestone.snapshot_id == row.id)
        ).all()
        items.append(_serialize_snapshot(row, milestones))
    return {"items": items}
