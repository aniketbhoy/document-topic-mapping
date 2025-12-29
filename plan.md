# Semantic Topic Mapping - Project Plan

## 🎯 Project Overview

Build an intelligent document navigation system that extracts topics, maps relationships, detects anomalies, and creates visual navigation tools for complex documents.

---

## 📋 Core Objectives

1. Extract ALL topics from documents (handle non-sequential numbering)
2. Build comprehensive topic relationship maps (hierarchies + cross-references)
3. Detect and flag structural anomalies and inconsistencies
4. Generate visual relationship diagrams
5. Design intelligent navigation architecture

---

## 🏗️ Technical Stack

### **Primary Framework**
- **LangGraph** - Agentic workflow orchestration with state management
  - Best for: Complex multi-step reasoning, stateful workflows, error recovery
  - Integration: Native OpenAI API support

### **LLM Provider**
- **OpenAI API**
  - GPT-4 (or GPT-4-turbo): Complex reasoning, ambiguity resolution
  - GPT-3.5-turbo: Bulk extraction, pattern matching
  - text-embedding-3-small: Semantic similarity, topic clustering

### **Core Libraries**

**Document Processing:**
- `python-docx` - Word document parsing
- `PyPDF2` / `pdfplumber` - PDF extraction
- `python-magic` - File type detection

**Graph & Data Structures:**
- `networkx` - Graph construction and topology analysis
- `pydantic` - Data validation and modeling
- `pandas` - Data manipulation and CSV generation

**NLP & Pattern Matching:**
- `spacy` - Entity extraction, linguistic analysis
- `re` (regex) - Topic numbering pattern detection
- `fuzzywuzzy` - Fuzzy string matching for cross-references

**Visualization:**
- `graphviz` / `pygraphviz` - Graph visualization
- `matplotlib` - Static plots
- `plotly` - Interactive visualizations
- `reportlab` / `weasyprint` - PDF generation

**Agentic Workflow:**
- `langgraph` - State management and agent orchestration
- `langchain` - LLM utilities and prompts
- `openai` - OpenAI API client

**Utilities:**
- `python-dotenv` - Environment variable management
- `loguru` - Advanced logging
- `tqdm` - Progress tracking

---

## 🔄 System Architecture

### **5-Phase Agentic Pipeline**

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Phase 1: Document Analysis                            │
│  ├─ Extract text and structure                         │
│  ├─ Detect all topics (sequential + non-sequential)    │
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

---

## 🤖 Agent Responsibilities

### **Agent 1: Document Parser**
**Purpose:** Extract and structure raw document content

**Key Tasks:**
- Load document (DOCX/PDF)
- Extract text with position metadata
- Detect topic markers using regex + LLM validation
- Handle edge cases (appendices, footnotes, tables)
- Identify content without clear topic assignment

**Output:** Structured document object with topic boundaries

---

### **Agent 2: Relationship Mapper**
**Purpose:** Build the complete topic relationship graph

**Key Tasks:**
- Construct hierarchical relationships (5 → 5.1 → 5.1.a)
- Extract explicit cross-references ("See Topic X")
- Detect implicit references using semantic analysis
- Identify forward/backward references
- Build NetworkX graph with typed edges

**Output:** topic_map.json + in-memory graph structure

---

### **Agent 3: Validator**
**Purpose:** Quality assurance and anomaly detection

**Key Tasks:**
- Validate numbering sequences (detect missing 18.2)
- Check cross-reference integrity
- Identify circular references
- Flag ambiguous topic boundaries
- Generate resolution strategies using GPT-4

**Output:** ambiguity_report.csv with severity levels

---

### **Agent 4: Visualizer**
**Purpose:** Generate visual artifacts

**Key Tasks:**
- Create directed graph visualization
- Color-code relationship types (hierarchy, cross-ref, forward, backward)
- Highlight anomalies and orphan content
- Generate legend and metadata
- Export high-quality PDF

**Output:** cross_reference_graph.pdf

---

### **Agent 5: Architecture Designer**
**Purpose:** Document the navigation system design

**Key Tasks:**
- Design RAG-based navigation interface
- Define query patterns and responses
- Document API endpoints
- Create resolution strategies for edge cases
- Specify handling for missing/broken references

