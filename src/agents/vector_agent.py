"""Vector Agent - Hybrid Vector Search and Retrieval"""

from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import numpy as np


class VectorSearchAgent:
    """Agent for vector-based and hybrid search across Qdrant/PostgreSQL vector store."""
    
    def __init__(
        self, 
        qdrant_host: str = "localhost", 
        qdrant_port: int = 6333,
        qdrant_api_key: str = None,
        pgvector_url: str = None
    ):
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port, api_key=qdrant_api_key)
        self.pgvector_url = pgvector_url
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        collection_name: str,
        limit: int = 10,
        filter_conditions: Dict = None
    ) -> List[Dict]:
        """Search for similar vectors in Qdrant collection."""
        filter_obj = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                must_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            filter_obj = Filter(must=must_conditions)
        
        results = self.qdrant.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=filter_obj
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def search_by_payload(
        self, 
        collection_name: str,
        field: str,
        value: Any,
        limit: int = 10
    ) -> List[Dict]:
        """Search by payload field value."""
        filter_obj = Filter(
            must=[FieldCondition(key=field, match=MatchValue(value=value))]
        )
        
        results = self.qdrant.search(
            collection_name=collection_name,
            query_vector=[0.0] * 1536,  # Dummy vector for payload-only search
            limit=limit,
            query_filter=filter_obj
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def hybrid_search(
        self, 
        query_text: str,
        query_embedding: List[float],
        collection_name: str,
        limit: int = 10,
        rerank: bool = True
    ) -> List[Dict]:
        """Perform hybrid search combining vector and text matching."""
        # Vector search
        vector_results = self.search_similar(
            query_embedding=query_embedding,
            collection_name=collection_name,
            limit=limit * 2,  # Get more for reranking
            filter_conditions=None
        )
        
        # Text/keyword search
        text_results = self.search_by_payload(
            collection_name=collection_name,
            field="text_snippet",
            value=query_text,
            limit=limit * 2
        )
        
        # Combine and deduplicate
        combined = {}
        for r in vector_results:
            pid = r["id"]
            combined[pid] = {"score": r["score"], "payload": r["payload"], "source": "vector"}
        
        for r in text_results:
            pid = r["id"]
            if pid in combined:
                # Take higher score
                combined[pid]["score"] = max(combined[pid]["score"], r["score"])
                combined[pid]["source"] = "hybrid"
            else:
                combined[pid] = {"score": r["score"], "payload": r["payload"], "source": "text"}
        
        # Sort by score and return top-k
        sorted_results = sorted(combined.items(), key=lambda x: x[1]["score"], reverse=True)
        return [combined[pid] for pid, _ in sorted_results[:limit]]
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """Get information about a Qdrant collection."""
        info = self.qdrant.get_collection(collection_name=collection_name)
        return {
            "name": info.config.params.vectors.size,
            "vectors_count": info.points_count,
            "config": {
                "distance_metric": info.config.params.distance_metric.name,
                "on_disk": info.config.params.on_disk
            }
        }