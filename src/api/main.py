"""FastAPI Application Main Entry Point"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from src.engine.rag_pipeline import AgenticRAGPipeline
from src.agents.evaluator import CRAGEvaluator

# Initialize FastAPI app
app = FastAPI(
    title="TacticoAI API",
    description="Multi-Modal Agentic RAG for Sports Analytics",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (initialized on startup)
pipeline: Optional[AgenticRAGPipeline] = None


# Pydantic models for API requests/response
class QueryRequest(BaseModel):
    """Request model for query processing."""
    query: str = Field(..., description="The user's natural language query")
    user_id: Optional[str] = Field(default="anonymous", description="User identifier")
    include_video_timestamps: bool = Field(
        default=True, description="Include video clip timestamps"
    )
    include_code_execution: bool = Field(
        default=True, description="Enable code execution for statistical analysis"
    )


class QueryResponse(BaseModel):
    """Response model for query processing."""
    response: str = Field(..., description="The natural language response")
    sources: List[Dict] = Field(
        default_factory=list, description="Retrieved source documents"
    )
    code_execution: Dict = Field(
        default_factory=dict, description="Code execution results if applicable"
    )
    video_timestamps: List[Dict] = Field(
        default_factory=list, description="Video clip timestamps"
    )
    routing_decision: Dict = Field(
        default_factory=dict, description="Query routing information"
    )
    crag_evaluation: Dict = Field(
        default_factory=dict, description="CRAG evaluation results"
    )


@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup."""
    global pipeline
    pipeline = AgenticRAGPipeline(
        confidence_threshold=0.7,
    )
    logger = __import__("logging").getLogger(__name__)
    logger.info("TacticoAI Pipeline initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "tacticoai-api",
        "version": "0.1.0",
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query through the Agentic RAG pipeline.
    
    This endpoint:
    1. Routes the query based on intent
    2. Retrieves relevant data from vector and graph stores
    3. Evaluates if retrieved data satisfies the query (CRAG)
    4. Executes code if needed for statistical analysis
    5. Synthesizes a final natural language response
    """
    global pipeline
    
    if not pipeline:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized. Service unavailable.",
        )
    
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
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}",
        )


# Additional API endpoints

@app.get("/api/v1/players/{player_id}/statistics")
async def get_player_statistics(
    player_id: str,
    period: Optional[str] = None,
    opponent: Optional[str] = None,
):
    """Get player performance statistics with optional filtering."""
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    # This would integrate with the graph agent
    # For now, return structured data
    return {
        "player_id": player_id,
        "period": period,
        "opponent": opponent,
        "statistics": {
            "total_sprints": 12,
            "avg_speed": 28.5,
            "max_speed": 35.2,
            "total_distance": 15.3,
        }
    }


@app.get("/api/v1/health/detail")
async def detailed_health():
    """Detailed health check including database status."""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "neo4j": "pending_check",
            "qdrant": "pending_check",
            "postgres": "pending_check",
            "redis": "pending_check",
        }
    }