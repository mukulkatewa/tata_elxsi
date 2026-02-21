# Tasks: AutoForge Self-Healing Build Loop

## Phase 1: Core Components Implementation

### 1.1 DockerBuilder Implementation
- [x] 1.1.1 Create DockerBuilder class with Docker availability detection
- [x] 1.1.2 Implement build_image method for Docker image creation
- [x] 1.1.3 Implement check_image_exists method
- [x] 1.1.4 Implement compile_service method with Docker compilation
- [x] 1.1.5 Implement _compile_fallback method for host g++ compilation
- [x] 1.1.6 Implement _prepare_cmake method for template substitution
- [x] 1.1.7 Implement _parse_errors method for error/warning extraction
- [x] 1.1.8 Add timeout handling (60s) for all subprocess calls
- [x] 1.1.9 Add comprehensive error handling for subprocess failures

### 1.2 StaticAnalyzer Implementation
- [x] 1.2.1 Create StaticAnalyzer class
- [x] 1.2.2 Implement run_cppcheck method with --enable=all and --std=c++14
- [x] 1.2.3 Implement check_misra_patterns method
- [x] 1.2.4 Implement _check_malloc_free pattern detection
- [x] 1.2.5 Implement _check_goto pattern detection
- [x] 1.2.6 Implement _check_printf_scanf pattern detection
- [x] 1.2.7 Implement _check_multiple_returns pattern detection
- [x] 1.2.8 Implement _check_null_usage pattern detection
- [x] 1.2.9 Implement line number detection for all violations
- [x] 1.2.10 Add timeout handling for cppcheck execution

### 1.3 CodeHealer Implementation
- [x] 1.3.1 Create CodeHealer class with OpenAI client initialization
- [x] 1.3.2 Implement heal method with LLM API call
- [x] 1.3.3 Implement extract_code method for parsing LLM responses
- [x] 1.3.4 Implement _construct_prompt method
- [x] 1.3.5 Add support for build errors in healing
- [x] 1.3.6 Add support for MISRA violations in healing
- [x] 1.3.7 Add errors_addressed tracking
- [x] 1.3.8 Add comprehensive error handling for API failures

### 1.4 SelfHealingBuildLoop Implementation
- [x] 1.4.1 Create SelfHealingBuildLoop class
- [x] 1.4.2 Implement run method with main loop logic
- [x] 1.4.3 Implement compilation → analysis → healing workflow
- [x] 1.4.4 Implement _save_attempt method for intermediate code versions
- [x] 1.4.5 Implement _certify_code method for certification
- [x] 1.4.6 Implement _generate_report method for build_report.json
- [x] 1.4.7 Implement print_summary method for human-readable output
- [x] 1.4.8 Add state management (current_attempt, current_code, attempts_history)
- [x] 1.4.9 Add max_attempts termination logic
- [x] 1.4.10 Add progress indicators with emojis

## Phase 2: Docker Infrastructure

### 2.1 Dockerfile Creation
- [x] 2.1.1 Create docker/Dockerfile with Ubuntu 22.04 base
- [x] 2.1.2 Install gcc, g++, cmake, make with --no-install-recommends
- [x] 2.1.3 Install cppcheck and python3
- [x] 2.1.4 Set /workspace as working directory
- [x] 2.1.5 Add apt-get clean and remove lists for minimal size

### 2.2 CMake Template Creation
- [x] 2.2.1 Create docker/CMakeLists.txt.template
- [x] 2.2.2 Add {{SERVICE_NAME}} placeholder
- [x] 2.2.3 Set cmake_minimum_required to 3.10
- [x] 2.2.4 Set CMAKE_CXX_STANDARD to 14
- [x] 2.2.5 Add compiler flags: -Wall -Wextra -Werror
- [x] 2.2.6 Define executable target with service name

## Phase 3: Integration and Entry Point

### 3.1 Phase 3 Entry Point
- [x] 3.1.1 Create run_phase3.py script
- [x] 3.1.2 Implement run_full_pipeline function
- [x] 3.1.3 Integrate Phase 2 orchestrator call
- [x] 3.1.4 Extract generated code from Phase 2 results
- [x] 3.1.5 Initialize Phase 3 components
- [x] 3.1.6 Execute build loop with generated code
- [x] 3.1.7 Implement demo_mode with preset requirement
- [x] 3.1.8 Implement interactive_mode for continuous processing
- [x] 3.1.9 Add command-line argument support
- [x] 3.1.10 Add final results summary

### 3.2 Module Initialization
- [x] 3.2.1 Create autoforge/build/__init__.py
- [x] 3.2.2 Export all Phase 3 classes

## Phase 4: Testing (Property-Based and Unit Tests)

