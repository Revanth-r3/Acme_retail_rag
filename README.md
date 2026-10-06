# Acme Retail RAG Assistant

A modular, multi-format Retrieval-Augmented Generation (RAG) application for asking grounded questions across retail business documents.

The project supports Excel, CSV, and PowerPoint documents, converts their content into a common chunk representation, stores embeddings in ChromaDB, retrieves relevant evidence, and generates answers using a local Llama 3.2 model through Ollama.

> **Project status:** demo-ready prototype. Core functional RAG tests: **6/6 passed**.

---

## 1. Problem Statement

Build a document-question-answering assistant that can:

- ingest Excel (`.xlsx`, `.xls`), CSV, and PowerPoint (`.ppt`, `.pptx`) files
- extract text and tabular content
- normalize extracted content into a common representation
- generate embeddings
- store and retrieve document chunks from a vector database
- generate answers grounded only in retrieved documents
- provide source references such as slide, sheet, and row
- support multiple uploaded documents
- skip unchanged documents during re-indexing
- provide a simple upload and Q&A interface

---

## 2. Architecture

```text
                 ┌─────────────────────┐
                 │   Streamlit UI      │
                 │ Upload + Q&A        │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Document Ingestion  │
                 │ Excel / CSV / PPT   │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Common Chunk Model  │
                 │ Text + Metadata     │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ SentenceTransformer │
                 │ all-MiniLM-L6-v2    │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │     ChromaDB        │
                 │ Persistent Vector DB│
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Semantic Retrieval  │
                 │ Top-K + Threshold   │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Ollama / Llama 3.2  │
                 │ Grounded Generation │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Answer + Sources    │
                 └─────────────────────┘
```

---

## 3. Project Structure

```text
Acme_retail_rag/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│
├── ingestion/
│   ├── __init__.py
│   ├── excel_parser.py
│   ├── csv_parser.py
│   └── ppt_parser.py
│
├── pipeline/
│   ├── __init__.py
│   ├── schemas.py
│   ├── ingestion.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   ├── retrieval.py
│   ├── generation.py
│   ├── document_tracker.py
│   └── indexer.py
│
├── services/
│   ├── __init__.py
│   └── rag_service.py
│
├── scripts/
│   ├── __init__.py
│   └── initialize_tracker.py
│
├── tests/
│   ├── __init__.py
│   └── test_rag.py
│
├── evaluation/
│   ├── __init__.py
│   ├── eval_dataset.json
│   └── evaluate_rag.py
│
└── .streamlit/
    └── config.toml
```

---

## 4. Supported Formats

| Format | Support | Extraction |
|---|---|---|
| `.xlsx` | Yes | Sheet rows/cells |
| `.xls` | Yes | Legacy Excel rows/cells |
| `.csv` | Yes | CSV rows |
| `.pptx` | Yes | Slide text, tables, notes, title |
| `.ppt` | Yes | Converted to temporary `.pptx`, then parsed |

### PowerPoint `.ppt` handling

Legacy `.ppt` files are converted to `.pptx` using LibreOffice in headless mode. The converted file is temporary and removed after parsing.

PowerPoint visual-only content such as images, scanned text, charts, and SmartArt is outside the current prototype extraction scope.

---

## 5. Common Document Representation

All parsers return a common `DocumentChunk` representation.

Conceptually:

```text
DocumentChunk
├── text
└── metadata
    ├── source
    ├── file_type
    ├── slide / sheet
    ├── row
    └── title
```

This keeps downstream embedding, storage, retrieval, and source rendering independent of the original document format.

---

## 6. Ingestion

### Excel

- `.xlsx` is parsed with `openpyxl`
- `.xls` is parsed with `xlrd`
- rows are converted into text chunks
- metadata includes sheet and row information

Example:

```text
Sheet: Regional Sales
Region: South
Revenue: 4.2
Target: 4.0
Customers: 1500
```

Metadata:

```text
file_type: excel
sheet: Regional Sales
row: 3
```

### CSV

CSV rows are converted into text chunks with row metadata.

### PowerPoint

The parser extracts:

- slide text
- PowerPoint tables
- speaker notes
- slide title
- slide number

