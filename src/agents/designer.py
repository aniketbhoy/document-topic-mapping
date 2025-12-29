"""Architecture Designer Agent - Design navigation system architecture."""

from typing import List, Dict
from loguru import logger
from ..models import Topic, Anomaly
from ..utils import LLMClient, GraphBuilder


class ArchitectureDesignerAgent:
    """Agent responsible for designing navigation system architecture."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the designer agent.

        Args:
            llm_client: LLM client for design generation
        """
        self.llm_client = llm_client

    def design(
        self,
        topics: List[Topic],
        graph_builder: GraphBuilder,
        anomalies: List[Anomaly],
        output_path: str
    ):
        """
        Generate navigation system architecture design document.

        Args:
            topics: List of topics
            graph_builder: Graph builder with relationships
            anomalies: List of anomalies
            output_path: Output markdown file path
        """
        logger.info("Generating navigation architecture design")

        # Analyze document structure
        analysis = self._analyze_structure(topics, graph_builder, anomalies)

        # Generate design sections
        sections = []
        sections.append(self._create_overview(analysis))
        sections.append(self._create_system_architecture())
        sections.append(self._create_query_interface(analysis))
        sections.append(self._create_resolution_strategies(anomalies))
        sections.append(self._create_api_specification())
        sections.append(self._create_implementation_notes(analysis))

        # Combine and save
        document = "\n\n".join(sections)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(document)
            logger.info(f"Navigation architecture design saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save design document: {e}")
            raise

    def _analyze_structure(
        self,
        topics: List[Topic],
        graph_builder: GraphBuilder,
        anomalies: List[Anomaly]
    ) -> Dict:
        """Analyze document structure for design insights."""
        stats = graph_builder.get_statistics()

        return {
            "total_topics": len(topics),
            "total_relationships": stats["total_edges"],
            "max_depth": self._calculate_max_depth(topics),
            "avg_children": self._calculate_avg_children(topics),
            "anomaly_count": len(anomalies),
            "high_severity_anomalies": len([a for a in anomalies if a.severity in ["high", "critical"]]),
            "topics_with_references": len([t for t in topics if t.cross_references])
        }

    def _calculate_max_depth(self, topics: List[Topic]) -> int:
        """Calculate maximum hierarchy depth."""
        max_depth = 0
        for topic in topics:
            depth = len(topic.id.split('.'))
            max_depth = max(max_depth, depth)
        return max_depth

    def _calculate_avg_children(self, topics: List[Topic]) -> float:
        """Calculate average number of children per topic."""
        total_children = sum(len(t.children) for t in topics)
        topics_with_children = len([t for t in topics if t.children])
        return total_children / max(topics_with_children, 1)

    def _create_overview(self, analysis: Dict) -> str:
        """Create overview section."""
        return f"""# Navigation Agent Design Document

## 1. System Overview

This document outlines the architecture for an intelligent navigation system designed to help users navigate complex documents with hierarchical topic structures and cross-references.

### Document Statistics

- **Total Topics**: {analysis['total_topics']}
- **Total Relationships**: {analysis['total_relationships']}
- **Maximum Hierarchy Depth**: {analysis['max_depth']}
- **Average Children per Topic**: {analysis['avg_children']:.2f}
- **Topics with Cross-References**: {analysis['topics_with_references']}
- **Detected Anomalies**: {analysis['anomaly_count']} ({analysis['high_severity_anomalies']} high/critical)

### Key Challenges

1. **Non-sequential Numbering**: Document contains gaps in topic numbering
2. **Complex Cross-References**: Multiple types of references (forward, backward, hierarchical)
3. **Structural Anomalies**: Broken references and missing topics require graceful handling
4. **Ambiguity Resolution**: System must handle requests for non-existent topics
"""

    def _create_system_architecture(self) -> str:
        """Create system architecture section."""
        return """## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Agent                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Query      │───▶│   Semantic   │───▶│ Response  │ │
│  │   Parser     │    │   Search     │    │ Generator │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         │                    │                   │      │
│         └────────────────────┼───────────────────┘      │
│                              ▼                          │
│                    ┌──────────────────┐                 │
│                    │  Topic Knowledge  │                │
│                    │      Base        │                │
│                    │  • Topic Map     │                │
│                    │  • Graph DB      │                │
│                    │  • Embeddings    │                │
│                    └──────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 2.1 Query Parser
- Parses natural language queries
- Extracts topic IDs and intent
- Handles variations in query format

#### 2.2 Semantic Search
- Uses embeddings for fuzzy matching
- Finds related topics when exact match fails
- Handles synonyms and alternative phrasings

#### 2.3 Response Generator
- Constructs contextual responses
- Includes related topics and navigation paths
- Handles edge cases (missing topics, broken references)

#### 2.4 Topic Knowledge Base
- Stores topic map and relationships
- Maintains graph structure for traversal
- Caches embeddings for fast retrieval
"""

    def _create_query_interface(self, analysis: Dict) -> str:
        """Create query interface section."""
        return """## 3. Query Interface

### Supported Query Types

#### 3.1 Direct Topic Lookup
**Query**: "Show me topic 18.3"
**Response**: Returns topic content, parent, children, and related topics

#### 3.2 Topic Navigation
**Query**: "What topics are under section 18?"
**Response**: Lists all child topics with brief descriptions

#### 3.3 Cross-Reference Traversal
**Query**: "What topics reference 18.3?"
**Response**: Lists all topics that reference the target

#### 3.4 Hierarchical Navigation
**Query**: "Show me the parent of 18.3"
**Response**: Returns parent topic (18) with navigation context

#### 3.5 Semantic Search
**Query**: "Topics about risk assessment"
**Response**: Returns semantically similar topics ranked by relevance

#### 3.6 Path Finding
**Query**: "How do I get from topic 5 to topic 22?"
**Response**: Returns navigation path through document structure

### Query Response Format

```json
{
  "query": "Show me topic 18.3",
  "status": "success",
  "topic": {
    "id": "18.3",
    "title": "Risk Assessment Procedures",
    "content": "...",
    "confidence": 0.95
  },
  "context": {
    "parent": "18",
    "children": [],
    "cross_references": ["8.2", "12.1"],
    "forward_references": ["22.1"],
    "backward_references": ["30.4"]
  },
  "navigation": {
    "breadcrumb": ["1", "18", "18.3"],
    "next_topic": "18.4",
    "previous_topic": "18.2"
  }
}
```
"""

    def _create_resolution_strategies(self, anomalies: List[Anomaly]) -> str:
        """Create resolution strategies section."""
        strategies_text = """## 4. Edge Case Handling

### 4.1 Missing Topic References

**Scenario**: User requests topic 18.2, which doesn't exist

**Strategy**:
1. Detect that topic is missing from knowledge base
2. Check for similar topic IDs (18.1, 18.3)
3. Provide alternatives and context

**Response Format**:
```json
{
  "query": "Show me topic 18.2",
  "status": "not_found",
  "message": "Topic 18.2 does not exist in this document",
  "suggestions": [
    {
      "id": "18.1",
      "title": "...",
      "reason": "Previous topic in section 18"
    },
    {
      "id": "18.3",
      "title": "...",
      "reason": "Next topic in section 18"
    },
    {
      "id": "18",
      "title": "...",
      "reason": "Parent section"
    }
  ],
  "possible_reasons": [
    "Topic may have been renumbered",
    "Content may exist under different topic ID",
    "Topic may be referenced but not present in document"
  ]
}
```

### 4.2 Broken Cross-References

**Strategy**:
1. Identify broken references during validation
2. Store alternative navigation paths
3. Provide warnings in responses

### 4.3 Circular References

**Strategy**:
1. Detect cycles during graph construction
2. Limit traversal depth in navigation
3. Provide warnings about circular paths

### 4.4 Ambiguous Queries

**Strategy**:
1. Use semantic search to find multiple matches
2. Present ranked results with confidence scores
3. Ask for clarification when needed
"""

        # Add specific anomaly examples
        if anomalies:
            strategies_text += "\n### 4.5 Detected Anomalies in Current Document\n\n"
            for i, anomaly in enumerate(anomalies[:5], 1):
                strategies_text += f"{i}. **{anomaly.type}**: {anomaly.description}\n"
                if anomaly.resolution_strategies:
                    strategies_text += f"   - Resolution: {anomaly.resolution_strategies[0]}\n"

        return strategies_text

    def _create_api_specification(self) -> str:
        """Create API specification section."""
        return """## 5. API Specification

### 5.1 GET /topics/{topic_id}

Get specific topic by ID.

**Parameters**:
- `topic_id`: Topic identifier (e.g., "18.3")

**Response**: Topic object with context

### 5.2 GET /topics/{topic_id}/children

Get child topics.

**Parameters**:
- `topic_id`: Parent topic identifier

**Response**: List of child topics

### 5.3 GET /topics/{topic_id}/references

Get all references to/from a topic.

**Parameters**:
- `topic_id`: Topic identifier
- `direction`: "to" | "from" | "both"

**Response**: List of related topics with relationship types

### 5.4 POST /search

Semantic search for topics.

**Body**:
```json
{
  "query": "risk assessment procedures",
  "limit": 10,
  "threshold": 0.7
}
```

**Response**: Ranked list of matching topics

### 5.5 POST /navigate

Find navigation path between topics.

**Body**:
```json
{
  "from": "5",
  "to": "22.1",
  "strategy": "shortest" | "hierarchical"
}
```

**Response**: Navigation path with steps

### 5.6 GET /anomalies

Get list of detected anomalies.

**Response**: List of anomalies with severities

### 5.7 GET /statistics

Get document statistics.

**Response**: Document metadata and statistics
"""

    def _create_implementation_notes(self, analysis: Dict) -> str:
        """Create implementation notes section."""
        return f"""## 6. Implementation Recommendations

### 6.1 Technology Stack

**Backend**:
- FastAPI or Flask for REST API
- NetworkX for graph operations
- Redis for caching
- PostgreSQL with pg_vector for embeddings

**Frontend** (Optional):
- React or Vue.js for web interface
- D3.js for interactive graph visualization
- React Flow for navigation diagrams

### 6.2 Performance Optimizations

1. **Caching Strategy**
   - Cache frequently accessed topics
   - Pre-compute common navigation paths
   - Cache embedding similarity results

2. **Indexing**
   - Create indexes on topic IDs
   - Build inverted index for text search
   - Use HNSW for vector similarity search

3. **Lazy Loading**
   - Load topic content on demand
   - Paginate long topic lists
   - Stream large responses

### 6.3 Scalability Considerations

- **Current Document**: {analysis['total_topics']} topics (small scale)
- **Target Scale**: Up to 10,000 topics
- **Concurrent Users**: Design for 100+ simultaneous queries

### 6.4 Testing Strategy

1. **Unit Tests**
   - Query parsing accuracy
   - Navigation path correctness
   - Edge case handling

2. **Integration Tests**
   - End-to-end query flows
   - API response formats
   - Error handling

3. **Load Tests**
   - Response time under load
   - Cache effectiveness
   - Database query performance

### 6.5 Monitoring and Observability

- Log all queries and response times
- Track common query patterns
- Monitor cache hit rates
- Alert on anomaly detection issues

## 7. Future Enhancements

1. **Natural Language Understanding**
   - Support conversational queries
   - Handle multi-turn interactions
   - Learn from user feedback

2. **Personalization**
   - Track user navigation patterns
   - Suggest relevant topics
   - Customize response formats

3. **Multi-Document Support**
   - Cross-document references
   - Unified navigation across documents
   - Document comparison

4. **Collaborative Features**
   - Annotations and comments
   - Shared navigation sessions
   - Document versioning

## 8. Conclusion

This navigation system provides robust handling of complex document structures, including edge cases and anomalies. The architecture is designed for extensibility and can scale to support larger documents and additional features.

**Key Success Metrics**:
- Query response time < 200ms
- 95%+ accuracy in topic retrieval
- Graceful handling of 100% of edge cases
- User satisfaction score > 4.5/5
"""
