from decimal import Decimal


def analyze_milestones(milestones: list[dict]) -> dict:
    cumulative_expected_reward = Decimal("0")
    cumulative_spend = Decimal("0")
    cumulative_hours = Decimal("0")
    best_value = Decimal("-999999")
    best_position = None
    best_rate = Decimal("0")

    for item in milestones:
        reward = Decimal(str(item.get("reward", 0)))
        probability = Decimal(str(item.get("completion_probability", 0.5)))
        tracking = Decimal(str(item.get("tracking_confidence", 0.8)))
        spend = Decimal(str(item.get("estimated_spend", 0)))
        hours = Decimal(str(item.get("estimated_hours", 0)))

        expected = reward * probability * tracking
        cumulative_expected_reward += expected
        cumulative_spend += spend
        cumulative_hours += hours
        net = cumulative_expected_reward - cumulative_spend
        rate = net / cumulative_hours if cumulative_hours > 0 else net
        utility = net + (rate * Decimal("2"))
        if utility > best_value:
            best_value = utility
            best_position = int(item.get("position", 0))
            best_rate = rate

    risk_penalty = Decimal("0")
    if milestones:
        avg_prob = sum(Decimal(str(x.get("completion_probability", 0.5))) for x in milestones) / Decimal(len(milestones))
        avg_tracking = sum(Decimal(str(x.get("tracking_confidence", 0.8))) for x in milestones) / Decimal(len(milestones))
        risk_penalty = (Decimal("1") - ((avg_prob + avg_tracking) / Decimal("2"))) * Decimal("35")

    base_score = min(Decimal("100"), max(Decimal("0"), Decimal("55") + best_rate * Decimal("8") - risk_penalty))
    score = int(base_score.quantize(Decimal("1")))
    verdict = "START" if score >= 70 else "CAUTION" if score >= 45 else "SKIP"

    return {
        "pd_score": score,
        "verdict": verdict,
        "recommended_stop_position": best_position,
        "expected_reward": cumulative_expected_reward.quantize(Decimal("0.01")),
        "expected_spend": cumulative_spend.quantize(Decimal("0.01")),
        "expected_hours": cumulative_hours.quantize(Decimal("0.01")),
        "effective_hourly_rate": best_rate.quantize(Decimal("0.01")),
        "explanation": "Score combines expected milestone rewards, completion probability, tracking confidence, spend and active playtime. The recommended stop is the point with the strongest estimated utility.",
    }
