# Initial Data Model

This model is intentionally provider-independent. Freecash is represented as one provider implementation, not as a special case in the domain model.

## Core entities

### User

```ts
type User = {
  id: string
  countryCode?: string
  preferredCurrency?: string
  devicePlatforms?: ('ios' | 'android')[]
  dailyMinutesAvailable?: number
  maxSpendPerOffer?: number
  minimumHourlyRate?: number
  createdAt: Date
  updatedAt: Date
}
```

### Provider

A rewarded-gaming platform or offerwall.

```ts
type Provider = {
  id: string
  slug: string
  name: string
  websiteUrl?: string
  status: 'active' | 'inactive'
  dataAccessMode: 'manual' | 'user_submitted' | 'partner_api' | 'public_api'
  createdAt: Date
  updatedAt: Date
}
```

Examples: Freecash, Swagbucks, RewardXP.

### Game

Canonical game identity independent of any reward platform.

```ts
type Game = {
  id: string
  slug: string
  title: string
  publisher?: string
  genre?: string
  supportedPlatforms: ('ios' | 'android' | 'web' | 'pc')[]
  appStoreId?: string
  googlePlayId?: string
  imageUrl?: string
  createdAt: Date
  updatedAt: Date
}
```

### ProgressionNode

Canonical progression step in a game. This allows provider milestones to map to one normalized game progression model.

```ts
type ProgressionNode = {
  id: string
  gameId: string
  key: string
  label: string
  sequence?: number
  nodeType: 'level' | 'building' | 'chapter' | 'board' | 'power' | 'purchase' | 'custom'
  targetValue?: number | string
  prerequisites?: string[]
}
```

Examples:

- Headquarters Level 20
- Board 70
- Player Level 25
- Make a $4.99 purchase

### Offer

A specific rewarded offer as observed at a point in time.

```ts
type Offer = {
  id: string
  providerId: string
  gameId: string
  countryCode: string
  platform: 'ios' | 'android' | 'web' | 'pc'
  advertisedRewardAmount: number
  currency: string
  deadlineDays?: number
  observedAt: Date
  sourceType: 'user_screenshot' | 'manual' | 'pasted_text' | 'partner_api' | 'public_api'
  sourceConfidence: number // 0..1
  status: 'active' | 'expired' | 'unknown'
}
```

Important: an Offer is versioned by observation. If payout or terms change, create a new observation/version rather than overwriting history.

### OfferMilestone

A provider-specific reward condition mapped, where possible, to a canonical progression node.

```ts
type OfferMilestone = {
  id: string
  offerId: string
  progressionNodeId?: string
  sequence: number
  rawRequirement: string
  rewardAmount: number
  currency: string
  milestoneType: 'progression' | 'purchase' | 'install' | 'login' | 'custom'
  relativeDeadlineDays?: number
}
```

## Intelligence entities

### MilestoneEstimate

Current model estimate for reaching a canonical progression node or provider milestone.

```ts
type MilestoneEstimate = {
  id: string
  gameId: string
  progressionNodeId?: string
  offerMilestoneId?: string
  segmentKey: string
  estimatedActiveMinutes: number
  estimatedCalendarDays: number
  estimatedRequiredSpend: number
  estimatedOptionalSpend: number
  completionProbability: number
  deadlineSuccessProbability?: number
  trackingSuccessProbability?: number
  confidence: number
  evidenceCount: number
  modelVersion: string
  calculatedAt: Date
}
```

`segmentKey` can initially be broad, for example `global:android:no-spend`, and become more granular as data volume grows.

### UserOffer

An offer the user has decided to track.

```ts
type UserOffer = {
  id: string
  userId: string
  offerId: string
  startedAt?: Date
  deadlineAt?: Date
  status: 'considering' | 'started' | 'completed' | 'stopped' | 'expired'
  actualSpend: number
  actualReward: number
  recommendedStopMilestoneId?: string
  createdAt: Date
  updatedAt: Date
}
```

### MilestoneOutcome

The primary first-party data flywheel.

```ts
type MilestoneOutcome = {
  id: string
  userOfferId: string
  offerMilestoneId: string
  status: 'reached' | 'failed' | 'skipped'
  reachedAt?: Date
  activeMinutesReported?: number
  incrementalSpend?: number
  rewardTracked?: boolean
  rewardReceived?: boolean
  source: 'user_report' | 'verified_integration'
  createdAt: Date
}
```

### OfferAnalysis

Snapshot of the decision shown to the user.

```ts
type OfferAnalysis = {
  id: string
  offerId: string
  userId?: string
  score: number
  verdict: 'start' | 'start_then_stop' | 'maybe' | 'skip'
  expectedAchievableReward: number
  expectedNetReward: number
  expectedActiveMinutes: number
  expectedSpend: number
  expectedHourlyRate: number
  recommendedStopMilestoneId?: string
  confidence: number
  scoringVersion: string
  createdAt: Date
}
```

## Evidence model

Every estimate should ultimately be traceable to evidence.

### EvidenceObservation

```ts
type EvidenceObservation = {
  id: string
  gameId: string
  progressionNodeId?: string
  observationType:
    | 'completion_time'
    | 'spend'
    | 'completion'
    | 'tracking'
    | 'strategy'
    | 'deadline'
  numericValue?: number
  booleanValue?: boolean
  textValue?: string
  sourceType: 'first_party_outcome' | 'community_report' | 'editorial_research' | 'model_estimate'
  sourceReference?: string
  confidence: number
  countryCode?: string
  platform?: string
  observedAt: Date
}
```

## Important modeling rules

### 1. Separate game truth from offer terms

Game progression belongs to `Game` / `ProgressionNode`. Rewards and deadlines belong to `Offer` / `OfferMilestone`.

### 2. Never overwrite historical offer terms

Reward offers change frequently. Preserve observations so PlayDirective can later show reward history and compare offer quality over time.

### 3. Estimate incremental effort, not only total effort

The decision engine needs to know whether going from milestone 5 to milestone 6 is worth it. Store or derive incremental time and spend between milestones.

### 4. Store uncertainty explicitly

Every derived estimate should have a confidence value and evidence count. A precise-looking number based on weak evidence is worse than an honest range.

### 5. Avoid provider-specific columns

Provider-specific metadata that cannot be normalized should go into a namespaced metadata JSON field later rather than polluting the main schema.

## Likely relational tables for MVP

```text
users
providers
games
progression_nodes
offers
offer_milestones
milestone_estimates
user_offers
milestone_outcomes
offer_analyses
evidence_observations
```

## Post-MVP additions

- Offer equivalence groups across providers
- Strategy variants
- Screenshot extraction audit trail
- Reward history aggregation
- Fraud/quality signals for user-submitted outcomes
- Game version / balance-change tracking
- Publisher and developer identities
- Provider tracking-incident records
