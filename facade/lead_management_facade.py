"""
facade/lead_management_facade.py
Facade Pattern: Single clean entry point for the entire system.
Callers interact only with this class — internal wiring is hidden.
"""

from models.lead import Lead, LeadStatus
from models.agent import Agent
from builders.lead_builder import LeadBuilder
from repositories.lead_repository import LeadRepository
from repositories.agent_repository import AgentRepository
from services.lead_service import LeadService
from services.scoring_service import ScoringService
from services.assignment_service import AssignmentService
from strategies.base_scoring_strategy import BaseScoringStrategy
from strategies.basic_scoring_strategy import BasicScoringStrategy
from observers.event_bus import EventBus, EmailNotifier, SMSNotifier, AuditLogger
from db.database import DatabaseConnection
from config.app_config import AppConfig


class LeadManagementFacade:
    """
    Facade Pattern: hides the complexity of repositories, services,
    factories, strategies, and observers behind a simple interface.
    """

    def __init__(self):
        # Boot singletons
        config = AppConfig()
        db = DatabaseConnection()
        db.connect(config.db_path)

        # Wire up repositories
        self._lead_repo = LeadRepository()
        self._agent_repo = AgentRepository()

        # Wire up event bus with observers (Observer Pattern)
        self._bus = EventBus()
        self._bus.subscribe_all(AuditLogger())
        self._bus.subscribe_all(EmailNotifier())
        self._bus.subscribe_all(SMSNotifier())

        # Wire up services
        scoring = ScoringService(BasicScoringStrategy())
        assignment = AssignmentService(self._agent_repo)

        self._lead_service = LeadService(
            lead_repo=self._lead_repo,
            agent_repo=self._agent_repo,
            scoring_service=scoring,
            assignment_service=assignment,
            event_bus=self._bus,
        )

    # ── Lead operations ────────────────────────────────────────────

    def new_lead_builder(self) -> LeadBuilder:
        """Return a builder for fluent lead construction."""
        return LeadBuilder()

    def submit_lead(self, lead: Lead) -> Lead:
        return self._lead_service.create_lead(lead)

    def assign_lead(self, lead_id: str) -> Agent | None:
        return self._lead_service.assign_lead(lead_id)

    def update_lead_status(self, lead_id: str, new_status: LeadStatus) -> Lead:
        return self._lead_service.update_status(lead_id, new_status)

    def rescore_lead(self, lead_id: str, strategy: BaseScoringStrategy) -> Lead:
        return self._lead_service.rescore_with_strategy(lead_id, strategy)

    def get_lead(self, lead_id: str) -> Lead | None:
        return self._lead_repo.find_by_id(lead_id)

    def list_leads(self) -> list[Lead]:
        return self._lead_repo.find_all()

    # ── Agent operations ───────────────────────────────────────────

    def add_agent(self, agent: Agent) -> Agent:
        return self._agent_repo.save(agent)

    def list_agents(self) -> list[Agent]:
        return self._agent_repo.find_all()

    # ── Reporting ──────────────────────────────────────────────────

    def get_report(self) -> dict:
        return self._lead_service.get_report()
