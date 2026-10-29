"""FastAPI Application Main Entry Point."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import get_settings
from src.utils import setup_logging
from src.engine.rag_pipeline import AgenticRAGPipeline
from src.agents.evaluator import CRAGEvaluator

logger = setup_logging("api")

app = FastAPI(
    title="TacticoAI API",
    description="Multi-Modal Agentic RAG for Sports Analytics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline: Optional[AgenticRAGPipeline] = None


class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's natural language query")
    user_id: Optional[str] = Field(default="anonymous", description="User identifier")
    include_video_timestamps: bool = Field(default=True, description="Include video clip timestamps")
    include_code_execution: bool = Field(default=True, description="Enable code execution for statistical analysis")


class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    code_execution: Dict[str, Any] = Field(default_factory=dict)
    video_timestamps: List[Dict[str, Any]] = Field(default_factory=list)
    routing_decision: Dict[str, Any] = Field(default_factory=dict)
    crag_evaluation: Dict[str, Any] = Field(default_factory=dict)


@app.on_event("startup")
async def startup_event():
    global pipeline
    pipeline = AgenticRAGPipeline(confidence_threshold=0.7)
    logger.info("TacticoAI Pipeline initialized (backend: %s)", pipeline.vector_agent.backend)


@app.on_event("shutdown")
async def shutdown_event():
    global pipeline
    if pipeline:
        pipeline.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tacticoai-api", "version": "1.0.0"}


@app.get("/api/v1/health/detail")
async def detailed_health():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "vector_backend": pipeline.vector_agent.backend if pipeline else "uninitialized",
            "graph_backend": pipeline.graph_agent.backend if pipeline else "uninitialized",
            "llm": "configured" if (pipeline and pipeline.llm.available) else "fallback",
        },
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global pipeline
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    try:
        result = pipeline.process_query(
            query=request.query,
            user_id=request.user_id,
            include_code_execution=request.include_code_execution,
            include_video_timestamps=request.include_video_timestamps,
        )
        return QueryResponse(**result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/api/v1/players")
async def list_players():
    from src.data import PLAYERS, TEAMS
    team_map = {t["team_id"]: t["name"] for t in TEAMS}
    return [{"player_id": p["player_id"], "name": p["name"], "team": team_map.get(p["team_id"]), "position": p["position"], "age": p["age"]} for p in PLAYERS]


@app.get("/api/v1/players/{player_id}/statistics")
async def get_player_statistics(player_id: str, period: Optional[str] = None, opponent: Optional[str] = None):
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    stats = pipeline.graph_agent.get_player_performance_stats(player_id, period=period, opponent=opponent)
    return {"player_id": player_id, "period": period, "opponent": opponent, "statistics": stats}


@app.get("/api/v1/teams")
async def list_teams():
    from src.data import TEAMS
    return TEAMS


@app.get("/api/v1/teams/{team_id}/formations")
async def team_formations(team_id: str):
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    return {"team_id": team_id, "formations": pipeline.graph_agent.get_team_formations(team_id)}


@app.get("/api/v1/injury-risk")
async def injury_risk_all():
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    from src.data import PLAYERS, workload_for
    from src.agents.predictive_analytics import PredictiveAnalyticsAgent
    pa = PredictiveAnalyticsAgent()
    out = []
    for p in PLAYERS:
        w = workload_for(p["player_id"])
        if w:
            risk = pa.calculate_injury_risk({"avg_minutes": w["avg_minutes"]}, {"recent_injuries": w["recent_injuries"]})
            out.append({"player_id": p["player_id"], "name": p["name"], **risk})
    return out