# PlayDirective Rewards

Decision intelligence for rewarded gaming.

PlayDirective Rewards helps users decide which rewarded-game offers are actually worth their time. Instead of ranking offers by headline payout alone, it estimates expected earnings, active playtime, spending requirements, completion probability, tracking confidence and the milestone where a user should stop.

## Current SaaS baseline

The repository now contains a runnable first SaaS rather than only a product specification:

- Next.js 15 + React 19 web application
- FastAPI + SQLAlchemy API
- PostgreSQL 16
- passwordless single-use magic-link authentication
- secure httpOnly browser session through a Next.js BFF
- private per-user offer workspace and analysis history
- manual offer + milestone analyzer
- PD Offer Score and stop-milestone recommendation
- Free / Pro / Max pricing model
- Stripe Checkout, subscription state, Customer Portal and signed webhook handling
- referral attribution, qualification and auditable credit ledger
- referral credit issued only after a qualifying successful payment
- Free-plan entitlement enforcement (5 analyses per month)
- Docker Compose for local and production-style deployment
- nginx reverse-proxy example
- GitHub Actions CI for Python tests and Next.js production builds

## Core promise

> Don't chase the biggest reward. Play the offer with the best expected outcome.

## Initial beachhead

Freecash is the first provider, but the domain model is provider-independent. The product can later compare the same game across Freecash, Swagbucks, RewardXP and other rewarded-gaming platforms.

## Local start

1. Copy `.env.example` to `.env`.
2. For local development without Resend, leave `RESEND_API_KEY` empty. Magic-link emails are printed to the API container logs.
3. Generate a strong `AUTH_SECRET` before exposing the stack anywhere outside localhost.
4. Run:

```bash
docker compose up --build
```

5. Open `http://localhost:3000`.
6. API health: `http://localhost:8000/health`.
7. API readiness: `http://localhost:8000/ready`.

To obtain a local passwordless login link when Resend is disabled:

```bash
docker compose logs -f api
```

## Stripe setup

Create recurring Stripe prices for the launch plans and set:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_PRO`
- `STRIPE_PRICE_MAX`

The initial UI launch prices are €4.99/month for Pro and €9.99/month for Max. Stripe remains the source of truth for the real billed amount.

For local Stripe testing, forward Stripe events to:

```text
http://localhost:8000/v1/billing/webhook
```

For the production nginx example, the public webhook path is:

```text
https://rewards.playdirective.com/api/stripe/webhook
```

Configure at least these Stripe events:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`

## Referral system

Every account receives a unique referral code. A referral is attached only when a new account is created through that code. Self-referrals are rejected and one referred account can have only one referrer.

The launch defaults are configuration-driven:

- qualifying payment threshold: €4.99
- referral credit: €5.00

On a qualifying `invoice.paid` event, PlayDirective writes an immutable-style credit ledger entry. If the referrer already has a Stripe customer, the service also attempts to transfer the credit to the Stripe customer balance. If that external transfer fails, the internal credit remains recorded instead of being lost.

Before a public launch, review the reward amount and fraud policy against actual unit economics.

## Repository map

```text
.
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── domain/scoring.py
│   │   │   ├── routes/auth.py
│   │   │   ├── routes/billing.py
│   │   │   ├── routes/offers.py
│   │   │   └── routes/referrals.py
│   │   ├── tests/
│   │   └── Dockerfile
│   └── web/
│       ├── app/
│       │   ├── app/
│       │   ├── api/
│       │   ├── auth/
│       │   ├── login/
│       │   └── pricing/
│       └── Dockerfile
├── deploy/
│   └── nginx-playdirective-rewards.conf.example
├── docs/
│   ├── PRODUCT.md
│   ├── DATA_MODEL.md
│   ├── PD_SCORE.md
│   └── MVP_ARCHITECTURE.md
├── docker-compose.yml
├── docker-compose.production.yml
└── .github/workflows/ci.yml
```

## Product principles

1. **User-aligned:** optimize for the user's expected net outcome, not advertiser payout.
2. **Explainable:** every score must decompose into understandable factors.
3. **Milestone-first:** an offer can be good up to one milestone and economically bad afterwards.
4. **Evidence-weighted:** distinguish verified outcomes, community estimates and model estimates.
5. **Provider-independent:** Freecash is the first provider, not the architecture.
6. **No unauthorized scraping dependency:** the SaaS must work without systematic automated copying of provider websites.
7. **Auditable money flows:** subscriptions, referral qualification and credits must be event-driven and traceable.

## Production notes

`Base.metadata.create_all()` intentionally keeps the first SaaS easy to boot. Before schema evolution begins in production, introduce Alembic migrations rather than relying on automatic table creation for upgrades.

The nginx example uses localhost ports `8092` for the Rewards web service and `8093` for the Rewards API so it can live next to the existing PlayDirective Roblox deployment without reusing its service ports.

The next product layer is data quality: screenshot ingestion, game identity resolution, shared game intelligence, community outcome logging, evidence weighting and cross-provider comparison. The current application is deliberately structured so those capabilities can be added without replacing auth, billing, workspace or referral infrastructure.
