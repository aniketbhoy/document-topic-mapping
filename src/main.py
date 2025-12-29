"""Main entry point for the Semantic Topic Mapping system."""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
from .graph import SemanticTopicMappingWorkflow


def setup_logging(verbose: bool = False):
    """
    Configure logging.

    Args:
        verbose: Enable verbose logging
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    if verbose:
        log_level = "DEBUG"

    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )


def validate_inputs(input_path: str, output_dir: str) -> tuple:
    """
    Validate input parameters.

    Args:
        input_path: Input document path
        output_dir: Output directory path

    Returns:
        Tuple of (validated_input_path, validated_output_dir)

    Raises:
        ValueError: If validation fails
    """
    # Check input file
    input_file = Path(input_path)
    if not input_file.exists():
        raise ValueError(f"Input file not found: {input_path}")

    if input_file.suffix.lower() not in [".docx", ".pdf"]:
        raise ValueError(f"Unsupported file format: {input_file.suffix}. Use .docx or .pdf")

    # Create output directory if needed
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    return str(input_file.absolute()), str(output_path.absolute())


def check_api_key():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("=" * 60)
        logger.warning("WARNING: OpenAI API key not configured!")
        logger.warning("Please set OPENAI_API_KEY in the .env file")
        logger.warning("The system will attempt to run but LLM features may fail")
        logger.warning("=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Semantic Topic Mapping - Extract topics, map relationships, and detect anomalies in documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a document
  python -m src.main --input document.docx --output ./outputs

  # Process with verbose logging
  python -m src.main --input document.pdf --output ./results --verbose

  # Process a specific document
  python -m src.main --input RE_Task1.docx

For more information, see the README.md file.
        """
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input document (.docx or .pdf)"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./outputs",
        help="Output directory for results (default: ./outputs)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    logger.info("Semantic Topic Mapping System")
    logger.info("=" * 60)

    try:
        # Check API key
        check_api_key()

        # Validate inputs
        input_path, output_dir = validate_inputs(args.input, args.output)

        logger.info(f"Input document: {input_path}")
        logger.info(f"Output directory: {output_dir}")

        # Create and run workflow
        workflow = SemanticTopicMappingWorkflow()
        final_state = workflow.run(input_path, output_dir)

        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Topics extracted: {len(final_state['topics'])}")
        logger.info(f"Relationships mapped: {final_state['topic_map']['metadata']['total_topics']}")
        logger.info(f"Anomalies detected: {len(final_state['anomalies'])}")
        logger.info("")
        logger.info("Deliverables:")
        logger.info(f"  1. topic_map.json         -> {final_state['topic_map_path']}")
        logger.info(f"  2. cross_reference_graph.pdf -> {final_state['graph_pdf_path']}")
        logger.info(f"  3. navigation_agent_design.md -> {final_state['design_doc_path']}")
        logger.info(f"  4. ambiguity_report.csv   -> {final_state['anomaly_report_path']}")
        logger.info("=" * 60)
        logger.info("SUCCESS: All deliverables generated!")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
