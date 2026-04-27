"""
models/policy.py
Policy dataclass model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Policy:
    """Represents an insurance policy linked to a converted lead."""
    id: str
    lead_id: str
    policy_type: str
    coverage_amount: float
    premium_amount: float
    start_date: str
    end_date: str
    agent_id: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