**Output:** navigation_agent_design.md

---

## 📊 Data Models

### **Topic Model**
```python
{
  "id": "18.3",
  "title": "Risk Assessment Procedures",
  "content": "...",
  "parent": "18",
  "children": [],
  "cross_references": ["8.2", "12.1"],
  "forward_references": ["22.1"],
  "backward_references": ["30.4"],
  "position": {"start": 1234, "end": 1567},
  "confidence": 0.95
}
```

### **Relationship Model**
```python
{
  "source": "18",
  "target": "18.2",
  "type": "cross_reference",
  "status": "broken",
  "context": "As discussed in Topic 18.2...",
  "severity": "high"
}
```

### **Anomaly Model**
```python
{
  "type": "missing_referenced_topic",
  "location": "18 → 18.2",
  "severity": "high",
  "description": "Topic 18 references 18.2, which does not exist",
  "resolution_strategies": ["...", "..."]
}
```

---

## 🎨 LLM Strategy

### **When to Use GPT-4**
- Ambiguous topic boundary detection
- Complex cross-reference interpretation
- Generating resolution strategies
- Natural language reasoning about document structure
- Final validation and sanity checks

### **When to Use GPT-3.5-turbo**
- Bulk text classification
- Simple pattern validation
- Extracting explicit cross-references
- Topic title generation
- Formatting and standardization

### **When to Use Embeddings**
- Semantic similarity for orphan content assignment
- Topic clustering and grouping
- Finding implicit cross-references
- Detecting duplicate or similar topics

### **Cost Optimization**
- Cache LLM responses for repeated queries
- Batch similar operations
- Use regex pre-filtering before LLM calls
- Implement tiered validation (regex → GPT-3.5 → GPT-4)

---

## 🚀 Implementation Phases

### **Phase 1: Foundation (Week 1)**
- Set up project structure and environment
- Implement document loading and basic parsing
- Create Pydantic models for data structures
- Set up LangGraph state management
- Build logging and error handling framework

### **Phase 2: Core Extraction (Week 1-2)**
- Implement topic detection (regex + LLM)
- Extract hierarchical relationships
- Build initial graph structure
- Handle edge cases (appendices, unnumbered sections)
- Test with sample documents

### **Phase 3: Relationship Intelligence (Week 2)**
- Implement cross-reference extraction
- Add semantic analysis for implicit references
- Build forward/backward reference detection
- Create relationship validation logic
- Test graph completeness

### **Phase 4: Validation & Anomaly Detection (Week 2-3)**
- Implement numbering consistency checks
- Add cross-reference validation
- Build anomaly detection system
- Generate resolution strategies
- Create comprehensive test cases (including the 18.2 trap)

### **Phase 5: Visualization & Documentation (Week 3)**
- Implement graph visualization
- Generate PDF exports
- Create navigation system design document
- Build final reporting system
- Generate all deliverables

### **Phase 6: Testing & Refinement (Week 3-4)**
- End-to-end testing with various documents
- Edge case validation
- Performance optimization
- Documentation and code cleanup
- Final deliverable verification

---

## 🎯 Deliverables Checklist

### **1. topic_map.json**
- Complete hierarchical structure
- All topics with metadata
- Full relationship mapping
- Confidence scores
- JSON schema validated

### **2. cross_reference_graph.pdf**
- Visual graph representation
- Color-coded relationships
- Highlighted anomalies
- Legend and metadata
- High-resolution export

### **3. navigation_agent_design.md**
- System architecture overview
- Query interface specification
- API endpoint documentation
- Edge case handling strategies
- Implementation recommendations

### **4. ambiguity_report.csv**
- All detected anomalies
- Severity classifications
- Detailed descriptions
- Resolution strategies
- Affected topics/references

---

## 🔧 Configuration & Setup

### **Environment Variables**
```bash
OPENAI_API_KEY=your_api_key_here
GPT4_MODEL=gpt-4-turbo-preview
GPT35_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
MAX_TOKENS=4096
TEMPERATURE=0.2
LOG_LEVEL=INFO
```

