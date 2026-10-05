# Multi-Format RAG Document Chatbot

A modular Retrieval-Augmented Generation (RAG) chatbot that allows users to upload and query business documents in multiple formats, including Excel, CSV, and PowerPoint.

The project is designed as an interview-ready AI/ML engineering prototype demonstrating document ingestion, metadata-aware chunking, embeddings, vector search, grounded LLM generation, incremental indexing, source traceability, evaluation, and a Streamlit interface.

---

## 1. Use Case

The chatbot is designed for a fictional **Acme Retail** business environment.

Example business documents contain information such as:

* Quarterly business reviews
* Regional sales
* Revenue and sales targets
* Customer growth
* Product performance
* Business risks
* Customer-level sales data

Users can upload multiple documents and ask questions across them.

Example questions:

* What was the revenue of the South region?
* Which product generated the highest revenue?
* What was the customer growth during Q1?
* What was the South region revenue and how much of the target did it achieve?
* What was the employee attrition rate?

The system should answer only when sufficient evidence exists in the indexed documents.

---

# 2. Features

* Multi-format document ingestion
* Excel (`.xlsx`, `.xls`) parsing
* CSV parsing
* PowerPoint (`.pptx`) parsing
* Common `DocumentChunk` representation
* Metadata preservation
* Sentence-transformer embeddings
* ChromaDB vector storage
* Top-K similarity retrieval
* Configurable retrieval distance threshold
* Local LLM generation using Ollama
* Grounded answer generation
* Explicit no-answer behavior
* Source/file traceability
* Slide, sheet, and row metadata
* Multi-document question answering
* Incremental document indexing
* SHA-256 document change detection
* Changed-document replacement
* Streamlit upload and Q&A interface
* Automated functional tests
* Custom RAG evaluation suite
* Retrieval latency and generation latency logging

---

# 3. Architecture

```text
                     ┌──────────────────────┐
                     │     Streamlit UI     │
                     │ Upload + Questioning │
                     └──────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐          ┌─────────────────┐
        │ Document Upload │          │ User Question   │
        └────────┬────────┘          └────────┬────────┘
                 │                            │
                 ▼                            ▼
        ┌─────────────────┐          ┌─────────────────┐
        │ Format Parser   │          │ Query Embedding │
        │ Excel / CSV /   │          └────────┬────────┘
        │ PowerPoint      │                   │
        └────────┬────────┘                   ▼
                 │                    ┌─────────────────┐
                 ▼                    │ ChromaDB Search │
        ┌─────────────────┐           └────────┬────────┘
        │ DocumentChunk   │                    │
        │ + Metadata      │                    ▼
        └────────┬────────┘           ┌─────────────────┐
                 │                    │ Relevant Chunks │
                 ▼                    └────────┬────────┘
        ┌─────────────────┐                    │
        │ Embedding Model │                    ▼
        │ MiniLM          │           ┌─────────────────┐
        └────────┬────────┘           │ Ollama / Llama  │
                 │                    │ 3.2 Generation  │
                 ▼                    └────────┬────────┘
        ┌─────────────────┐                    │
        │ ChromaDB        │                    ▼
        │ Persistent DB   │           ┌─────────────────┐
        └─────────────────┘           │ Answer + Sources│
                                      └─────────────────┘
```

---

# 4. Project Structure

```text
Use_case_Rag_chatbot/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── sales_q1.xlsx
│   ├── customer_sales.csv
│   └── q1_business_review.pptx
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
└── evaluation/
    ├── __init__.py
    ├── eval_dataset.json
    └── evaluate_rag.py
```

`chroma_db/` is created locally at runtime and is excluded from Git through `.gitignore`.

---

# 5. End-to-End Flow

```text
Upload Document
      ↓
Calculate SHA-256 Hash
      ↓
Check Document Tracker
      ↓
 ┌───────────────┐
 │ Unchanged?    │
 └───────┬───────┘
         │
    Yes  │  No
         │
         ▼
      Skip          Parse Document
                        ↓
                  Create Chunks
                        ↓
                 Generate Embeddings
                        ↓
                    ChromaDB
                        ↓
                 Store File Hash
```

Question answering:

```text
User Question
      ↓
Generate Query Embedding
      ↓
ChromaDB Similarity Search
      ↓
Top-K Candidate Chunks
      ↓
Distance Threshold Filtering
      ↓
Relevant Context
      ↓
Ollama / Llama 3.2
      ↓
Grounded Answer
      ↓
Source Metadata from Retrieved Chunks
      ↓
Streamlit UI
```

