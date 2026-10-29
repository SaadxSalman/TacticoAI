"""Self-Corrective RAG (CRAG) Evaluator."""

from __future__ import annotations

from typing import Any, Dict, List

import re


class CRAGEvaluator:
    def __init__(self, llm_client=None, confidence_threshold: float = 0.7):
        self.llm_client = llm_client
        self.confidence_threshold = confidence_threshold

    def evaluate(self, query, retrieved_chunks, context_metadata=None):
        heuristic = self._heuristic_evaluate(query, retrieved_chunks)
        # Optional LLM deep eval
        if self.llm_client is not None and getattr(self.llm_client, "available", False) and heuristic["confidence_score"] < self.confidence_threshold:
            try:
                prompt = f"Query: {query}\nRetrieved: {retrieved_chunks[:3]}\nIs the retrieved context sufficient? Reply JSON with satisfied bool and missing_info list."
                txt = self.llm_client.complete(prompt)
                # best-effort parse
                if "true" in txt.lower():
                    heuristic["satisfied"] = True
            except Exception:
                pass
        return heuristic

    def _heuristic_evaluate(self, query, retrieved_chunks):
        if not retrieved_chunks:
            return {"satisfied": False, "confidence_score": 0.0, "missing_info": ["No relevant documents retrieved"], "suggestion": "Trigger expanded search with modified query terms"}

        query_lower = query.lower()
        total_content = ""
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {}) if isinstance(chunk, dict) else {}
            content = payload.get("content", "") or chunk.get("content", "") if isinstance(chunk, dict) else ""
            total_content += " " + str(content)

        satisfaction_score = 0.0
        if any(kw in query_lower for kw in ["when", "during", "after", "before"]):
            if any(kw in total_content.lower() for kw in ["half", "period", "minute", "time"]):
                satisfaction_score += 0.3
        if any(kw in query_lower for kw in ["player", "team", "who", "what"]):
            if len(total_content) > 50:
                satisfaction_score += 0.3
        if any(kw in query_lower for kw in ["how many", "how much", "count", "percentage", "calculate", "average"]):
            if re.search(r"\d+(?:\.\d+)?", total_content):
                satisfaction_score += 0.3
        if any(kw in query_lower for kw in ["formation", "tactics", "strategy", "system"]):
            if any(kw in total_content.lower() for kw in ["formation", "system", "tactics", "press"]):
                satisfaction_score += 0.3

        satisfied = satisfaction_score >= 0.7 or (satisfaction_score > 0 and len(retrieved_chunks) >= 3)

        missing_info = []
        if not satisfied:
            if any(kw in query_lower for kw in ["how many", "count"]):
                if not re.search(r"\d+(?:\.\d+)?", total_content):
                    missing_info.append("Numerical counts/statistics")
            if any(kw in query_lower for kw in ["when", "during"]):
                if not any(kw in total_content.lower() for kw in ["half", "period", "minute", "time"]):
                    missing_info.append("Temporal references")
            if any(kw in query_lower for kw in ["player"]):
                missing_info.append("Specific player information")

        confidence = min(1.0, satisfaction_score + 0.1 * len(retrieved_chunks))
        suggestion = self._generate_suggestion(satisfied, missing_info, retrieved_chunks)
        return {"satisfied": satisfied, "confidence_score": confidence, "missing_info": missing_info, "suggestion": suggestion}

    def _generate_suggestion(self, satisfied, missing_info, retrieved_chunks):
        if satisfied:
            return "Proceed to synthesis engine - context appears sufficient"
        if not retrieved_chunks:
            return "Expand search to additional collections and modify query terms"
        suggestions = []
        if any("temporal" in m.lower() for m in missing_info):
            suggestions.append("Add time-based filters to search query")
        if any("statistical" in m.lower() for m in missing_info):
            suggestions.append("Include numerical aggregation in retrieval")
        if any("player" in m.lower() for m in missing_info):
            suggestions.append("Specify player names or IDs in query")
        if not suggestions:
            suggestions.append("Review query for additional specificity")
        return "; ".join(suggestions)