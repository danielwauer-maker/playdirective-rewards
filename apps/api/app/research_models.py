from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models import utcnow


class ResearchScreenshot(Base):
    __tablename__ = "research_screenshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(80))
    byte_size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    storage_path: Mapped[str] = mapped_column(String(500))
    extraction_status: Mapped[str] = mapped_column(String(32), default="manual_review_required")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OfferSnapshot(Base):
    __tablename__ = "offer_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    imported_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    screenshot_id: Mapped[int | None] = mapped_column(ForeignKey("research_screenshots.id"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    game_name: Mapped[str] = mapped_column(String(220), index=True)
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    headline_reward: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    deadline_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_kind: Mapped[str] = mapped_column(String(40), default="first_party_app_observation")
    source_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(String(24), default="verified_manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OfferSnapshotMilestone(Base):
    __tablename__ = "offer_snapshot_milestones"
    __table_args__ = (UniqueConstraint("snapshot_id", "position", name="uq_snapshot_milestone_position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("offer_snapshots.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(260))
    reward: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    milestone_type: Mapped[str] = mapped_column(String(32), default="progress")
    purchase_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
