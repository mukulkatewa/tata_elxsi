# Requirements Document

## Introduction

AutoForge is a Retrieval-Augmented Generation (RAG) knowledge base system designed for automotive GenAI pipelines in Software Defined Vehicle (SDV) development. The system provides automotive-specific context including Vehicle Signal Specification (VSS) data, MISRA-C++ coding rules, and ASPICE compliance standards to ensure generated code meets industry requirements. This RAG system will be used in a Tata Elxsi hackathon project to accelerate SDV development by providing relevant domain knowledge to language models.

## Glossary

- **RAG_System**: The Retrieval-Augmented Generation knowledge base system that stores, indexes, and retrieves automotive domain knowledge
- **Ingestor**: The component that loads documents, chunks them, creates embeddings, and stores them in the vector database
- **Retriever**: The component that accepts queries and returns relevant context from the vector database
- **ChromaDB**: The persistent vector database used to store embedded document chunks
- **VSS**: Vehicle Signal Specification - standardized automotive signal definitions
- **MISRA**: Motor Industry Software Reliability Association coding standards for C++
- **ASPICE**: Automotive SPICE (Software Process Improvement and Capability Determination) quality standards
- **Embedding_Model**: The sentence-transformers model (all-MiniLM-L6-v2) that converts text to vector representations
- **Document_Chunk**: A segment of text from source documents that is embedded and stored as a retrievable unit
- **Collection**: A named group of embedded chunks in ChromaDB organized by document type

## Requirements

### Requirement 1: Vehicle Signal Specification Knowledge Base

**User Story:** As an automotive software developer, I want a comprehensive VSS signal database, so that generated code can reference correct signal names, datatypes, units, and valid ranges.

#### Acceptance Criteria

1. THE RAG_System SHALL store 30 vehicle signal definitions in JSON format at knowledge_base/vss_signals.json
2. FOR EACH signal definition, THE RAG_System SHALL include signal_name, datatype, unit, min_value, max_value, and description fields
3. THE signal definitions SHALL cover speed, motion, tire pressure for all 4 wheels, battery state of charge, EV range, brake, throttle, steering, gear position, motor temperature, and coolant temperature categories
4. WHEN a signal_name is stored, THE RAG_System SHALL use VSS hierarchical dot notation format
5. THE description field SHALL contain 1 to 2 sentences explaining the signal purpose

### Requirement 2: MISRA-C++ Coding Rules Knowledge Base

**User Story:** As a code quality engineer, I want MISRA-C++ rules documented, so that generated automotive code complies with industry safety standards.

#### Acceptance Criteria

1. THE RAG_System SHALL store 25 MISRA-C++ rules in markdown format at knowledge_base/misra_rules.md
2. FOR EACH rule, THE RAG_System SHALL include rule ID, short title, and 2-line description
3. THE rule descriptions SHALL explain what is required and why the rule exists
4. THE rules SHALL focus on memory management, variable initialization, control flow, type safety, and function design topics
5. THE rules SHALL be formatted as a numbered list in markdown

### Requirement 3: ASPICE Compliance Checklist Knowledge Base

**User Story:** As a process compliance manager, I want ASPICE SWE requirements documented, so that development processes meet automotive quality standards.

#### Acceptance Criteria

1. THE RAG_System SHALL store 20 ASPICE SWE process requirements in markdown format at knowledge_base/aspice_checklist.md
2. FOR EACH requirement, THE RAG_System SHALL format it as a checkbox item with brief explanation
3. THE requirements SHALL cover requirement traceability, design documentation, code review, unit test coverage, static analysis, and configuration management
4. THE checklist SHALL be formatted in markdown with checkbox syntax

### Requirement 4: Document Ingestion and Embedding

**User Story:** As a system administrator, I want to ingest knowledge base documents into a vector database, so that they can be efficiently retrieved based on semantic similarity.

#### Acceptance Criteria

