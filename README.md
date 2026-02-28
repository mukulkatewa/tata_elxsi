# 🚗 AutoForge — The Compliant GenAI Pipeline for SDV

**A multi-agent, RAG-powered code generation system for automotive Software Defined Vehicle (SDV) services — with compliance guardrails, self-healing builds, and predictive diagnostics.**

Built for the Tata Elxsi Teliport Hackathon.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent Code Generation** | DevAgent generates MISRA-compliant service code from natural language requirements |
| 📋 **Requirement Refinement** | RequirementAgent refines high-level requirements into structured technical specifications |
| 🔨 **Self-Healing Build Pipeline** | Compile → Error → LLM-Fix → Retry loop (up to 3 iterations) |
| 📋 **MISRA Static Analysis** | cppcheck-based static analysis with MISRA-C++ compliance checking |
| 🧪 **Automated Test Generation** | QAAgent generates comprehensive test suites for generated code |
| 📡 **OTA Service Registry** | Dynamic service registration with version management and subscription tiers |
| 🔮 **Predictive Diagnostics** | AI-powered trend analysis with time-to-threshold prediction and anomaly detection |
| 🏭 **Vehicle Variant Support** | ICE, Hybrid, and EV configurations with variant-specific signals and thresholds |
| 🌐 **Multi-Language Support** | C++ (default), Rust, and Kotlin code generation |
| 📊 **Live Dashboard** | Real-time VSS signal monitoring with gauges, charts, and alerts |
| 🧠 **RAG Knowledge Base** | Offline-first retrieval with VSS signals, MISRA rules, and ASPICE standards |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoForge Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 Phase 0         📝 Phase 1         🔨 Phase 2          │
│  Requirement   →    Code          →    Self-Healing         │
│  Refinement         Generation         Build Pipeline       │
│                                                             │
│  📋 Phase 3         🧪 Phase 4         📡 Phase 5          │
│  Static Analysis →  Test          →    OTA Service          │
│  (MISRA Check)      Generation         Registration         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  RAG Context: VSS Signals │ MISRA Rules │ ASPICE Standards  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# For Google Gemini (free tier available)
GEMINI_API_KEY=your-gemini-key-here
LLM_PROVIDER=gemini
MODEL_NAME=gemini-2.0-flash

# OR for OpenAI
# OPENAI_API_KEY=sk-your-key-here
# LLM_PROVIDER=openai
# MODEL_NAME=gpt-4o-mini
```

Get a Gemini API key for free at: https://aistudio.google.com/apikey

### 3. Ingest RAG Knowledge Base (one-time setup)

```bash
python3 autoforge/rag/ingestor.py
```

This loads 50 knowledge chunks (30 VSS signals + 13 MISRA rules + 7 ASPICE items) into ChromaDB.

### 4. Launch the Dashboard

```bash
python3 run_dashboard.py
```

Open **http://localhost:8501** in your browser. You'll see:
- **🏠 Home Page** — System overview and status
- **🤖 Code Generator** — Enter requirements, generate code with full pipeline
- **🏠 Live Dashboard** — Real-time vehicle signal monitoring

### 5. Generate Code (CLI alternative)

```bash
python3 -c "from autoforge import AutoForgeOrchestrator; AutoForgeOrchestrator().run_interactive()"
```

---

## 📝 Example Requirements

Try these in the Code Generator or CLI:

| Service | Example Prompt |
|---------|---------------|
| Battery Monitor | *"Create a battery health monitoring service that tracks state of charge, predicts remaining EV range, and alerts when SOC drops below 20%"* |
| Tyre Pressure | *"Create a tyre pressure monitoring service that reads pressure from all four tyres, detects slow leaks, and alerts the driver"* |
| Motor Temperature | *"Create a motor temperature monitoring service that tracks motor and coolant temps, predicts overheating, and triggers cooling alerts"* |
| Speed Limiter | *"Create a speed limiter service that monitors vehicle speed, enforces configurable limits, and logs violations"* |
| Cruise Control | *"Create an adaptive cruise control service that reads vehicle speed and distance to vehicle ahead, adjusts throttle and brake to maintain safe following distance"* |

---

## 📁 Project Structure

```
autoforge/
├── agents/                         # Multi-agent system
│   ├── dev_agent.py               # Code generation agent (C++/Rust/Kotlin)
│   ├── qa_agent.py                # Test generation agent
│   └── requirement_agent.py       # Requirement refinement agent
├── build_pipeline.py              # Self-healing build (compile → fix → retry)
├── static_analyzer.py             # cppcheck MISRA compliance checker
├── orchestrator.py                # 6-phase pipeline orchestrator
├── config.py                      # Configuration (Gemini + OpenAI support)
├── ota_registry.py                # OTA service registry with subscriptions
├── vehicle_variants.py            # ICE/Hybrid/EV variant configurations
├── dashboard/                      # Streamlit dashboard
│   ├── app.py                     # Main entry point (home page)
│   ├── pages/
│   │   ├── code_generator.py      # Code generation UI with pipeline
│   │   └── live_dashboard.py      # Real-time vehicle monitoring
│   ├── components/
│   │   ├── gauges.py              # Plotly gauge visualizations
│   │   ├── charts.py              # Trend chart components
│   │   └── alerts.py              # Alert rendering components
│   ├── simulation/
│   │   ├── vehicle_simulator.py   # VSS signal simulator (13 signals)
│   │   └── scenarios.py           # Fault scenario definitions
│   ├── predictive_engine.py       # Predictive diagnostics (regression + anomaly)
│   ├── data_bridge.py             # Simulator ↔ dashboard bridge
│   └── assets/                    # Images and static assets
├── rag/                            # RAG knowledge base
│   ├── ingestor.py                # Document ingestion pipeline
│   └── retriever.py               # Context retrieval interface
├── knowledge_base/                 # Source documents
│   ├── vss_signals.json           # 30 VSS signal definitions
│   ├── misra_rules.md             # MISRA-C++ rules
│   └── aspice_checklist.md        # ASPICE process requirements
└── data/
    └── chroma_db/                 # ChromaDB vector database

