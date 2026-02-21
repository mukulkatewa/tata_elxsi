# AutoForge Phase 3 Quick Start Guide

## Overview

Phase 3 adds a self-healing build loop to AutoForge that automatically compiles, analyzes, and fixes generated C++ code. The system uses Docker-based compilation, static analysis (cppcheck + MISRA patterns), and LLM-powered code healing to iteratively improve code until it's certified.

## Architecture

```
Phase 2: Code Generation → Phase 3: Self-Healing Build Loop
                              ↓
                         Compile (Docker/g++)
                              ↓
                         Analyze (cppcheck + MISRA)
                              ↓
                         Heal (LLM) if issues found
                              ↓
                         Certify if all checks pass
```

## Prerequisites

### Required
- Python 3.8+
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)

### Optional (for Docker mode)
- Docker installed and running
- If Docker is unavailable, system automatically falls back to host `g++` compiler

### For Fallback Mode
- g++ compiler installed
- cppcheck installed (for static analysis)

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. **Build Docker image (optional but recommended):**
```bash
docker build -t autoforge-builder:latest -f docker/Dockerfile docker/
```

If you skip this step, the system will build the image automatically on first use, or fall back to host g++ if Docker is unavailable.

## Verification

Run the verification script to ensure everything is set up correctly:

```bash
python verify_phase3.py
```

This tests:
- All modules can be imported
- DockerBuilder error parsing
- StaticAnalyzer MISRA pattern detection
- CodeHealer code extraction
- CMake template substitution
- File structure completeness

## Usage

### Demo Mode (Recommended for First Run)

Run the preset tyre pressure monitoring example:

```bash
python run_phase3.py
```

This will:
1. Generate code using Phase 2 multi-agent system
2. Compile the code in Docker (or using g++)
3. Run static analysis (cppcheck + MISRA checks)
4. Heal any issues using LLM
5. Certify the code if all checks pass

### Interactive Mode

Process multiple requirements continuously:

```bash
python run_phase3.py --interactive
```

Enter requirements at the prompt. Type `quit` to exit.

### Command-Line Mode

Process a single requirement:

```bash
python run_phase3.py "Create a BatteryMonitor service that tracks voltage and alerts on low battery"
```

## Output Structure

After running Phase 3, you'll find:

```
autoforge/outputs/
└── ServiceName/
    ├── ServiceName.cpp              # Current code
    ├── ServiceName_attempt_1.cpp    # First attempt
    ├── ServiceName_attempt_2.cpp    # Second attempt (if needed)
    ├── ServiceName_final.cpp        # Final code
    ├── build_report.json            # Detailed build report
    └── certified/                   # Only if certified
        ├── ServiceName.cpp          # Certified code
        └── CERTIFIED.txt            # Certification details
```

## Build Report

The `build_report.json` contains:

```json
{
  "service_name": "TyrePressureMonitor",
  "final_status": "CERTIFIED",
  "total_attempts": 2,
  "max_attempts": 3,
  "attempts": [
    {
      "attempt_number": 1,
      "compilation_success": false,
      "compilation_errors": ["..."],
      "static_analysis_passed": null,
      "healing_applied": true,
      "errors_addressed": ["..."]
    },
    {
      "attempt_number": 2,
      "compilation_success": true,
      "static_analysis_passed": true,
      "healing_applied": false
    }
  ],
  "certification_timestamp": "2024-01-15T10:30:45.123456",
  "certified_code_path": "outputs/certified/TyrePressureMonitor.cpp"
}
```

## MISRA Checks

Phase 3 automatically checks for these MISRA-C++ violations:

1. **malloc/free usage** - Use `new`/`delete` instead
2. **goto statements** - Forbidden in automotive code
3. **printf/scanf usage** - Unsafe for embedded systems
4. **Multiple return statements** - Single exit point required
5. **NULL usage** - Use `nullptr` in C++14

