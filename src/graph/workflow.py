"""LangGraph workflow orchestration for the semantic topic mapping pipeline."""

from typing import TypedDict, List, Dict, Annotated
import operator
from loguru import logger
from langgraph.graph import StateGraph, END
from ..models import Topic, Anomaly
from ..utils import DocumentLoader, LLMClient, GraphBuilder
from ..agents import (
    DocumentParserAgent,
    RelationshipMapperAgent,
    ValidatorAgent,
    VisualizerAgent,
    ArchitectureDesignerAgent
)


class PipelineState(TypedDict):
    """State object for the pipeline workflow."""

    # Input
    file_path: str
    output_dir: str

    # Document data
    document_text: str
    document_metadata: Dict

    # Processing results
    topics: Annotated[List[Topic], operator.add]
    graph_builder: GraphBuilder
    topic_map: Dict
    anomalies: List[Anomaly]

    # Output paths
    topic_map_path: str
    graph_pdf_path: str
    design_doc_path: str
    anomaly_report_path: str

    # Status
    current_phase: str
    error: str


class SemanticTopicMappingWorkflow:
    """LangGraph workflow for semantic topic mapping."""

    def __init__(self):
        """Initialize the workflow."""
        self.llm_client = LLMClient()
        self.document_loader = DocumentLoader()

        # Initialize agents
        self.parser_agent = DocumentParserAgent(self.llm_client)
        self.mapper_agent = RelationshipMapperAgent(self.llm_client)
        self.validator_agent = ValidatorAgent(self.llm_client)
        self.visualizer_agent = VisualizerAgent()
        self.designer_agent = ArchitectureDesignerAgent(self.llm_client)

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(PipelineState)

        # Add nodes for each phase
        workflow.add_node("load_document", self._load_document)
        workflow.add_node("parse_topics", self._parse_topics)
        workflow.add_node("extract_references", self._extract_references)
        workflow.add_node("map_relationships", self._map_relationships)
        workflow.add_node("validate", self._validate)
        workflow.add_node("visualize", self._visualize)
        workflow.add_node("design_architecture", self._design_architecture)

        # Define workflow edges
        workflow.set_entry_point("load_document")
        workflow.add_edge("load_document", "parse_topics")
        workflow.add_edge("parse_topics", "extract_references")
        workflow.add_edge("extract_references", "map_relationships")
        workflow.add_edge("map_relationships", "validate")
        workflow.add_edge("validate", "visualize")
        workflow.add_edge("visualize", "design_architecture")
        workflow.add_edge("design_architecture", END)

        return workflow.compile()

    def _load_document(self, state: PipelineState) -> PipelineState:
        """
        Phase 1: Load and extract document content.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 1: Loading document")
        state["current_phase"] = "loading"

        try:
            text, metadata = self.document_loader.load_document(state["file_path"])
            state["document_text"] = text
            state["document_metadata"] = metadata
            logger.info(f"Document loaded: {metadata['character_count']} characters")
        except Exception as e:
            logger.error(f"Document loading failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _parse_topics(self, state: PipelineState) -> PipelineState:
        """
        Phase 2: Parse document and extract topics.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 2: Parsing topics")
        state["current_phase"] = "parsing"

        try:
            topics = self.parser_agent.parse(
                state["document_text"],
                state["document_metadata"]
            )
            state["topics"] = topics
            logger.info(f"Parsed {len(topics)} topics")
        except Exception as e:
            logger.error(f"Topic parsing failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _extract_references(self, state: PipelineState) -> PipelineState:
        """
        Phase 2.5: Extract cross-references from topics.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 2.5: Extracting cross-references")

        try:
            topics_with_refs = self.parser_agent.extract_cross_references(state["topics"])
            state["topics"] = topics_with_refs
            total_refs = sum(len(t.cross_references) for t in topics_with_refs)
            logger.info(f"Extracted {total_refs} cross-references")
        except Exception as e:
            logger.error(f"Reference extraction failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _map_relationships(self, state: PipelineState) -> PipelineState:
        """
        Phase 3: Build topic relationship map.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 3: Mapping relationships")
        state["current_phase"] = "mapping"

        try:
            graph_builder, topic_map = self.mapper_agent.map_relationships(state["topics"])
            state["graph_builder"] = graph_builder
            state["topic_map"] = topic_map

            # Save topic map
            topic_map_path = f"{state['output_dir']}/topic_map.json"
            self.mapper_agent.save_topic_map(topic_map, topic_map_path)
            state["topic_map_path"] = topic_map_path

            logger.info("Relationship mapping complete")
        except Exception as e:
            logger.error(f"Relationship mapping failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _validate(self, state: PipelineState) -> PipelineState:
        """
        Phase 4: Validate structure and detect anomalies.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 4: Validating and detecting anomalies")
        state["current_phase"] = "validating"

        try:
            anomalies = self.validator_agent.validate(
                state["topics"],
                state["graph_builder"]
            )
            state["anomalies"] = anomalies

            # Save anomaly report
            anomaly_report_path = f"{state['output_dir']}/ambiguity_report.csv"
            self.validator_agent.save_anomaly_report(anomalies, anomaly_report_path)
            state["anomaly_report_path"] = anomaly_report_path

            logger.info(f"Validation complete: {len(anomalies)} anomalies detected")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _visualize(self, state: PipelineState) -> PipelineState:
        """
        Phase 5: Generate visualizations.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 5: Generating visualizations")
        state["current_phase"] = "visualizing"

        try:
            graph_pdf_path = f"{state['output_dir']}/cross_reference_graph.pdf"
            self.visualizer_agent.generate_multiple_views(
                state["graph_builder"],
                state["anomalies"],
                graph_pdf_path
            )
            state["graph_pdf_path"] = graph_pdf_path

            logger.info("Visualization complete")
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def _design_architecture(self, state: PipelineState) -> PipelineState:
        """
        Phase 6: Design navigation architecture.

        Args:
            state: Current pipeline state

        Returns:
            Updated state
        """
        logger.info("Phase 6: Designing navigation architecture")
        state["current_phase"] = "designing"

        try:
            design_doc_path = f"{state['output_dir']}/navigation_agent_design.md"
            self.designer_agent.design(
                state["topics"],
                state["graph_builder"],
                state["anomalies"],
                design_doc_path
            )
            state["design_doc_path"] = design_doc_path

            logger.info("Architecture design complete")
        except Exception as e:
            logger.error(f"Architecture design failed: {e}")
            state["error"] = str(e)
            raise

        return state

    def run(self, file_path: str, output_dir: str = "./outputs") -> PipelineState:
        """
        Run the complete pipeline.

        Args:
            file_path: Path to input document
            output_dir: Output directory for results

        Returns:
            Final pipeline state
        """
        logger.info("=" * 60)
        logger.info("Starting Semantic Topic Mapping Pipeline")
        logger.info("=" * 60)

        # Initialize state
        initial_state = PipelineState(
            file_path=file_path,
            output_dir=output_dir,
            document_text="",
            document_metadata={},
            topics=[],
            graph_builder=None,
            topic_map={},
            anomalies=[],
            topic_map_path="",
            graph_pdf_path="",
            design_doc_path="",
            anomaly_report_path="",
            current_phase="initialized",
            error=""
        )

        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)

            logger.info("=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 60)
            logger.info(f"Outputs:")
            logger.info(f"  - Topic Map: {final_state['topic_map_path']}")
            logger.info(f"  - Graph Visualization: {final_state['graph_pdf_path']}")
            logger.info(f"  - Architecture Design: {final_state['design_doc_path']}")
            logger.info(f"  - Anomaly Report: {final_state['anomaly_report_path']}")
            logger.info("=" * 60)

            return final_state
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
