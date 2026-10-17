from decimal import Decimal

from app.domain.scoring import analyze_milestones


def test_scoring_returns_actionable_result():
    result = analyze_milestones([
        {
            "position": 1,
            "reward": Decimal("10"),
            "estimated_hours": Decimal("1"),
            "estimated_spend": Decimal("0"),
            "completion_probability": Decimal("0.95"),
            "tracking_confidence": Decimal("0.95"),
        },
        {
            "position": 2,
            "reward": Decimal("20"),
            "estimated_hours": Decimal("3"),
            "estimated_spend": Decimal("2"),
            "completion_probability": Decimal("0.75"),
            "tracking_confidence": Decimal("0.9"),
        },
    ])
    assert 0 <= result["pd_score"] <= 100
    assert result["verdict"] in {"START", "CAUTION", "SKIP"}
    assert result["recommended_stop_position"] in {1, 2}
    assert result["expected_reward"] > 0


def test_high_cost_low_probability_offer_scores_worse():
    strong = analyze_milestones([{"position": 1, "reward": 30, "estimated_hours": 2, "estimated_spend": 0, "completion_probability": .95, "tracking_confidence": .95}])
    weak = analyze_milestones([{"position": 1, "reward": 30, "estimated_hours": 15, "estimated_spend": 20, "completion_probability": .3, "tracking_confidence": .6}])
    assert strong["pd_score"] > weak["pd_score"]
