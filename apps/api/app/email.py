import httpx

from app.config import get_settings


async def send_email(to: str, subject: str, html: str) -> None:
    settings = get_settings()
    if not settings.resend_api_key:
        if settings.environment == "development":
            print(f"[DEV EMAIL] to={to} subject={subject}\n{html}")
            return
        raise RuntimeError("RESEND_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"},
            json={"from": settings.resend_from_email, "to": [to], "subject": subject, "html": html},
        )
        response.raise_for_status()
