"""
db/database.py
Singleton Pattern: Ensures a single shared SQLite connection across the app.
"""

import sqlite3
import threading
from pathlib import Path


class DatabaseConnection:
    """Singleton database connection manager."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Singleton Pattern: only one instance ever created
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._connection = None
        return cls._instance

    def connect(self, db_path: str = "insurance_leads.db") -> None:
        if self._connection is None:
            self._connection = sqlite3.connect(db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self.connect()
        return self._connection

    def _initialize_schema(self) -> None:
        cursor = self._connection.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                max_capacity INTEGER DEFAULT 10,
                current_load INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                lead_type TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                age INTEGER,
                income REAL,
                coverage_amount REAL,
                lead_source TEXT,
                prior_insurance INTEGER DEFAULT 0,
                status TEXT DEFAULT 'NEW',
                score REAL DEFAULT 0.0,
                agent_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT,
                event TEXT,
                details TEXT,
                timestamp TEXT
            );
        """)
        self._connection.commit()

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
