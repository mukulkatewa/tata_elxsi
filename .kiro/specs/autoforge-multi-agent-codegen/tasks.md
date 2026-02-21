# Implementation Plan: AutoForge Multi-Agent Code Generation System

## Overview

This implementation plan breaks down the AutoForge Phase 2 multi-agent code generation system into discrete coding tasks. The system extends Phase 1's RAG knowledge base with LLM-powered orchestration that generates MISRA-compliant C++ automotive services and test code from natural language requirements. Implementation follows a bottom-up approach: configuration and templates first, then agents, orchestration, and finally the entry point.

## Tasks

- [x] 1. Set up configuration module and environment management
  - Create autoforge/config.py with environment variable loading
  - Implement load_config() function returning configuration dictionary
  - Implement get_llm_client() function returning OpenAI client instance
  - Implement validate_config() function with validation logic
  - Add error handling for missing OPENAI_API_KEY, invalid CHROMA_DB_PATH, invalid MODEL_NAME, and invalid MAX_TOKENS
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_

- [ ]* 1.1 Write unit tests for configuration module
  - Test default values for all configuration settings
  - Test missing OPENAI_API_KEY raises ValueError with specific message
  - Test missing CHROMA_DB_PATH raises FileNotFoundError
  - Test invalid MODEL_NAME raises ValueError
  - Test invalid MAX_TOKENS raises ValueError
  - Test get_llm_client returns OpenAI instance
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9, 18.2, 18.4, 18.5, 18.6_

- [x] 2. Create prompt templates for Dev Agent and QA Agent
  - [x] 2.1 Create prompts/dev_agent_prompt.txt with Dev Agent instructions
    - Include placeholders: {requirement}, {vss_context}, {misra_context}, {aspice_context}
    - Specify role as senior automotive embedded software engineer
    - Define C++ service structure requirements (constructor, init, process, getAlerts)
    - Require MISRA compliance with inline comments format
    - Require VSS signal validation and file headers
    - Instruct to return ONLY raw C++ code without markdown
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_
  
  - [x] 2.2 Create prompts/qa_agent_prompt.txt with QA Agent instructions
    - Include placeholders: {requirement}, {generated_code}, {service_name}
    - Specify role as automotive QA engineer
    - Define test structure requirements (main function, assert statements, MockDataProvider)
    - Require test cases for normal, boundary, out-of-range, and missing signal scenarios
    - Require print statements in format "PASS: [test name]" or "FAIL: [test name]"
    - Instruct to return ONLY raw C++ code without markdown
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [ ]* 2.3 Write unit tests for prompt templates
  - Test dev_agent_prompt.txt exists at expected path
  - Test qa_agent_prompt.txt exists at expected path
  - Test dev template contains all required placeholders
  - Test qa template contains all required placeholders
  - Test template loading with UTF-8 encoding
  - _Requirements: 2.1, 3.1, 19.1, 19.2, 19.4_

- [x] 3. Implement Dev Agent for service code generation
  - [x] 3.1 Create autoforge/agents/dev_agent.py with DevAgent class
    - Implement __init__ method accepting llm_client, rag_retriever, prompt_template_path, model_name, max_tokens
    - Implement generate method accepting requirement string
    - Implement _load_prompt_template method with UTF-8 encoding and FileNotFoundError handling
    - Implement _fill_prompt_template method with placeholder replacement and KeyError handling
    - Implement _derive_service_name method with stop word filtering and snake_case conversion
    - Implement _extract_vss_signals method using "Vehicle." pattern matching
    - Implement _parse_llm_response method handling markdown code blocks and raw code
    - Add OpenAI API call with error handling for authentication, rate limit, and network errors
    - Add progress message printing with 🤖 emoji
    - Return dictionary with service_name, header_code, source_code, full_code, requirement, vss_signals_used
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 10.1, 10.3, 10.4, 10.5, 10.6, 12.1, 12.2, 12.3, 12.4, 13.1, 13.2, 13.3, 13.4, 15.1, 15.2, 15.3, 16.1, 16.4, 19.3, 19.4, 19.5, 19.6_

