# Implementation Plan: AutoForge RAG Knowledge Base

## Overview

This implementation plan creates an offline-first RAG knowledge base system for automotive domain knowledge. The system ingests VSS signals, MISRA-C++ rules, and ASPICE checklists into ChromaDB using sentence-transformers embeddings, then provides semantic retrieval for GenAI pipeline context injection. Implementation follows a bottom-up approach: knowledge base files → ingestion pipeline → retrieval interface → testing.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure: autoforge/knowledge_base/, autoforge/rag/, autoforge/data/
  - Create requirements.txt with chromadb, sentence-transformers, langchain, langchain-community, python-dotenv, pytest, hypothesis
  - Create autoforge/__init__.py and autoforge/rag/__init__.py as empty files
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 2. Create knowledge base files
  - [ ] 2.1 Create VSS signals JSON file
    - Create autoforge/knowledge_base/vss_signals.json with 30 vehicle signal definitions
    - Include signals for: speed, motion, tire pressure (4 wheels), battery SOC, EV range, brake, throttle, steering, gear, motor temp, coolant temp
    - Each signal must have: signal_name (VSS dot notation), datatype, unit, min_value, max_value, description (1-2 sentences)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 2.2 Write property test for VSS signal structure
    - **Property 1: Signal Field Completeness**
    - **Property 2: VSS Hierarchical Naming**
    - **Property 3: Signal Description Length**
    - **Validates: Requirements 1.2, 1.4, 1.5**
  
  - [ ] 2.3 Create MISRA-C++ rules markdown file
    - Create autoforge/knowledge_base/misra_rules.md with 25 MISRA-C++ rules
    - Format as numbered list with rule ID, short title, and 2-line description
    - Cover topics: memory management, variable initialization, control flow, type safety, function design
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 2.4 Write property test for MISRA rule structure
    - **Property 4: MISRA Rule Structure**
    - **Validates: Requirements 2.2**
  
  - [ ] 2.5 Create ASPICE checklist markdown file
    - Create autoforge/knowledge_base/aspice_checklist.md with 20 ASPICE SWE requirements
    - Format as markdown checkboxes with brief explanations
    - Cover: requirement traceability, design docs, code review, unit test coverage, static analysis, config management
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 2.6 Write property test for ASPICE checkbox format
    - **Property 5: ASPICE Checkbox Format**
    - **Validates: Requirements 3.2**

- [ ] 3. Checkpoint - Verify knowledge base files
  - Ensure all knowledge base files are created with correct format, ask the user if questions arise.

- [ ] 4. Implement document loading functions
  - [ ] 4.1 Implement VSS signal loader in autoforge/rag/ingestor.py
    - Create load_vss_signals(file_path: Path) -> List[Dict[str, Any]] function
    - Load JSON file with UTF-8 encoding
    - Handle FileNotFoundError and JSONDecodeError with clear error messages
    - _Requirements: 4.1_
  
  - [ ]* 4.2 Write unit tests for VSS signal loader
    - Test loading valid JSON file
    - Test FileNotFoundError handling
    - Test JSONDecodeError handling for malformed JSON
    - _Requirements: 4.1_
  
  - [ ] 4.3 Implement markdown document loader in autoforge/rag/ingestor.py
    - Create load_markdown_document(file_path: Path) -> str function
    - Load markdown file with UTF-8 encoding
    - Handle FileNotFoundError and UnicodeDecodeError with clear error messages
    - _Requirements: 4.1_
  
  - [ ]* 4.4 Write unit tests for markdown loader
    - Test loading valid markdown file
    - Test FileNotFoundError handling
    - Test UnicodeDecodeError handling
    - _Requirements: 4.1_

