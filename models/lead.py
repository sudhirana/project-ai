"""
models/lead.py
Core Lead dataclass model and LeadStatus state machine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class LeadType(str, Enum):
    AUTO = "AUTO"
    HEALTH = "HEALTH"
    LIFE = "LIFE"
    HOME = "HOME"


# State machine: defines valid transitions
VALID_TRANSITIONS: dict[LeadStatus, list[LeadStatus]] = {
    LeadStatus.NEW:       [LeadStatus.CONTACTED, LeadStatus.LOST],
    LeadStatus.CONTACTED: [LeadStatus.QUALIFIED, LeadStatus.LOST],
    LeadStatus.QUALIFIED: [LeadStatus.CONVERTED, LeadStatus.LOST],
    LeadStatus.CONVERTED: [],
    LeadStatus.LOST:      [],
}


@dataclass
class Lead:
    """Core lead entity."""
    id: str
    lead_type: LeadType
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    age: int = 0
    income: float = 0.0
    coverage_amount: float = 0.0
    lead_source: str = "WEBSITE"
    prior_insurance: bool = False
    status: LeadStatus = LeadStatus.NEW
    score: float = 0.0
    agent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def can_transition_to(self, new_status: LeadStatus) -> bool:
        """State machine validation."""
        return new_status in VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: LeadStatus) -> None:
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition: {self.status} → {new_status}"
            )
        self.status = new_status
        self.updated_at = datetime.now().isoformat()
