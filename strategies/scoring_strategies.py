"""
strategies/premium_scoring_strategy.py
Strategy Pattern: Income and coverage-weighted scoring for high-value leads.
"""

from models.lead import Lead
from strategies.base_scoring_strategy import BaseScoringStrategy


class PremiumScoringStrategy(BaseScoringStrategy):
    """Weights income and coverage heavily — targets high-value prospects."""

    def score(self, lead: Lead) -> float:
        score = 0.0

        # Income is king in this strategy (40 pts)
        if lead.income >= 150_000:
            score += 40
        elif lead.income >= 100_000:
            score += 30
        elif lead.income >= 60_000:
            score += 20
        elif lead.income >= 30_000:
            score += 10

        # Coverage amount (35 pts)
        if lead.coverage_amount >= 1_000_000:
            score += 35
        elif lead.coverage_amount >= 500_000:
            score += 25
        elif lead.coverage_amount >= 100_000:
            score += 15
        else:
            score += 5

        # Source quality (15 pts)
        source_scores = {"REFERRAL": 15, "AGENT": 12, "WEBSITE": 8, "SOCIAL_MEDIA": 4}
        score += source_scores.get(lead.lead_source.upper(), 3)

        # Prior insurance (10 pts)
        if lead.prior_insurance:
            score += 10

        return min(round(score, 2), 100.0)


"""
strategies/risk_based_scoring_strategy.py
Strategy Pattern: Risk-adjusted scoring — penalises high-risk profiles.
"""

from models.lead import Lead
from strategies.base_scoring_strategy import BaseScoringStrategy


class RiskBasedScoringStrategy(BaseScoringStrategy):
    """
    Risk-adjusted scoring. High age or no prior insurance reduces score.
    Useful for life/health insurance products.
    """

    def score(self, lead: Lead) -> float:
        score = 50.0  # Start at midpoint, adjust up/down

        # Age risk (penalty for age extremes)
        if lead.age < 25:
            score -= 10
        elif 25 <= lead.age <= 40:
            score += 20
        elif 41 <= lead.age <= 55:
            score += 10
        elif lead.age > 55:
            score -= 15  # Higher risk

        # Income stability
        if lead.income >= 60_000:
            score += 15
        elif lead.income >= 30_000:
            score += 8
        else:
            score -= 10

        # Prior insurance shows responsibility
        if lead.prior_insurance:
            score += 15
        else:
            score -= 10

        # Coverage amount reasonableness
        if 0 < lead.coverage_amount <= 500_000:
            score += 10
        elif lead.coverage_amount > 500_000:
            score += 5  # Very high coverage = higher risk product

        return min(max(round(score, 2), 0.0), 100.0)
