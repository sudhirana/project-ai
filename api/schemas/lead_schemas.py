"""
api/schemas/lead_schemas.py
Pydantic models for Lead API request validation and response serialisation.
Kept separate from domain models — API shape can evolve independently.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models.lead import LeadStatus, LeadType


class LeadCreateRequest(BaseModel):
    lead_type: LeadType
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3)
    phone: str = ""
    age: int = Field(0, ge=0, le=120)
    income: float = Field(0.0, ge=0)
    coverage_amount: float = Field(0.0, ge=0)
    lead_source: str = "WEBSITE"
    prior_insurance: bool = False

    model_config = {"json_schema_extra": {"example": {
        "lead_type": "AUTO",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "07700900001",
        "age": 34,
        "income": 55000,
        "coverage_amount": 25000,
        "lead_source": "REFERRAL",
        "prior_insurance": True
    }}}


class LeadStatusUpdateRequest(BaseModel):
    new_status: LeadStatus

    model_config = {"json_schema_extra": {"example": {"new_status": "CONTACTED"}}}


class LeadRescoreRequest(BaseModel):
    strategy: str = Field(..., pattern="^(basic|premium|risk)$")

    model_config = {"json_schema_extra": {"example": {"strategy": "premium"}}}


class LeadResponse(BaseModel):
    id: str
    lead_type: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    age: int
    income: float
    coverage_amount: float
    lead_source: str
    prior_insurance: bool
    status: str
    score: float
    agent_id: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