prompts/                            # LLM prompt templates
├── dev_agent_prompt.txt           # Code generation prompt
└── qa_agent_prompt.txt            # Test generation prompt

docker/
├── Dockerfile                     # Build environment (g++ + cppcheck)
└── CMakeLists.txt.template        # CMake template for builds

tests/                              # Unit tests
└── unit/
    ├── test_scenarios.py
    ├── test_vehicle_simulator_scenarios.py
    └── test_vehicle_simulator_tick.py
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Google Gemini (default) or OpenAI GPT |
| **RAG Database** | ChromaDB with persistent SQLite storage |
| **Embeddings** | all-MiniLM-L6-v2 (384 dimensions, CPU-only) |
| **Dashboard** | Streamlit + Plotly |
| **Build Tools** | g++ / Docker |
| **Static Analysis** | cppcheck with MISRA-C++ addon |
| **Languages** | Python 3.8+ |

---

## 🔄 Pipeline Details

### Phase 0: Requirement Refinement
The `RequirementAgent` takes a natural language requirement and produces a structured technical specification including identified VSS signals, interfaces, data flow, applicable MISRA rules, and ASPICE requirements.

### Phase 1: Code Generation
The `DevAgent` generates service code using RAG-enriched prompts. Supports C++, Rust, and Kotlin. Includes automotive-specific patterns (SOME/IP, VSS signal access, MISRA compliance).

### Phase 2: Self-Healing Build
The `BuildPipeline` compiles the generated code with `g++`. If compilation fails, it captures error messages and feeds them back to the LLM for automatic fixing. Up to 3 retry iterations.

### Phase 3: Static Analysis
The `StaticAnalyzer` runs `cppcheck --enable=all` on the generated code, focusing on MISRA-C++ compliance. Results are categorized by severity (error, warning, style, performance).

### Phase 4: Test Generation
The `QAAgent` generates comprehensive test suites covering unit tests, boundary tests, and integration tests for the generated service code.

### Phase 5: OTA Registration
The `OTAServiceRegistry` registers the generated service with version tracking, deployment status, and subscription tier management.

---

## 📊 Dashboard Features

### Live Vehicle Dashboard
- **Real-time gauges**: Speed, tyre pressure (4 wheels), battery SOC, temperature
- **Trend charts**: Rolling 60-tick windows with threshold warning lines
- **Fault injection**: Apply preset scenarios (flat tyre, battery drain, overheat, etc.)
- **Predictive diagnostics**: Linear regression + anomaly detection
- **Vehicle variants**: Switch between ICE, Hybrid, and EV configurations

### Code Generator
- **Example prompts**: Pre-built examples for common automotive services
- **Multi-language**: Generate C++, Rust, or Kotlin code
- **Live pipeline**: Watch all 6 phases execute with progress indicators
- **Code viewer**: Browse generated services, tests, and analysis reports

---

## 🏎️ Vehicle Variants

| Variant | Signals | Features |
|---------|---------|----------|
| **⚡ EV** | Battery SOC, motor temp, regen braking, charge rate | Range prediction, battery health |
| **🔋 Hybrid** | Engine + motor temps, fuel + battery levels | Dual powertrain monitoring |
| **⛽ ICE** | Engine RPM, fuel level, oil pressure, exhaust temp | Traditional drivetrain alerts |

---

## 📄 License

This project is part of the Tata Elxsi Teliport Hackathon for automotive GenAI development.
