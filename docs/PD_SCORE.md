# PD Offer Score

The PD Offer Score is an explainable 0–100 score representing how attractive a rewarded-game offer is for a specific user or default user segment.

It is not a simple payout ranking.

## Core idea

An offer is good when it provides strong expected net value for the time, money and risk required.

At a high level:

```text
Expected Value =
  achievable reward
  - expected spend
  - risk-adjusted loss from failure / non-tracking

Decision Quality =
  Expected Value
  relative to active time, deadline pressure and uncertainty
```

## Score components

Recommended initial weighting:

| Component | Weight |
|---|---:|
| Expected hourly value | 30% |
| Completion probability | 20% |
| Net reward quality | 15% |
| Spend efficiency | 10% |
| Deadline feasibility | 10% |
| Tracking reliability | 10% |
| Evidence confidence | 5% |

Weights should remain versioned and tunable.

## Component definitions

### 1. Expected hourly value

Measures risk-adjusted expected net reward per active hour.

```text
expected_net_reward =
  Σ(milestone_reward × milestone_success_probability × tracking_probability)
  - expected_spend

expected_hourly_value = expected_net_reward / expected_active_hours
```

Do not assume every advertised milestone should be pursued. Calculate the optimal stopping point first.

### 2. Completion probability

Measures whether the recommended milestone path is realistically achievable for the user's segment.

Inputs may include:

- observed completion rates
- progression curve
- user time availability
- device/platform
- deadline
- required spend

### 3. Net reward quality

Rewards offers that produce meaningful net earnings rather than impressive headline amounts with poor realizability.

### 4. Spend efficiency

Penalizes:

- mandatory purchases
- high expected spend relative to reward
- spend required before uncertain milestones

Optional high-ROI acceleration purchases may be treated differently from effectively mandatory purchases.

### 5. Deadline feasibility

```text
deadline_margin = available_calendar_time - estimated_calendar_time
```

Score should fall sharply when the estimate is close to or beyond the deadline.

### 6. Tracking reliability

Based on observed tracking outcomes by provider, game, device and milestone where evidence exists.

### 7. Evidence confidence

Prevents weakly researched offers from receiving overconfident scores.

Confidence inputs:

- evidence count
- source quality
- recency
- variance between observations
- match quality between evidence and current region/device/offer

## Milestone-level decision model

The core calculation should work incrementally.

For milestone `i`:

```text
incremental_expected_reward_i =
  reward_i × probability_of_reaching_i × tracking_probability_i

incremental_net_value_i =
  incremental_expected_reward_i - incremental_expected_spend_i

incremental_hourly_value_i =
  incremental_net_value_i / incremental_active_hours_i
```

The engine should evaluate every possible stopping point and choose the path with the best user-adjusted utility.

## Recommended stopping point

For ordered milestones `1..n`, calculate a cumulative path for each candidate stop `k`.

```text
utility(k) =
  expected_net_reward(1..k)
  - time_cost(1..k)
  - risk_penalty(1..k)
```

The user-specific time cost can be derived from a minimum acceptable hourly rate when available.

Example:

```text
time_cost = active_hours × user.minimumHourlyRate
```

The recommended stopping milestone is the `k` that maximizes utility while meeting minimum confidence and feasibility requirements.

## Verdict thresholds — initial hypothesis

These are product defaults, not immutable rules.

```text
85–100  EXCELLENT / START
70–84   GOOD / START
55–69   CONDITIONAL / MAYBE
40–54   WEAK / USUALLY SKIP
0–39    POOR / SKIP
```

A separate override can return `START, STOP AT X` when the overall advertised offer is poor but a profitable prefix exists.

## Example

Advertised offer: €300 total.

```text
Milestone 1: +€5,   +0.5h, +€0 spend
Milestone 2: +€15,  +2h,   +€0 spend
Milestone 3: +€35,  +5h,   +€2 spend
Milestone 4: +€70,  +12h,  +€10 spend
Milestone 5: +€175, +40h,  +€50 spend
```

The engine may conclude:

```text
Advertised maximum: €300
Recommended stop: Milestone 3
Expected achievable reward: €49
Expected spend: €1.50
Expected active time: 7.1h
Expected net: €47.50
Expected hourly value: €6.69/h
Verdict: START, STOP AT MILESTONE 3
```

This is the central PlayDirective behavior: optimize the user's outcome, not completion of the full offer.

## Score transparency

The UI should expose the most decision-relevant reasons, not the complete mathematical model.

Example:

```text
PD Score 82 — GOOD

+ Strong € / hour through Level 25
+ No purchase required for recommended path
+ 78% observed completion to Level 25
- Progression slows sharply after Level 25
- Tracking confidence is only medium

Recommended: Stop at Level 25
```

## Versioning

Every analysis should persist:

- `scoringVersion`
- `modelVersion`
- evidence snapshot / timestamp

This lets us compare predictions with realized outcomes and improve the model without rewriting history.

## MVP implementation recommendation

Start deterministic and explainable.

Do not begin with a black-box ML score. Use weighted heuristics and empirical distributions first. Machine learning becomes useful after PlayDirective has accumulated enough first-party milestone outcomes to train and validate against real results.
