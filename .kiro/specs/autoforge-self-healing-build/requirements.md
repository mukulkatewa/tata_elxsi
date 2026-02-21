# Requirements Document

## Introduction

AutoForge Phase 3 extends Phase 2's multi-agent code generation system with a self-healing build loop that automatically compiles, analyzes, and fixes generated C++ code. The system uses Docker-based compilation, static analysis tools (cppcheck), MISRA pattern checking, and LLM-powered error correction to iteratively improve generated code until it passes both compilation and static analysis checks. This automated quality assurance loop ensures that generated automotive embedded software is not only syntactically correct but also compliant with industry safety standards, reducing manual debugging effort and accelerating the path from requirements to certified production code.

## Glossary

- **DockerBuilder**: The component responsible for building Docker images and compiling C++ services in isolated containers with automotive toolchains
- **StaticAnalyzer**: The component that runs cppcheck and custom MISRA pattern checks on compiled code to detect violations
- **CodeHealer**: The LLM-powered component that analyzes build errors and static analysis violations to generate fixed code
- **SelfHealingBuildLoop**: The orchestrator that coordinates compilation, analysis, healing, and certification across multiple attempts
- **Build_Attempt**: A single iteration of the build loop including compilation, analysis, and optional healing
- **CERTIFIED**: The status indicating code has passed both compilation and static analysis without violations
- **Build_Report**: A JSON file containing complete history of all build attempts, errors, violations, and final status
- **Attempt_History**: The collection of intermediate code versions saved as [service_name]_attempt_N.cpp files
- **Docker_Fallback**: The mechanism to use host g++ compiler when Docker is unavailable
- **MISRA_Violation**: A detected pattern in code that violates MISRA-C++ safety guidelines (malloc/free, goto, printf/scanf, multiple returns, NULL vs nullptr)
- **CMake_Template**: A template CMakeLists.txt file with {{SERVICE_NAME}} placeholder for build configuration
- **Compile_Timeout**: The maximum duration (60 seconds) allowed for a compilation attempt before termination
- **Max_Healing_Attempts**: The maximum number of healing iterations (3) before marking build as failed

## Requirements

### Requirement 1: Docker Image Build

**User Story:** As a build system, I want to build a Docker image with automotive C++ toolchains, so that I can compile services in a consistent isolated environment.

#### Acceptance Criteria

1. THE DockerBuilder SHALL provide a build_image method that accepts a dockerfile_path parameter
2. WHEN build_image is called, THE DockerBuilder SHALL execute docker build command with the provided Dockerfile
3. THE DockerBuilder SHALL tag the built image as "autoforge-builder:latest"
4. WHEN build_image succeeds, THE DockerBuilder SHALL return True
5. IF docker build fails, THE DockerBuilder SHALL raise an exception with the docker error message
6. THE DockerBuilder SHALL provide a check_image_exists method that verifies if "autoforge-builder:latest" image exists
7. WHEN check_image_exists is called, THE DockerBuilder SHALL execute docker images command and search for the image name
8. THE DockerBuilder SHALL return True if the image exists, False otherwise

### Requirement 2: Dockerfile Specification

**User Story:** As a build environment, I want a minimal Docker image with C++ compilation and analysis tools, so that I can compile and check automotive embedded code efficiently.

#### Acceptance Criteria