1. WHEN the Ingestor runs, THE Ingestor SHALL load all 3 documents from the knowledge_base folder
2. WHEN processing vss_signals.json, THE Ingestor SHALL convert each signal object into a text chunk containing signal name, unit, range, and description
3. WHEN processing markdown files, THE Ingestor SHALL split content by heading or every 500 characters with 50-character overlap
4. THE Ingestor SHALL create embeddings using the sentence-transformers library with model all-MiniLM-L6-v2
5. THE Ingestor SHALL store embedded chunks in ChromaDB with 3 separate collections named vss_signals, misra_rules, and aspice_checklist
6. THE Ingestor SHALL persist the vector database to data/chroma_db/ directory
7. THE Ingestor SHALL provide a main function that executes full ingestion
8. WHEN ingestion completes, THE Ingestor SHALL print the count of chunks stored per document
9. THE Ingestor SHALL use relative file paths with pathlib.Path
10. DURING ingestion, THE Ingestor SHALL print progress statements

### Requirement 5: Context Retrieval

**User Story:** As a GenAI pipeline developer, I want to query the knowledge base with natural language, so that I can retrieve relevant automotive context for code generation.

#### Acceptance Criteria

1. WHEN the Retriever initializes, THE Retriever SHALL load the existing ChromaDB from data/chroma_db/
2. THE Retriever SHALL provide a retrieve_context function that accepts a query string and top_k integer parameter with default value 5
3. WHEN retrieve_context is called, THE Retriever SHALL return a dictionary with three keys: vss_signals, misra_rules, and aspice_items
4. FOR EACH key in the returned dictionary, THE Retriever SHALL provide a list of relevant document chunks
5. THE Retriever SHALL query each ChromaDB collection separately to organize results by document type
6. THE Retriever SHALL provide a build_prompt_context function that accepts a query string
7. WHEN build_prompt_context is called, THE Retriever SHALL format retrieved results into a clean string block suitable for LLM prompt injection
8. THE Retriever SHALL be importable as a standalone module by other Python modules
9. THE Retriever SHALL use relative file paths with pathlib.Path

### Requirement 6: Offline Operation

**User Story:** As a developer in a restricted network environment, I want the RAG system to work without internet connectivity, so that I can develop without external API dependencies.

#### Acceptance Criteria

1. THE RAG_System SHALL use sentence-transformers for embeddings to enable offline operation
2. THE Embedding_Model SHALL run locally without requiring API keys
3. THE RAG_System SHALL NOT depend on external API services for core functionality

### Requirement 7: Project Structure and Dependencies

**User Story:** As a developer setting up the project, I want clear project structure and dependency specifications, so that I can quickly install and run the system.

#### Acceptance Criteria

1. THE RAG_System SHALL organize files in the structure: autoforge/ containing knowledge_base/, rag/, and data/ directories
2. THE knowledge_base directory SHALL contain vss_signals.json, misra_rules.md, and aspice_checklist.md
3. THE rag directory SHALL contain ingestor.py, retriever.py, and __init__.py
4. THE data directory SHALL contain the chroma_db subdirectory for persistent storage
5. THE RAG_System SHALL provide a requirements.txt file listing chromadb, sentence-transformers, langchain, langchain-community, and python-dotenv dependencies
6. THE chroma_db directory SHALL be auto-created by the Ingestor when it does not exist

### Requirement 8: Round-Trip Data Integrity

**User Story:** As a quality assurance engineer, I want to verify that ingested data can be accurately retrieved, so that the RAG system maintains data fidelity.

#### Acceptance Criteria

1. FOR ALL vehicle signals ingested, THE RAG_System SHALL preserve signal_name, datatype, unit, min_value, max_value, and description in retrievable chunks
2. WHEN a signal is ingested and then retrieved with its exact signal_name as query, THE Retriever SHALL return a chunk containing all original signal fields
3. FOR ALL MISRA rules ingested, THE RAG_System SHALL preserve rule ID, title, and description in retrievable chunks
4. FOR ALL ASPICE items ingested, THE RAG_System SHALL preserve the checkbox format and explanation in retrievable chunks
