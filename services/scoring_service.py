"""
services/scoring_service.py
Orchestrates lead scoring. Holds a swappable Strategy — no DB access here.
"""

from models.lead import Lead
from strategies.base_scoring_strategy import BaseScoringStrategy
from strategies.basic_scoring_strategy import BasicScoringStrategy


class ScoringService:
    """
    Strategy Pattern: the scoring algorithm is injected and can be
    swapped at runtime without changing any other code.
    """

    def __init__(self, strategy: BaseScoringStrategy | None = None):
        self._strategy = strategy or BasicScoringStrategy()

    def set_strategy(self, strategy: BaseScoringStrategy) -> None:
        self._strategy = strategy

    def score(self, lead: Lead) -> float:
        return self._strategy.score(lead)
