"""
repositories/agent_repository.py
Repository Pattern: All Agent data access isolated here.
"""

import sqlite3
from typing import Optional

from db.database import DatabaseConnection
from models.agent import Agent
from repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Handles all CRUD operations for Agent entities."""

    def __init__(self):
        self._db = DatabaseConnection()

    def _row_to_agent(self, row: sqlite3.Row) -> Agent:
        return Agent(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row["phone"] or "",
            max_capacity=row["max_capacity"],
            current_load=row["current_load"],
            is_active=bool(row["is_active"]),
        )

    def save(self, agent: Agent) -> Agent:
        conn = self._db.get_connection()
        conn.execute("""
            INSERT INTO agents (id, name, email, phone, max_capacity, current_load, is_active)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                current_load=excluded.current_load,
                is_active=excluded.is_active
        """, (
            agent.id, agent.name, agent.email, agent.phone,
            agent.max_capacity, agent.current_load, int(agent.is_active),
        ))
        conn.commit()
        return agent

    def find_by_id(self, entity_id: str) -> Optional[Agent]:
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT * FROM agents WHERE id = ?", (entity_id,)
        ).fetchone()
        return self._row_to_agent(row) if row else None

    def find_all(self) -> list[Agent]:
        conn = self._db.get_connection()
        rows = conn.execute("SELECT * FROM agents").fetchall()
        return [self._row_to_agent(r) for r in rows]

    def find_available(self) -> list[Agent]:
        conn = self._db.get_connection()
        rows = conn.execute("""
            SELECT * FROM agents
            WHERE is_active = 1 AND current_load < max_capacity
            ORDER BY current_load ASC
        """).fetchall()
        return [self._row_to_agent(r) for r in rows]

    def increment_load(self, agent_id: str) -> None:
        conn = self._db.get_connection()
        conn.execute(
            "UPDATE agents SET current_load = current_load + 1 WHERE id = ?",
            (agent_id,)
        )
        conn.commit()

    def delete(self, entity_id: str) -> bool:
        conn = self._db.get_connection()
        cur = conn.execute("DELETE FROM agents WHERE id = ?", (entity_id,))
        conn.commit()
        return cur.rowcount > 0

    def get_performance(self) -> list[dict]:
        """Returns agent conversion rate data for reporting."""
        conn = self._db.get_connection()
        rows = conn.execute("""
            SELECT a.name, a.email,
                COUNT(l.id) as total_leads,
                SUM(CASE WHEN l.status='CONVERTED' THEN 1 ELSE 0 END) as converted
            FROM agents a
            LEFT JOIN leads l ON l.agent_id = a.id
            GROUP BY a.id
        """).fetchall()
        result = []
        for r in rows:
            total = r["total_leads"] or 0
            converted = r["converted"] or 0
            rate = round((converted / total * 100), 1) if total > 0 else 0.0
            result.append({
                "agent": r["name"],
                "email": r["email"],
                "total_leads": total,
                "converted": converted,
                "conversion_rate": rate,
            })
        return result
