from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PlayDirective Rewards"
    environment: str = "development"
    public_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://playdirective:playdirective@postgres:5432/playdirective_rewards"

    session_days: int = 30
    magic_link_minutes: int = 20
    auth_secret: str = "change-me-in-production"

    resend_api_key: str | None = None
    resend_from_email: str = "PlayDirective Rewards <noreply@playdirective.com>"

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_pro: str | None = None
    stripe_price_max: str | None = None
    stripe_currency: str = "eur"

    referral_reward_cents: int = 500
    referral_min_payment_cents: int = 499

    admin_email: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
