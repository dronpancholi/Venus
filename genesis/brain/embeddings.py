"""
Embedding Manager — Placeholder for all 5 embedding types.

Each entity in the Engineering Brain can have 5 embedding vectors:
  - semantic: meaning-based (e.g., sentence-transformers)
  - knowledge: knowledge-graph-based (e.g., TransE, node2vec)
  - structural: code-structure-based (e.g., AST embeddings)
  - behavioral: runtime-behavior-based (e.g., execution traces)
  - evolution: change-history-based (e.g., git log embeddings)

Current: storage only. Actual embedding computation will be added
in later phases with appropriate models.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from genesis.brain.entity import EntityEmbedding


EMBEDDING_KINDS = ("semantic", "knowledge", "structural", "behavioral", "evolution")


class EmbeddingStore:
    """
    Persistent store for entity embeddings.

    Backed by JSON files (one per embedding kind) for now.
    Future: pgvector, ChromaDB, Qdrant, or FAISS.
    """

    def __init__(self, storage_path: str = ""):
        self._path = Path(storage_path) if storage_path else Path.cwd() / ".brain_embeddings"
        self._path.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, EntityEmbedding]] = {k: {} for k in EMBEDDING_KINDS}
        self._load_all()

    def _file_for(self, kind: str) -> Path:
        return self._path / f"{kind}_embeddings.json"

    def _load_all(self):
        for kind in EMBEDDING_KINDS:
            f = self._file_for(kind)
            if f.exists():
                try:
                    data = json.loads(f.read_text())
                    for entity_id, emb_data in data.items():
                        self._cache[kind][entity_id] = EntityEmbedding(**emb_data)
                except Exception:
                    pass

    def _save_kind(self, kind: str):
        data = {
            eid: emb.to_dict()
            for eid, emb in self._cache[kind].items()
        }
        self._file_for(kind).write_text(json.dumps(data, indent=2))

    def store(self, entity_id: str, kind: str, vector: list[float],
              model: str = "") -> EntityEmbedding:
        """Store an embedding for an entity."""
        if kind not in EMBEDDING_KINDS:
            raise ValueError(f"Unknown embedding kind: {kind}. Use one of {EMBEDDING_KINDS}")

        emb = EntityEmbedding(vector=vector, model=model)
        self._cache[kind][entity_id] = emb
        self._save_kind(kind)
        return emb

    def get(self, entity_id: str, kind: str) -> EntityEmbedding | None:
        """Retrieve an embedding."""
        return self._cache.get(kind, {}).get(entity_id)

    def has(self, entity_id: str, kind: str) -> bool:
        return entity_id in self._cache.get(kind, {})

    def delete(self, entity_id: str, kind: str) -> bool:
        if kind in self._cache and entity_id in self._cache[kind]:
            del self._cache[kind][entity_id]
            self._save_kind(kind)
            return True
        return False

    def delete_all(self, entity_id: str) -> int:
        count = 0
        for kind in EMBEDDING_KINDS:
            if entity_id in self._cache[kind]:
                del self._cache[kind][entity_id]
                count += 1
        for kind in EMBEDDING_KINDS:
            self._save_kind(kind)
        return count

    def all_for_kind(self, kind: str) -> dict[str, EntityEmbedding]:
        return dict(self._cache.get(kind, {}))

    def count(self, kind: str | None = None) -> int:
        if kind:
            return len(self._cache.get(kind, {}))
        return sum(len(v) for v in self._cache.values())

    def summary(self) -> dict[str, Any]:
        return {
            kind: len(self._cache[kind])
            for kind in EMBEDDING_KINDS
        }
