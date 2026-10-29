"""Vector agent: Qdrant when available, in-memory vector store otherwise."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.config import get_settings
from src.utils import setup_logging
from src.bootstrap import VECTOR_STORE, dummy_embedding

logger = setup_logging("vector_agent")


class VectorSearchAgent:
    def __init__(self, qdrant_host=None, qdrant_port=None, qdrant_api_key=None, pgvector_url=None):
        self.settings = get_settings()
        self.host = qdrant_host or self.settings.qdrant_host
        self.port = qdrant_port or self.settings.qdrant_port
        self._client = None
        try:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host=self.host, port=self.port, api_key=qdrant_api_key or self.settings.qdrant_api_key)
            self._client.get_collections()
        except Exception as e:
            logger.warning("Qdrant unavailable, using in-memory store: %s", e)
            self._client = None
        self.store = VECTOR_STORE
        self.collection = "knowledge"

    @property
    def backend(self):
        return "qdrant" if self._client else "inmemory"

    def _embed(self, text):
        from src.llm import LLMClient
        llm = LLMClient()
        vecs = llm.embed([text])
        return vecs[0] if vecs else dummy_embedding(text)

    def search_similar(self, query_embedding, collection_name=None, limit=10, filter_conditions=None):
        collection_name = collection_name or self.collection
        if self._client:
            try:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                filt = None
                if filter_conditions:
                    filt = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter_conditions.items()])
                res = self._client.search(collection_name=collection_name, query_vector=query_embedding, limit=limit, query_filter=filt)
                return [{"id": r.id, "score": float(r.score), "payload": r.payload} for r in res]
            except Exception as e:
                logger.warning("Qdrant search failed: %s", e)
        return self.store.search(collection_name, query_embedding, limit=limit, filter_conditions=filter_conditions)

    def search_by_payload(self, collection_name=None, field="text_snippet", value=None, limit=10):
        collection_name = collection_name or self.collection
        out = []
        for p in self.store.all_payloads(collection_name):
            if value and value.lower() in str(p.get(field, "")).lower():
                out.append({"id": p.get("id", ""), "score": 1.0, "payload": p})
        return out[:limit]

    def hybrid_search(self, query_text, query_embedding, collection_name=None, limit=10, rerank=True):
        collection_name = collection_name or self.collection
        vec_results = self.search_similar(query_embedding, collection_name, limit=limit * 2)
        q_tokens = set(query_text.lower().split())
        text_scored = []
        for p in self.store.all_payloads(collection_name):
            txt = (p.get("content") or "").lower()
            overlap = len(q_tokens & set(txt.split()))
            if overlap > 0:
                text_scored.append({"id": p.get("id", ""), "score": float(overlap), "payload": p})
        text_scored.sort(key=lambda x: x["score"], reverse=True)
        text_results = text_scored[: limit * 2]

        combined = {}
        for r in vec_results:
            pid = r["id"]
            combined[pid] = {"score": r["score"], "payload": r["payload"], "source": "vector"}
        for r in text_results:
            pid = r["id"]
            if pid in combined:
                combined[pid]["score"] = max(combined[pid]["score"], r["score"])
                combined[pid]["source"] = "hybrid"
            else:
                combined[pid] = {"score": r["score"], "payload": r["payload"], "source": "text"}
        sorted_results = sorted(combined.items(), key=lambda x: x[1]["score"], reverse=True)
        return [combined[pid] for pid, _ in sorted_results[:limit]]

    def get_collection_info(self, collection_name=None):
        collection_name = collection_name or self.collection
        return {"name": collection_name, "vectors_count": self.store.count(collection_name)}