- [ ] 5. Implement document chunking functions
  - [ ] 5.1 Implement VSS signal chunking in autoforge/rag/ingestor.py
    - Create chunk_vss_signals(signals: List[Dict]) -> List[str] function
    - Convert each signal to text format: "Signal: {name}\nType: {datatype}\nUnit: {unit}\nRange: {min} to {max}\nDescription: {description}"
    - _Requirements: 4.2_
  
  - [ ]* 5.2 Write property test for signal chunk completeness
    - **Property 6: Signal Chunk Completeness**
    - **Validates: Requirements 4.2**
  
  - [ ]* 5.3 Write unit tests for VSS signal chunking
    - Test chunk format includes all required fields
    - Test handling of empty signal list
    - _Requirements: 4.2_
  
  - [ ] 5.4 Implement markdown chunking in autoforge/rag/ingestor.py
    - Create chunk_markdown(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str] function
    - Split by markdown headings (##) when possible
    - Otherwise split every 500 characters with 50-character overlap
    - _Requirements: 4.3_
  
  - [ ]* 5.5 Write property test for markdown chunking overlap
    - **Property 7: Markdown Chunking Overlap**
    - **Validates: Requirements 4.3**
  
  - [ ]* 5.6 Write unit tests for markdown chunking
    - Test splitting by headings
    - Test splitting with 500 char limit and 50 char overlap
    - Test edge case: empty content
    - Test edge case: content shorter than chunk size
    - _Requirements: 4.3_

- [ ] 6. Implement embedding generation
  - [ ] 6.1 Implement embedding function in autoforge/rag/ingestor.py
    - Create create_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]] function
    - Use sentence-transformers library to load model
    - Generate embeddings for all text chunks
    - Handle model loading errors with clear error messages suggesting internet connectivity check
    - _Requirements: 4.4, 6.1, 6.2_
  
  - [ ]* 6.2 Write unit tests for embedding generation
    - Test embedding dimensions are 384 for all-MiniLM-L6-v2
    - Test model loads successfully
    - Test batch embedding for multiple chunks
    - Test error handling for model loading failures
    - _Requirements: 4.4, 6.1, 6.2_

- [ ] 7. Checkpoint - Verify chunking and embedding pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement ChromaDB storage
  - [ ] 8.1 Implement ChromaDB storage function in autoforge/rag/ingestor.py
    - Create store_in_chromadb(collection_name: str, chunks: List[str], embeddings: List[List[float]], db_path: Path) function
    - Initialize PersistentClient with db_path
    - Create or get collection by name
    - Store chunks with embeddings and auto-generated IDs
    - Create database directory if it doesn't exist using Path.mkdir(parents=True, exist_ok=True)
    - Handle database initialization errors with clear error messages
    - _Requirements: 4.5, 4.6, 7.6_
  
  - [ ]* 8.2 Write unit tests for ChromaDB storage
    - Test database initialization and persistence
    - Test collection creation
    - Test storing chunks with embeddings
    - Test database directory auto-creation
    - Test error handling for permission errors
    - _Requirements: 4.5, 4.6, 7.6_

- [ ] 9. Implement main ingestion pipeline
  - [ ] 9.1 Implement main ingestion function in autoforge/rag/ingestor.py
    - Create ingest_all_documents(knowledge_base_path: Path, db_path: Path) function
    - Load all 3 documents (VSS, MISRA, ASPICE)
    - Chunk each document appropriately
    - Generate embeddings for all chunks
    - Store in 3 separate ChromaDB collections: vss_signals, misra_rules, aspice_checklist
    - Print progress statements during ingestion
    - Print count of chunks stored per document at completion
    - Use relative paths with pathlib.Path
    - _Requirements: 4.1, 4.5, 4.7, 4.8, 4.9, 4.10_
  
  - [ ]* 9.2 Write integration tests for full ingestion pipeline
    - Test full pipeline: load → chunk → embed → store
    - Test all 3 collections are created
    - Test chunk counts match expected values
    - Test offline operation (no network calls after model download)
    - Test relative path resolution
    - _Requirements: 4.1, 4.5, 4.7, 4.8, 4.9, 4.10, 6.3_

- [ ] 10. Checkpoint - Verify ingestion pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement retriever initialization
  - [ ] 11.1 Create RAGRetriever class in autoforge/rag/retriever.py
    - Create RAGRetriever class with __init__(self, db_path: Path) method
    - Initialize ChromaDB PersistentClient connection
    - Load all 3 collections: vss_signals, misra_rules, aspice_checklist
    - Handle database loading errors with clear error messages
    - Use relative paths with pathlib.Path
    - _Requirements: 5.1, 5.9_
  
  - [ ]* 11.2 Write unit tests for retriever initialization
    - Test successful initialization with existing database
    - Test error handling for missing database
    - Test error handling for corrupted database
    - Test relative path resolution
    - _Requirements: 5.1, 5.9_

