# PlayDirective Rewards

Decision intelligence for rewarded gaming.

PlayDirective Rewards helps users decide which rewarded-game offers are actually worth their time. Instead of ranking offers by headline payout alone, the product estimates realistic earnings, active playtime, spending requirements, completion probability, tracking risk, and the best milestone at which to stop.

## Core promise

> Don't chase the biggest reward. Play the offer with the best expected outcome.

## Initial beachhead

The MVP starts with Freecash offers, but the product is intentionally platform-independent. The long-term goal is to compare rewarded-game offers across multiple providers and recommend the best option for each user.

## MVP flow

1. User submits an offer manually or from a screenshot.
2. PlayDirective identifies the game, platform, deadline, total reward and milestones.
3. The system enriches the offer with game progression intelligence and community outcome data.
4. Each milestone receives an expected-value assessment.
5. The user gets a clear verdict: **START**, **SKIP**, or **STOP AT MILESTONE X**.

## Primary outputs

- PD Offer Score (0–100)
- Expected achievable reward
- Expected net reward after spend
- Estimated active playtime
- Effective earnings per hour
- Completion probability per milestone
- Required / optional in-app spend
- Deadline risk
- Tracking confidence
- Recommended stopping point

## Repository map

```text
.
├── README.md
├── docs/
│   ├── PRODUCT.md
│   ├── DATA_MODEL.md
│   ├── PD_SCORE.md
│   └── MVP_ARCHITECTURE.md
└── .gitignore
```

## Product principles

1. **User-aligned:** optimize for the user's expected net outcome, not advertiser payout.
2. **Explainable:** every score should be decomposable into understandable factors.
3. **Milestone-first:** an offer can be good up to a point and bad afterwards.
4. **Evidence-weighted:** distinguish verified outcome data, community estimates and model estimates.
5. **Platform-independent:** Freecash is the first provider, not the architecture.
6. **No unauthorized scraping dependency:** the MVP must work without systematic automated copying of provider websites.

## Current status

Foundation / product design phase.

See the `/docs` directory for the initial product specification, data model, scoring framework and MVP architecture.
