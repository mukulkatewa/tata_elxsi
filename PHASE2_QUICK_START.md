# AutoForge Phase 2: Quick Start Guide

## Prerequisites

1. **Phase 1 Setup Complete**
   - RAG knowledge base initialized at `autoforge/data/chroma_db`
   - If not done, run Phase 1 setup first

2. **OpenAI API Key**
   - Obtain an API key from [OpenAI Platform](https://platform.openai.com/)
   - Create a `.env` file in the project root

3. **Python Environment**
   - Python 3.8 or higher
   - Virtual environment activated

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- All Phase 1 dependencies (chromadb, sentence-transformers, etc.)

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults shown)
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
MAX_TOKENS=2048
CHROMA_DB_PATH=autoforge/data/chroma_db
OUTPUTS_DIR=autoforge/outputs
```

### 3. Verify Setup

Run the verification script:
```bash
python verify_phase2.py
```

Expected output:
```
======================================================================
AutoForge Phase 2 Verification
======================================================================

Verifying file structure...
✅ autoforge/config.py
✅ autoforge/agents/__init__.py
✅ autoforge/agents/dev_agent.py
✅ autoforge/agents/qa_agent.py
✅ autoforge/orchestrator.py
✅ prompts/dev_agent_prompt.txt
✅ prompts/qa_agent_prompt.txt
✅ run_phase2.py
✅ requirements.txt

Verifying imports...
✅ Config module imported successfully
✅ DevAgent imported successfully
✅ QAAgent imported successfully
✅ Orchestrator imported successfully

Verifying prompt templates...
✅ Dev Agent prompt has all required placeholders
✅ QA Agent prompt has all required placeholders

Verifying configuration...
✅ Configuration loaded successfully

======================================================================
Verification Summary
======================================================================
✅ PASS: File Structure
✅ PASS: Module Imports
✅ PASS: Prompt Templates
✅ PASS: Configuration

🎉 All verification checks passed!
```

## Usage

### Demo Mode (Recommended for First Run)

Run with preset requirements to see the system in action:

```bash
python run_phase2.py --demo
```

This will generate code for 2 preset requirements:
1. **Tyre Pressure Monitoring Service** - Alerts when pressure drops below 28 PSI
2. **Battery State of Charge Service** - Monitors EV range and triggers low battery warnings

**Output Location:** `autoforge/outputs/[service_name]/`

### Interactive Mode

For custom requirements:

```bash
python run_phase2.py
```

You'll see:
```
======================================================================
🚀 AutoForge Phase 2: Multi-Agent Code Generation System
======================================================================

Welcome to AutoForge interactive mode!
Enter your requirements to generate automotive C++ services.
Type 'quit' or 'exit' to terminate.

📝 Enter requirement: 
```

**Example Requirements:**
- "Create a speed limit warning service that alerts when vehicle exceeds posted speed limit"
- "Create an adaptive cruise control service that maintains safe following distance"
- "Create a lane departure warning service that detects lane boundary crossings"

### Understanding the Output

For each requirement, the system generates:

```
autoforge/outputs/[service_name]/
├── [service_name].cpp           # C++ service implementation
├── test_[service_name].cpp      # Test suite with mock data
└── metadata.json                # Generation metadata
```

**Example Output:**
```
======================================================================
✅ Generation Complete: tyre_pressure_monitoring
======================================================================
📄 Service Code: autoforge/outputs/tyre_pressure_monitoring/tyre_pressure_monitoring.cpp
🧪 Test Code: autoforge/outputs/tyre_pressure_monitoring/test_tyre_pressure_monitoring.cpp
📋 Metadata: autoforge/outputs/tyre_pressure_monitoring/metadata.json
======================================================================
```

## What Gets Generated

### 1. Service Code (.cpp)
- MISRA-compliant C++ implementation
- VSS signal integration
- Signal validation against min/max ranges
- Alert generation logic
- Comprehensive file headers

### 2. Test Code (test_*.cpp)
- MockDataProvider class
- Test cases for:
  - Normal operating conditions
  - Boundary values
  - Out-of-range values
  - Missing signals
- Assert-based validation
- Pass/Fail reporting

### 3. Metadata (metadata.json)
```json
{
  "requirement": "Original requirement text",
  "service_name": "derived_service_name",
  "vss_signals_used": [
    "Vehicle.Signal.Path.One",
    "Vehicle.Signal.Path.Two"
  ],
  "timestamp": "2024-01-15T10:30:45.123456",
  "model_used": "gpt-4o-mini"
}
```

## Workflow

```
User Requirement
      ↓