---

## 7. Embeddings

The project uses:

```text
SentenceTransformer
all-MiniLM-L6-v2
```

Embedding dimension:

```text
384
```

The same embedding model is used for document chunks and user queries.

---

## 8. Vector Database

The project uses persistent local ChromaDB.

Collection:

```text
acme_documents
```

Storage:

```text
./chroma_db
```

Each indexed chunk stores:

- original text
- embedding
- source metadata

The vector database is local and is excluded from Git.

---

## 9. Retrieval

The retriever:

1. embeds the user question
2. performs semantic search in ChromaDB
3. retrieves the top candidates
4. applies a distance threshold
5. returns only sufficiently relevant chunks

Current configuration:

```text
Top-K = 3
Maximum distance = 0.8
```

The threshold was empirically configured and validated against the project's small evaluation dataset

---

## 10. Grounded Generation

The application uses:

```text
Ollama
└── llama3.2:latest
```

The generation prompt explicitly instructs the model to:

- use only retrieved context
- avoid outside knowledge
- avoid assumptions
- avoid inventing facts
- provide concise answers
- avoid exposing internal source labels

If the retrieved context is insufficient, the required fallback is:

```text
I cannot answer this based on the provided documents.
```

The application also uses this fallback when LLM inference fails.

---

## 11. Source Traceability

Sources are derived from document metadata rather than generated by the LLM.

Examples:

```text
q1_business_review.pptx — Slide 6 — South Region
sales_q1.xlsx — Sheet: Regional Sales — Row: 3
```

This provides traceability from the generated answer back to the source document location.

---

## 12. Multi-Document Question Answering

Multiple files can be uploaded and indexed together.

A question can retrieve evidence from different formats/documents.

Example:

```text
Question:
What was the South region revenue and how much of the target did it achieve?

Retrieved evidence:
- PowerPoint: South Region, Slide 6
- Excel: Regional Sales, Row 3

Answer:
The South region revenue was $4.2M. The target achievement was 105%.
```

---

## 13. Incremental Indexing

The document tracker uses SHA-256 hashes.

Conceptually:

```text
Upload document
      │
      ▼
Calculate SHA-256
      │
      ├── Same hash ──► Skip indexing
      │
      └── Changed hash
               │
               ▼
        Delete old chunks
               │
               ▼
          Parse document
               │
               ▼
       Generate embeddings
               │
               ▼
          Store chunks
               │
               ▼
          Update hash
```

This avoids unnecessary embedding work and prevents stale chunks from remaining in the vector store.

---

## 14. Streamlit UI

The UI provides:

### Upload Documents

Supported:

```text
.xlsx
.xls
.csv
.ppt
.pptx
```

Multiple documents can be uploaded together.

### Index Uploaded Documents

Uploaded files are stored under the local `data/` directory and passed through the indexing pipeline.

### Ask a Question

Users receive:

- generated answer
- supporting source locations when available

---

## 15. Security

The current prototype includes basic security controls.

### Implemented

- upload extension allow-list
- `.ppt` and `.pptx` support restricted to the supported formats
- maximum upload size of **200 MB per file**
- filename normalization using `os.path.basename()`
- uploaded files stored under `data/`
- local LLM inference through Ollama
- no hard-coded API keys
- `.env` excluded from Git
- uploaded `data/` excluded from Git
- ChromaDB excluded from Git
- Streamlit configuration excluded from Git

The filename handling prevents an uploaded filename from directly escaping the intended `data/` directory.

### Production Security Considerations

The project is not intended to be production-secure. A production deployment should additionally consider:

- authentication
- authorization
- multi-user / tenant isolation
- MIME and content validation
- malware scanning
- isolated upload storage
- encrypted storage
- secure model endpoints
- rate limiting
- audit logging
- stronger prompt-injection defenses
- output validation

Retrieved documents should be treated as untrusted content. Production systems should ensure document text cannot override system instructions or trigger unauthorized actions.

---

## 16. Error Handling

The ingestion/indexing pipeline handles common failures such as:

- missing files
- unsupported formats
- invalid/corrupt documents
- empty extracted content
- indexing failures

The generation layer catches LLM inference failures and returns the standard no-answer response.

