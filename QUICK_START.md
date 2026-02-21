# AutoForge RAG - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (5-10 minutes)

```bash
pip install -r requirements.txt
```

**What this installs:**
- `chromadb` - Vector database
- `sentence-transformers` - Embedding model
- `langchain` & `langchain-community` - Document utilities
- `python-dotenv` - Configuration

**Note**: First run will download the embedding model (~80MB)

### Step 2: Ingest Knowledge Base (2-3 minutes)

```bash
python autoforge/rag/ingestor.py
```

**What this does:**
- Loads 30 VSS signals, 25 MISRA rules, 24 ASPICE items
- Generates embeddings for all documents
- Stores in ChromaDB at `autoforge/data/chroma_db/`

**Expected output:**
```
============================================================
AutoForge RAG Knowledge Base - Document Ingestion
============================================================

[1/3] Processing VSS Signals...
Loaded 30 VSS signals
Created 30 VSS signal chunks
...
Ingestion Complete!
VSS Signals: 30 chunks
MISRA Rules: X chunks
ASPICE Checklist: X chunks
```

### Step 3: Query the Knowledge Base

```bash
python autoforge/examples/query_example.py
```

**Or use in your code:**

```python
from pathlib import Path
from autoforge.rag.retriever import RAGRetriever

# Initialize
retriever = RAGRetriever(Path("autoforge/data/chroma_db"))

# Query
results = retriever.retrieve_context("battery state of charge", top_k=5)

# Get formatted context for LLM
context = retriever.build_prompt_context("tire pressure monitoring")
print(context)
```

## 📋 Verify Setup

Run validation script to check everything is correct:

```bash
python test_setup.py
```

Should output:
```
✓ VSS signals: 30 signals validated
✓ MISRA rules: 25 rules validated
✓ ASPICE checklist: 24 items validated
✓ Python code syntax: All files valid
```

## 🎯 Example Queries

Try these queries to explore the knowledge base:

```python
# Vehicle signals
retriever.retrieve_context("vehicle speed sensor")
retriever.retrieve_context("battery state of charge")
retriever.retrieve_context("tire pressure monitoring")

# Coding rules
retriever.retrieve_context("memory management")
retriever.retrieve_context("type safety and casting")
retriever.retrieve_context("variable initialization")

# Process requirements
retriever.retrieve_context("unit test coverage")
retriever.retrieve_context("code review process")
retriever.retrieve_context("requirements traceability")
```

## 📁 What You Get

**Knowledge Base:**
- 30 VSS signal definitions (speed, battery, tire pressure, etc.)
- 25 MISRA-C++ coding rules (safety and quality standards)
- 24 ASPICE compliance requirements (process standards)

**Capabilities:**
- Semantic search across all documents
- Results organized by document type
- LLM-ready formatted context
- Fully offline operation

## 🔧 Troubleshooting

**Issue**: `pip install` takes too long
- **Solution**: Install packages one at a time or use a faster mirror

**Issue**: Model download fails
- **Solution**: Check internet connectivity. Model downloads on first run only.

**Issue**: `FileNotFoundError` when running retriever
- **Solution**: Run `python autoforge/rag/ingestor.py` first to create the database

**Issue**: Import errors
- **Solution**: Make sure you're running from the project root directory

## 💡 Integration Example

Use in your GenAI pipeline:

```python
from autoforge.rag.retriever import RAGRetriever
from pathlib import Path

# Initialize retriever
retriever = RAGRetriever(Path("autoforge/data/chroma_db"))

# Get context for code generation
user_request = "Generate code to read tire pressure sensors"
context = retriever.build_prompt_context(user_request, top_k=3)

# Build LLM prompt
prompt = f"""
You are an automotive software engineer. Use the following context to help generate code:

{context}

User Request: {user_request}

Generate the code:
"""

# Send to your LLM...
```

## 📚 Learn More

- **README.md** - Full documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **autoforge/examples/query_example.py** - More examples

## ✅ System Requirements

- Python 3.8 or higher
- ~500MB disk space (model + database)
- No GPU required (CPU-only)
- Internet connection for initial setup only

---

**Ready to use!** The system is fully implemented and validated. Just install dependencies and run the ingestion pipeline.
