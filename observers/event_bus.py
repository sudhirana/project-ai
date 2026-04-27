"""
observers/event_bus.py
Observer Pattern + Singleton: A single shared EventBus that notifies
all registered observers when lead events occur.
"""

import threading
from abc import ABC, abstractmethod
from typing import Callable


class LeadEvent:
    """Data object passed to observers on each event."""
    def __init__(self, event_type: str, lead_id: str, details: dict):
        self.event_type = event_type
        self.lead_id = lead_id
        self.details = details


class BaseObserver(ABC):
    """Observer Pattern: interface all observers must implement."""

    @abstractmethod
    def update(self, event: LeadEvent) -> None:
        ...


class EventBus:
    """
    Singleton + Observer Pattern:
    Central hub — observers subscribe to event types and are
    notified automatically when publish() is called.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._subscribers: dict[str, list[BaseObserver]] = {}
        return cls._instance

    def subscribe(self, event_type: str, observer: BaseObserver) -> None:
        self._subscribers.setdefault(event_type, []).append(observer)

    def subscribe_all(self, observer: BaseObserver) -> None:
        """Subscribe observer to all events using wildcard key."""
        self._subscribers.setdefault("*", []).append(observer)

    def publish(self, event: LeadEvent) -> None:
        """Notify all observers registered for this event type or wildcard."""
        for observer in self._subscribers.get(event.event_type, []):
            observer.update(event)
        for observer in self._subscribers.get("*", []):
            observer.update(event)


# ── Concrete Observers ──────────────────────────────────────────────────────

class EmailNotifier(BaseObserver):
    """Observer: simulates sending email notifications on lead events."""

    def update(self, event: LeadEvent) -> None:
        # In production, integrate with SendGrid / SES here
        print(f"  [EMAIL] → Lead {event.lead_id[:8]}... | "
              f"Event: {event.event_type} | {event.details.get('message', '')}")


class SMSNotifier(BaseObserver):
    """Observer: simulates sending SMS notifications."""

    def update(self, event: LeadEvent) -> None:
        # In production, integrate with Twilio here
        print(f"  [SMS]   → Lead {event.lead_id[:8]}... | "
              f"Event: {event.event_type} | {event.details.get('message', '')}")


class AuditLogger(BaseObserver):
    """Observer: persists all events to the audit_log table."""

    def __init__(self):
        from db.database import DatabaseConnection
        self._db = DatabaseConnection()

    def update(self, event: LeadEvent) -> None:
        from datetime import datetime
        import json
        conn = self._db.get_connection()
        conn.execute("""
            INSERT INTO audit_log (lead_id, event, details, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            event.lead_id,
            event.event_type,
            json.dumps(event.details),
            datetime.now().isoformat(),
        ))
        conn.commit()
        print(f"  [AUDIT] → Lead {event.lead_id[:8]}... | "
              f"Event: {event.event_type} logged to DB")