1. THE Dockerfile SHALL be located at docker/Dockerfile
2. THE Dockerfile SHALL use Ubuntu 22.04 as the base image
3. THE Dockerfile SHALL install gcc with --no-install-recommends flag for minimal size
4. THE Dockerfile SHALL install g++ with --no-install-recommends flag
5. THE Dockerfile SHALL install cmake with --no-install-recommends flag
6. THE Dockerfile SHALL install make with --no-install-recommends flag
7. THE Dockerfile SHALL install cppcheck with --no-install-recommends flag
8. THE Dockerfile SHALL install python3 with --no-install-recommends flag
9. THE Dockerfile SHALL set /workspace as the working directory
10. THE Dockerfile SHALL run apt-get clean and remove /var/lib/apt/lists/* to minimize image size

### Requirement 3: CMake Template

**User Story:** As a build system, I want a CMake template with automotive compiler flags, so that I can generate build configurations for each service.

#### Acceptance Criteria

1. THE CMake_Template SHALL be located at docker/CMakeLists.txt.template
2. THE CMake_Template SHALL contain a {{SERVICE_NAME}} placeholder for service name substitution
3. THE CMake_Template SHALL specify cmake_minimum_required version 3.10
4. THE CMake_Template SHALL set CMAKE_CXX_STANDARD to 14
5. THE CMake_Template SHALL set CMAKE_CXX_STANDARD_REQUIRED to ON
6. THE CMake_Template SHALL add compiler flags -Wall for all warnings
7. THE CMake_Template SHALL add compiler flags -Wextra for extra warnings
8. THE CMake_Template SHALL add compiler flags -Werror to treat warnings as errors
9. THE CMake_Template SHALL define an executable target using the service name
10. THE CMake_Template SHALL add the service .cpp file to the executable target

### Requirement 4: Docker-Based Compilation

**User Story:** As a build system, I want to compile C++ services in Docker containers, so that I can ensure consistent build environments and isolate compilation from the host system.

#### Acceptance Criteria

1. THE DockerBuilder SHALL provide a compile_service method that accepts service_dir and service_name parameters
2. WHEN compile_service is called, THE DockerBuilder SHALL check if the Docker image exists using check_image_exists
3. IF the Docker image does not exist, THE DockerBuilder SHALL call build_image to create it
4. WHEN compiling, THE DockerBuilder SHALL mount the service directory to /workspace in the container
5. WHEN compiling, THE DockerBuilder SHALL execute cmake and make commands inside the container
6. THE DockerBuilder SHALL set a 60 second timeout for the compilation process
7. WHEN compilation succeeds, THE DockerBuilder SHALL return success=True, stdout, stderr, empty error_lines, empty warning_lines, and attempt_number
8. WHEN compilation fails, THE DockerBuilder SHALL parse stderr to extract error lines and warning lines
9. WHEN compilation fails, THE DockerBuilder SHALL return success=False, stdout, stderr, error_lines, warning_lines, and attempt_number
10. IF the compilation timeout is exceeded, THE DockerBuilder SHALL terminate the container and return success=False with timeout error message

### Requirement 5: Docker Fallback Mechanism

**User Story:** As a build system, I want to fall back to host g++ compiler when Docker is unavailable, so that the system remains functional in environments without Docker.

#### Acceptance Criteria

1. WHEN Docker is not available on the host system, THE DockerBuilder SHALL detect the unavailability
2. IF Docker is unavailable, THE DockerBuilder SHALL print a warning message indicating fallback to host g++ compiler
3. WHEN using fallback mode, THE DockerBuilder SHALL execute g++ directly on the host with -std=c++14 -Wall -Wextra -Werror flags
4. WHEN using fallback mode, THE DockerBuilder SHALL apply the same 60 second timeout as Docker compilation
5. WHEN using fallback mode, THE DockerBuilder SHALL return the same output format as Docker compilation (success, stdout, stderr, error_lines, warning_lines, attempt_number)

### Requirement 6: Build Error Parsing

**User Story:** As an error analysis system, I want to parse compiler output to extract error and warning lines, so that I can provide structured feedback to the code healer.

#### Acceptance Criteria

1. WHEN parsing compiler stderr, THE DockerBuilder SHALL identify lines containing "error:" as error lines
2. WHEN parsing compiler stderr, THE DockerBuilder SHALL identify lines containing "warning:" as warning lines
3. THE DockerBuilder SHALL return error_lines as a list of strings containing the full error messages
4. THE DockerBuilder SHALL return warning_lines as a list of strings containing the full warning messages
5. THE DockerBuilder SHALL preserve the original line formatting in error_lines and warning_lines for readability

### Requirement 7: Static Analysis with Cppcheck

**User Story:** As a code quality system, I want to run cppcheck on compiled code, so that I can detect potential bugs and style violations beyond compilation errors.

#### Acceptance Criteria

1. THE StaticAnalyzer SHALL provide a run_cppcheck method that accepts service_dir and service_name parameters
2. WHEN run_cppcheck is called, THE StaticAnalyzer SHALL execute cppcheck with --enable=all flag
3. WHEN run_cppcheck is called, THE StaticAnalyzer SHALL execute cppcheck with --std=c++14 flag
4. WHEN run_cppcheck is called, THE StaticAnalyzer SHALL execute cppcheck on the service .cpp file
5. THE StaticAnalyzer SHALL capture cppcheck stdout and stderr output
6. WHEN cppcheck detects violations, THE StaticAnalyzer SHALL parse the output to extract violation details
7. THE StaticAnalyzer SHALL return passed=True if no violations are found, passed=False otherwise
8. THE StaticAnalyzer SHALL return violations as a list of dictionaries containing violation details
9. THE StaticAnalyzer SHALL return warnings as a list of warning messages
10. THE StaticAnalyzer SHALL return raw_output containing the complete cppcheck output for debugging

### Requirement 8: MISRA Pattern Checking

**User Story:** As a safety compliance system, I want to check for common MISRA-C++ violations using pattern matching, so that I can enforce automotive safety standards on generated code.

#### Acceptance Criteria

1. THE StaticAnalyzer SHALL provide a check_misra_patterns method that accepts code as a string parameter
2. WHEN check_misra_patterns is called, THE StaticAnalyzer SHALL check for malloc or free function usage
3. WHEN check_misra_patterns is called, THE StaticAnalyzer SHALL check for goto statement usage
4. WHEN check_misra_patterns is called, THE StaticAnalyzer SHALL check for printf or scanf function usage
5. WHEN check_misra_patterns is called, THE StaticAnalyzer SHALL check for multiple return statements in functions
6. WHEN check_misra_patterns is called, THE StaticAnalyzer SHALL check for NULL usage instead of nullptr
7. FOR EACH detected pattern violation, THE StaticAnalyzer SHALL create a violation dictionary with type, line_number, and message fields
8. THE StaticAnalyzer SHALL return passed=True if no MISRA violations are found, passed=False otherwise
9. THE StaticAnalyzer SHALL return violations as a list of dictionaries
10. THE StaticAnalyzer SHALL return warnings as an empty list (MISRA violations are errors, not warnings)

### Requirement 9: LLM-Powered Code Healing

**User Story:** As an automated debugging system, I want to use LLM to fix compilation errors and static analysis violations, so that I can iteratively improve generated code without manual intervention.

#### Acceptance Criteria

1. THE CodeHealer SHALL provide a heal method that accepts original_code, build_errors, misra_violations, and attempt parameters
2. WHEN heal is called, THE CodeHealer SHALL construct a prompt instructing the LLM to fix all listed issues
3. THE prompt SHALL instruct the LLM to not change the logic of the code
4. THE prompt SHALL instruct the LLM to return raw C++ code only without markdown formatting or explanations
5. WHEN heal is called, THE CodeHealer SHALL make an OpenAI API call with the constructed prompt
6. THE CodeHealer SHALL parse the LLM response to extract fixed code using extract_code method
7. THE CodeHealer SHALL strip markdown code fences (```cpp) from the response
8. WHEN healing succeeds, THE CodeHealer SHALL return fixed_code, attempt number, errors_addressed list, and success=True
9. IF the OpenAI API call fails, THE CodeHealer SHALL return success=False with error message
10. THE CodeHealer SHALL include the attempt number in the return dictionary for tracking

### Requirement 10: Code Extraction from LLM Response

**User Story:** As a code parsing system, I want to reliably extract C++ code from LLM responses, so that I can handle various response formats including markdown fences.

#### Acceptance Criteria

1. THE CodeHealer SHALL provide an extract_code method that accepts an LLM response string
2. WHEN extract_code is called, THE CodeHealer SHALL search for markdown code blocks with ```cpp or ``` delimiters
3. IF markdown code blocks are found, THE CodeHealer SHALL extract the content between the delimiters
4. IF no markdown code blocks are found, THE CodeHealer SHALL treat the entire response as raw code
5. THE CodeHealer SHALL strip leading and trailing whitespace from extracted code
6. THE CodeHealer SHALL return the cleaned code string

### Requirement 11: Self-Healing Build Loop Orchestration

**User Story:** As a build automation system, I want to orchestrate compilation, analysis, and healing in a loop, so that I can automatically fix code issues until certification or max attempts are reached.

#### Acceptance Criteria

1. THE SelfHealingBuildLoop SHALL provide a run method that accepts service_dir, service_name, and initial_code parameters
2. THE SelfHealingBuildLoop SHALL initialize with max_attempts parameter defaulting to 3
3. WHEN run is called, THE SelfHealingBuildLoop SHALL write the initial code to [service_name].cpp in the service directory
4. FOR EACH attempt up to max_attempts, THE SelfHealingBuildLoop SHALL execute the following workflow: compile, check compilation result, analyze if compiled, heal if issues found
5. WHEN compilation fails, THE SelfHealingBuildLoop SHALL call CodeHealer.heal with build errors and retry compilation
6. WHEN compilation succeeds, THE SelfHealingBuildLoop SHALL call StaticAnalyzer.run_cppcheck and StaticAnalyzer.check_misra_patterns
7. WHEN static analysis finds violations, THE SelfHealingBuildLoop SHALL call CodeHealer.heal with violations and retry from compilation step
8. WHEN both compilation and static analysis pass, THE SelfHealingBuildLoop SHALL mark the code as CERTIFIED
9. THE SelfHealingBuildLoop SHALL save each attempt's code to [service_name]_attempt_N.cpp for debugging
10. WHEN CERTIFIED, THE SelfHealingBuildLoop SHALL save final code to [service_name]_final.cpp
11. WHEN CERTIFIED, THE SelfHealingBuildLoop SHALL copy final code to certified/[service_name].cpp directory
12. WHEN CERTIFIED, THE SelfHealingBuildLoop SHALL create a CERTIFIED.txt file in the certified directory with certification timestamp
13. THE SelfHealingBuildLoop SHALL save a build_report.json file with complete attempt history
14. WHEN run completes, THE SelfHealingBuildLoop SHALL call print_summary to display results

### Requirement 12: Attempt History Tracking

**User Story:** As a debugging engineer, I want to see all intermediate code versions during the healing process, so that I can understand how the code evolved and diagnose issues.

#### Acceptance Criteria

1. FOR EACH build attempt, THE SelfHealingBuildLoop SHALL save the code version to [service_name]_attempt_N.cpp where N is the attempt number
2. THE attempt files SHALL be saved in the service output directory
3. THE attempt files SHALL contain the exact code that was compiled in that attempt
4. THE attempt files SHALL be preserved even if subsequent attempts fail
5. THE attempt numbering SHALL start at 1 for the initial code

### Requirement 13: Build Report Generation

**User Story:** As a project manager, I want a detailed build report with all attempts and outcomes, so that I can track code quality metrics and healing effectiveness.

#### Acceptance Criteria

1. THE SelfHealingBuildLoop SHALL generate a build_report.json file in the service output directory
2. THE build_report SHALL include a service_name field
3. THE build_report SHALL include a final_status field with values "CERTIFIED", "FAILED", or "MAX_ATTEMPTS_REACHED"
4. THE build_report SHALL include a total_attempts field indicating the number of attempts made
5. THE build_report SHALL include an attempts array containing details for each attempt
6. FOR EACH attempt in the attempts array, THE build_report SHALL include attempt_number, compilation_success, compilation_errors, static_analysis_passed, static_analysis_violations, healing_applied, and code_file_path fields
7. THE build_report SHALL include a certification_timestamp field if status is CERTIFIED
8. THE build_report.json file SHALL be formatted with indentation for human readability
9. THE build_report SHALL include a final_code_path field pointing to the final code file

### Requirement 14: Certification Process

**User Story:** As a quality assurance system, I want to certify code that passes all checks, so that I can distinguish production-ready code from work-in-progress.

#### Acceptance Criteria

1. WHEN code passes both compilation and static analysis, THE SelfHealingBuildLoop SHALL mark the code as CERTIFIED
2. WHEN code is CERTIFIED, THE SelfHealingBuildLoop SHALL create a certified/ subdirectory in the service output directory
3. WHEN code is CERTIFIED, THE SelfHealingBuildLoop SHALL copy the final code to certified/[service_name].cpp
4. WHEN code is CERTIFIED, THE SelfHealingBuildLoop SHALL create a CERTIFIED.txt file in the certified directory
5. THE CERTIFIED.txt file SHALL contain the certification timestamp in ISO 8601 format
6. THE CERTIFIED.txt file SHALL contain the service name
7. THE CERTIFIED.txt file SHALL contain the total number of attempts required to achieve certification
8. THE CERTIFIED.txt file SHALL contain a message "Code has passed compilation and static analysis checks"

### Requirement 15: Build Summary Display

**User Story:** As a system user, I want a human-readable summary of the build process, so that I can quickly understand the outcome without reading JSON files.

#### Acceptance Criteria

1. THE SelfHealingBuildLoop SHALL provide a print_summary method that accepts a build_report dictionary
2. WHEN print_summary is called, THE SelfHealingBuildLoop SHALL display ASCII art or emoji indicators for visual appeal
3. THE summary SHALL include the service name
4. THE summary SHALL include the final status (CERTIFIED, FAILED, or MAX_ATTEMPTS_REACHED)
5. THE summary SHALL include the total number of attempts
6. IF status is CERTIFIED, THE summary SHALL display a success message with 🎉 emoji
7. IF status is FAILED or MAX_ATTEMPTS_REACHED, THE summary SHALL display a failure message with ❌ emoji
8. THE summary SHALL include the path to the build_report.json file
9. IF status is CERTIFIED, THE summary SHALL include the path to the certified code file

### Requirement 16: Progress Indicators

**User Story:** As a system user, I want real-time progress feedback during the build loop, so that I understand what the system is doing at each step.

#### Acceptance Criteria

1. WHEN starting compilation, THE SelfHealingBuildLoop SHALL print a message with 🔨 emoji indicating "Compiling [service_name] (Attempt N)"
2. WHEN starting static analysis, THE SelfHealingBuildLoop SHALL print a message with 🔍 emoji indicating "Analyzing [service_name]"
3. WHEN starting code healing, THE SelfHealingBuildLoop SHALL print a message with 🩺 emoji indicating "Healing [service_name] (Attempt N)"
4. WHEN compilation succeeds, THE SelfHealingBuildLoop SHALL print a success message with ✅ emoji
5. WHEN compilation fails, THE SelfHealingBuildLoop SHALL print a failure message with ❌ emoji and error count
6. WHEN static analysis finds violations, THE SelfHealingBuildLoop SHALL print a message with ⚠️ emoji and violation count
7. WHEN code is certified, THE SelfHealingBuildLoop SHALL print a certification message with 🎉 emoji

### Requirement 17: Phase 3 Entry Point

**User Story:** As a developer, I want an entry point script that runs the full Phase 2 + Phase 3 pipeline, so that I can generate and certify code end-to-end with a single command.

#### Acceptance Criteria

1. THE Entry_Point_Script SHALL be named run_phase3.py
2. THE Entry_Point_Script SHALL provide a run_full_pipeline function that accepts a requirement string
3. WHEN run_full_pipeline is called, THE Entry_Point_Script SHALL execute Phase 2 code generation using AutoForgeOrchestrator
4. WHEN Phase 2 completes, THE Entry_Point_Script SHALL extract the generated code from Phase 2 output
5. WHEN Phase 2 completes, THE Entry_Point_Script SHALL execute Phase 3 self-healing build loop using SelfHealingBuildLoop
6. THE Entry_Point_Script SHALL pass the service directory, service name, and generated code to the build loop
7. THE Entry_Point_Script SHALL return the combined results from Phase 2 and Phase 3
8. THE Entry_Point_Script SHALL provide a demo mode that runs a preset tyre pressure requirement through the full pipeline
9. THE Entry_Point_Script SHALL provide an interactive mode that continuously accepts requirements for full pipeline execution
10. WHEN run without arguments, THE Entry_Point_Script SHALL execute demo mode

### Requirement 18: Subprocess Timeout Handling

**User Story:** As a build system, I want to enforce timeouts on compilation and analysis processes, so that the system doesn't hang on infinite loops or deadlocks.

#### Acceptance Criteria

1. WHEN executing docker run commands, THE DockerBuilder SHALL set a timeout of 60 seconds
2. WHEN executing g++ commands in fallback mode, THE DockerBuilder SHALL set a timeout of 60 seconds
3. WHEN executing cppcheck commands, THE StaticAnalyzer SHALL set a timeout of 60 seconds
4. IF a subprocess exceeds its timeout, THE system SHALL terminate the process
5. IF a subprocess times out, THE system SHALL return an error indicating timeout exceeded
6. THE timeout value SHALL be configurable through a parameter with default value 60

### Requirement 19: Subprocess Error Handling

**User Story:** As a robust build system, I want to handle subprocess failures gracefully, so that the system provides clear error messages and continues operation.

#### Acceptance Criteria

1. WHEN executing subprocess commands, THE system SHALL wrap calls in try-except blocks
2. IF a subprocess raises CalledProcessError, THE system SHALL catch the exception and extract the error message
3. IF a subprocess raises TimeoutExpired, THE system SHALL catch the exception and return a timeout error message
4. IF a subprocess raises FileNotFoundError, THE system SHALL catch the exception and return a message indicating the command is not available
5. THE system SHALL include the original subprocess error details in all error messages for debugging

### Requirement 20: Max Attempts Configuration

**User Story:** As a system administrator, I want to configure the maximum number of healing attempts, so that I can balance between code quality and execution time.

#### Acceptance Criteria

1. THE SelfHealingBuildLoop SHALL accept a max_attempts parameter in its constructor
2. THE max_attempts parameter SHALL default to 3 if not provided
3. WHEN the number of attempts reaches max_attempts, THE SelfHealingBuildLoop SHALL terminate the loop
4. WHEN max_attempts is reached without certification, THE SelfHealingBuildLoop SHALL set final_status to "MAX_ATTEMPTS_REACHED"
5. THE max_attempts value SHALL be included in the build_report.json file

### Requirement 21: CMake Template Substitution

**User Story:** As a build system, I want to substitute service names into CMake templates, so that I can generate service-specific build configurations.

#### Acceptance Criteria

1. WHEN preparing compilation, THE DockerBuilder SHALL read the CMakeLists.txt.template file
2. THE DockerBuilder SHALL replace all occurrences of {{SERVICE_NAME}} with the actual service name
3. THE DockerBuilder SHALL write the substituted CMakeLists.txt to the service directory
4. THE substituted CMakeLists.txt SHALL be used for cmake configuration
5. IF the template file is missing, THE DockerBuilder SHALL raise a FileNotFoundError

### Requirement 22: Build Report Persistence

**User Story:** As a traceability system, I want build reports saved with each service, so that I can maintain a history of build outcomes and debugging information.

#### Acceptance Criteria

1. FOR EACH service build, THE SelfHealingBuildLoop SHALL create a build_report.json file in the service output directory
2. THE build_report.json file SHALL persist even if the build fails
3. THE build_report.json file SHALL be overwritten if the same service is built multiple times
4. THE build_report.json file SHALL use UTF-8 encoding
5. THE build_report.json file SHALL be formatted with 2-space indentation

### Requirement 23: Healing Prompt Construction

**User Story:** As a code healing system, I want to construct effective prompts for the LLM, so that the healer understands the issues and generates correct fixes.

#### Acceptance Criteria

1. WHEN constructing healing prompts, THE CodeHealer SHALL include the original code in the prompt
2. WHEN build errors are present, THE CodeHealer SHALL include all error messages in the prompt
3. WHEN MISRA violations are present, THE CodeHealer SHALL include all violation details in the prompt
4. THE prompt SHALL instruct the LLM to act as a C++ expert fixing automotive embedded code
5. THE prompt SHALL instruct the LLM to fix ALL listed issues
6. THE prompt SHALL instruct the LLM to preserve the original logic and functionality
7. THE prompt SHALL instruct the LLM to return ONLY raw C++ code without explanations or markdown
8. THE prompt SHALL include the attempt number for context

### Requirement 24: Docker Availability Detection

**User Story:** As a build system, I want to detect Docker availability at runtime, so that I can automatically fall back to host compilation when needed.

#### Acceptance Criteria

1. WHEN initializing DockerBuilder, THE DockerBuilder SHALL check if Docker is available by executing "docker --version"
2. IF the docker command is not found, THE DockerBuilder SHALL set a docker_available flag to False
3. IF the docker command succeeds, THE DockerBuilder SHALL set docker_available flag to True
4. WHEN docker_available is False, THE DockerBuilder SHALL use host g++ compiler for all compilation operations
5. WHEN docker_available is True, THE DockerBuilder SHALL use Docker containers for compilation

### Requirement 25: Final Code Persistence

**User Story:** As a code management system, I want to save the final code version separately, so that I can easily identify the last attempted code regardless of certification status.

#### Acceptance Criteria

1. WHEN the build loop completes, THE SelfHealingBuildLoop SHALL save the final code to [service_name]_final.cpp
2. THE final code file SHALL be saved in the service output directory
3. THE final code file SHALL contain the code from the last attempt
4. THE final code file SHALL be saved regardless of whether certification was achieved
5. IF certification is achieved, THE final code SHALL also be copied to the certified/ directory

### Requirement 26: Static Analysis Violation Structure

**User Story:** As an error reporting system, I want structured violation data from static analysis, so that I can provide clear feedback to the code healer and users.

#### Acceptance Criteria

1. FOR EACH violation detected by StaticAnalyzer, THE violation dictionary SHALL include a type field indicating the violation category
2. FOR EACH violation, THE violation dictionary SHALL include a line_number field indicating where the violation occurs
3. FOR EACH violation, THE violation dictionary SHALL include a message field describing the violation
4. FOR EACH violation, THE violation dictionary SHALL include a severity field with values "error" or "warning"
5. THE violations list SHALL be sorted by line_number for readability

### Requirement 27: Healing Effectiveness Tracking

**User Story:** As a metrics system, I want to track which errors were addressed in each healing attempt, so that I can measure healing effectiveness and identify persistent issues.

#### Acceptance Criteria

1. WHEN CodeHealer.heal returns, THE return dictionary SHALL include an errors_addressed field
2. THE errors_addressed field SHALL be a list of strings describing which issues were targeted for fixing
3. FOR EACH build error, THE errors_addressed list SHALL include a summary of the error
4. FOR EACH MISRA violation, THE errors_addressed list SHALL include the violation type
5. THE errors_addressed list SHALL be included in the build_report.json for each attempt

### Requirement 28: Compilation Output Preservation

**User Story:** As a debugging system, I want to preserve compilation stdout and stderr, so that I can diagnose build issues and understand compiler behavior.

#### Acceptance Criteria

1. WHEN compilation completes, THE DockerBuilder SHALL capture both stdout and stderr
2. THE DockerBuilder SHALL return stdout as a string in the compilation result
3. THE DockerBuilder SHALL return stderr as a string in the compilation result
4. THE compilation stdout and stderr SHALL be included in the build_report.json for each attempt
5. THE compilation output SHALL preserve original formatting including newlines and indentation

### Requirement 29: MISRA Violation Line Number Detection

**User Story:** As a code analysis system, I want to identify the line numbers where MISRA violations occur, so that I can provide precise feedback for fixing.

#### Acceptance Criteria

1. WHEN detecting malloc/free usage, THE StaticAnalyzer SHALL identify the line number where the function call appears
2. WHEN detecting goto statements, THE StaticAnalyzer SHALL identify the line number of the goto keyword
3. WHEN detecting printf/scanf usage, THE StaticAnalyzer SHALL identify the line number where the function call appears
4. WHEN detecting multiple return statements, THE StaticAnalyzer SHALL identify all line numbers with return statements
5. WHEN detecting NULL usage, THE StaticAnalyzer SHALL identify the line number where NULL appears
6. THE line numbers SHALL be 1-indexed to match standard editor line numbering

### Requirement 30: Build Loop State Management

**User Story:** As a build orchestrator, I want to maintain state across build attempts, so that I can track progress and make informed decisions about continuing or terminating the loop.

#### Acceptance Criteria

1. THE SelfHealingBuildLoop SHALL maintain a current_attempt counter starting at 1
2. THE SelfHealingBuildLoop SHALL maintain a current_code variable containing the code being processed
3. THE SelfHealingBuildLoop SHALL maintain an attempts_history list containing details of all attempts
4. WHEN an attempt completes, THE SelfHealingBuildLoop SHALL increment current_attempt
5. WHEN healing produces new code, THE SelfHealingBuildLoop SHALL update current_code
6. WHEN an attempt completes, THE SelfHealingBuildLoop SHALL append attempt details to attempts_history
7. THE attempts_history SHALL be used to generate the build_report.json

