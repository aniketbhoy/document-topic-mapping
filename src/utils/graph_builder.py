"""Graph building utilities using NetworkX."""

from typing import List, Dict, Set, Tuple
import networkx as nx
from loguru import logger
from ..models import Topic, Relationship


class GraphBuilder:
    """Build and analyze topic relationship graphs."""

    def __init__(self):
        """Initialize the graph builder."""
        self.graph = nx.DiGraph()

    def add_topic(self, topic: Topic):
        """
        Add a topic node to the graph.

        Args:
            topic: Topic to add
        """
        self.graph.add_node(
            topic.id,
            title=topic.title,
            content=topic.content,
            confidence=topic.confidence
        )
        logger.debug(f"Added topic node: {topic.id}")

    def add_relationship(self, relationship: Relationship):
        """
        Add a relationship edge to the graph.

        Args:
            relationship: Relationship to add
        """
        self.graph.add_edge(
            relationship.source,
            relationship.target,
            type=relationship.type,
            status=relationship.status,
            context=relationship.context,
            severity=relationship.severity
        )
        logger.debug(f"Added relationship: {relationship.source} -> {relationship.target}")

    def build_from_topics(self, topics: List[Topic]):
        """
        Build graph from list of topics.

        Args:
            topics: List of topics
        """
        for topic in topics:
            self.add_topic(topic)

        # Add hierarchical relationships
        for topic in topics:
            if topic.parent:
                self.add_relationship(Relationship(
                    source=topic.parent,
                    target=topic.id,
                    type="hierarchical",
                    status="valid"
                ))

            # Add cross-references
            for ref in topic.cross_references:
                self.add_relationship(Relationship(
                    source=topic.id,
                    target=ref,
                    type="cross_reference",
                    status="valid"  # Will be validated later
                ))

            # Add forward references
            for ref in topic.forward_references:
                self.add_relationship(Relationship(
                    source=topic.id,
                    target=ref,
                    type="forward_reference",
                    status="valid"
                ))

            # Add backward references
            for ref in topic.backward_references:
                self.add_relationship(Relationship(
                    source=topic.id,
                    target=ref,
                    type="backward_reference",
                    status="valid"
                ))

        logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def get_topic_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get hierarchical structure of topics.

        Returns:
            Dictionary mapping parent topics to children
        """
        hierarchy = {}
        for node in self.graph.nodes():
            children = [
                target for source, target, data in self.graph.edges(node, data=True)
                if data.get("type") == "hierarchical"
            ]
            if children:
                hierarchy[node] = children
        return hierarchy

    def find_broken_references(self) -> List[Relationship]:
        """
        Find broken references in the graph.

        Returns:
            List of broken relationships
        """
        broken = []
        for source, target, data in self.graph.edges(data=True):
            if target not in self.graph.nodes():
                broken.append(Relationship(
                    source=source,
                    target=target,
                    type=data.get("type", "unknown"),
                    status="broken",
                    context=data.get("context"),
                    severity="high"
                ))
        return broken

    def detect_circular_references(self) -> List[List[str]]:
        """
        Detect circular references in the graph.

        Returns:
            List of cycles (each cycle is a list of topic IDs)
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                logger.warning(f"Found {len(cycles)} circular references")
            return cycles
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return []

    def get_orphan_nodes(self) -> List[str]:
        """
        Find nodes with no incoming or outgoing edges.

        Returns:
            List of orphan topic IDs
        """
        orphans = [
            node for node in self.graph.nodes()
            if self.graph.in_degree(node) == 0 and self.graph.out_degree(node) == 0
        ]
        return orphans

    def get_topic_ancestors(self, topic_id: str) -> List[str]:
        """
        Get all ancestor topics in the hierarchy.

        Args:
            topic_id: Topic ID

        Returns:
            List of ancestor topic IDs
        """
        if topic_id not in self.graph:
            return []

        ancestors = []
        try:
            for node in self.graph.nodes():
                if nx.has_path(self.graph, node, topic_id):
                    # Check if it's a hierarchical path
                    path = nx.shortest_path(self.graph, node, topic_id)
                    if self._is_hierarchical_path(path):
                        ancestors.append(node)
        except Exception as e:
            logger.error(f"Error finding ancestors: {e}")

        return ancestors

    def _is_hierarchical_path(self, path: List[str]) -> bool:
        """Check if a path consists only of hierarchical edges."""
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data and edge_data.get("type") != "hierarchical":
                return False
        return True

    def export_to_dict(self) -> Dict:
        """
        Export graph to dictionary format.

        Returns:
            Dictionary representation of the graph
        """
        return {
            "nodes": [
                {"id": node, **self.graph.nodes[node]}
                for node in self.graph.nodes()
            ],
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in self.graph.edges(data=True)
            ]
        }

    def get_statistics(self) -> Dict:
        """
        Get graph statistics.

        Returns:
            Dictionary of graph statistics
        """
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "orphan_nodes": len(self.get_orphan_nodes()),
            "circular_references": len(self.detect_circular_references()),
            "average_degree": sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1)
        }