### 4.1 DockerBuilder Tests
- [ ] 4.1.1 Test Docker availability detection
- [ ] 4.1.2 Test image build success/failure
- [ ] 4.1.3 Test image existence checking
- [ ] 4.1.4 Test CMake template substitution (Property Test)
- [ ] 4.1.5 Test Docker compilation success
- [ ] 4.1.6 Test Docker compilation failure with error parsing
- [ ] 4.1.7 Test fallback mode compilation
- [ ] 4.1.8 Test timeout enforcement
- [ ] 4.1.9 Test subprocess error handling
- [ ] 4.1.10 Property Test: Compiler output parsing across random stderr

### 4.2 StaticAnalyzer Tests
- [ ] 4.2.1 Test cppcheck execution with correct flags
- [ ] 4.2.2 Test cppcheck output parsing
- [ ] 4.2.3 Test malloc/free detection (Property Test)
- [ ] 4.2.4 Test goto detection (Property Test)
- [ ] 4.2.5 Test printf/scanf detection (Property Test)
- [ ] 4.2.6 Test multiple returns detection (Property Test)
- [ ] 4.2.7 Test NULL usage detection (Property Test)
- [ ] 4.2.8 Property Test: Line number detection accuracy
- [ ] 4.2.9 Property Test: Violation structure completeness
- [ ] 4.2.10 Test timeout handling

### 4.3 CodeHealer Tests
- [ ] 4.3.1 Test prompt construction with build errors
- [ ] 4.3.2 Test prompt construction with MISRA violations
- [ ] 4.3.3 Property Test: Prompt completeness across random errors
- [ ] 4.3.4 Property Test: Code extraction from various markdown formats
- [ ] 4.3.5 Test code extraction from raw responses
- [ ] 4.3.6 Test OpenAI API call success
- [ ] 4.3.7 Test OpenAI API call failure handling
- [ ] 4.3.8 Test errors_addressed tracking
- [ ] 4.3.9 Test empty response handling
- [ ] 4.3.10 Test API key validation

### 4.4 SelfHealingBuildLoop Tests
- [ ] 4.4.1 Test initial code file writing
- [ ] 4.4.2 Property Test: Attempt file naming and persistence
- [ ] 4.4.3 Test compilation failure → healing workflow
- [ ] 4.4.4 Test static analysis failure → healing workflow
- [ ] 4.4.5 Test successful certification workflow
- [ ] 4.4.6 Test max_attempts termination
- [ ] 4.4.7 Property Test: Build report structure completeness
- [ ] 4.4.8 Test certification file creation
- [ ] 4.4.9 Test final code persistence
- [ ] 4.4.10 Test state management across attempts

### 4.5 Integration Tests
- [ ] 4.5.1 Test full Phase 2 → Phase 3 pipeline
- [ ] 4.5.2 Test end-to-end certification of valid code
- [ ] 4.5.3 Test end-to-end failure handling
- [ ] 4.5.4 Test Docker and fallback mode switching
- [ ] 4.5.5 Test multiple healing iterations

### 4.6 Property Test Configuration
- [ ] 4.6.1 Set up hypothesis library
- [ ] 4.6.2 Configure 100 iterations per property test
- [ ] 4.6.3 Add property test tags with feature and property references
- [ ] 4.6.4 Create test data generators for C++ code
- [ ] 4.6.5 Create test data generators for compiler output
- [ ] 4.6.6 Create test data generators for LLM responses

## Phase 5: Documentation and Deployment

### 5.1 Documentation
- [ ] 5.1.1 Create PHASE3_QUICK_START.md
- [ ] 5.1.2 Document Docker setup requirements
- [ ] 5.1.3 Document fallback mode usage
- [ ] 5.1.4 Add usage examples for run_phase3.py
- [ ] 5.1.5 Document build report structure
- [ ] 5.1.6 Document certification process
- [ ] 5.1.7 Add troubleshooting guide

### 5.2 Deployment Preparation
- [ ] 5.2.1 Update requirements.txt with new dependencies
- [ ] 5.2.2 Create Docker image build script
- [ ] 5.2.3 Add CI/CD pipeline configuration
- [ ] 5.2.4 Create performance benchmarks
- [ ] 5.2.5 Add pre-commit hooks for testing

## Phase 6: Verification and Validation

### 6.1 System Verification
- [ ] 6.1.1 Verify Docker image builds successfully
- [ ] 6.1.2 Verify fallback mode works without Docker
- [ ] 6.1.3 Verify all MISRA patterns are detected
- [ ] 6.1.4 Verify LLM healing produces valid fixes
- [ ] 6.1.5 Verify certification process creates all required files
- [ ] 6.1.6 Verify build reports contain all required fields

### 6.2 End-to-End Validation
- [ ] 6.2.1 Run demo mode and verify certification
- [ ] 6.2.2 Test with intentionally broken code
- [ ] 6.2.3 Test with MISRA-violating code
- [ ] 6.2.4 Test max_attempts termination
- [ ] 6.2.5 Validate all progress indicators display correctly
- [ ] 6.2.6 Validate build summary output
