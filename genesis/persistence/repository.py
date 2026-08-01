"""
VENUS-II-PERS-REP-01: Repository Pattern — Abstract Storage Provider

Normative References:
  - VPS Part X: Storage Model
  - VPS Part X §10.1: Storage Providers (Artifact, Knowledge, History, Metadata, Checkpoint)
  - GENESIS_II_ARCHITECTURE §5.6: Repository Pattern
  - ADR-006: Repository Pattern for Persistence, Not Active Record

Purpose:
  Define the abstract repository interface that all storage providers implement.
  Decouples platform logic from storage technology — SQLite, JSON, and Neo4j
  backends all implement the same Repository protocol.

Key Design Decisions:
  - Repository pattern (not Active Record): entities are pure data, repositories
    handle persistence — aligns with DI, testability, and multiple backends
  - InMemoryRepository provided as default fallback (zero dependencies)
  - SQLiteRepository will be implemented in Phase 4
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """
    Abstract repository interface for entity persistence.

    All Venus storage providers implement this interface.
    T is the entity type managed by this repository.

    NORMATIVE:
      - save() must be idempotent (same entity, same state → no error)
      - get() must return None for non-existent entities (not raise)
      - delete() must not raise for non-existent entities
      - find() must return an empty list when no matches exist
    """

    @abstractmethod
    def save(self, entity: T) -> None:
        """
        Persist an entity.

        Preconditions:
          - entity has a valid entity_id and semantic_type
        Postconditions:
          - entity is stored and retrievable by entity_id
          - If entity already exists, it is overwritten
        """
        ...

    @abstractmethod
    def get(self, entity_id: str) -> T | None:
        """
        Retrieve an entity by ID.

        Preconditions:
          - entity_id is a string
        Postconditions:
          - Returns the entity if found, None otherwise
        """
        ...

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        """
        Delete an entity by ID.

        Preconditions:
          - entity_id is a string
        Postconditions:
          - Entity is no longer retrievable by entity_id
          - No error if entity does not exist
        """
        ...

    @abstractmethod
    def find(self, **filters: Any) -> list[T]:
        """
        Find entities matching all given filter criteria.

        Preconditions:
          - filters are keyword arguments where keys are attribute names
        Postconditions:
          - Returns a list of matching entities (empty list if none)
          - All filter criteria are ANDed together
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities in this repository."""
        ...

    @abstractmethod
    def all(self) -> list[T]:
        """Return all entities in this repository."""
        ...


class InMemoryRepository(Repository[T]):
    """
    In-memory implementation of Repository.

    Used as the default storage provider. All data is lost on restart.
    This is the Genesis-I compatible fallback — Phase 4 replaces this
    with SQLiteRepository for persistent storage.
    """

    def __init__(self):
        self._store: dict[str, T] = {}
        self._index: dict[str, dict[str, list[str]]] = {}  # attr -> value -> [entity_id]

    def save(self, entity: T) -> None:
        entity_id = str(getattr(entity, "entity_id", id(entity)))
        self._store[entity_id] = entity

    def get(self, entity_id: str) -> T | None:
        return self._store.get(entity_id)

    def delete(self, entity_id: str) -> None:
        self._store.pop(entity_id, None)

    def find(self, **filters: Any) -> list[T]:
        results = list(self._store.values())
        for key, value in filters.items():
            results = [
                e for e in results
                if getattr(e, key, None) == value
            ]
        return results

    def count(self) -> int:
        return len(self._store)

    def all(self) -> list[T]:
        return list(self._store.values())

    def clear(self) -> None:
        """Remove all entities. Used primarily in testing."""
        self._store.clear()