Dev Agent (🤖)
  - Retrieves automotive context from RAG
  - Generates MISRA-compliant C++ service
  - Extracts VSS signals used
      ↓
QA Agent (🧪)
  - Generates comprehensive test suite
  - Creates mock data providers
  - Validates service behavior
      ↓
Orchestrator
  - Saves service code
  - Saves test code
  - Persists metadata
  - Prints summary
```

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable is not set"
**Solution:** Create `.env` file with your OpenAI API key

### Error: "RAG database not initialized"
**Solution:** Run Phase 1 setup to create the ChromaDB knowledge base

### Error: "OpenAI rate limit exceeded"
**Solution:** Wait a few moments and try again, or upgrade your OpenAI plan

### Error: "QA Agent failed"
**Don't worry!** The system uses graceful degradation:
- Service code is still saved
- Metadata is still saved
- You can manually create tests or retry later

### No Output Visible
**Solution:** Check the `autoforge/outputs/` directory directly

## Tips for Best Results

### Writing Good Requirements

**Good:**
- "Create a tyre pressure monitoring service that alerts when pressure drops below 28 PSI on any wheel"
- "Create a battery state of charge service that monitors EV range and triggers low battery warnings below 20%"

**Too Vague:**
- "Create a monitoring service"
- "Make something for cars"

**Too Complex:**
- "Create a comprehensive vehicle management system with 15 different features including..."

### Optimal Requirement Format
```
Create a [service_name] service that [specific_behavior] when [condition]
```

### VSS Signal Usage
The system automatically:
- Retrieves relevant VSS signals from the knowledge base
- Validates signal ranges
- Extracts signal usage for traceability

You don't need to specify VSS signals in your requirement!

## Advanced Configuration

### Using Different Models

Edit `.env`:
```env
MODEL_NAME=gpt-4  # More capable but slower/expensive
# or
MODEL_NAME=gpt-3.5-turbo  # Faster but less capable
```

### Adjusting Token Limits

Edit `.env`:
```env
MAX_TOKENS=4096  # For longer/more complex code
```

### Custom Output Directory

Edit `.env`:
```env
OUTPUTS_DIR=my_custom_outputs
```

## Next Steps

1. **Try Demo Mode** - See the system in action
2. **Experiment with Requirements** - Try different automotive scenarios
3. **Review Generated Code** - Understand the output structure
4. **Customize Prompts** - Edit `prompts/*.txt` for different code styles
5. **Integrate with Build System** - Compile and test generated code

## Support

For issues or questions:
1. Check this guide
2. Review `PHASE2_IMPLEMENTATION.md` for technical details
3. Verify setup with `python verify_phase2.py`
4. Check the `.env` file configuration

## Example Session

```bash
$ python run_phase2.py --demo

======================================================================
🎬 AutoForge Demo Mode
======================================================================

Executing preset requirements to demonstrate system capabilities...

======================================================================
Demo 1/2: Tyre Pressure Monitoring
======================================================================
🤖 Dev Agent generating tyre_pressure_monitoring...
🧪 QA Agent generating tests for tyre_pressure_monitoring...

======================================================================
✅ Generation Complete: tyre_pressure_monitoring
======================================================================
📄 Service Code: autoforge/outputs/tyre_pressure_monitoring/tyre_pressure_monitoring.cpp
🧪 Test Code: autoforge/outputs/tyre_pressure_monitoring/test_tyre_pressure_monitoring.cpp
📋 Metadata: autoforge/outputs/tyre_pressure_monitoring/metadata.json
======================================================================

======================================================================
Demo 2/2: Battery State of Charge
======================================================================
🤖 Dev Agent generating battery_state_charge...
🧪 QA Agent generating tests for battery_state_charge...

======================================================================
✅ Generation Complete: battery_state_charge
======================================================================
📄 Service Code: autoforge/outputs/battery_state_charge/battery_state_charge.cpp
🧪 Test Code: autoforge/outputs/battery_state_charge/test_battery_state_charge.cpp
📋 Metadata: autoforge/outputs/battery_state_charge/metadata.json
======================================================================

======================================================================
✅ Demo Complete!
======================================================================

Check the 'autoforge/outputs/' directory for generated code.
```

Happy coding! 🚀