## Troubleshooting

### Docker Issues

**Problem:** Docker not available
```
⚠️  Docker not available. Falling back to host g++ compiler.
```
**Solution:** This is normal. The system will use your host g++ compiler instead.

**Problem:** Docker build fails
```
❌ Docker build failed: ...
```
**Solution:** Check Docker is running and you have permissions. Or use fallback mode.

### Compilation Issues

**Problem:** g++ not found in fallback mode
```
❌ g++ compiler not found on host system
```
**Solution:** Install g++:
- Ubuntu/Debian: `sudo apt-get install g++`
- macOS: `xcode-select --install`
- Windows: Install MinGW or WSL

### Static Analysis Issues

**Problem:** cppcheck not found
```
❌ cppcheck not found - please install cppcheck
```
**Solution:** Install cppcheck:
- Ubuntu/Debian: `sudo apt-get install cppcheck`
- macOS: `brew install cppcheck`
- Windows: Download from cppcheck.net

### LLM Healing Issues

**Problem:** OpenAI API key not set
```
❌ OpenAI API key not provided and OPENAI_API_KEY not set
```
**Solution:** Add your API key to `.env`:
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

**Problem:** API rate limit exceeded
```
❌ LLM healing failed: Rate limit exceeded
```
**Solution:** Wait a moment and try again, or upgrade your OpenAI plan.

## Configuration

### Max Attempts

Change the maximum number of healing attempts (default: 3):

```python
from autoforge.build import SelfHealingBuildLoop

build_loop = SelfHealingBuildLoop(
    builder, analyzer, healer,
    max_attempts=5  # Try up to 5 times
)
```

### Compilation Timeout

Timeouts are set to 60 seconds by default. To change:

Edit `autoforge/build/docker_builder.py` and `autoforge/build/static_analyzer.py`:
```python
timeout=120  # 2 minutes
```

## Docker Image Details

The AutoForge builder image includes:
- Ubuntu 22.04 base
- gcc, g++, cmake, make
- cppcheck for static analysis
- Python 3 for scripting

Image size: ~300MB (minimal installation)

## Performance

Typical execution times:
- Phase 2 (Code Generation): 30-60 seconds
- Phase 3 (Single Attempt): 10-20 seconds
  - Docker compilation: 5-10 seconds
  - Static analysis: 2-5 seconds
  - LLM healing: 3-10 seconds

Total pipeline (with 1-2 healing attempts): 1-2 minutes

## Next Steps

1. **Run the demo** to see the full pipeline in action
2. **Try your own requirements** in interactive mode
3. **Examine the build reports** to understand the healing process
4. **Check certified code** in the `certified/` directory
5. **Integrate with CI/CD** for automated code generation and certification

## Advanced Usage

### Programmatic API

```python
from autoforge.build import DockerBuilder, StaticAnalyzer, CodeHealer, SelfHealingBuildLoop

# Initialize components
builder = DockerBuilder()
analyzer = StaticAnalyzer()
healer = CodeHealer()
build_loop = SelfHealingBuildLoop(builder, analyzer, healer)

# Run build loop
result = build_loop.run(
    service_dir="outputs/MyService",
    service_name="MyService",
    initial_code=generated_cpp_code
)

# Check result
if result['final_status'] == 'CERTIFIED':
    print(f"Success! Code at: {result['certified_code_path']}")
else:
    print(f"Failed after {result['total_attempts']} attempts")
```

### Custom Static Analysis

Add your own checks to `StaticAnalyzer`:

```python
def _check_custom_pattern(self, code: str) -> List[Dict]:
    """Check for custom pattern."""
    violations = []
    # Your pattern detection logic
    return violations
```

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review the design document: `.kiro/specs/autoforge-self-healing-build/design.md`
3. Check the build report for detailed error information
4. Examine intermediate code versions (`_attempt_N.cpp` files)

## License

Part of the AutoForge project.