---

# 6. Document Representation

All supported document formats are normalized into a common representation:

```python
@dataclass
class DocumentChunk:
    text: str
    metadata: Dict
```

This allows the downstream embedding, vector storage, retrieval, and generation layers to remain independent of the original document format.

---

# 7. Document Parsing

## Excel

Excel files are parsed sheet by sheet.

Each data row becomes a retrieval chunk.

Example metadata:

```python
{
    "source": "data/sales_q1.xlsx",
    "file_type": "excel",
    "sheet": "Regional Sales",
    "row": 3
}
```

This allows the application to identify the original worksheet and row associated with retrieved information.

## CSV

CSV files are parsed row by row.

Example metadata:

```python
{
    "source": "data/customer_sales.csv",
    "file_type": "csv",
    "row": 2
}
```

## PowerPoint

PowerPoint files are parsed slide by slide.

The parser extracts:

* Slide text
* PowerPoint tables
* Speaker notes when available
* Slide title metadata

Example metadata:

```python
{
    "source": "data/q1_business_review.pptx",
    "file_type": "pptx",
    "slide": 6,
    "title": "South Region"
}
```

---

# 8. PowerPoint Limitation

The current PowerPoint implementation supports `.pptx`.

It extracts slide text and PowerPoint table content.

It does **not** currently perform:

* OCR on scanned slides
* Image understanding
* Chart-data extraction
* SmartArt extraction
* Legacy `.ppt` parsing

The application therefore exposes `.pptx` in the Streamlit upload interface.

These capabilities could be added in a production implementation using OCR, image-capable models, or additional document conversion tooling.

---

# 9. Embeddings

The project uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

Embedding dimension:

```text
384
```

The same embedding model is used for:

* Document embeddings during indexing
* Query embeddings during retrieval

This ensures that documents and queries exist in the same vector space.

---

# 10. Vector Database

The project uses:

```text
ChromaDB
```

with persistent local storage.

Collection:

```text
acme_documents
```

Each chunk is stored with:

* Chunk ID
* Original text
* Embedding
* Metadata

The chunk ID includes a source-derived prefix to avoid collisions between different documents.

---

# 11. Retrieval

The retriever performs vector similarity search using the query embedding.

Current configuration:

```text
Top-K = 3
Maximum distance = 0.8
```

The retriever first obtains up to three candidates from ChromaDB and then removes candidates whose distance exceeds the configured threshold.

The `0.8` threshold was selected empirically using the project's evaluation dataset.

It is **not intended to be a universal threshold**. A production system should tune retrieval parameters using a larger representative evaluation dataset.

---

# 12. Retrieval Threshold Experiment

Two distance thresholds were evaluated.

| Metric             | Threshold 0.9 | Threshold 0.8 |
| ------------------ | ------------: | ------------: |
| Context Precision  |         0.528 |     **0.667** |
| Context Recall     |         1.000 |     **1.000** |
| Context Relevance  |         0.537 |     **0.566** |
| Answer Correctness |         1.000 |     **1.000** |
| Faithfulness       |        1.000* |     **1.000** |
| Answer Relevancy   |        0.333* |     **0.500** |

* Results can vary because the faithfulness and answer-relevancy metrics use an LLM judge.

The stricter `0.8` threshold reduced irrelevant retrieved chunks while maintaining the required evidence on the current evaluation set.

---

# 13. LLM Generation

The project uses:

```text
Ollama
Llama 3.2
```

The model runs locally.

The generation prompt instructs the model to:

* Use only retrieved context
* Avoid outside knowledge
* Avoid assumptions
* Avoid invented facts
* Give concise answers
* Avoid source-number labels
* Return a fixed fallback when sufficient evidence is unavailable

The fallback response is:

```text
I cannot answer this based on the provided documents.
```

---

# 14. Why Ollama?

Ollama was selected for the prototype because it provides:

* Local inference
* No API key requirement
* No hosted inference cost
* A simple development setup
* A privacy-friendly local execution path

The generation layer is isolated in:

```text
pipeline/generation.py
```

Therefore, the LLM provider can be changed later without redesigning the ingestion, embedding, vector-store, or retrieval layers.

For production, the model provider could be evaluated based on:

* Latency
* Throughput
* Cost
* Model quality
* Privacy
* Deployment requirements

