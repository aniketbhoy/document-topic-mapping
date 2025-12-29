"""Validator Agent - Detect anomalies and validate document structure."""

import csv
from typing import List, Dict, Set, Tuple
from loguru import logger
from ..models import Topic, Anomaly
from ..utils import LLMClient, GraphBuilder


class ValidatorAgent:
    """Agent responsible for validation and anomaly detection."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the validator agent.

        Args:
            llm_client: LLM client for resolution strategies
        """
        self.llm_client = llm_client

    def validate(self, topics: List[Topic], graph_builder: GraphBuilder) -> List[Anomaly]:
        """
        Validate document structure and detect anomalies.

        Args:
            topics: List of topics
            graph_builder: Graph builder with relationships

        Returns:
            List of detected anomalies
        """
        logger.info("Starting validation and anomaly detection")

        anomalies = []

        # Check numbering consistency
        anomalies.extend(self._check_numbering_gaps(topics))

        # Validate cross-references
        anomalies.extend(self._validate_cross_references(topics))

        # Detect circular references
        anomalies.extend(self._detect_circular_references(graph_builder))

        # Find orphan content
        anomalies.extend(self._find_orphan_content(graph_builder))

        # Check for duplicate topics
        anomalies.extend(self._check_duplicates(topics))

        logger.info(f"Found {len(anomalies)} anomalies")

        # Generate resolution strategies for high-severity anomalies
        self._generate_resolution_strategies(anomalies)

        return anomalies

    def _check_numbering_gaps(self, topics: List[Topic]) -> List[Anomaly]:
        """
        Check for missing topic numbers in sequences.

        Args:
            topics: List of topics

        Returns:
            List of numbering gap anomalies
        """
        anomalies = []

        # Group topics by their parent
        topic_groups = {}
        for topic in topics:
            parent = topic.parent or "root"
            if parent not in topic_groups:
                topic_groups[parent] = []
            topic_groups[parent].append(topic.id)

        # Check each group for gaps
        for parent, children in topic_groups.items():
            # Extract numeric parts
            numeric_children = []
            for child_id in children:
                try:
                    # Get the last numeric part
                    parts = child_id.split('.')
                    if parts[-1].isdigit():
                        numeric_children.append((int(parts[-1]), child_id))
                except (ValueError, IndexError):
                    continue

            if not numeric_children:
                continue

            numeric_children.sort()

            # Check for gaps
            for i in range(len(numeric_children) - 1):
                current_num, current_id = numeric_children[i]
                next_num, next_id = numeric_children[i + 1]

                if next_num - current_num > 1:
                    # Found a gap
                    missing_nums = list(range(current_num + 1, next_num))
                    for missing_num in missing_nums:
                        missing_id = self._construct_missing_id(current_id, missing_num)

                        anomaly = Anomaly(
                            type="numbering_gap",
                            location=f"Between {current_id} and {next_id}",
                            severity="high",
                            description=f"Missing topic {missing_id} in sequence",
                            affected_topics=[current_id, next_id]
                        )
                        anomalies.append(anomaly)
                        logger.warning(f"Numbering gap detected: {missing_id}")

        return anomalies

    def _construct_missing_id(self, reference_id: str, missing_num: int) -> str:
        """Construct the ID of a missing topic."""
        parts = reference_id.split('.')
        parts[-1] = str(missing_num)
        return '.'.join(parts)

    def _validate_cross_references(self, topics: List[Topic]) -> List[Anomaly]:
        """
        Validate that all cross-references point to existing topics.

        Args:
            topics: List of topics

        Returns:
            List of broken reference anomalies
        """
        anomalies = []
        topic_ids = {topic.id for topic in topics}

        for topic in topics:
            all_refs = (
                topic.cross_references +
                topic.forward_references +
                topic.backward_references
            )

            for ref_id in all_refs:
                if ref_id not in topic_ids:
                    anomaly = Anomaly(
                        type="broken_cross_reference",
                        location=f"{topic.id} → {ref_id}",
                        severity="high",
                        description=f"Topic {topic.id} references {ref_id}, which does not exist",
                        affected_topics=[topic.id]
                    )
                    anomalies.append(anomaly)
                    logger.warning(f"Broken reference: {topic.id} → {ref_id}")

        return anomalies

    def _detect_circular_references(self, graph_builder: GraphBuilder) -> List[Anomaly]:
        """
        Detect circular references in the graph.

        Args:
            graph_builder: Graph builder

        Returns:
            List of circular reference anomalies
        """
        anomalies = []
        cycles = graph_builder.detect_circular_references()

        for cycle in cycles:
            anomaly = Anomaly(
                type="circular_reference",
                location=" → ".join(cycle + [cycle[0]]),
                severity="medium",
                description=f"Circular reference detected involving {len(cycle)} topics",
                affected_topics=cycle
            )
            anomalies.append(anomaly)
            logger.warning(f"Circular reference: {' → '.join(cycle)}")

        return anomalies

    def _find_orphan_content(self, graph_builder: GraphBuilder) -> List[Anomaly]:
        """
        Find topics with no connections.

        Args:
            graph_builder: Graph builder

        Returns:
            List of orphan content anomalies
        """
        anomalies = []
        orphans = graph_builder.get_orphan_nodes()

        for orphan_id in orphans:
            anomaly = Anomaly(
                type="orphan_content",
                location=orphan_id,
                severity="low",
                description=f"Topic {orphan_id} has no connections to other topics",
                affected_topics=[orphan_id]
            )
            anomalies.append(anomaly)
            logger.info(f"Orphan topic: {orphan_id}")

        return anomalies

    def _check_duplicates(self, topics: List[Topic]) -> List[Anomaly]:
        """
        Check for duplicate topic IDs.

        Args:
            topics: List of topics

        Returns:
            List of duplicate anomalies
        """
        anomalies = []
        seen_ids = {}

        for topic in topics:
            if topic.id in seen_ids:
                anomaly = Anomaly(
                    type="duplicate_topic",
                    location=topic.id,
                    severity="critical",
                    description=f"Duplicate topic ID: {topic.id}",
                    affected_topics=[topic.id]
                )
                anomalies.append(anomaly)
                logger.error(f"Duplicate topic ID: {topic.id}")
            else:
                seen_ids[topic.id] = topic

        return anomalies

    def _generate_resolution_strategies(self, anomalies: List[Anomaly]):
        """
        Generate resolution strategies for anomalies using LLM.

        Args:
            anomalies: List of anomalies
        """
        for anomaly in anomalies:
            if anomaly.severity in ["high", "critical"]:
                strategies = self._llm_generate_strategies(anomaly)
                anomaly.resolution_strategies = strategies

    def _llm_generate_strategies(self, anomaly: Anomaly) -> List[str]:
        """
        Use LLM to generate resolution strategies.

        Args:
            anomaly: Anomaly to resolve

        Returns:
            List of resolution strategies
        """
        try:
            prompt = f"""
Analyze this document structure anomaly and suggest 3-5 concrete resolution strategies:

Type: {anomaly.type}
Location: {anomaly.location}
Description: {anomaly.description}
Affected Topics: {', '.join(anomaly.affected_topics)}

Provide specific, actionable strategies to resolve this issue. Consider:
- Possible renumbering errors
- Content that may have been missed
- Alternative navigation approaches
- Document structure corrections

Format your response as a numbered list.
"""
            response = self.llm_client.call_gpt4(
                prompt,
                system_message="You are a document structure expert. Provide clear, actionable resolution strategies."
            )

            # Parse strategies from response
            strategies = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    clean_line = line.lstrip('0123456789.-) ')
                    if clean_line:
                        strategies.append(clean_line)

            return strategies[:5]  # Limit to 5 strategies
        except Exception as e:
            logger.error(f"Failed to generate resolution strategies: {e}")
            return ["Manual review required"]

    def save_anomaly_report(self, anomalies: List[Anomaly], output_path: str):
        """
        Save anomaly report to CSV file.

        Args:
            anomalies: List of anomalies
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "Type",
                    "Location",
                    "Severity",
                    "Description",
                    "Affected Topics",
                    "Resolution Strategies"
                ])

                # Write anomalies
                for anomaly in anomalies:
                    writer.writerow([
                        anomaly.type,
                        anomaly.location,
                        anomaly.severity,
                        anomaly.description,
                        "; ".join(anomaly.affected_topics),
                        " | ".join(anomaly.resolution_strategies)
                    ])

            logger.info(f"Anomaly report saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save anomaly report: {e}")
            raise