### **Project Structure**
```
semantic-topic-mapper/
├── src/
│   ├── agents/
│   │   ├── parser.py
│   │   ├── mapper.py
│   │   ├── validator.py
│   │   ├── visualizer.py
│   │   └── designer.py
│   ├── models/
│   │   ├── topic.py
│   │   ├── relationship.py
│   │   └── anomaly.py
│   ├── utils/
│   │   ├── document_loader.py
│   │   ├── graph_builder.py
│   │   └── llm_utils.py
│   ├── graph/
│   │   └── workflow.py
│   └── main.py
├── tests/
├── outputs/
├── requirements.txt
├── .env
└── README.md
```

---

## 🧪 Testing Strategy

### **Unit Tests**
- Topic detection accuracy
- Relationship extraction precision
- Anomaly detection coverage
- Graph construction validity

### **Integration Tests**
- End-to-end pipeline flow
- State management consistency
- Error recovery mechanisms
- Output format validation

### **Edge Case Tests**
- Missing topic numbers (18.2 scenario)
- Circular references
- Duplicate topics
- Malformed cross-references
- Non-standard numbering schemes

---

## 🎓 Key Design Principles

### **1. Robustness Over Perfection**
Handle edge cases gracefully; flag uncertainties rather than failing

### **2. Explainability**
Every decision should be traceable (why was 18.2 flagged as missing?)

### **3. Scalability**
Design for documents of varying sizes (10 pages to 1000 pages)

### **4. Modularity**
Each agent should be independently testable and replaceable

### **5. Cost-Conscious**
Optimize LLM usage without compromising quality

---

## 🎯 Success Metrics

- **Extraction Accuracy:** >95% topic detection rate
- **Relationship Precision:** >90% cross-reference accuracy
- **Anomaly Detection:** 100% coverage of structural issues
- **Processing Speed:** <2 minutes for 100-page document
- **Visual Clarity:** Graph readable at standard zoom levels

---

## 🚨 Critical Considerations

### **The Hidden Trap (Missing 18.2)**
**Challenge:** Topic 18 references 18.2, but 18.2 doesn't exist. Topic 18.3 exists.

**Detection Strategy:**
1. Build complete numbering schema
2. Identify sequence gaps
3. Cross-check with reference targets

**Resolution Strategy:**
1. Flag as "Missing Referenced Topic" (HIGH severity)
2. Check if 18.3 should be 18.2 (renumbering error)
3. Search for unnumbered content between 18.1 and 18.3
4. Provide navigation alternatives (show 18.1, 18.3 when user seeks 18.2)

**Implementation:**
- Validator agent runs integrity checks
- LLM proposes multiple resolution hypotheses
- Report includes all possibilities with confidence scores

---

## 📚 Additional Resources

### **Documentation to Reference**
- LangGraph: https://langchain-ai.github.io/langgraph/
- OpenAI API: https://platform.openai.com/docs
- NetworkX: https://networkx.org/documentation/stable/
- Graphviz: https://graphviz.org/documentation/

### **Research Papers/Concepts**
- Document structure analysis
- Hierarchical topic modeling
- Graph-based information retrieval
- Automated anomaly detection

---

## 🎬 Getting Started

### **Quick Start Commands**
```bash
# Setup
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI API key

# Run the pipeline
python src/main.py --input document.docx --output ./outputs

# Run with verbose logging
python src/main.py --input document.docx --output ./outputs --verbose

# Generate specific deliverable
python src/main.py --input document.docx --only visualization
```

---

## 💡 Future Enhancements

- Multi-document relationship mapping
- Real-time collaborative editing support
- Web-based interactive navigation interface
- Support for additional formats (HTML, Markdown, LaTeX)
- Machine learning for topic classification
- Auto-correction of detected anomalies
- Version control integration for document changes

---

## 📝 Notes

- Prioritize clarity in outputs over technical complexity
- Document all assumptions and limitations
- Maintain detailed logs for debugging
- Design for extensibility (new document types, new relationship types)
- Keep user experience in mind for navigation design

---

**Project Timeline:** 3-4 weeks  
**Complexity Level:** Advanced  
**Primary Skills Required:** Python, LLM orchestration, graph theory, document processing  
**Estimated API Cost:** $10-50 depending on document size and iterations
