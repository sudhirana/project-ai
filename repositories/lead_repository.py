"""
repositories/lead_repository.py
Repository Pattern: All Lead data access in one place. Zero business logic.
"""

import sqlite3
from typing import Optional

from db.database import DatabaseConnection
from models.lead import Lead, LeadStatus, LeadType
from repositories.base_repository import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """Handles all CRUD operations for Lead entities."""

    def __init__(self):
        self._db = DatabaseConnection()

    def _row_to_lead(self, row: sqlite3.Row) -> Lead:
        return Lead(
            id=row["id"],
            lead_type=LeadType(row["lead_type"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"] or "",
            age=row["age"] or 0,
            income=row["income"] or 0.0,
            coverage_amount=row["coverage_amount"] or 0.0,
            lead_source=row["lead_source"] or "WEBSITE",
            prior_insurance=bool(row["prior_insurance"]),
            status=LeadStatus(row["status"]),
            score=row["score"] or 0.0,
            agent_id=row["agent_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def save(self, lead: Lead) -> Lead:
        conn = self._db.get_connection()
        conn.execute("""
            INSERT INTO leads (id, lead_type, first_name, last_name, email,
                phone, age, income, coverage_amount, lead_source,
                prior_insurance, status, score, agent_id, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                score=excluded.score,
                agent_id=excluded.agent_id,
                updated_at=excluded.updated_at
        """, (
            lead.id, lead.lead_type.value, lead.first_name, lead.last_name,
            lead.email, lead.phone, lead.age, lead.income, lead.coverage_amount,
            lead.lead_source, int(lead.prior_insurance), lead.status.value,
            lead.score, lead.agent_id, lead.created_at, lead.updated_at,
        ))
        conn.commit()
        return lead

    def find_by_id(self, entity_id: str) -> Optional[Lead]:
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT * FROM leads WHERE id = ?", (entity_id,)
        ).fetchone()
        return self._row_to_lead(row) if row else None

    def find_all(self) -> list[Lead]:
        conn = self._db.get_connection()
        rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
        return [self._row_to_lead(r) for r in rows]

    def find_by_status(self, status: LeadStatus) -> list[Lead]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM leads WHERE status = ?", (status.value,)
        ).fetchall()
        return [self._row_to_lead(r) for r in rows]

    def find_by_agent(self, agent_id: str) -> list[Lead]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM leads WHERE agent_id = ?", (agent_id,)
        ).fetchall()
        return [self._row_to_lead(r) for r in rows]

    def top_scored(self, n: int) -> list[Lead]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY score DESC LIMIT ?", (n,)
        ).fetchall()
        return [self._row_to_lead(r) for r in rows]

    def count_by_status(self) -> dict[str, int]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM leads GROUP BY status"
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}

    def delete(self, entity_id: str) -> bool:
        conn = self._db.get_connection()
        cur = conn.execute("DELETE FROM leads WHERE id = ?", (entity_id,))
        conn.commit()
        return cur.rowcount > 0