---

## 17. Observability

The application currently logs useful development/runtime information including:

- extracted chunk counts
- embedding shape
- stored document counts
- retrieval time
- generation time
- indexing status
- skipped vs re-indexed documents
- indexing errors

Example:

```text
Retrieval time: 0.160 seconds
Generation time: 16.879 seconds
```

Local LLM latency can vary depending on model loading and hardware.

For production, additional observability could include latency percentiles, token usage, retrieval hit rate, model errors, user feedback, evaluation trends, and cost/request.

---

## 18. Testing

Functional RAG tests cover:

1. South region revenue
2. Highest-revenue product
3. Customer growth
4. Multi-document South region revenue + target
5. Missing employee attrition information
6. Missing profit-margin information

Latest result:

```text
TEST SUMMARY: 6/6 tests passed
```

The tests verify answer behavior as well as source and no-answer behavior.

Run:

```powershell
python -m tests.test_rag
```

---

## 19. RAG Evaluation

The project includes:

```text
evaluation/eval_dataset.json
evaluation/evaluate_rag.py
```

The custom evaluation framework measures:

- Answer Correctness
- Context Precision
- Context Recall
- Context Relevance
- Faithfulness
- Answer Relevancy

This is a **custom lightweight evaluation framework**, not a RAGAS implementation.

### Evaluation methodology

**Answer Correctness**

Checks generated answers against expected answer content.

**Context Precision**

Measures how much of the retrieved context corresponds to acceptable evidence sources.

**Context Recall**

Measures whether expected evidence sources were retrieved.

**Context Relevance**

Uses semantic similarity between the question and retrieved chunks as a project-specific relevance proxy.

**Faithfulness**

Uses the local Llama 3.2 model as an LLM judge to assess whether the answer is supported by retrieved context.

**Answer Relevancy**

Uses the local Llama 3.2 model as an LLM judge to assess whether the answer addresses the question.

LLM-judge metrics can vary and should not be treated as absolute ground truth.

Run:

```powershell
python -m evaluation.evaluate_rag
```

---

## 20. Evaluation Results

Final retrieval configuration:

```text
Top-K = 3
Maximum distance = 0.8
```

Latest evaluation averages:

```text
Answer Correctness : 1.000
Context Precision  : 0.667
Context Recall     : 1.000
Context Relevance  : 0.566
Faithfulness       : 1.000
Answer Relevancy   : 0.500
```

These results are based on a small six-question evaluation dataset and should not be interpreted as production benchmark results.

---

## 21. Known Limitations

### Document extraction

Current PowerPoint extraction does not process:

- images
- scanned text
- chart data
- SmartArt

### Chunking

The current design uses format-aware row/slide chunks rather than advanced semantic chunking.

### Retrieval

Retrieval currently uses a fixed Top-K and distance threshold.

### Evaluation

The evaluation dataset contains only six questions.

### LLM

The prototype uses local Llama 3.2 through Ollama. Production inference may require a different architecture depending on latency, throughput, quality, and infrastructure.

### Security

The application is an interview demo prototype and does not implement the full security controls required for a production multi-user system.

---

## 22. Future Production Improvements

Potential improvements include:

### Retrieval

- hybrid keyword + vector search
- reranking
- query expansion
- better metadata filtering
- larger evaluation datasets
- retrieval parameter optimization

### Document Processing

- OCR
- image understanding
- chart extraction
- semantic chunking
- additional document formats
- improved table normalization

### Generation

- hosted or optimized inference
- streaming responses
- structured outputs
- model-provider abstraction
- response validation

### Evaluation

- larger golden datasets
- continuous evaluation
- automated regression evaluation
- stronger LLM-as-a-judge methodology
- standardized RAG evaluation frameworks where appropriate

### Production Architecture

```text
User
  ↓
Authentication
  ↓
API Layer
  ↓
Document Storage
  ↓
Async Ingestion
  ↓
Embedding Service
  ↓
Vector Database
  ↓
Retriever / Reranker
  ↓
LLM Service
  ↓
Response Validation
  ↓
User
```

---

## 23. Installation

### Prerequisites

The project is currently tested with:

