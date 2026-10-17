from datetime import UTC, datetime

import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from app.config import get_settings
from app.models import CreditLedgerEntry, Referral, StripeWebhookEvent, Subscription, User
from app.security import SessionDep, UserDep

router = APIRouter(prefix="/v1/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan_id: str


def _configure_stripe() -> None:
    key = get_settings().stripe_secret_key
    if not key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    stripe.api_key = key


def _price_for_plan(plan_id: str) -> str:
    settings = get_settings()
    mapping = {"pro": settings.stripe_price_pro, "max": settings.stripe_price_max}
    price = mapping.get(plan_id)
    if not price:
        raise HTTPException(status_code=422, detail="Unknown or unconfigured plan")
    return price


def _subscription(session: SessionDep, user_id: int) -> Subscription:
    row = session.scalar(select(Subscription).where(Subscription.user_id == user_id))
    if not row:
        row = Subscription(user_id=user_id, plan_id="free", status="free")
        session.add(row)
        session.flush()
    return row


@router.get("/status")
def billing_status(user: UserDep, session: SessionDep):
    row = _subscription(session, user.id)
    return {
        "plan_id": row.plan_id,
        "status": row.status,
        "current_period_end": row.current_period_end,
        "cancel_at_period_end": row.cancel_at_period_end,
        "stripe_customer": bool(row.stripe_customer_id),
    }


@router.post("/checkout")
def create_checkout(payload: CheckoutRequest, user: UserDep, session: SessionDep):
    _configure_stripe()
    settings = get_settings()
    price_id = _price_for_plan(payload.plan_id)
    sub = _subscription(session, user.id)

    customer_id = sub.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"playdirective_user_id": str(user.id)})
        customer_id = customer.id
        sub.stripe_customer_id = customer_id
        session.commit()

    checkout = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.public_origin}/app?billing=success",
        cancel_url=f"{settings.public_origin}/pricing?billing=cancelled",
        allow_promotion_codes=True,
        subscription_data={"metadata": {"playdirective_user_id": str(user.id), "plan_id": payload.plan_id}},
        metadata={"playdirective_user_id": str(user.id), "plan_id": payload.plan_id},
    )
    return {"url": checkout.url}


@router.post("/portal")
def create_portal(user: UserDep, session: SessionDep):
    _configure_stripe()
    settings = get_settings()
    sub = _subscription(session, user.id)
    if not sub.stripe_customer_id:
        raise HTTPException(status_code=409, detail="No Stripe customer exists yet")
    portal = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{settings.public_origin}/app/billing",
    )
    return {"url": portal.url}


def _reward_referrer_if_qualified(session: SessionDep, referred_user: User, invoice_id: str, amount_paid: int) -> None:
    settings = get_settings()
    if amount_paid < settings.referral_min_payment_cents:
        return
    referral = session.scalar(select(Referral).where(Referral.referred_user_id == referred_user.id))
    if not referral or referral.status == "rewarded":
        return

    referral.status = "rewarded"
    referral.qualified_at = referral.qualified_at or datetime.now(UTC)
    referral.rewarded_at = datetime.now(UTC)
    session.add(CreditLedgerEntry(
        user_id=referral.referrer_user_id,
        amount_cents=settings.referral_reward_cents,
        currency="EUR",
        entry_type="credit",
        source_type="referral_invoice",
        source_id=invoice_id,
        description=f"Referral reward for user #{referred_user.id}",
    ))

    referrer_sub = session.scalar(select(Subscription).where(Subscription.user_id == referral.referrer_user_id))
    if referrer_sub and referrer_sub.stripe_customer_id and settings.stripe_secret_key:
        try:
            stripe.api_key = settings.stripe_secret_key
            stripe.Customer.create_balance_transaction(
                referrer_sub.stripe_customer_id,
                amount=-settings.referral_reward_cents,
                currency=settings.stripe_currency,
                description="PlayDirective referral credit",
            )
            session.add(CreditLedgerEntry(
                user_id=referral.referrer_user_id,
                amount_cents=-settings.referral_reward_cents,
                currency="EUR",
                entry_type="applied_to_stripe",
                source_type="referral_invoice",
                source_id=f"{invoice_id}:stripe",
                description="Referral credit transferred to Stripe customer balance",
            ))
        except Exception:
            # Preserve internal credit if the Stripe customer-balance transfer is unavailable.
            pass


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None, alias="stripe-signature")):
    settings = get_settings()
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    if settings.stripe_secret_key:
        stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook") from exc

    from app.db import SessionLocal
    session = SessionLocal()
    try:
        if session.scalar(select(StripeWebhookEvent.id).where(StripeWebhookEvent.stripe_event_id == event["id"])):
            return {"received": True, "duplicate": True}
        session.add(StripeWebhookEvent(stripe_event_id=event["id"], event_type=event["type"]))

        obj = event["data"]["object"]
        event_type = event["type"]

        if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
            customer_id = obj.get("customer")
            sub = session.scalar(select(Subscription).where(Subscription.stripe_customer_id == customer_id))
            if sub:
                metadata = obj.get("metadata") or {}
                sub.stripe_subscription_id = obj.get("id")
                sub.plan_id = metadata.get("plan_id") or sub.plan_id
                sub.status = obj.get("status") or sub.status
                sub.cancel_at_period_end = bool(obj.get("cancel_at_period_end"))
                period_end = obj.get("current_period_end")
                sub.current_period_end = datetime.fromtimestamp(period_end, tz=UTC) if period_end else None

        if event_type == "checkout.session.completed":
            customer_id = obj.get("customer")
            metadata = obj.get("metadata") or {}
            user_id = metadata.get("playdirective_user_id")
            if user_id:
                sub = _subscription(session, int(user_id))
                sub.stripe_customer_id = customer_id or sub.stripe_customer_id
                sub.stripe_subscription_id = obj.get("subscription") or sub.stripe_subscription_id
                sub.plan_id = metadata.get("plan_id") or sub.plan_id
                sub.status = "active"

        if event_type == "invoice.paid":
            customer_id = obj.get("customer")
            sub = session.scalar(select(Subscription).where(Subscription.stripe_customer_id == customer_id))
            if sub:
                user = session.get(User, sub.user_id)
                if user:
                    _reward_referrer_if_qualified(session, user, obj.get("id", event["id"]), int(obj.get("amount_paid") or 0))

        session.commit()
        return {"received": True}
    finally:
        session.close()
