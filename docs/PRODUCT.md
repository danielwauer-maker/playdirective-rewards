# Product Concept

## Product name

**PlayDirective Rewards**

## Vision

Become the independent decision layer for rewarded gaming: help users decide which offers to start, how far to play, when to stop, and which platform provides the best expected return.

## User problem

Reward platforms prominently show maximum payouts, but users still have to answer harder questions themselves:

- Is the advertised reward realistically achievable?
- How many active hours are required?
- Is spending money effectively necessary?
- Which milestones are profitable and which are traps?
- Can the deadline realistically be met?
- Does the offer track reliably?
- Is the same game better rewarded elsewhere?

Users currently piece this together from Reddit, YouTube, spreadsheets, guides and trial-and-error.

## Core job to be done

> Before I commit time or money to a rewarded-game offer, tell me whether it is worth starting and where I should stop.

## MVP target user

A user who regularly uses Freecash or similar rewarded-gaming platforms and wants to maximize net earnings while minimizing wasted time and unnecessary in-app purchases.

## Core MVP experience

### 1. Submit an offer

Input methods, in priority order:

1. Screenshot upload
2. Manual form
3. Paste offer text
4. Later: supported partner/API integrations

The system extracts or asks for:

- Provider
- Game
- Country/region
- Device/platform
- Offer start date
- Deadline
- Total advertised reward
- Milestones and individual payouts
- Purchase-specific tasks

### 2. Analyze the offer

For each milestone estimate:

- Active playtime
- Calendar time
- Direct spend
- Optional acceleration spend
- Completion probability
- Deadline probability
- Tracking confidence
- Incremental net reward
- Incremental effective hourly rate

### 3. Give a decision

Top-level verdicts:

- **START** — attractive expected value
- **START, STOP AT X** — early milestones are worthwhile but later ones are not
- **MAYBE** — outcome depends strongly on user profile, spend tolerance or uncertain data
- **SKIP** — poor expected value or excessive risk

### 4. Explain why

The decision must show the most important reasons, for example:

- Strong early milestones
- Sharp progression slowdown after level 25
- Likely purchase requirement
- Low observed completion rate
- High tracking risk
- Better equivalent offer available elsewhere

## Key product surfaces

### Offer Analyzer

The first acquisition and activation surface. User submits an offer and receives a decision.

### Game Intelligence Page

Canonical game page containing progression intelligence independent of any single reward provider.

### Offer Detail Page

Provider-specific offer terms mapped onto the underlying game progression model.

### Milestone Planner

Shows which milestones to pursue and the optimal stopping point.

### My Offers

Tracks offers a user has started, deadlines, completed milestones, spend and realized earnings.

### Offer Comparator — post-MVP

Compares equivalent game offers across providers using expected net value instead of advertised maximum payout.

### Personal Earnings Planner — post-MVP

Optimizes a set of offers for a user's time budget, spend tolerance, device and earnings target.

## Personalization inputs

Useful user-level variables include:

- iOS / Android
- Country
- Daily available time
- Total available days
- Spend tolerance
- Preferred genres
- Existing familiarity with the game
- New-user eligibility
- Desired minimum €/hour

## North-star behavior

The most important behavioral signal is not page views. It is:

> Users repeatedly check PlayDirective before starting or continuing a rewarded-game offer.

## MVP success metrics

### Activation

- % of visitors completing an offer analysis
- % receiving a confident verdict

### Decision value

- % of analyzed offers users choose to start
- % of started offers where users follow the recommended stopping point
- Difference between predicted and realized time/spend/reward

### Retention

- Users analyzing a second offer within 30 days
- Monthly returning decision-makers

### Data flywheel

- % of started offers with at least one outcome update
- Milestone outcome reports per active user
- Games with sufficient verified/community evidence

## Long-term moat

The moat should be the outcome dataset rather than copied offer catalogs.

For each game and milestone, PlayDirective can accumulate observations such as:

- Time to completion
- Spend
- Completion rate
- Drop-off rate
- Deadline success
- Tracking success/failure
- Device and region differences
- Strategy variants

As this dataset grows, predictions become more accurate and increasingly difficult for static guide sites to replicate.

## Monetization hypotheses

### Consumer subscription

Low-cost optional Pro tier for:

- Unlimited analyses
- Personalized thresholds
- Historical reward data
- Cross-provider comparison
- Portfolio planner
- Alerts

### Referral / acquisition revenue

Where provider terms permit, earn referral or acquisition revenue when users choose a platform through PlayDirective.

Important principle: commercial relationships must not silently override the ranking model.

### B2B intelligence — later

Aggregated, privacy-safe outcome intelligence for publishers, offerwalls and user-acquisition teams.

## Non-goals for MVP

- Building a complete reward platform
- Automating gameplay
- Bypassing game or provider restrictions
- Depending on unauthorized provider scraping
- Supporting every provider and every game from day one
- Predicting exact outcomes when evidence is weak

## Initial scope recommendation

Start with approximately 20–30 high-volume rewarded games. Prefer games with repeated appearances across offer platforms and clear progression milestones. Build excellent intelligence for a small catalog before expanding breadth.
