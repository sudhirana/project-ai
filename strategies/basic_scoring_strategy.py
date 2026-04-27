"""
strategies/basic_scoring_strategy.py
Strategy Pattern: Simple equal-weight scoring across all lead attributes.
"""

from models.lead import Lead
from strategies.base_scoring_strategy import BaseScoringStrategy


class BasicScoringStrategy(BaseScoringStrategy):
    """Equal-weight scoring — good for initial triage."""

    def score(self, lead: Lead) -> float:
        score = 0.0

        # Age factor (25–55 is sweet spot)
        if 25 <= lead.age <= 55:
            score += 20
        elif lead.age > 55:
            score += 10

        # Income factor
        if lead.income >= 80000:
            score += 20
        elif lead.income >= 40000:
            score += 12
        else:
            score += 5

        # Coverage amount
        if lead.coverage_amount >= 500_000:
            score += 20
        elif lead.coverage_amount >= 100_000:
            score += 12
        else:
            score += 5

        # Lead source
        source_scores = {
            "REFERRAL": 20, "AGENT": 18, "WEBSITE": 12,
            "SOCIAL_MEDIA": 8, "COLD_CALL": 5,
        }
        score += source_scores.get(lead.lead_source.upper(), 5)

        # Prior insurance
        if lead.prior_insurance:
            score += 20

        return min(round(score, 2), 100.0)
