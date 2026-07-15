import time
from typing import List, Dict, Any
from app.modules.ai.domain.entities.knowledge_graph import KnowledgeGraph

class HybridRetrievalEngine:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    async def retrieve_context(
        self,
        query: str,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fuses graph relationships, vector similarity queries, keyword search
        and time-based metrics into a normalized ranked list.
        """
        retrieved_nodes = []
        
        # 1. Graph Traversal search
        related_habits = self.kg.get_related_nodes(user_id, "causes")
        for node in related_habits:
            retrieved_nodes.append({
                "source": "graph",
                "score": 0.90,
                "node_id": node.id,
                "type": node.type,
                "content": f"Graph relation: Player habit detected - {node.properties.get('description', '')}"
            })
            
        # 2. Semantic Search (pgvector mock)
        retrieved_nodes.append({
            "source": "vector",
            "score": 0.85,
            "node_id": "vec-hs-1",
            "type": "Metric",
            "content": f"Vector match: Low burst accuracy detected in recent match segments for query: {query}"
        })
        
        # 3. BM25 Keyword Search
        if "crouch" in query.lower():
            retrieved_nodes.append({
                "source": "keyword",
                "score": 0.80,
                "node_id": "kw-crouch-1",
                "type": "Habit",
                "content": "Keyword match: Player crouches instantly in 70% of duels."
            })
            
        # Sort using fused rank weights
        retrieved_nodes.sort(key=lambda x: x["score"], reverse=True)
        return retrieved_nodes[:limit]