- [ ] 12. Implement context retrieval
  - [ ] 12.1 Implement retrieve_context method in RAGRetriever class
    - Create retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, List[str]] method
    - Validate query string is non-empty
    - Query each ChromaDB collection separately
    - Return dictionary with keys: vss_signals, misra_rules, aspice_items
    - Each key maps to list of relevant document chunks
    - Handle query errors gracefully, return empty lists for collections with no matches
    - _Requirements: 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 12.2 Write property test for retrieval result structure
    - **Property 8: Retrieval Result Structure**
    - **Validates: Requirements 5.3, 5.4**
  
  - [ ]* 12.3 Write unit tests for retrieve_context
    - Test returns correct dictionary structure
    - Test with various top_k values
    - Test with empty database returns empty lists
    - Test with non-existent query returns empty lists
    - Test empty query string raises ValueError
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [ ] 13. Implement prompt context formatting
  - [ ] 13.1 Implement build_prompt_context method in RAGRetriever class
    - Create build_prompt_context(self, query: str, top_k: int = 5) -> str method
    - Call retrieve_context internally
    - Format results into clean string block suitable for LLM prompt injection
    - Include section headers for each document type
    - _Requirements: 5.6, 5.7_
  
  - [ ]* 13.2 Write property test for prompt context format
    - **Property 9: Prompt Context String Format**
    - **Validates: Requirements 5.7**
  
  - [ ]* 13.3 Write unit tests for build_prompt_context
    - Test returns non-empty formatted string
    - Test includes section headers
    - Test handles empty retrieval results gracefully
    - _Requirements: 5.6, 5.7_

- [ ] 14. Implement retriever as importable module
  - [ ] 14.1 Add module-level convenience functions in autoforge/rag/retriever.py
    - Ensure RAGRetriever class can be imported by other modules
    - Add docstrings for all public methods
    - _Requirements: 5.8_
  
  - [ ]* 14.2 Write integration tests for retriever module
    - Test importing RAGRetriever from external module
    - Test full retrieval pipeline: query → retrieve → format
    - _Requirements: 5.8_

- [ ] 15. Checkpoint - Verify retrieval pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement round-trip data integrity tests
  - [ ]* 16.1 Write property test for signal round-trip integrity
    - **Property 10: Signal Ingestion-Retrieval Round Trip**
    - **Validates: Requirements 8.1, 8.2**
  
  - [ ]* 16.2 Write property test for MISRA rule round-trip integrity
    - **Property 11: MISRA Rule Ingestion-Retrieval Round Trip**
    - **Validates: Requirements 8.3**
  
  - [ ]* 16.3 Write property test for ASPICE item round-trip integrity
    - **Property 12: ASPICE Item Ingestion-Retrieval Round Trip**
    - **Validates: Requirements 8.4**

- [ ] 17. Create main execution scripts
  - [ ] 17.1 Add main execution block to autoforge/rag/ingestor.py
    - Add if __name__ == "__main__": block
    - Call ingest_all_documents with default paths
    - Use Path(__file__).parent.parent to resolve relative paths
    - _Requirements: 4.7_
  
  - [ ] 17.2 Create example usage script for retriever
    - Create autoforge/examples/query_example.py demonstrating retriever usage
    - Show initialization, retrieve_context, and build_prompt_context usage
    - Include sample queries for VSS signals, MISRA rules, and ASPICE items
    - _Requirements: 5.8_

- [ ] 18. Final checkpoint - Run full test suite
  - Run all unit tests and property tests
  - Verify test coverage meets goals (85% line coverage, 80% branch coverage)
  - Run full integration test: ingest all documents, then retrieve with sample queries
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples, edge cases, and error handling
- Implementation uses Python with sentence-transformers, ChromaDB, and pytest/Hypothesis
- All file paths use pathlib.Path for cross-platform compatibility
- System is designed for offline operation after initial model download