- [ ]* 3.2 Write unit tests for Dev Agent
  - Test generate() accepts requirement string
  - Test generate() calls RAGRetriever.retrieve_context (mock verification)
  - Test generate() calls OpenAI API with filled prompt (mock verification)
  - Test service name derivation examples (tyre_pressure_monitoring, battery_state_charge)
  - Test VSS signal extraction from sample code with duplicates
  - Test progress message printing with emoji
  - Test OpenAI API authentication error handling
  - Test OpenAI API rate limit error handling
  - Test OpenAI API network error handling
  - Test LLM response parsing for markdown code blocks
  - Test LLM response parsing for raw code
  - Test whitespace stripping
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.8, 4.9, 4.10, 10.3, 10.4, 10.5, 12.1, 12.2, 12.3, 13.2, 13.3, 15.1, 15.2, 15.3, 16.1_

- [ ]* 3.3 Write property test for service name format compliance
  - **Property 1: Service Name Format Compliance**
  - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**
  - Test that for any requirement string, derived service_name contains only lowercase letters, numbers, and underscores
  - Test that service_name is derived from first 3-4 meaningful words excluding stop words

- [ ]* 3.4 Write property test for Dev Agent output structure
  - **Property 2: Dev Agent Output Structure Completeness**
  - **Validates: Requirements 4.7**
  - Test that for any requirement, DevAgent.generate() returns dict with all required keys: service_name, header_code, source_code, full_code, requirement, vss_signals_used
  - Test that all values are non-null

- [ ]* 3.5 Write property test for VSS signal extraction
  - **Property 6: VSS Signal Extraction Correctness**
  - **Validates: Requirements 13.2, 13.3**
  - Test that for any code with VSS signals matching "Vehicle." pattern, extraction finds all unique signals with no duplicates

- [x] 4. Implement QA Agent for test code generation
  - [x] 4.1 Create autoforge/agents/qa_agent.py with QAAgent class
    - Implement __init__ method accepting llm_client, prompt_template_path, model_name, max_tokens
    - Implement generate_tests method accepting requirement, generated_code, service_name
    - Implement _load_prompt_template method with UTF-8 encoding and FileNotFoundError handling
    - Implement _fill_prompt_template method with placeholder replacement
    - Implement _parse_llm_response method handling markdown code blocks and raw code
    - Add OpenAI API call with error handling for authentication, rate limit, and network errors
    - Add progress message printing with 🧪 emoji
    - Format test_file_name as "test_[service_name].cpp"
    - Return dictionary with test_code, service_name, test_file_name
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 10.2, 10.3, 10.4, 10.5, 10.6, 15.2, 15.3, 15.4, 16.2, 16.4, 19.2, 19.3, 19.4, 19.5, 19.6_

- [ ]* 4.2 Write unit tests for QA Agent
  - Test generate_tests() accepts requirement, code, and service_name
  - Test generate_tests() calls OpenAI API (mock verification)
  - Test test filename formatting: "test_[service_name].cpp"
  - Test progress message printing with emoji
  - Test OpenAI API error handling
  - Test LLM response parsing consistency with Dev Agent
  - _Requirements: 5.1, 5.3, 5.5, 5.6, 5.7, 10.3, 10.4, 10.5, 15.4, 16.2_

- [ ]* 4.3 Write property test for QA Agent output structure
  - **Property 3: QA Agent Output Structure Completeness**
  - **Validates: Requirements 5.4**
  - Test that for any valid inputs, QAAgent.generate_tests() returns dict with all required keys: test_code, service_name, test_file_name
  - Test that all values are non-null

- [ ]* 4.4 Write property test for test filename format
  - **Property 4: Test Filename Format**
  - **Validates: Requirements 5.5**
  - Test that for any service_name, test_file_name is formatted as "test_[service_name].cpp"

- [x] 5. Implement orchestrator for workflow coordination
  - [x] 5.1 Create autoforge/orchestrator.py with AutoForgeOrchestrator class
    - Implement __init__ method creating RAGRetriever, DevAgent, and QAAgent instances
    - Implement run method accepting requirement string
    - Implement _create_output_directory method with Path.mkdir(parents=True, exist_ok=True)
    - Implement _save_code_file method with UTF-8 encoding and parent directory creation
    - Implement _save_metadata method with JSON formatting and indentation
    - Implement _print_summary method with emoji indicators and file paths
    - Add workflow logic: derive service_name, create directory, call Dev Agent, save code, call QA Agent, save test, save metadata
    - Add graceful degradation: catch QA Agent exceptions, save service code and metadata, log error, continue execution
    - Return dictionary with service_name, code_file_path, test_file_path, metadata_file_path, dev_agent_output, qa_agent_output, error
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 11.1, 11.2, 11.3, 11.4, 12.5, 13.5, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 16.3, 16.4, 16.5, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 20.3_

