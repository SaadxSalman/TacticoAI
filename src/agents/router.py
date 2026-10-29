"""Router Agent - Query Intent Classification and Routing"""

from enum import Enum
from typing import Literal


class QueryIntent(Enum):
    """Enumeration of possible query intents."""
    SEMANTIC_SEARCH = "semantic_search"
    STRUCTURED_QUERY = "structured_query"
    CODE_EXECUTION = "code_execution"
    TACTICAL_ANALYSIS = "tactical_analysis"
    INJURY_RISK = "injury_risk"
    GENERAL_KNOWLEDGE = "general_knowledge"


class RoutingDecision:
    """Result of query routing decision."""
    
    def __init__(
        self,
        intent: QueryIntent,
        target_modules: list[str],
        confidence: float,
        requires_code_execution: bool = False,
        requires_graph: bool = False,
    ):
        self.intent = intent
        self.target_modules = target_modules
        self.confidence = confidence
        self.requires_code_execution = requires_code_execution
        self.requires_graph = requires_graph
    
    def __repr__(self):
        return f"RoutingDecision(intent={self.intent}, modules={self.target_modules}, conf={self.confidence:.2f})"


def route_query(query: str) -> RoutingDecision:
    """
    Analyze the user query and determine the optimal retrieval strategy.
    
    Args:
        query: The user's natural language query
        
    Returns:
        RoutingDecision with the recommended strategy
    """
    query_lower = query.lower()
    
    # Keywords for Code Execution requests
    code_keywords = [
        "calculate", "compute", "analyze", "statistics", "average", 
        "total", "count", "sum", "percentage", "trend", "correlation"
    ]
    
    # Keywords for Graph/Neo4j requests
    graph_keywords = [
        "formation", "tactical", "defensive scheme", "player role",
        "plays for", "team", "against", "formation"
    ]
    
    # Keywords for Injury/Risk requests
    injury_keywords = [
        "injury", "fatigue", "risk", "load", "workload",
        "recovery", "muscle", "strain"
    ]
    
    # Count keyword matches
    code_score = sum(1 for kw in code_keywords if kw in query_lower)
    graph_score = sum(1 for kw in graph_keywords if kw in query_lower)
    injury_score = sum(1 for kw in injury_keywords if kw in query_lower)
    
    # Determine intent
    if injury_score > 0:
        intent = QueryIntent.INJURY_RISK
        target = ["graph_agent", "vector_agent"]
        confidence = min(0.9, 0.6 + injury_score * 0.1)
    elif graph_score > 0:
        intent = QueryIntent.STRUCTURED_QUERY
        target = ["graph_agent"]
        confidence = min(0.95, 0.7 + graph_score * 0.1)
    elif code_score > 0:
        intent = QueryIntent.CODE_EXECUTION
        target = ["vector_agent", "engine"]
        confidence = min(0.9, 0.65 + code_score * 0.1)
    elif any(kw in query_lower for kw in ["compare", "vs", "versus", "difference"]):
        intent = QueryIntent.SEMANTIC_SEARCH
        target = ["vector_agent", "reranker"]
        confidence = 0.85
    elif any(kw in query_lower for kw in ["tactics", "strategy", "coach", "playbook"]):
        intent = QueryIntent.TACTICAL_ANALYSIS
        target = ["graph_agent", "vector_agent"]
        confidence = 0.88
    else:
        intent = QueryIntent.SEMANTIC_SEARCH
        target = ["vector_agent", "reranker"]
        confidence = 0.75
    
    requires_code = intent == QueryIntent.CODE_EXECUTION
    requires_graph = intent in [QueryIntent.STRUCTURED_QUERY, QueryIntent.INJURY_RISK]
    
    return RoutingDecision(
        intent=intent,
        target_modules=target,
        confidence=confidence,
        requires_code_execution=requires_code,
        requires_graph=requires_graph,
    )