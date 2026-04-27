"""
services/assignment_service.py
Round-robin agent assignment logic. Pure business logic — no DB calls directly.
"""

from models.agent import Agent
from models.lead import Lead
from repositories.agent_repository import AgentRepository


class AssignmentService:
    """Assigns leads to agents using round-robin with capacity enforcement."""

    def __init__(self, agent_repo: AgentRepository):
        self._agent_repo = agent_repo
        self._rr_index = 0  # Round-robin pointer

    def assign(self, lead: Lead) -> Agent | None:
        """
        Assign a lead to the next available agent (round-robin).
        Returns the assigned agent, or None if none are available.
        """
        available = self._agent_repo.find_available()
        if not available:
            return None

        # Round-robin: cycle through available agents
        agent = available[self._rr_index % len(available)]
        self._rr_index += 1

        lead.agent_id = agent.id
        agent.current_load += 1
        self._agent_repo.save(agent)

        return agent
