# AutoForge Phase 2: Multi-Agent Code Generation System

## Implementation Summary

This document summarizes the implementation of AutoForge Phase 2, which extends the Phase 1 RAG knowledge base with an LLM-powered multi-agent code generation pipeline for automotive embedded software development.

## Completed Tasks

### ✅ Task 1: Configuration Module
**File:** `autoforge/config.py`

Implemented centralized configuration management with:
- Environment variable loading using python-dotenv
- Default values for all settings (LLM_PROVIDER, MODEL_NAME, MAX_TOKENS, etc.)
- `load_config()` function returning configuration dictionary
- `get_llm_client()` function returning initialized OpenAI client
- `validate_config()` function with comprehensive validation
- Error handling for missing API keys and invalid paths

### ✅ Task 2: Prompt Templates
**Files:** 
- `prompts/dev_agent_prompt.txt`
- `prompts/qa_agent_prompt.txt`

Created structured prompt templates with:
- **Dev Agent Prompt:** Instructions for generating MISRA-compliant C++ services with placeholders for requirement, VSS context, MISRA context, and ASPICE context
- **QA Agent Prompt:** Instructions for generating comprehensive test code with mock data providers and assertion-based validation

### ✅ Task 3: Dev Agent Implementation
**File:** `autoforge/agents/dev_agent.py`

Implemented DevAgent class with:
- `generate()` method accepting requirement string
- RAG context retrieval integration
- Prompt template loading and filling
- OpenAI API integration with error handling
- Service name derivation (snake_case from first 3-4 meaningful words)
- VSS signal extraction using pattern matching
- LLM response parsing (handles markdown and raw code)
- Progress message printing with emoji indicators

### ✅ Task 4: QA Agent Implementation
**File:** `autoforge/agents/qa_agent.py`

Implemented QAAgent class with:
- `generate_tests()` method accepting requirement, code, and service name
- Prompt template loading and filling
- OpenAI API integration with error handling
- Test filename formatting (`test_[service_name].cpp`)
- LLM response parsing consistent with Dev Agent
- Progress message printing with emoji indicators

### ✅ Task 5: Orchestrator Implementation
**File:** `autoforge/orchestrator.py`

Implemented AutoForgeOrchestrator class with:
- Initialization of RAGRetriever, DevAgent, and QAAgent
- `run()` method coordinating complete workflow
- Output directory creation with safe file system operations
- Code file saving with UTF-8 encoding
- Metadata persistence in JSON format
- Graceful degradation (saves service code even if QA Agent fails)
- Summary printing with file paths

### ✅ Task 6: Interactive Mode
**File:** `autoforge/orchestrator.py` (method: `run_interactive()`)

Implemented interactive mode with:
- Welcome message display
- Continuous requirement prompting
- Quit/exit command handling
- Graceful error handling that continues the loop

### ✅ Task 7: Entry Point Script
**File:** `run_phase2.py`

Created entry point script with:
- Command-line argument parsing (`--demo` flag)
- Demo mode with 2 preset requirements:
  1. Tyre pressure monitoring service
  2. Battery state of charge service
- Interactive mode fallback (when no `--demo` flag)
- Orchestrator initialization and error handling

### ✅ Task 8: Dependencies Update
**File:** `requirements.txt`

Updated requirements.txt with:
- `openai` package for LLM API access
- `python-dotenv` for environment variable management
- Preserved all Phase 1 dependencies (chromadb, sentence-transformers, langchain, langchain-community)

## Project Structure

```
tata_elxsi/
├── autoforge/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── dev_agent.py          # Dev Agent implementation
│   │   └── qa_agent.py           # QA Agent implementation
│   ├── config.py                 # Configuration module
│   ├── orchestrator.py           # Multi-agent orchestrator
│   ├── rag/                      # Phase 1 RAG system
│   │   ├── retriever.py
│   │   └── ingestor.py
│   ├── data/
│   │   └── chroma_db/            # Phase 1 knowledge base
│   └── outputs/                  # Generated code output directory
├── prompts/
│   ├── dev_agent_prompt.txt      # Dev Agent prompt template
│   └── qa_agent_prompt.txt       # QA Agent prompt template
├── run_phase2.py                 # Entry point script
├── verify_phase2.py              # Verification script
├── requirements.txt              # Updated dependencies
└── .env                          # Environment variables (user creates)
```

## Key Features Implemented

### 1. Configuration Management
- Centralized environment-based configuration
- Secure API key handling
- Validation with clear error messages
- Cross-platform path handling using pathlib

### 2. Multi-Agent Architecture
- **Dev Agent:** Generates MISRA-compliant C++ service code
- **QA Agent:** Generates comprehensive test suites
- **Orchestrator:** Coordinates agents and manages workflow

### 3. RAG Integration
- Retrieves automotive domain knowledge (VSS signals, MISRA rules, ASPICE guidelines)
- Injects context into LLM prompts for domain-specific code generation

### 4. Graceful Degradation
- Saves service code even if test generation fails
- Logs errors without terminating workflow
- Includes error field in output dictionary

### 5. Metadata Tracking
- Persists generation metadata in JSON format
- Tracks requirement, service name, VSS signals used, timestamp, and model version
- Human-readable formatting with indentation

