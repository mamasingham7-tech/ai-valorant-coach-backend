from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class GraphNode:
    id: str
    type: str  # Player, Habit, Strength, Weakness, Recommendation, Metric, Agent, Role, Map, Round, Decision, Drill
    properties: Dict[str, str] = field(default_factory=dict)

@dataclass
class GraphRelationship:
    source_id: str
    target_id: str
    type: str  # causes, improves, depends_on, countered_by, resolved_by, recommended_for

class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        # Maps source_id to a list of relationships
        self.relationships: Dict[str, List[GraphRelationship]] = {}

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    def add_relationship(self, rel: GraphRelationship) -> None:
        if rel.source_id not in self.relationships:
            self.relationships[rel.source_id] = []
        self.relationships[rel.source_id].append(rel)

    def get_related_nodes(self, node_id: str, rel_type: str = None) -> List[GraphNode]:
        """Traverse relationship paths to return related nodes."""
        rels = self.relationships.get(node_id, [])
        results = []
        for rel in rels:
            if rel_type is None or rel.type == rel_type:
                target = self.nodes.get(rel.target_id)
                if target:
                    results.append(target)
        return results
