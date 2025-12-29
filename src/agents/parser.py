"""Document Parser Agent - Extract and structure document content."""

import re
from typing import List, Dict, Optional, Tuple
from loguru import logger
from ..models import Topic, TopicPosition
from ..utils import LLMClient


class DocumentParserAgent:
    """Agent responsible for parsing documents and extracting topics."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the parser agent.

        Args:
            llm_client: LLM client for validation
        """
        self.llm_client = llm_client

        # Regex patterns for topic detection
        self.topic_patterns = [
            r'^(\d+(?:\.\d+)*(?:\.[a-z])?)\s+(.+?)$',  # 18.3, 5.1.a
            r'^([IVX]+(?:\.[IVX]+)*)\s+(.+?)$',  # Roman numerals
            r'^([A-Z](?:\.[A-Z])*)\s+(.+?)$',  # A, A.B
        ]

    def parse(self, text: str, metadata: Dict) -> List[Topic]:
        """
        Parse document and extract all topics.

        Args:
            text: Document text content
            metadata: Document metadata

        Returns:
            List of extracted topics
        """
        logger.info("Starting document parsing")

        # Split into lines for processing
        lines = text.split('\n')

        # Extract potential topics
        raw_topics = self._extract_raw_topics(lines)
        logger.info(f"Found {len(raw_topics)} potential topics")

        # Validate and structure topics
        validated_topics = self._validate_topics(raw_topics)
        logger.info(f"Validated {len(validated_topics)} topics")

        # Build hierarchical relationships
        topics_with_hierarchy = self._build_hierarchy(validated_topics)

        return topics_with_hierarchy

    def _extract_raw_topics(self, lines: List[str]) -> List[Dict]:
        """
        Extract potential topics using regex patterns.

        Args:
            lines: Document lines

        Returns:
            List of raw topic dictionaries
        """
        raw_topics = []
        position = 0

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                position += 1
                continue

            # Try each pattern
            for pattern in self.topic_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    topic_id = match.group(1)
                    title = match.group(2).strip()

                    # Extract content (next few lines until next topic)
                    content = self._extract_topic_content(lines, line_num + 1)

                    raw_topics.append({
                        "id": topic_id,
                        "title": title,
                        "content": content,
                        "position": {
                            "start": position,
                            "end": position + len(content)
                        },
                        "line_num": line_num
                    })
                    break

            position += len(line) + 1

        return raw_topics

    def _extract_topic_content(self, lines: List[str], start_idx: int) -> str:
        """
        Extract content for a topic until the next topic marker.

        Args:
            lines: All document lines
            start_idx: Starting line index

        Returns:
            Topic content
        """
        content_lines = []

        for i in range(start_idx, len(lines)):
            line = lines[i].strip()

            # Check if this is a new topic
            is_new_topic = False
            for pattern in self.topic_patterns:
                if re.match(pattern, line):
                    is_new_topic = True
                    break

            if is_new_topic:
                break

            if line:
                content_lines.append(line)

            # Limit content length
            if len(content_lines) > 100:
                break

        return " ".join(content_lines)

    def _validate_topics(self, raw_topics: List[Dict]) -> List[Topic]:
        """
        Validate topics using LLM for ambiguous cases.

        Args:
            raw_topics: Raw extracted topics

        Returns:
            List of validated Topic objects
        """
        validated_topics = []

        for raw_topic in raw_topics:
            # Simple validation
            if len(raw_topic["title"]) < 3:
                logger.warning(f"Skipping topic with short title: {raw_topic['id']}")
                continue

            # Create Topic object
            topic = Topic(
                id=raw_topic["id"],
                title=raw_topic["title"],
                content=raw_topic["content"],
                position=TopicPosition(**raw_topic["position"]),
                confidence=0.95  # High confidence for regex matches
            )

            # For ambiguous cases, validate with LLM
            if self._is_ambiguous(topic):
                confidence = self._llm_validate_topic(topic)
                topic.confidence = confidence

                if confidence < 0.5:
                    logger.warning(f"Low confidence topic: {topic.id} ({confidence})")
                    continue

            validated_topics.append(topic)

        return validated_topics

    def _is_ambiguous(self, topic: Topic) -> bool:
        """Check if a topic is ambiguous and needs LLM validation."""
        # Check for very short content
        if len(topic.content) < 20:
            return True

        # Check for unusual numbering
        if not re.match(r'^\d+(?:\.\d+)*(?:\.[a-z])?$', topic.id):
            return True

        return False

    def _llm_validate_topic(self, topic: Topic) -> float:
        """
        Use LLM to validate ambiguous topics.

        Args:
            topic: Topic to validate

        Returns:
            Confidence score (0-1)
        """
        try:
            prompt = f"""
Analyze if this is a valid document topic/section:

ID: {topic.id}
Title: {topic.title}
Content: {topic.content[:200]}

Respond with a confidence score between 0 and 1, where:
- 1.0 = Definitely a valid topic
- 0.5 = Unclear
- 0.0 = Not a valid topic

Just respond with the number.
"""
            response = self.llm_client.call_gpt35(prompt)
            confidence = float(response.strip())
            return max(0.0, min(1.0, confidence))
        except Exception as e:
            logger.error(f"LLM validation failed: {e}")
            return 0.7  # Default to moderate confidence

    def _build_hierarchy(self, topics: List[Topic]) -> List[Topic]:
        """
        Build parent-child relationships between topics.

        Args:
            topics: List of topics

        Returns:
            Topics with hierarchy populated
        """
        # Create mapping of topic IDs
        topic_map = {topic.id: topic for topic in topics}

        for topic in topics:
            # Find parent based on numbering
            parent_id = self._find_parent_id(topic.id)
            if parent_id and parent_id in topic_map:
                topic.parent = parent_id
                topic_map[parent_id].children.append(topic.id)

        return topics

    def _find_parent_id(self, topic_id: str) -> Optional[str]:
        """
        Find parent topic ID based on numbering hierarchy.

        Args:
            topic_id: Topic ID (e.g., "18.3")

        Returns:
            Parent topic ID or None
        """
        # For numeric topics like "18.3" -> parent is "18"
        parts = topic_id.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])

        return None

    def extract_cross_references(self, topics: List[Topic]) -> List[Topic]:
        """
        Extract cross-references from topic content.

        Args:
            topics: List of topics

        Returns:
            Topics with cross-references populated
        """
        # Pattern for cross-references
        ref_patterns = [
            r'(?:see|refer to|as in|discussed in)\s+(?:topic|section)\s+(\d+(?:\.\d+)*(?:\.[a-z])?)',
            r'(?:topic|section)\s+(\d+(?:\.\d+)*(?:\.[a-z])?)',
            r'\((\d+(?:\.\d+)*(?:\.[a-z])?)\)'
        ]

        for topic in topics:
            content_lower = topic.content.lower()

            for pattern in ref_patterns:
                matches = re.finditer(pattern, content_lower)
                for match in matches:
                    ref_id = match.group(1)
                    if ref_id != topic.id:  # Don't self-reference
                        # Determine if forward or backward reference
                        if self._is_forward_reference(topic.id, ref_id):
                            if ref_id not in topic.forward_references:
                                topic.forward_references.append(ref_id)
                        else:
                            if ref_id not in topic.backward_references:
                                topic.backward_references.append(ref_id)

                        if ref_id not in topic.cross_references:
                            topic.cross_references.append(ref_id)

        return topics

    def _is_forward_reference(self, source_id: str, target_id: str) -> bool:
        """
        Check if target is a forward reference from source.

        Args:
            source_id: Source topic ID
            target_id: Target topic ID

        Returns:
            True if target comes after source
        """
        try:
            source_num = float(source_id.split('.')[0])
            target_num = float(target_id.split('.')[0])
            return target_num > source_num
        except (ValueError, IndexError):
            return False