Possible future providers include hosted or self-hosted inference services.

---

# 15. Source Traceability

Source metadata is preserved during ingestion and stored with each vector.

After retrieval, the Python application builds source information from the retrieved chunks.

For example:

```text
data/q1_business_review.pptx
Slide 6
South Region
```

or:

```text
data/sales_q1.xlsx
Sheet: Regional Sales
Row: 3
```

This provides traceability from the generated answer back to the retrieved document locations.

The LLM itself does not decide which source numbers to display. The application derives source metadata from the retrieved chunks.

---

# 16. Multi-Document QA

The vector store contains chunks from multiple uploaded documents.

A single query can therefore retrieve evidence from multiple sources.

For example:

```text
Question:
What was the South region revenue and how much of the target did it achieve?
```

The system can retrieve:

```text
PowerPoint:
South Region
Revenue = $4.2M
Target Achievement = 105%

Excel:
Regional Sales
South
Revenue = 4.2
Target = 4.0
```

The LLM then generates a grounded answer using the combined retrieved context.

---

# 17. No-Answer Behavior

The system is designed to avoid fabricating information when evidence is insufficient.

Example:

```text
Question:
What was the employee attrition rate?

Answer:
I cannot answer this based on the provided documents.
```

The system also returns no sources for a rejected/no-answer response.

This provides a basic grounding safeguard against unsupported answers.

---

# 18. Incremental Indexing

The project avoids unnecessarily re-embedding unchanged documents.

Each document is assigned a SHA-256 hash.

The document tracker stores:

```text
file path → SHA-256 hash
```

When a document is processed:

### Unchanged document

```text
Current hash == Stored hash
        ↓
Skip indexing
```

### Changed document

```text
Current hash != Stored hash
        ↓
Delete old chunks
        ↓
Parse new document
        ↓
Generate new embeddings
        ↓
Store new chunks
        ↓
Update hash
```

This avoids unnecessary embedding computation and prevents stale document chunks from remaining in the vector store.

---

# 19. Streamlit UI

The application provides:

### Upload Documents

Supported UI formats:

```text
.xlsx
.xls
.csv
.pptx
```

Multiple documents can be uploaded together.

### Index Documents

Uploaded documents are saved to the local `data/` directory and passed through the indexing pipeline.

### Ask a Question

Users can enter natural-language questions and receive:

* Generated answer
* Supporting source locations when available

---

# 20. Error Handling

The indexing pipeline handles common errors including:

* Missing files
* Unsupported file formats
* Invalid/corrupt documents
* Empty extracted content
* General indexing failures

The LLM generation layer also catches inference failures and returns the standard no-answer response.

---

# 21. Observability

The application currently logs:

* Number of extracted chunks
* Embedding shape
* Number of stored documents
* Retrieval time
* Generation time
* Indexing status
* Whether documents were skipped or re-indexed
* Indexing errors

Example:

```text
Retrieval time: 0.036 seconds
Generation time: 3.049 seconds
```

Local LLM generation latency can vary significantly, particularly during initial model loading/warm-up.

For production, additional metrics could include:

* Query latency percentiles
* Token usage
* Model errors
* Retrieval hit rate
* User feedback
* Evaluation trends
* Cost per request

---

# 22. Testing

The project contains functional RAG tests covering:

1. South region revenue
2. Highest-revenue product
3. Customer growth
4. Multi-document South region revenue + target question
5. Missing employee attrition information
6. Missing profit-margin information

Latest result:

```text
TEST SUMMARY: 6/6 tests passed
```

The tests verify both answer content and source/no-answer behavior.

---

# 23. RAG Evaluation

The project contains a separate evaluation dataset:

```text
evaluation/eval_dataset.json
```

and evaluation script:

```text
evaluation/evaluate_rag.py
```

The current evaluation measures:

* Answer Correctness
* Context Precision
* Context Recall
* Context Relevance
* Faithfulness
* Answer Relevancy

The evaluation is a **custom lightweight evaluation framework**, not a full RAGAS implementation.

## Evaluation methodology

### Answer Correctness

A deterministic dataset-based check verifies whether the expected answer content appears in the generated answer.

For unanswerable questions, correctness checks whether the expected fallback response is returned.

### Context Precision

Measures the proportion of retrieved chunks that match the acceptable source locations defined in the evaluation dataset.

### Context Recall

