# MVP Architecture

## Goal

Build the smallest system that can turn a rewarded-game offer into a trustworthy user decision while creating a first-party outcome-data flywheel.

The architecture should support Freecash first without coupling the domain model to Freecash.

## Recommended MVP shape

```text
Web / Mobile Web UI
        |
        v
Application API
        |
        +--> Offer ingestion / extraction
        +--> Game intelligence service
        +--> Decision engine
        +--> Outcome tracking
        |
        v
Relational database
        |
        +--> Offers + milestones
        +--> Canonical games + progression
        +--> Evidence + estimates
        +--> User tracked offers + outcomes
```

## Suggested stack

This is a recommendation, not yet a hard dependency.

### Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS

Reasons:

- fast SEO-friendly product pages
- good server/client rendering options
- straightforward image/screenshot upload flow
- suitable for both public game pages and authenticated dashboards

### Backend

For MVP, keep backend logic in the same TypeScript codebase where practical.

- Next.js server routes / server actions or a thin API layer
- domain services kept framework-independent
- background jobs only when actually needed

Avoid premature microservices.

### Database

- PostgreSQL
- ORM: Prisma or Drizzle

PostgreSQL fits the strongly relational domain while still allowing JSON metadata for provider-specific details.

### Object storage

Needed for user-submitted offer screenshots.

Use an S3-compatible store or managed equivalent.

Store derived extraction results separately from the raw image so screenshots can later be deleted according to retention policy without losing normalized offer records when appropriate.

### Authentication

Use a managed auth solution or provider already used by the wider PlayDirective ecosystem if one exists.

Anonymous analyses should be possible before sign-in to reduce activation friction.

## Domain modules

Recommended code boundaries:

```text
src/
  domain/
    games/
    providers/
    offers/
    progression/
    evidence/
    scoring/
    tracking/
  application/
    analyze-offer/
    track-offer/
    record-outcome/
  infrastructure/
    db/
    storage/
    extraction/
  app/
    ... UI routes ...
```

## Offer ingestion pipeline

### MVP inputs

1. Screenshot
2. Pasted text
3. Manual fields

### Normalization pipeline

```text
raw input
  -> extraction
  -> game resolution
  -> provider resolution
  -> milestone parsing
  -> validation
  -> normalized offer observation
  -> analysis
```

Every extracted field should carry confidence where useful.

If game identity or a milestone is ambiguous, ask the user to confirm rather than silently inventing a mapping.

## Screenshot extraction

The extraction layer should return a structured draft, for example:

```ts
type ExtractedOfferDraft = {
  provider?: { value: string; confidence: number }
  gameTitle?: { value: string; confidence: number }
  platform?: { value: string; confidence: number }
  deadlineDays?: { value: number; confidence: number }
  advertisedReward?: { value: number; currency: string; confidence: number }
  milestones: Array<{
    requirement: string
    reward: number
    currency: string
    confidence: number
  }>
}
```

Do not write extraction output directly into canonical tables without validation/normalization.

## Decision engine

Keep the scoring engine as a pure domain service with explicit inputs and outputs.

```ts
type AnalyzeOfferInput = {
  offer: OfferWithMilestones
  estimates: MilestoneEstimate[]
  userPreferences?: DecisionPreferences
}

type AnalyzeOfferOutput = {
  score: number
  verdict: 'start' | 'start_then_stop' | 'maybe' | 'skip'
  recommendedStopMilestoneId?: string
  expectedReward: number
  expectedSpend: number
  expectedNetReward: number
  expectedActiveMinutes: number
  expectedHourlyRate: number
  confidence: number
  reasons: DecisionReason[]
  milestoneDecisions: MilestoneDecision[]
}
```

The engine should be deterministic for the same inputs and scoring version.

## Evidence pipeline

MVP evidence can come from:

- editorial/manual research
- structured community reports
- first-party user outcomes
- derived estimates

Each evidence item should preserve source type, timestamp and confidence.

Do not collapse all evidence into one number without keeping provenance.

## Outcome data flywheel

After a user starts an offer:

1. Save start time and deadline.
2. Ask for lightweight milestone updates.
3. Record time/spend where possible.
4. Ask whether reward tracking succeeded.
5. Compare realized outcome with the prediction.
6. Recalculate aggregated milestone estimates.

The UX must make this inexpensive; otherwise users will not report data.

A simple update might be:

```text
Reached Level 20?
[ Yes ] [ Not yet ] [ Stopped ]

Spent money since last update?
[ €0 ] [ Enter amount ]
```

## Public pages and SEO

Recommended initial public routes:

```text
/
/analyze
/games/[gameSlug]
/games/[gameSlug]/offers/[providerSlug]
/providers/[providerSlug]
```

Later:

```text
/compare/[gameSlug]
/best-offers
/best-offers/[country]
```

Public pages should clearly distinguish:

- current observed offer data
- historical data
- game progression intelligence
- estimates vs verified observations

## Internal/admin tooling

An internal editor is valuable very early.

Minimum admin functions:

- create/edit canonical games
- define progression nodes
- map raw milestone wording to progression nodes
- add editorial evidence
- inspect low-confidence screenshot extractions
- merge duplicate game identities
- review suspicious outcome reports

Without this tooling, data cleanup will become the bottleneck.

## API boundaries — candidate endpoints

```text
POST /api/offers/extract
POST /api/offers/analyze
POST /api/user-offers
POST /api/user-offers/:id/outcomes
GET  /api/games/:slug
GET  /api/games/:slug/offers
```

Exact routing can change with the chosen framework.

## Data safety and abuse considerations

- Rate-limit anonymous extraction endpoints.
- Validate image type and size.
- Do not execute or trust arbitrary uploaded content.
- Do not encourage gameplay automation or platform-rule circumvention.
- Build moderation/quality controls for crowdsourced outcomes.
- Minimize retention of screenshots and personal data.

## Provider integration principle

Do not make unauthorized scraping a runtime dependency.

Preferred ingestion hierarchy:

1. official/partner API
2. user-submitted offer data
3. permitted public API/feed
4. manual editorial observation

If a provider partnership becomes available, add an adapter implementing the same normalized provider interface.

```ts
interface OfferProviderAdapter {
  providerId: string
  fetchOffers?(context: ProviderContext): Promise<NormalizedOfferDraft[]>
  resolveOffer?(externalId: string): Promise<NormalizedOfferDraft | null>
}
```

## MVP release slices

### Slice 1 — analyst prototype

- canonical game records
- manual offer entry
- manual milestone estimates
- deterministic score
- analysis result page

### Slice 2 — user-facing analyzer

- screenshot/paste input
- extraction confirmation
- anonymous analysis
- public game pages

### Slice 3 — tracking flywheel

- accounts
- start/track offer
- deadline reminders
- milestone outcome reporting
- prediction vs actual comparison

### Slice 4 — intelligence expansion

- aggregated community completion stats
- better segmentation
- historical offers
- cross-provider comparison

## What not to build yet

- Microservices
- Real-time streaming infrastructure
- Complex ML recommendation systems
- Native apps before web validation
- Full marketplace ingestion
- Broad social/community features

The MVP should prove one thing first:

> Users trust PlayDirective enough to consult it before committing time or money to a rewarded-game offer.