* Python 3.11.x
* CPU-based PyTorch
* Ollama
* LibreOffice — required only for legacy `.ppt` file support

### Create a virtual environment

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Python dependencies

```powershell
pip install -r requirements.txt
```

The `requirements.txt` file includes the dependencies required for:

* Excel (`.xlsx` / `.xls`) parsing
* CSV parsing
* PowerPoint (`.pptx`) parsing
* Sentence Transformer embeddings
* PyTorch CPU inference
* ChromaDB
* Ollama client
* Streamlit

The project is currently configured for CPU-based PyTorch.

### Sentence Transformer model

The project uses:

```text
all-MiniLM-L6-v2
```

through the `sentence-transformers` library.

The model generates 384-dimensional embeddings for document chunks and user queries.

On the first run, Sentence Transformers may download the model weights if they are not already available in the local cache. An internet connection may therefore be required during the first model initialization.

---

## 24. Ollama Setup

The project uses Ollama to run the local Llama 3.2 model.

Install Ollama separately from the Python dependencies.

After installation, download the required model:

```powershell
ollama pull llama3.2:latest
```

Verify that the model is available:

```powershell
ollama list
```

The project currently uses:

```text
llama3.2:latest
```

If the Ollama server is not already running, start it with:

```powershell
ollama serve
```

The Python application communicates with the local Ollama server for answer generation and LLM-based evaluation.

---

## 25. LibreOffice Setup

LibreOffice is required only when processing legacy PowerPoint `.ppt` files.

The project uses LibreOffice in headless mode to convert:

```text
.ppt → temporary .pptx
```

The converted presentation is then parsed using `python-pptx`.

Install LibreOffice separately and ensure the `soffice` executable is available at the configured path or through the system `PATH`.

If you only use `.pptx` files, LibreOffice is not required.

---

## 26. Initialize Document Tracker

The project uses a SHA-256 based document tracker to determine whether a document is new, unchanged, or modified.

Initialize the tracker with:

```powershell
python -m scripts.initialize_tracker
```

This allows unchanged documents to be skipped during subsequent indexing instead of being unnecessarily re-embedded.

---

## 27. Run the Application

Start the Streamlit application:

```powershell
streamlit run app.py
```

The application provides:

1. Document upload
2. Document indexing
3. Natural-language question answering
4. Source traceability

Supported upload formats:

```text
.xlsx
.xls
.csv
.pptx
.ppt
```

The Streamlit configuration limits each uploaded file to **200 MB**.

### First-run note

The first application startup may take longer because the Sentence Transformer embedding model needs to be loaded, and the model may need to be downloaded if it is not already cached locally.

After startup, users can upload documents, index them, and ask questions through the Streamlit interface.


## 27. Summary

This project demonstrates an end-to-end RAG pipeline:

```text
Multi-format documents
        ↓
Format-specific parsing
        ↓
Common DocumentChunk representation
        ↓
Metadata-aware indexing
        ↓
SentenceTransformer embeddings
        ↓
Persistent ChromaDB
        ↓
Top-K semantic retrieval
        ↓
Distance threshold filtering
        ↓
Grounded Llama 3.2 generation
        ↓
Answer + source traceability
```

Key engineering decisions:

- modular ingestion by file type
- common chunk schema across formats
- metadata preserved for traceability
- persistent vector storage
- incremental indexing using SHA-256
- explicit retrieval threshold
- grounded generation with a deterministic no-answer fallback
- local LLM inference using Ollama
- functional testing and custom RAG evaluation
- basic upload and repository security controls

### Current implementation status

**Completed**

- Excel `.xlsx`
- Legacy Excel `.xls`
- CSV
- PowerPoint `.pptx`
- Legacy PowerPoint `.ppt`
- common document representation
- metadata-aware chunks
- embeddings
- persistent ChromaDB
- semantic retrieval
- retrieval threshold
- local Llama 3.2 generation
- grounded answers
- no-answer behavior
- multi-document QA
- source traceability
- SHA-256 incremental indexing
- changed-document replacement
- Streamlit UI
- upload size and filename protections
- functional tests
- custom RAG evaluation

**Current functional test result: 6/6 passed.**
