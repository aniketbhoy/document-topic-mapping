# Semantic Topic Mapping System

An intelligent document navigation system that extracts topics, maps relationships, detects anomalies, and creates visual navigation tools for complex documents using LangGraph and OpenAI.

## Features

- **Comprehensive Topic Extraction**: Handles sequential and non-sequential numbering
- **Smart OCR**: Automatically detects and processes image-based PDFs using OpenAI Vision API
- **Relationship Mapping**: Builds hierarchical structures and cross-references
- **Anomaly Detection**: Identifies missing topics, broken references, and structural issues
- **Visual Graphs**: Generates PDF visualizations of topic relationships
- **Navigation Architecture**: Designs intelligent navigation system specifications
- **LangGraph Orchestration**: Multi-agent workflow with state management

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (required for both text analysis and image-based PDF processing)

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd /mnt/e/Placements_2026/assignment_hobasa
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API key**:
   Edit the `.env` file and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Install Graphviz** (required for visualizations):
   - **Ubuntu/Debian**: `sudo apt-get install graphviz`
   - **macOS**: `brew install graphviz`
   - **Windows**: Download from [graphviz.org](https://graphviz.org/download/)

   **Note**: The system automatically detects if a PDF contains text or is image-based, and uses OpenAI Vision API for OCR when needed. **No additional system packages needed** - PyMuPDF is pure Python!

## Usage

### Basic Usage

Process a document and generate all deliverables:

```bash
python -m src.main --input document.docx --output ./outputs
```

### Process Existing Documents

Process one of the sample documents:

```bash
# Process RE_Task1.docx
python -m src.main --input RE_Task1.docx --output ./outputs

# Process ZCPP_2 1.pdf
python -m src.main --input "ZCPP_2 1.pdf" --output ./outputs

# Process RE_Task6.docx
python -m src.main --input RE_Task6.docx --output ./outputs
```

### Verbose Mode

Enable detailed logging:

```bash
python -m src.main --input document.docx --output ./outputs --verbose
```

### Command-Line Options

```
--input, -i    Path to input document (.docx or .pdf) [REQUIRED]
--output, -o   Output directory for results (default: ./outputs)
--verbose, -v  Enable verbose logging
```

## Output Files

The system generates four deliverables:

1. **`topic_map.json`**: Complete hierarchical structure with all topics and relationships
2. **`cross_reference_graph.pdf`**: Visual graph representation with color-coded relationships
3. **`navigation_agent_design.md`**: Navigation system architecture specification
4. **`ambiguity_report.csv`**: Detected anomalies with severity levels and resolution strategies

## OCR Support for Image-Based PDFs

### Automatic Detection

The system **automatically detects** whether a PDF contains:
- **Text layer**: Extracts text directly (fast, accurate)
- **Images only**: Uses OpenAI Vision API to extract text (handles scanned documents)

### How It Works

1. **First Attempt**: Try to extract text directly from PDF
2. **Detection**: If less than 100 characters are found, PDF is likely image-based
3. **Vision API Fallback**: Automatically converts PDF pages to images and uses GPT-4 Vision for OCR
4. **Progress Logging**: Shows OCR progress for each page

### Example Output

```
Loading PDF file: scanned_document.pdf
PDF appears to be image-based (no text layer detected)
Attempting OCR extraction...
Starting OCR extraction using OpenAI Vision API for: scanned_document.pdf
Converting PDF pages to images...
Processing page 1/10 with OpenAI Vision API...
Processing page 2/10 with OpenAI Vision API...
...
OCR extraction complete: 10 pages processed
Extracted 15,234 characters
```

### Advantages of OpenAI Vision API

- **No System Dependencies**: No need to install Tesseract or other OCR software
- **High Accuracy**: GPT-4 Vision provides excellent text recognition
- **Multi-Language Support**: Automatically handles multiple languages
- **Better Layout Understanding**: Preserves formatting and structure better than traditional OCR
- **Handles Complex Documents**: Works well with tables, multi-column layouts, and mixed content

### Performance & Cost Notes

- **Text-based PDF**: ~1-2 seconds per page (no API cost)
- **Image-based PDF (Vision API)**: ~3-5 seconds per page
- **API Cost**: Approximately $0.01-0.02 per page for image-based PDFs
- Large image-based documents will incur OpenAI API costs based on the number of pages

## Project Structure

```
assignment_hobasa/
├── src/
│   ├── agents/          # 5 specialized agents
│   │   ├── parser.py           # Document Parser Agent
│   │   ├── mapper.py           # Relationship Mapper Agent
│   │   ├── validator.py        # Validator Agent
│   │   ├── visualizer.py       # Visualizer Agent
│   │   └── designer.py         # Architecture Designer Agent
│   ├── models/          # Pydantic data models
│   │   ├── topic.py
│   │   ├── relationship.py
│   │   └── anomaly.py
│   ├── utils/           # Utility functions
│   │   ├── document_loader.py
│   │   ├── llm_utils.py
│   │   └── graph_builder.py
│   ├── graph/           # LangGraph workflow
│   │   └── workflow.py
│   └── main.py          # Entry point
├── outputs/             # Generated deliverables
├── tests/               # Unit tests
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── plan.md             # Project plan
└── README.md           # This file
```

## Architecture

### 5-Phase Agentic Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Phase 1: Document Analysis                            │
│  ├─ Extract text and structure                         │
│  ├─ Detect all topics                                  │
│  └─ Identify orphan content                            │
│                    ↓                                    │
│  Phase 2: Relationship Mapping                         │
│  ├─ Build parent-child hierarchies                     │
│  ├─ Extract cross-references                           │
│  └─ Create graph structure                             │
│                    ↓                                    │
│  Phase 3: Validation & Anomaly Detection               │
│  ├─ Check numbering consistency                        │
│  ├─ Validate cross-references                          │
│  └─ Flag missing/broken links                          │
│                    ↓                                    │
│  Phase 4: Visualization                                │
│  ├─ Generate graph diagrams                            │
│  ├─ Create relationship maps                           │
│  └─ Export to PDF                                      │
│                    ↓                                    │
│  Phase 5: Navigation Architecture                      │
│  ├─ Design query interface                             │
│  ├─ Document resolution strategies                     │
│  └─ Create architecture spec                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

1. **Document Parser**: Extracts topics using regex + LLM validation
2. **Relationship Mapper**: Builds NetworkX graph with typed relationships
3. **Validator**: Detects anomalies and generates resolution strategies
4. **Visualizer**: Creates multi-view PDF visualizations
5. **Architecture Designer**: Generates navigation system design document

## Key Features

### Anomaly Detection

The system automatically detects:
- Missing topic numbers (e.g., topic 18.2 referenced but doesn't exist)
- Broken cross-references
- Circular references
- Duplicate topics
- Orphan content
- Numbering gaps

### Intelligent Resolution

For each anomaly, the system:
- Assigns severity level (low, medium, high, critical)
- Generates multiple resolution strategies using GPT-4
- Provides context and affected topics
- Suggests alternative navigation paths

### Visual Graph Features

- Color-coded relationship types
- Highlighted anomalies
- Multiple views (full, hierarchical, cross-references)
- Interactive legend and metadata
- High-resolution PDF export

## Configuration

Edit `.env` to customize:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
GPT4_MODEL=gpt-4-turbo-preview
GPT35_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small

# LLM Parameters
MAX_TOKENS=4096
TEMPERATURE=0.2

# Logging
LOG_LEVEL=INFO

# Output
OUTPUT_DIR=./outputs
```

## Cost Optimization

The system uses:
- **GPT-4**: Complex reasoning and resolution strategies only
- **GPT-3.5-turbo**: Bulk text processing and validation
- **Embeddings**: Semantic similarity for implicit references
- **Caching**: Repeated queries are cached to reduce API calls

Estimated cost: $10-50 per document depending on size and complexity.

## Error Handling

The system includes:
- Graceful degradation when API calls fail
- Detailed error logging
- State recovery in LangGraph workflow
- Input validation and type checking
- Comprehensive exception handling

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Document Formats

Extend `DocumentLoader` in `src/utils/document_loader.py`:

```python
@staticmethod
def _load_custom_format(file_path: str) -> Tuple[str, dict]:
    # Your implementation
    pass
```

### Adding New Agents

1. Create agent in `src/agents/`
2. Add to workflow in `src/graph/workflow.py`
3. Update state type in `PipelineState`

## Troubleshooting

### GraphViz Not Found

Install GraphViz system package (see Installation section).

### API Key Errors

Ensure `.env` file exists and contains valid OpenAI API key.

### Memory Issues

For very large documents, increase available memory or process in chunks.

### Visualization Fails

Check that matplotlib and graphviz are properly installed.

### OCR Fails or Not Working

1. **PyMuPDF Not Installed**: Install with `pip install PyMuPDF`
2. **API Key Not Set**: Ensure OPENAI_API_KEY is configured in .env file
3. **Vision API Access**: Make sure your OpenAI account has access to GPT-4 Vision (gpt-4o model)
4. **API Rate Limits**: Large documents may hit rate limits - the system will continue processing remaining pages
5. **Poor Image Quality**: Very low-resolution scans may produce suboptimal results

### PDF Processing Takes Too Long

This is normal for image-based PDFs with many pages (each page requires an API call). Use `--verbose` to monitor progress.

### High API Costs

Image-based PDFs use OpenAI Vision API which incurs costs per page. To reduce costs:
- Convert image-based PDFs to text-based PDFs when possible
- Process only necessary documents
- Monitor API usage in OpenAI dashboard

## Examples

### Example Output

After processing a document:

```
Topics extracted: 45
Relationships mapped: 45
Anomalies detected: 3

Deliverables:
  1. topic_map.json         -> ./outputs/topic_map.json
  2. cross_reference_graph.pdf -> ./outputs/cross_reference_graph.pdf
  3. navigation_agent_design.md -> ./outputs/navigation_agent_design.md
  4. ambiguity_report.csv   -> ./outputs/ambiguity_report.csv
```

### Example Anomaly Report

```csv
Type,Location,Severity,Description
missing_referenced_topic,18 → 18.2,high,Topic 18 references 18.2 which does not exist
numbering_gap,Between 18.1 and 18.3,high,Missing topic 18.2 in sequence
orphan_content,Appendix A,low,Topic has no connections to other topics
```

## Contributing

This project was built following the plan in `plan.md`. To extend or modify:

1. Review the plan document
2. Update relevant agents or workflow
3. Test with sample documents
4. Update documentation

## License

This project is provided as-is for educational and research purposes.

## Support

For issues or questions:
1. Check this README
2. Review `plan.md` for architecture details
3. Check the generated `navigation_agent_design.md` for system design
4. Enable verbose mode (`-v`) for detailed logging

## Acknowledgments

Built using:
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agentic workflow orchestration
- [OpenAI API](https://platform.openai.com/docs) - LLM and embeddings
- [NetworkX](https://networkx.org/) - Graph analysis
- [Graphviz](https://graphviz.org/) - Graph visualization

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-12-11