Measures whether the expected evidence sources were successfully retrieved.

### Context Relevance

Uses cosine similarity between the question embedding and retrieved chunk embeddings as a semantic relevance proxy.

This is a project-specific proxy rather than the canonical RAGAS implementation.

### Faithfulness

Uses the local Llama 3.2 model as an LLM judge to determine whether the generated answer is supported by the retrieved context.

### Answer Relevancy

Uses the local Llama 3.2 model as an LLM judge to determine whether the answer appropriately addresses the question.

Because the judge is itself an LLM, these scores can vary and should not be treated as absolute ground truth.

---

# 24. Final Evaluation Results

Using the final retrieval configuration:

```text
Top-K = 3
Maximum distance = 0.8
```

the latest evaluation produced:

```text
Average Answer Correctness: 1.000
Average Context Precision: 0.667
Average Context Recall:    1.000
Average Context Relevance: 0.566
Average Faithfulness:      1.000
Average Answer Relevancy:  0.500
```

These results are based on the project's small six-question evaluation dataset and should not be interpreted as production-level benchmark results.

The strongest observations are:

* Expected answers were correct on the evaluation set.
* Required evidence was successfully retrieved.
* The stricter retrieval threshold improved context precision compared with `0.9`.
* Generated answers were judged faithful to the retrieved context.
* Answer-relevancy scoring is more variable for extremely short answers such as `"Laptop."`.

---

# 25. Security Considerations

The prototype is designed with basic security awareness but is not production-ready.

Current considerations include:

* Local LLM inference
* No hard-coded API keys
* `.env` excluded from Git
* Uploaded filenames sanitized using the base filename
* Supported upload extensions restricted by the UI
* Local document and vector-store processing

For production deployment, additional controls would be required:

* Authentication
* Authorization
* Tenant isolation
* MIME/content validation
* Malware scanning
* Isolated upload storage
* Internal document identifiers
* Encrypted storage
* Secure model endpoints
* Rate limiting
* Audit logging
* Stronger prompt-injection defenses
* Output validation

Retrieved documents should be treated as untrusted content. A production system should prevent document text from overriding system instructions or causing unauthorized tool actions.

---

# 26. Data Privacy

The prototype can operate entirely locally:

```text
Documents
   ↓
Local parsing
   ↓
Local embeddings
   ↓
Local ChromaDB
   ↓
Local Ollama model
```

This provides a useful privacy characteristic for development and interview demonstrations.

Production deployments would require organization-specific data-governance and access-control policies.

---

# 27. Cost Considerations

The prototype uses:

* Local Sentence Transformer embeddings
* Local ChromaDB
* Local Ollama inference

Therefore, there are no per-request hosted embedding or LLM API charges during local execution.

Production cost would depend on:

* Embedding infrastructure
* LLM infrastructure
* Storage
* Vector database
* Compute
* Monitoring
* Network traffic
* Number of queries
* Model size

---

# 28. Current Limitations

The current prototype intentionally has several limitations.

### Document extraction

PowerPoint image content, scanned documents, chart data, and SmartArt are not extracted.

### Legacy PowerPoint

The supported PowerPoint workflow is `.pptx`.

### Chunking

The current design uses format-aware row/slide chunks rather than a sophisticated semantic chunking strategy.

### Retrieval

The current retrieval layer uses a fixed Top-K and distance threshold.

The threshold was tuned on a small evaluation dataset and would require further tuning for production.

### Evaluation

The evaluation dataset contains only six questions.

The evaluation metrics are custom lightweight implementations rather than a full standardized RAG evaluation framework.

### LLM

The prototype uses a local Llama 3.2 model through Ollama.

Production deployment may require a different inference architecture depending on latency, throughput, quality, and infrastructure requirements.

### Security

The application is suitable as an interview/demo prototype but requires additional production security controls.

---

# 29. Potential Production Improvements

Future improvements could include:

### Retrieval

* Hybrid keyword + vector retrieval
* Reranking
* Query expansion
* Better metadata filtering
* Larger evaluation datasets
* Retrieval parameter optimization

### Document processing

* OCR
* Image extraction
* Chart understanding
* Semantic chunking
* More document formats
* Better table normalization

### Generation

* Hosted or optimized inference
* Streaming responses
* Structured outputs
* Provider abstraction
* Response validation

### Evaluation

* Larger golden datasets
* Continuous evaluation
* Automated regression evaluation
* More robust LLM-as-a-judge methodology
* Standardized RAG evaluation frameworks where appropriate

