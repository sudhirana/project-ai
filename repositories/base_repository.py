"""
repositories/base_repository.py
Repository Pattern: Abstract base defining the contract for all repositories.
No business logic here — only data access interface.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository — Repository Pattern interface."""

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new or updated entity."""
        ...

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve a single entity by its ID."""
        ...

    @abstractmethod
    def find_all(self) -> list[T]:
        """Retrieve all entities."""
        ...

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Remove an entity by ID."""
        ...
