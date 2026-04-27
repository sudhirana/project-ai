"""
factories/lead_factory.py
Factory Pattern: Centralises creation of different lead types.
Callers never instantiate Lead directly — they ask the factory.
"""

import uuid
from datetime import datetime

from models.lead import Lead, LeadType


class AutoInsuranceLead(Lead):
    """Auto insurance specialisation (can carry extra attributes if needed)."""
    pass


class HealthInsuranceLead(Lead):
    pass


class LifeInsuranceLead(Lead):
    pass


class HomeInsuranceLead(Lead):
    pass


# Maps string keys to concrete classes
_LEAD_TYPE_MAP: dict[str, type[Lead]] = {
    LeadType.AUTO:   AutoInsuranceLead,
    LeadType.HEALTH: HealthInsuranceLead,
    LeadType.LIFE:   LifeInsuranceLead,
    LeadType.HOME:   HomeInsuranceLead,
}


class LeadFactory:
    """
    Factory Pattern: creates the correct Lead subclass based on lead_type.
    Add new lead types here without touching any other module.
    """

    @staticmethod
    def create(
        lead_type: str,
        first_name: str,
        last_name: str,
        email: str,
        **kwargs,
    ) -> Lead:
        lead_type_enum = LeadType(lead_type.upper())
        cls = _LEAD_TYPE_MAP.get(lead_type_enum, Lead)

        return cls(
            id=kwargs.pop("id", str(uuid.uuid4())),
            lead_type=lead_type_enum,
            first_name=first_name,
            last_name=last_name,
            email=email,
            created_at=kwargs.pop("created_at", datetime.now().isoformat()),
            updated_at=kwargs.pop("updated_at", datetime.now().isoformat()),
            **kwargs,
        )
