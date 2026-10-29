"""In-memory vector store with cosine similarity (fallback when Qdrant unavailable)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._collections: dict[str, list[dict]] = {}

    def ensure_collection(self, name: str) -> None:
        self._collections.setdefault(name, [])

    def upsert(self, collection: str, points: List[Dict[str, Any]]) -> None:
        self.ensure_collection(collection)
        existing = {p["id"]: i for i, p in enumerate(self._collections[collection])}
        for pt in points:
            if pt["id"] in existing:
                self._collections[collection][existing[pt["id"]]] = pt
            else:
                self._collections[collection].append(pt)

    def search(self, collection: str, query_vector: List[float], limit: int = 10, filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        self.ensure_collection(collection)
        items = self._collections[collection]
        if filter_conditions:
            filtered = []
            for it in items:
                payload = it.get("payload", {}) or {}
                ok = all(payload.get(k) == v for k, v in filter_conditions.items())
                if ok:
                    filtered.append(it)
            items = filtered

        def cosine(a, b):
            if not a or not b:
                return 0.0
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(x * x for x in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)

        scored = []
        for it in items:
            score = cosine(query_vector, it.get("vector", []))
            scored.append({"id": it["id"], "score": float(score), "payload": it.get("payload", {})})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def count(self, collection: str) -> int:
        self.ensure_collection(collection)
        return len(self._collections[collection])

    def all_payloads(self, collection: str) -> List[Dict[str, Any]]:
        self.ensure_collection(collection)
        return [it.get("payload", {}) for it in self._collections[collection]]
