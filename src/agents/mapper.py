"""Relationship Mapper Agent - Build topic relationship graphs."""

import json
from typing import List, Dict, Tuple
from loguru import logger
import numpy as np
from ..models import Topic, Relationship
from ..utils import LLMClient, GraphBuilder


class RelationshipMapperAgent:
    """Agent responsible for mapping relationships between topics."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the mapper agent.

        Args:
            llm_client: LLM client for semantic analysis
        """
        self.llm_client = llm_client
        self.graph_builder = GraphBuilder()

    def map_relationships(self, topics: List[Topic]) -> Tuple[GraphBuilder, Dict]:
        """
        Build complete topic relationship map.

        Args:
            topics: List of topics

        Returns:
            Tuple of (GraphBuilder, topic_map_dict)
        """
        logger.info("Starting relationship mapping")

        # Build graph from topics
        self.graph_builder.build_from_topics(topics)

        # Detect implicit references using semantic analysis
        implicit_refs = self._detect_implicit_references(topics)
        logger.info(f"Found {len(implicit_refs)} implicit references")

        for ref in implicit_refs:
            self.graph_builder.add_relationship(ref)

        # Create topic map dictionary
        topic_map = self._create_topic_map(topics)

        return self.graph_builder, topic_map

    def _detect_implicit_references(self, topics: List[Topic]) -> List[Relationship]:
        """
        Detect implicit references using semantic similarity.

        Args:
            topics: List of topics

        Returns:
            List of implicit relationships
        """
        implicit_refs = []

        # Get embeddings for all topics
        topic_embeddings = {}
        for topic in topics:
            # Combine title and content for embedding
            text = f"{topic.title} {topic.content[:500]}"
            try:
                embedding = self.llm_client.get_embedding(text)
                topic_embeddings[topic.id] = embedding
            except Exception as e:
                logger.error(f"Failed to get embedding for {topic.id}: {e}")

        # Calculate similarities
        similarity_threshold = 0.75  # High threshold for implicit references

        for topic in topics:
            if topic.id not in topic_embeddings:
                continue

            source_embedding = topic_embeddings[topic.id]

            for other_topic in topics:
                if topic.id == other_topic.id:
                    continue

                if other_topic.id not in topic_embeddings:
                    continue

                # Skip if already explicitly referenced
                if other_topic.id in topic.cross_references:
                    continue

                # Calculate cosine similarity
                target_embedding = topic_embeddings[other_topic.id]
                similarity = self._cosine_similarity(source_embedding, target_embedding)

                if similarity >= similarity_threshold:
                    # Verify with LLM
                    if self._llm_verify_implicit_reference(topic, other_topic):
                        implicit_refs.append(Relationship(
                            source=topic.id,
                            target=other_topic.id,
                            type="cross_reference",
                            status="valid",
                            context=f"Implicit semantic similarity: {similarity:.2f}"
                        ))
                        logger.debug(f"Implicit reference: {topic.id} -> {other_topic.id}")

        return implicit_refs

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0

    def _llm_verify_implicit_reference(self, topic1: Topic, topic2: Topic) -> bool:
        """
        Use LLM to verify if there's an implicit relationship.

        Args:
            topic1: Source topic
            topic2: Target topic

        Returns:
            True if relationship is verified
        """
        try:
            prompt = f"""
Analyze if there's a meaningful relationship between these two document topics:

Topic 1: {topic1.id} - {topic1.title}
Content: {topic1.content[:300]}

Topic 2: {topic2.id} - {topic2.title}
Content: {topic2.content[:300]}

Does Topic 1 implicitly reference or relate to Topic 2? Consider:
- Similar concepts or terminology
- Related procedures or processes
- Dependencies or prerequisites

Answer with just "yes" or "no".
"""
            response = self.llm_client.call_gpt35(prompt).strip().lower()
            return response == "yes"
        except Exception as e:
            logger.error(f"LLM verification failed: {e}")
            return False

    def _create_topic_map(self, topics: List[Topic]) -> Dict:
        """
        Create structured topic map dictionary.

        Args:
            topics: List of topics

        Returns:
            Topic map dictionary
        """
        topic_map = {
            "metadata": {
                "total_topics": len(topics),
                "version": "1.0"
            },
            "topics": {},
            "hierarchy": self.graph_builder.get_topic_hierarchy(),
            "statistics": self.graph_builder.get_statistics()
        }

        for topic in topics:
            topic_map["topics"][topic.id] = {
                "id": topic.id,
                "title": topic.title,
                "content": topic.content,
                "parent": topic.parent,
                "children": topic.children,
                "cross_references": topic.cross_references,
                "forward_references": topic.forward_references,
                "backward_references": topic.backward_references,
                "position": {
                    "start": topic.position.start if topic.position else 0,
                    "end": topic.position.end if topic.position else 0
                },
                "confidence": topic.confidence
            }

        return topic_map

    def save_topic_map(self, topic_map: Dict, output_path: str):
        """
        Save topic map to JSON file.

        Args:
            topic_map: Topic map dictionary
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(topic_map, f, indent=2, ensure_ascii=False)
            logger.info(f"Topic map saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save topic map: {e}")
            raise

    def load_topic_map(self, input_path: str) -> Dict:
        """
        Load topic map from JSON file.

        Args:
            input_path: Input file path

        Returns:
            Topic map dictionary
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                topic_map = json.load(f)
            logger.info(f"Topic map loaded from {input_path}")
            return topic_map
        except Exception as e:
            logger.error(f"Failed to load topic map: {e}")
            raise
