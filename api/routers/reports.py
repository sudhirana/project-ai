"""
api/routers/reports.py
FastAPI router for reporting and analytics endpoints.
"""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_facade():
    from api.app import facade
    return facade


@router.get("/summary", summary="Full summary report")
def summary_report():
    """Returns leads by status, agent performance, and top scored leads."""
    return get_facade().get_report()


@router.get("/leads-by-status", summary="Lead count by status")
def leads_by_status():
    report = get_facade().get_report()
    return report["leads_by_status"]


@router.get("/agent-performance", summary="Agent conversion rates")
def agent_performance():
    report = get_facade().get_report()
    return report["agent_performance"]


@router.get("/top-leads", summary="Top scored leads")
def top_leads(n: int = Query(5, ge=1, le=50, description="Number of top leads to return")):
    report = get_facade().get_report()
    return report["top_scored_leads"][:n]
