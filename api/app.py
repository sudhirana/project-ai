"""
api/app.py
FastAPI application factory. Mounts all routers and bootstraps the facade.
This is the ONLY place the facade is instantiated for the web layer.
"""

import sys
import os

# Ensure project root is on the path when running from api/ folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from facade.lead_management_facade import LeadManagementFacade
from api.routers import leads, agents, reports

# ── Single shared facade instance (Singleton behaviour at app level) ──────
facade = LeadManagementFacade()

# ── FastAPI app ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Insurance Lead Management System",
    description="""
## 🛡 Insurance Lead Management API

A fully modular REST API built with **FastAPI** on top of a clean
Python architecture using 7 design patterns.

### Features
- **Lead lifecycle** — create, assign, transition status (state machine validated)
- **Lead scoring** — swap between Basic, Premium, and Risk-Based strategies at runtime
- **Agent management** — round-robin assignment with capacity enforcement
- **Event notifications** — every status change fires Email, SMS, and Audit observers
- **Reporting** — leads by status, agent performance, top scored leads

### Design Patterns Used
`Factory` `Builder` `Repository` `Strategy` `Observer` `Facade` `Singleton`
    """,
    version="1.0.0",
    contact={"name": "Insurance Lead System"},
    license_info={"name": "MIT"},
)

# ── CORS (allows frontend on any port to call this API) ───────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ─────────────────────────────────────────────────────────
app.include_router(leads.router)
app.include_router(agents.router)
app.include_router(reports.router)


# ── Root endpoint — simple health check ───────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {
        "status": "ok",
        "app": "Insurance Lead Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"], summary="Liveness probe")
def health():
    return {"status": "healthy"}
