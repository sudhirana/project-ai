"""
api/routers/leads.py
FastAPI router for all Lead endpoints.
All business logic delegated to LeadManagementFacade — router is thin.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.schemas.lead_schemas import (
    LeadCreateRequest, LeadResponse,
    LeadStatusUpdateRequest, LeadRescoreRequest
)
from models.lead import LeadStatus
from strategies.basic_scoring_strategy import BasicScoringStrategy
from strategies.scoring_strategies import PremiumScoringStrategy, RiskBasedScoringStrategy

router = APIRouter(prefix="/leads", tags=["Leads"])

_STRATEGY_MAP = {
    "basic":   BasicScoringStrategy,
    "premium": PremiumScoringStrategy,
    "risk":    RiskBasedScoringStrategy,
}


def _lead_to_dict(lead) -> dict:
    return {
        "id": lead.id,
        "lead_type": lead.lead_type.value,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "full_name": lead.full_name,
        "email": lead.email,
        "phone": lead.phone,
        "age": lead.age,
        "income": lead.income,
        "coverage_amount": lead.coverage_amount,
        "lead_source": lead.lead_source,
        "prior_insurance": lead.prior_insurance,
        "status": lead.status.value,
        "score": lead.score,
        "agent_id": lead.agent_id,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
    }


def get_facade():
    from api.app import facade
    return facade


@router.get("/", response_model=list[LeadResponse], summary="List all leads")
def list_leads(status: Optional[str] = Query(None, description="Filter by status")):
    """Return all leads, optionally filtered by status."""
    leads = get_facade().list_leads()
    if status:
        leads = [l for l in leads if l.status.value == status.upper()]
    return [_lead_to_dict(l) for l in leads]


@router.post("/", response_model=LeadResponse, status_code=201, summary="Create a new lead")
def create_lead(body: LeadCreateRequest):
    """Create and score a new insurance lead."""
    facade = get_facade()
    lead = (
        facade.new_lead_builder()
        .of_type(body.lead_type.value)
        .for_person(body.first_name, body.last_name, body.email, age=body.age)
        .with_contact(phone=body.phone)
        .with_financials(income=body.income, coverage_amount=body.coverage_amount)
        .from_source(body.lead_source)
        .with_prior_insurance(body.prior_insurance)
        .build()
    )
    result = facade.submit_lead(lead)
    return _lead_to_dict(result)


@router.get("/{lead_id}", response_model=LeadResponse, summary="Get a lead by ID")
def get_lead(lead_id: str):
    lead = get_facade().get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    return _lead_to_dict(lead)


@router.post("/{lead_id}/assign", response_model=dict, summary="Assign lead to an agent")
def assign_lead(lead_id: str):
    """Assign a lead to the next available agent using round-robin."""
    lead = get_facade().get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    agent = get_facade().assign_lead(lead_id)
    if not agent:
        raise HTTPException(status_code=409, detail="No available agents")
    return {"message": f"Lead assigned to {agent.name}", "agent_id": agent.id}


@router.patch("/{lead_id}/status", response_model=LeadResponse, summary="Update lead status")
def update_status(lead_id: str, body: LeadStatusUpdateRequest):
    """Transition a lead's status through the state machine."""
    try:
        lead = get_facade().update_lead_status(lead_id, body.new_status)
        return _lead_to_dict(lead)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{lead_id}/rescore", response_model=LeadResponse, summary="Re-score a lead")
def rescore_lead(lead_id: str, body: LeadRescoreRequest):
    """Re-score a lead using a different scoring strategy at runtime."""
    strategy = _STRATEGY_MAP[body.strategy]()
    try:
        lead = get_facade().rescore_lead(lead_id, strategy)
        return _lead_to_dict(lead)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{lead_id}", status_code=204, summary="Delete a lead")
def delete_lead(lead_id: str):
    facade = get_facade()
    lead = facade.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    facade._lead_repo.delete(lead_id)