### 6. Service Name Derivation
- Extracts meaningful words from requirements
- Filters stop words
- Converts to snake_case format
- Consistent naming across files and directories

### 7. VSS Signal Extraction
- Pattern matching for "Vehicle.*" references
- Deduplication of signal names
- Traceability in metadata

## Usage

### Prerequisites
1. Complete Phase 1 setup (RAG knowledge base initialized)
2. Set `OPENAI_API_KEY` in `.env` file
3. Install dependencies: `pip install -r requirements.txt`

### Demo Mode
```bash
python run_phase2.py --demo
```

Executes 2 preset requirements:
1. Tyre pressure monitoring service
2. Battery state of charge service

### Interactive Mode
```bash
python run_phase2.py
```

Continuously prompts for requirements until user enters "quit" or "exit".

### Verification
```bash
python verify_phase2.py
```

Verifies:
- File structure completeness
- Module imports
- Prompt template placeholders
- Configuration loading

## Output Structure

For each generated service, the system creates:

```
autoforge/outputs/[service_name]/
├── [service_name].cpp           # Generated service code
├── test_[service_name].cpp      # Generated test code
└── metadata.json                # Generation metadata
```

### Example Metadata
```json
{
  "requirement": "Create a tyre pressure monitoring service...",
  "service_name": "tyre_pressure_monitoring",
  "vss_signals_used": [
    "Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure",
    "Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.Pressure"
  ],
  "timestamp": "2024-01-15T10:30:45.123456",
  "model_used": "gpt-4o-mini"
}
```

## Error Handling

### Configuration Errors
- Missing `OPENAI_API_KEY`: Raises ValueError with clear message
- Invalid `CHROMA_DB_PATH`: Raises FileNotFoundError
- Invalid `MODEL_NAME` or `MAX_TOKENS`: Raises ValueError

### API Errors
- Authentication errors: Clear message about invalid/missing API key
- Rate limit errors: Indicates rate limit exceeded
- Network errors: Indicates connection failure
- All errors preserve original error message for debugging

### File System Errors
- Safe directory creation with `parents=True, exist_ok=True`
- UTF-8 encoding for all file operations
- Clear error messages with file paths

### Graceful Degradation
- QA Agent failures don't lose Dev Agent work
- Service code and metadata saved regardless
- Error logged and included in return dictionary

## Requirements Coverage

All 20 requirements from the specification are implemented:
- ✅ Requirement 1: Environment Configuration Management
- ✅ Requirement 2: Dev Agent Prompt Template
- ✅ Requirement 3: QA Agent Prompt Template
- ✅ Requirement 4: Dev Agent Code Generation
- ✅ Requirement 5: QA Agent Test Generation
- ✅ Requirement 6: Multi-Agent Orchestration
- ✅ Requirement 7: Interactive Mode
- ✅ Requirement 8: Demo Mode Execution
- ✅ Requirement 9: Dependency Management
- ✅ Requirement 10: API Error Handling
- ✅ Requirement 11: File System Safety
- ✅ Requirement 12: Service Name Derivation
- ✅ Requirement 13: VSS Signal Extraction
- ✅ Requirement 14: Metadata Persistence
- ✅ Requirement 15: Code Parsing and Extraction
- ✅ Requirement 16: Progress Feedback
- ✅ Requirement 17: Graceful Degradation
- ✅ Requirement 18: Configuration Validation
- ✅ Requirement 19: Prompt Template Loading
- ✅ Requirement 20: Round-Trip Code Integrity

## Next Steps

### For Users
1. Set up `.env` file with `OPENAI_API_KEY`
2. Verify Phase 1 RAG database exists at `autoforge/data/chroma_db`
3. Run verification: `python verify_phase2.py`
4. Try demo mode: `python run_phase2.py --demo`
5. Use interactive mode for custom requirements

### For Testing (Optional)
The implementation plan includes optional test tasks (marked with *):
- Unit tests for all modules
- Property-based tests for correctness properties
- Integration tests for full workflow

These can be implemented later for comprehensive validation.

## Technical Notes

### LLM Response Parsing
- Handles both markdown code blocks (```cpp) and raw code
- Strips leading/trailing whitespace
- Concatenates multiple code blocks if present

### Service Name Algorithm
1. Tokenize requirement into words
2. Filter stop words (create, a, the, that, when, etc.)
3. Extract first 3-4 meaningful words
4. Convert to lowercase and join with underscores
5. Remove special characters except underscores

### VSS Signal Pattern
- Pattern: `Vehicle\.[A-Za-z0-9.]+`
- Extracts all unique occurrences
- Sorted alphabetically in output

### Prompt Template Placeholders
- Dev Agent: `{requirement}`, `{vss_context}`, `{misra_context}`, `{aspice_context}`
- QA Agent: `{requirement}`, `{generated_code}`, `{service_name}`

## Conclusion

AutoForge Phase 2 successfully implements a multi-agent code generation system that:
- Generates MISRA-compliant C++ automotive services
- Creates comprehensive test suites
- Integrates automotive domain knowledge via RAG
- Provides both demo and interactive modes
- Handles errors gracefully
- Tracks metadata for traceability

The system is ready for demonstration and can be extended with additional testing and features as needed.
