"""
config/app_config.py
Singleton Pattern: Single shared configuration object for the entire application.
"""

import os
import threading


class AppConfig:
    """Singleton application configuration."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._load_defaults()
        return cls._instance

    def _load_defaults(self) -> None:
        self.db_path = os.getenv("DB_PATH", "insurance_leads.db")
        self.max_agent_capacity = 10
        self.scoring_strategy = "basic"
        self.assignment_strategy = "round_robin"
        self.email_notifications_enabled = True
        self.sms_notifications_enabled = True
        self.audit_log_enabled = True
        self.app_name = "Insurance Lead Management System"
        self.version = "1.0.0"

    def get(self, key: str, default=None):
        return getattr(self, key, default)
