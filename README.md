# AutoForge RAG Knowledge Base

An offline-first Retrieval-Augmented Generation (RAG) knowledge base system for automotive GenAI pipelines in Software Defined Vehicle (SDV) development.

## Overview

AutoForge provides automotive-specific context including:
- **Vehicle Signal Specification (VSS)** data - 30 standardized automotive signal definitions
- **MISRA-C++ coding rules** - 25 safety and quality coding standards
- **ASPICE compliance standards** - 20 process requirements for automotive software

The system uses ChromaDB for vector storage and sentence-transformers for local embedding generation, enabling fully offline operation after initial setup.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- chromadb - Vector database for semantic search
- sentence-transformers - Local embedding model (all-MiniLM-L6-v2)
- langchain & langchain-community - Document processing utilities
- python-dotenv - Environment configuration
- pytest & hypothesis - Testing frameworks

## Usage

### Step 1: Ingest Knowledge Base Documents

Run the ingestion pipeline to load documents into ChromaDB:

```bash
python autoforge/rag/ingestor.py
```

This will:
1. Load all knowledge base files from `autoforge/knowledge_base/`
2. Chunk documents appropriately (VSS signals as individual entries, markdown with 500 char chunks)
3. Generate embeddings using all-MiniLM-L6-v2 model
4. Store in ChromaDB at `autoforge/data/chroma_db/`

Expected output:
```
============================================================
AutoForge RAG Knowledge Base - Document Ingestion
============================================================

[1/3] Processing VSS Signals...
Loaded 30 VSS signals
Created 30 VSS signal chunks
...
```

### Step 2: Query the Knowledge Base

Use the retriever to search for relevant context:

```python
from pathlib import Path
from autoforge.rag.retriever import RAGRetriever

# Initialize retriever
db_path = Path("autoforge/data/chroma_db")
retriever = RAGRetriever(db_path)

# Query for relevant context
results = retriever.retrieve_context("vehicle speed signal", top_k=5)

# Results organized by document type
print(results['vss_signals'])    # VSS signal definitions
print(results['misra_rules'])    # MISRA coding rules
print(results['aspice_items'])   # ASPICE requirements

# Or get formatted context for LLM prompts
prompt_context = retriever.build_prompt_context("battery state of charge")
print(prompt_context)
```

### Example Queries

Run the example script to see sample queries:

```bash
python autoforge/examples/query_example.py
```

## Project Structure

```
autoforge/
├── knowledge_base/          # Source documents
│   ├── vss_signals.json    # 30 VSS signal definitions
│   ├── misra_rules.md      # 25 MISRA-C++ rules
│   └── aspice_checklist.md # 20 ASPICE requirements
├── rag/                     # RAG components
│   ├── ingestor.py         # Document ingestion pipeline
│   ├── retriever.py        # Context retrieval interface
│   └── __init__.py
├── data/                    # Persistent storage
│   └── chroma_db/          # ChromaDB vector database
└── examples/
    └── query_example.py    # Usage examples
```

## Features

- **Offline Operation**: Works without internet after initial model download
- **Semantic Search**: Uses embeddings for intelligent context retrieval
- **Organized Results**: Returns results grouped by document type
- **LLM-Ready**: Formats context for direct prompt injection
- **Automotive Focus**: Domain-specific knowledge for SDV development

## Technical Details

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions, ~80MB)
- **Vector Database**: ChromaDB with persistent SQLite storage
- **Chunking Strategy**: 
  - VSS signals: One chunk per signal with all fields
  - Markdown: Split by headings or 500 chars with 50 char overlap
- **Distance Metric**: Cosine similarity

## Requirements

- Python 3.8+
- ~500MB disk space (model + database)
- No GPU required (CPU-only operation)

## License

This project is part of the Tata Elxsi hackathon for automotive GenAI development.
