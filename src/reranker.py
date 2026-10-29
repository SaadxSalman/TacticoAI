"""Reranker: Cohere Rerank with heuristic fallback."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.config import get_settings
from src.utils import setup_logging

logger = setup_logging("reranker")


class Reranker:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        if self.settings.cohere_configured:
            try:
                import cohere
                key = self.settings.cohere_rerank_api_key or self.settings.cohere_api_key
                self._client = cohere.ClientV2(api_key=key)
            except Exception as e:
                logger.warning("Cohere init failed: %s", e)
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        if not documents:
            return []
        if self._client is not None:
            try:
                texts = [d.get("content") or d.get("payload", {}).get("content", "") or str(d) for d in documents]
                resp = self._client.rerank(model="rerank-v3.5", query=query, documents=texts, top_n=min(top_n, len(texts)))
                out = []
                for r in resp.results:
                    doc = documents[r.index].copy()
                    doc["rerank_score"] = float(r.relevance_score)
                    out.append(doc)
                return out
            except Exception as e:
                logger.warning("Cohere rerank failed: %s", e)
        # Heuristic fallback: keyword overlap
        q_tokens = set(query.lower().split())
        scored = []
        for d in documents:
            text = (d.get("content") or d.get("payload", {}).get("content", "") or "").lower()
            overlap = len(q_tokens & set(text.split()))
            scored.append((overlap, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, d in scored[:top_n]:
            dd = d.copy()
            dd["rerank_score"] = float(score)
            out.append(dd)
        return out