- [ ]* 5.2 Write unit tests for orchestrator
  - Test initialization creates RAGRetriever, DevAgent, QAAgent instances
  - Test run() creates output directory with correct path
  - Test run() calls DevAgent.generate()
  - Test run() saves service code to correct file path
  - Test run() calls QAAgent.generate_tests()
  - Test run() saves test code to correct file path
  - Test run() saves metadata.json with all required fields
  - Test run() prints summary with file paths
  - Test graceful degradation when QA Agent fails (service code saved, metadata saved, error logged, no exception raised)
  - Test directory creation with parents=True and exist_ok=True
  - Test file saving with UTF-8 encoding
  - Test cross-platform path handling with pathlib.Path
  - _Requirements: 6.1, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.12, 11.1, 11.2, 11.4, 14.2, 14.3, 14.4, 14.5, 14.6, 16.3, 16.5, 17.1, 17.2, 17.3, 17.4, 17.6_

- [ ]* 5.3 Write property test for orchestrator output structure
  - **Property 5: Orchestrator Output Structure Completeness**
  - **Validates: Requirements 6.11**
  - Test that for any requirement, Orchestrator.run() returns dict with all required keys: service_name, code_file_path, test_file_path, metadata_file_path, dev_agent_output, qa_agent_output, error

- [ ]* 5.4 Write property test for metadata field completeness
  - **Property 7: Metadata Field Completeness**
  - **Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6**
  - Test that for any generated service, metadata.json contains all required fields: requirement, service_name, vss_signals_used, timestamp (ISO 8601), model_used

- [ ]* 5.5 Write property test for code file round-trip integrity
  - **Property 9: Code File Round-Trip Integrity**
  - **Validates: Requirements 20.1, 20.3, 20.4**
  - Test that for any generated C++ code, saving to file with UTF-8 and reading back produces exact byte-for-byte match

- [ ]* 5.6 Write property test for metadata round-trip integrity
  - **Property 10: Metadata Round-Trip Integrity**
  - **Validates: Requirements 20.2**
  - Test that for any metadata dictionary, JSON serialization and parsing preserves all fields and values

- [ ]* 5.7 Write property test for service name consistency
  - **Property 15: Service Name Consistency**
  - **Validates: Requirements 12.5**
  - Test that for any generated service, service_name is used consistently across directory names, code file names, test file names, and metadata

- [x] 6. Implement interactive mode for continuous requirement input
  - [x] 6.1 Add run_interactive method to AutoForgeOrchestrator class
    - Display welcome message
    - Loop: prompt for requirement, check for "quit" or "exit", call run() method, handle errors gracefully
    - Continue loop after errors without terminating
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ]* 6.2 Write unit tests for interactive mode
  - Test run_interactive() displays welcome message
  - Test run_interactive() terminates on "quit" or "exit"
  - Test run_interactive() handles errors gracefully and continues loop
  - _Requirements: 7.2, 7.5, 7.6_

- [x] 7. Create entry point script with demo and interactive modes
  - [x] 7.1 Create run_phase2.py with main function
    - Parse command-line arguments for --demo flag
    - If --demo: execute 2 preset requirements (tyre pressure monitoring, battery state of charge)
    - If not --demo: call orchestrator.run_interactive()
    - Import AutoForgeOrchestrator and handle initialization
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ]* 7.2 Write unit tests for entry point script
  - Test run_phase2.py exists
  - Test --demo flag support
  - Test demo mode executes 2 preset requirements
  - Test preset requirement 1: tyre pressure monitoring
  - Test preset requirement 2: battery state of charge
  - Test without --demo flag calls run_interactive()
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 8. Update requirements.txt with Phase 2 dependencies
  - Add openai package
  - Add python-dotenv package
  - Preserve all Phase 1 dependencies (chromadb, sentence-transformers, langchain, langchain-community)
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify test coverage meets goals (85% line coverage, 80% branch coverage)
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 10. Write integration tests for full workflow
  - Test full workflow: requirement → Dev Agent → QA Agent → file outputs
  - Test RAG context injection into prompts
  - Test metadata persistence and loading
  - Test service name consistency across directory, files, and metadata
  - _Requirements: 4.2, 6.5, 6.6, 6.7, 6.8, 6.9, 12.5, 13.5, 14.1_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Implementation uses Python with OpenAI API for LLM calls
- System extends Phase 1 RAG knowledge base with multi-agent orchestration
- Graceful degradation ensures service code is saved even if test generation fails
