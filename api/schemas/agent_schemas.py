"""
api/schemas/agent_schemas.py
Pydantic models for Agent API requests and responses.
"""

from pydantic import BaseModel, Field


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3)
    phone: str = ""
    max_capacity: int = Field(10, ge=1, le=100)

    model_config = {"json_schema_extra": {"example": {
        "name": "Sarah Mitchell",
        "email": "sarah@insure.com",
        "phone": "07700111001",
        "max_capacity": 10
    }}}


class AgentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    max_capacity: int
    current_load: int
    is_active: bool
    is_available: bool
    utilisation_pct: float

    model_config = {"from_attributes": True}
