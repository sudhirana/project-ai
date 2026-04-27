"""
models/agent.py
Agent dataclass model.
"""

from dataclasses import dataclass, field


@dataclass
class Agent:
    """Represents an insurance agent."""
    id: str
    name: str
    email: str
    phone: str = ""
    max_capacity: int = 10
    current_load: int = 0
    is_active: bool = True

    @property
    def is_available(self) -> bool:
        return self.is_active and self.current_load < self.max_capacity

    @property
    def utilisation_pct(self) -> float:
        if self.max_capacity == 0:
            return 0.0
        return round((self.current_load / self.max_capacity) * 100, 1)
