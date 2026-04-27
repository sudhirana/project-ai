"""
api/routers/agents.py
FastAPI router for Agent endpoints.
"""

import uuid
from fastapi import APIRouter, HTTPException

from api.schemas.agent_schemas import AgentCreateRequest, AgentResponse
from models.agent import Agent

router = APIRouter(prefix="/agents", tags=["Agents"])


def get_facade():
    from api.app import facade
    return facade


def _agent_to_dict(agent) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "email": agent.email,
        "phone": agent.phone,
        "max_capacity": agent.max_capacity,
        "current_load": agent.current_load,
        "is_active": agent.is_active,
        "is_available": agent.is_available,
        "utilisation_pct": agent.utilisation_pct,
    }


@router.get("/", response_model=list[AgentResponse], summary="List all agents")
def list_agents():
    return [_agent_to_dict(a) for a in get_facade().list_agents()]


@router.post("/", response_model=AgentResponse, status_code=201, summary="Add a new agent")
def create_agent(body: AgentCreateRequest):
    agent = Agent(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        phone=body.phone,
        max_capacity=body.max_capacity,
    )
    result = get_facade().add_agent(agent)
    return _agent_to_dict(result)


@router.get("/{agent_id}", response_model=AgentResponse, summary="Get agent by ID")
def get_agent(agent_id: str):
    agents = get_facade().list_agents()
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return _agent_to_dict(agent)
