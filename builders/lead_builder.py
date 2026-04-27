"""
builders/lead_builder.py
Builder Pattern: Fluent interface for constructing complex Lead objects
step-by-step with method chaining. Delegates creation to LeadFactory.
"""

from factories.lead_factory import LeadFactory
from models.lead import Lead


class LeadBuilder:
    """
    Builder Pattern: construct a Lead via a readable, fluent chain.
    Example:
        lead = (LeadBuilder()
                .of_type("AUTO")
                .for_person("Jane", "Doe", "jane@example.com")
                .with_contact(phone="07700900000")
                .with_financials(income=55000, coverage_amount=25000)
                .from_source("REFERRAL")
                .with_prior_insurance(True)
                .build())
    """

    def __init__(self):
        self._data: dict = {}

    def of_type(self, lead_type: str) -> "LeadBuilder":
        self._data["lead_type"] = lead_type
        return self

    def for_person(
        self, first_name: str, last_name: str, email: str, age: int = 0
    ) -> "LeadBuilder":
        self._data.update(
            first_name=first_name, last_name=last_name,
            email=email, age=age,
        )
        return self

    def with_contact(self, phone: str = "") -> "LeadBuilder":
        self._data["phone"] = phone
        return self

    def with_financials(
        self, income: float = 0.0, coverage_amount: float = 0.0
    ) -> "LeadBuilder":
        self._data.update(income=income, coverage_amount=coverage_amount)
        return self

    def from_source(self, lead_source: str) -> "LeadBuilder":
        self._data["lead_source"] = lead_source
        return self

    def with_prior_insurance(self, has_prior: bool) -> "LeadBuilder":
        self._data["prior_insurance"] = has_prior
        return self

    def build(self) -> Lead:
        required = {"lead_type", "first_name", "last_name", "email"}
        missing = required - self._data.keys()
        if missing:
            raise ValueError(f"LeadBuilder missing required fields: {missing}")

        lead_type = self._data.pop("lead_type")
        first_name = self._data.pop("first_name")
        last_name = self._data.pop("last_name")
        email = self._data.pop("email")

        return LeadFactory.create(
            lead_type=lead_type,
            first_name=first_name,
            last_name=last_name,
            email=email,
            **self._data,
        )
