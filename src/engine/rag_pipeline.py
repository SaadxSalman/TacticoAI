"""Core Agentic RAG Workflow Engine."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.agents.router import route_query
from src.agents.vector_agent import VectorSearchAgent
from src.agents.graph_agent import Neo4jGraphAgent
from src.agents.evaluator import CRAGEvaluator
from src.reranker import Reranker
from src.code_executor import CodeExecutionEngine
from src.llm import LLMClient
from src.utils import setup_logging
from src.bootstrap import dummy_embedding
from src.data import get_player, TEAMS, PLAYERS

logger = setup_logging("rag_pipeline")


class AgenticRAGPipeline:
    def __init__(self, llm_client=None, confidence_threshold=0.7, vector_agent=None, graph_agent=None):
        self.llm = llm_client or LLMClient()
        self.vector_agent = vector_agent or VectorSearchAgent()
        self.graph_agent = graph_agent or Neo4jGraphAgent()
        self.evaluator = CRAGEvaluator(llm_client=self.llm, confidence_threshold=confidence_threshold)
        self.reranker = Reranker()
        self.code_engine = CodeExecutionEngine()
        self.confidence_threshold = confidence_threshold

    def close(self):
        try:
            self.graph_agent.close()
        except Exception:
            pass

    def process_query(self, query, user_id="anonymous", include_code_execution=True, include_video_timestamps=True):
        logger.info("Processing query: %s", query[:100])
        routing = route_query(query)
        logger.info("Routing: %s", routing.intent.value)

        retrieval_results = self._execute_retrieval(query, routing)
        reranked = self.reranker.rerank(query, retrieval_results, top_n=5) if retrieval_results else []

        eval_result = self.evaluator.evaluate(query, reranked if reranked else retrieval_results)

        code_result = {}
        if include_code_execution and (routing.requires_code_execution or self._needs_stats(query)):
            code_result = self._run_code_analysis(query)

        final_response = self._synthesize(query, reranked if reranked else retrieval_results, routing, code_result)

        video_timestamps = []
        if include_video_timestamps:
            video_timestamps = self._extract_timestamps(query, reranked if reranked else retrieval_results)

        return {
            "response": final_response,
            "sources": [{"id": r.get("id", r.get("payload", {}).get("id")), "score": r.get("rerank_score", r.get("score", 0.0)), "source": r.get("payload", {}).get("source", r.get("source"))} for r in (reranked if reranked else retrieval_results)],
            "code_execution": code_result,
            "video_timestamps": video_timestamps,
            "routing_decision": {
                "intent": routing.intent.value,
                "confidence": routing.confidence,
                "modules": routing.target_modules,
            },
            "crag_evaluation": eval_result,
        }
    def _execute_retrieval(self, query, routing):
        results = []
        try:
            q_emb = self.llm.embed([query])[0]
        except Exception:
            q_emb = dummy_embedding(query)

        try:
            vs = self.vector_agent.hybrid_search(query, q_emb, collection_name="knowledge", limit=8)
            for r in vs:
                r.setdefault("content", r.get("payload", {}).get("content", ""))
            results.extend(vs)
        except Exception as e:
            logger.warning("Vector retrieval failed: %s", e)

        if routing.requires_graph or "graph_agent" in routing.target_modules:
            graph_results = self._graph_retrieve(query)
            results.extend(graph_results)

        seen = set()
        deduped = []
        for r in results:
            rid = r.get("id") or r.get("payload", {}).get("id") or str(r)
            if rid in seen:
                continue
            seen.add(rid)
            deduped.append(r)
        return deduped

    def _graph_retrieve(self, query):
        out = []
        q = query.lower()
        for p in PLAYERS:
            if p["name"].lower() in q or p["player_id"].lower() in q:
                out.append({"id": f"player_{p['player_id']}", "content": f"Player {p['name']} plays as {p['position']} for team {p['team_id']}.", "payload": {"content": f"Player {p['name']} plays as {p['position']} for team {p['team_id']}.", "source": "graph"}, "score": 0.9})
                stats = self.graph_agent.get_player_performance_stats(p["player_id"])
                if stats:
                    for st in stats:
                        txt = f"{p['name']} in {st['game_id']}: {st['total_sprints']} sprints, avg speed {st['avg_speed']} km/h, max speed {st['max_speed']} km/h."
                        out.append({"id": f"stats_{p['player_id']}_{st['game_id']}", "content": txt, "payload": {"content": txt, "source": "graph"}, "score": 0.85})
        if "formation" in q or "tactic" in q or "system" in q:
            for tid in ["T_LIV", "T_MCI", "T_ARS", "T_CHE"]:
                forms = self.graph_agent.get_team_formations(tid)
                for f in forms:
                    txt = f"Team {tid} uses formation {f.get('formation_name')}."
                    out.append({"id": f"form_{tid}", "content": txt, "payload": {"content": txt, "source": "graph"}, "score": 0.7})
        if "weakness" in q or "counter" in q or "defensive" in q:
            for tid in ["T_LIV", "T_MCI", "T_ARS", "T_CHE"]:
                ws = self.graph_agent.find_defensive_weaknesses(tid, "4-3-3")
                for w in ws:
                    txt = f"Team {tid} weakness: {w['vulnerability']} (success rate {w['success_rate']})."
                    out.append({"id": f"weak_{tid}_{w['weakness_id']}", "content": txt, "payload": {"content": txt, "source": "graph"}, "score": 0.75})
        if "injury" in q or "risk" in q or "fatigue" in q or "load" in q:
            from src.data import workload_for
            for p in PLAYERS:
                w = workload_for(p["player_id"])
                if w:
                    txt = f"Player {p['name']} workload: avg minutes {w['avg_minutes']}, recent injuries {w['recent_injuries']}, load index {w['load_index']}."
                    out.append({"id": f"wl_{p['player_id']}", "content": txt, "payload": {"content": txt, "source": "graph"}, "score": 0.8})
        return out

    def _needs_stats(self, query):
        ql = query.lower()
        return any(kw in ql for kw in ["calculate", "compute", "average", "total", "count", "how many", "sprint", "speed"])
    def _run_code_analysis(self, query):
        ql = query.lower()
        target_player = None
        for p in PLAYERS:
            if p["name"].lower() in ql or p["player_id"].lower() in ql:
                target_player = p["player_id"]
                break
        if target_player:
            period = "second_half" if "second half" in ql else ("first_half" if "first half" in ql else None)
            stats = self.code_engine.compute_player_stats(target_player, period)
            from src.data import workload_for
            w = workload_for(target_player)
            risk = None
            if w:
                from src.agents.predictive_analytics import PredictiveAnalyticsAgent
                pa = PredictiveAnalyticsAgent()
                risk = pa.calculate_injury_risk({"avg_minutes": w["avg_minutes"]}, {"recent_injuries": w["recent_injuries"]})
            return {"player_id": target_player, "stats": stats, "injury_risk": risk}
        return {}

    def _synthesize(self, query, retrieved, routing, code_result):
        context = "\n".join([f"- {r.get('content') or r.get('payload', {}).get('content', '')}" for r in retrieved[:8]])
        if self.llm.available:
            system = "You are TacticoAI, a sports analytics assistant. Use the provided context to answer the user's query concisely and accurately. Include specific numbers when available."
            prompt = f"Context:\n{context}\n\nCode analysis: {code_result}\n\nQuery: {query}\n\nAnswer:"
            resp = self.llm.complete(prompt, system=system)
            if resp:
                return resp
        return self._fallback_synthesize(query, retrieved, code_result)

    def _fallback_synthesize(self, query, retrieved, code_result):
        parts = []
        ql = query.lower()
        if code_result and code_result.get("stats"):
            st = code_result["stats"]
            pname = None
            for p in PLAYERS:
                if p["player_id"] == code_result.get("player_id"):
                    pname = p["name"]
            parts.append(f"Analysis for {pname or code_result.get('player_id')}: {st.get('count', 0)} sprints, avg speed {st.get('avg_speed', 0)} km/h, max speed {st.get('max_speed', 0)} km/h, total distance {st.get('total_distance', 0)} km.")
            if code_result.get("injury_risk"):
                r = code_result["injury_risk"]
                parts.append(f"Injury risk: {r.get('risk_level')} (score {round(r.get('risk_score', 0), 2)}). Recommendations: {', '.join(r.get('recommendations', []))}.")
        if retrieved:
            parts.append("Key retrieved insights:")
            for r in retrieved[:4]:
                c = r.get("content") or r.get("payload", {}).get("content", "")
                if c:
                    parts.append(f"  - {c}")
        if not parts:
            parts.append(f"Processed query: {query}. No specific data found in demo dataset; try mentioning a player name (e.g., Mohamed Salah) or topic (formation, injury risk, sprints).")
        return "\n".join(parts)

    def _extract_timestamps(self, query, retrieved):
        ts = []
        for r in retrieved:
            payload = r.get("payload", {}) if isinstance(r, dict) else {}
            if payload.get("minute") is not None:
                ts.append({"game_id": payload.get("game_id"), "minute": payload.get("minute"), "player_id": payload.get("player_id")})
        seen = set()
        out = []
        for t in ts:
            key = (t.get("game_id"), t.get("minute"))
            if key in seen:
                continue
            seen.add(key)
            out.append(t)
        return out[:5]