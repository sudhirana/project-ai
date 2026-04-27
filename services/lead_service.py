"""
services/lead_service.py
Core business logic for lead lifecycle. Coordinates repositories,
scoring, assignment, and event publishing. No raw DB calls here.
"""

from models.lead import Lead, LeadStatus
from models.agent import Agent
from repositories.lead_repository import LeadRepository
from repositories.agent_repository import AgentRepository
from services.scoring_service import ScoringService
from services.assignment_service import AssignmentService
from observers.event_bus import EventBus, LeadEvent
from strategies.base_scoring_strategy import BaseScoringStrategy


class LeadService:
    """
    Orchestrates the full lead lifecycle:
    create → score → assign → transition status → notify
    """

    def __init__(
        self,
        lead_repo: LeadRepository,
        agent_repo: AgentRepository,
        scoring_service: ScoringService,
        assignment_service: AssignmentService,
        event_bus: EventBus,
    ):
        self._lead_repo = lead_repo
        self._agent_repo = agent_repo
        self._scoring = scoring_service
        self._assignment = assignment_service
        self._bus = event_bus

    def create_lead(self, lead: Lead) -> Lead:
        """Score, persist, and publish a new lead creation event."""
        lead.score = self._scoring.score(lead)
        self._lead_repo.save(lead)

        self._bus.publish(LeadEvent(
            event_type="LEAD_CREATED",
            lead_id=lead.id,
            details={"message": f"New {lead.lead_type.value} lead for {lead.full_name}",
                     "score": lead.score},
        ))
        return lead

    def assign_lead(self, lead_id: str) -> Agent | None:
        """Assign an existing lead to an agent and persist."""
        lead = self._lead_repo.find_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        agent = self._assignment.assign(lead)
        if agent:
            self._lead_repo.save(lead)
            self._bus.publish(LeadEvent(
                event_type="LEAD_ASSIGNED",
                lead_id=lead.id,
                details={"message": f"Assigned to agent {agent.name}",
                         "agent_id": agent.id},
            ))
        return agent

    def update_status(self, lead_id: str, new_status: LeadStatus) -> Lead:
        """Validate and apply a status transition, then notify observers."""
        lead = self._lead_repo.find_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        old_status = lead.status
        lead.transition_to(new_status)  # State machine validates here
        self._lead_repo.save(lead)

        self._bus.publish(LeadEvent(
            event_type="STATUS_CHANGED",
            lead_id=lead.id,
            details={
                "message": f"Status {old_status.value} → {new_status.value}",
                "old_status": old_status.value,
                "new_status": new_status.value,
            },
        ))
        return lead

    def rescore_with_strategy(
        self, lead_id: str, strategy: BaseScoringStrategy
    ) -> Lead:
        """Swap scoring strategy and re-score a lead at runtime."""
        lead = self._lead_repo.find_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")
        self._scoring.set_strategy(strategy)
        lead.score = self._scoring.score(lead)
        self._lead_repo.save(lead)
        return lead

    def get_report(self) -> dict:
        """Aggregated reporting data."""
        return {
            "leads_by_status": self._lead_repo.count_by_status(),
            "agent_performance": self._agent_repo.get_performance(),
            "top_scored_leads": [
                {"name": l.full_name, "type": l.lead_type.value,
                 "score": l.score, "status": l.status.value}
                for l in self._lead_repo.top_scored(5)
            ],
        }
