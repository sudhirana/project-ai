"""
strategies/base_scoring_strategy.py
Strategy Pattern: Abstract interface all scoring strategies must implement.
"""

from abc import ABC, abstractmethod
from models.lead import Lead


class BaseScoringStrategy(ABC):
    """Strategy Pattern: defines the scoring contract."""

    @abstractmethod
    def score(self, lead: Lead) -> float:
        """Return a score between 0 and 100."""
        ...
