"""
tests/test_lead_service.py
Unit tests for LeadService business logic.
"""

import sys
import os
import uuid
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.lead import Lead, LeadStatus, LeadType
from models.agent import Agent
from repositories.lead_repository import LeadRepository
from repositories.agent_repository import AgentRepository
from services.lead_service import LeadService
from services.scoring_service import ScoringService
from services.assignment_service import AssignmentService
from strategies.basic_scoring_strategy import BasicScoringStrategy
from observers.event_bus import EventBus
from db.database import DatabaseConnection


@pytest.fixture(autouse=True)
def setup_db():
    db = DatabaseConnection()
    db.connect(":memory:")
    yield
    db.close()
    DatabaseConnection._instance = None
    EventBus._instance = None


def make_lead(**kwargs) -> Lead:
    defaults = dict(
        id=str(uuid.uuid4()), lead_type=LeadType.AUTO,
        first_name="Test", last_name="User", email="test@example.com",
        age=35, income=60000, coverage_amount=100000,
        lead_source="WEBSITE", prior_insurance=True,
    )
    defaults.update(kwargs)
    return Lead(**defaults)


def make_service():
    lead_repo = LeadRepository()
    agent_repo = AgentRepository()
    scoring = ScoringService(BasicScoringStrategy())
    assignment = AssignmentService(agent_repo)
    bus = EventBus()
    return LeadService(lead_repo, agent_repo, scoring, assignment, bus), lead_repo, agent_repo


def test_create_lead_assigns_score():
    service, lead_repo, _ = make_service()
    lead = make_lead()
    result = service.create_lead(lead)
    assert result.score > 0
    assert lead_repo.find_by_id(lead.id) is not None


def test_status_transition_valid():
    service, _, _ = make_service()
    lead = make_lead()
    service.create_lead(lead)
    updated = service.update_status(lead.id, LeadStatus.CONTACTED)
    assert updated.status == LeadStatus.CONTACTED


def test_status_transition_invalid():
    service, _, _ = make_service()
    lead = make_lead()
    service.create_lead(lead)
    with pytest.raises(ValueError):
        service.update_status(lead.id, LeadStatus.CONVERTED)  # must go via QUALIFIED


def test_assign_lead():
    service, lead_repo, agent_repo = make_service()
    agent = Agent(id=str(uuid.uuid4()), name="A", email="a@x.com", max_capacity=5)
    agent_repo.save(agent)
    lead = make_lead()
    service.create_lead(lead)
    assigned = service.assign_lead(lead.id)
    assert assigned is not None
    updated_lead = lead_repo.find_by_id(lead.id)
    assert updated_lead.agent_id == agent.id