### Production architecture

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

# 30. Installation

Create and activate a Python virtual environment.

Example:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages.

The project uses a CPU PyTorch build.

For the CPU PyTorch installation, use the appropriate PyTorch CPU package index if required by the environment.

Then install the remaining dependencies from:

```text
requirements.txt
```

---

# 31. Ollama Setup

Install and start Ollama.

Verify that the required model is available:

```powershell
ollama list
```

The project currently uses:

```text
llama3.2:latest
```

Start the Ollama server if required:

```powershell
ollama serve
```

---

# 32. Initialize Document Tracker

Run:

```powershell
python -m scripts.initialize_tracker
```

This initializes the document-tracking state used for incremental indexing.

---

# 33. Run the Application

Start Streamlit:

```powershell
streamlit run app.py
```

The application provides the upload and question-answering interface.

---

# 34. Run Functional Tests

Run:

```powershell
python -m tests.test_rag
```

Expected result:

```text
TEST SUMMARY: 6/6 tests passed
```

---

# 35. Run RAG Evaluation

Run:

```powershell
python -m evaluation.evaluate_rag
```

The evaluation script reports:

```text
Average Answer Correctness
Average Context Precision
Average Context Recall
Average Context Relevance
Average Faithfulness
Average Answer Relevancy
```

---

# 36. Design Principles

The project follows several practical design principles:

### Separation of concerns

Document parsing, embeddings, vector storage, retrieval, generation, indexing, and UI are separated into different modules.

### Traceability

Metadata is retained from the original document through retrieval and displayed with the answer.

### Incremental processing

Unchanged documents are not re-embedded.

### Grounded generation

The LLM is instructed to use only retrieved context.

### Explicit uncertainty

The system returns a fixed no-answer response when sufficient evidence is unavailable.

### Testability

Core functionality can be tested independently from the Streamlit UI.

### Replaceable components

The embedding model, vector store, and LLM generation layers are isolated so that components can be replaced as requirements evolve.

---

# 37. Project Status

## Completed

* Multi-format ingestion
* Excel parsing
* CSV parsing
* PowerPoint parsing
* Common document representation
* Metadata preservation
* Embedding generation
* Persistent ChromaDB storage
* Similarity retrieval
* Retrieval threshold tuning
* Local LLM generation
* Grounded responses
* No-answer handling
* Multi-document QA
* Source traceability
* Incremental indexing
* Changed-document replacement
* Streamlit UI
* Error handling
* Functional testing
* RAG evaluation
* Security review
* Documentation

## Current Prototype Status

**Interview/demo ready.**

The system demonstrates the complete RAG lifecycle:

```text
Ingest
  ↓
Parse
  ↓
Normalize
  ↓
Embed
  ↓
Store
  ↓
Retrieve
  ↓
Generate
  ↓
Trace Sources
  ↓
Evaluate
```

It should be presented as an **interview-ready prototype rather than a production-grade enterprise RAG platform**.

---

# 38. Interview Summary

A concise way to describe the project:

> I built a multi-format RAG document chatbot for a retail business scenario. It accepts Excel, CSV, and PowerPoint documents, converts them into a common metadata-aware chunk representation, generates embeddings using Sentence Transformers, and stores them in ChromaDB. For a user query, the system generates a query embedding, retrieves relevant chunks using similarity search with a tuned distance threshold, and passes the retrieved context to a locally hosted Llama 3.2 model through Ollama. The model is explicitly constrained to answer only from the retrieved documents, and the application derives source references from the retrieved metadata so users can trace answers back to the original slide, sheet, or row.
>
> I also implemented SHA-256 based incremental indexing so unchanged documents are skipped and modified documents have their old chunks replaced. I created functional tests and a custom RAG evaluation suite covering answer correctness, context precision, context recall, context relevance, faithfulness, and answer relevancy. On the current six-question evaluation set, the system achieved 1.0 answer correctness, 1.0 context recall, and 1.0 faithfulness, with context precision of 0.667 after tuning the retrieval threshold from 0.9 to 0.8.
>
> The current implementation is an interview/demo prototype. For production, I would add stronger authentication and authorization, tenant isolation, OCR and richer document extraction, hybrid retrieval and reranking, larger evaluation datasets, stronger prompt-injection defenses, monitoring, and a production-grade model-serving architecture.
