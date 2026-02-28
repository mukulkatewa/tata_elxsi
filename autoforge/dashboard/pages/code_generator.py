"""
AutoForge Code Generator Page

Interactive UI for entering requirements and running the full GenAI pipeline:
Requirement Refinement → Code Generation → Build → MISRA Check → Tests → OTA
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

import streamlit as st

# Ensure project root is on sys.path so autoforge imports work
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load .env file for OPENAI_API_KEY
from dotenv import load_dotenv
load_dotenv(Path(PROJECT_ROOT) / ".env")


def render_code_generator():
    """Render the code generator page."""
    
    st.title("🤖 AutoForge — Code Generator")
    st.markdown("Enter a requirement and AutoForge will generate compliant automotive service code.")
    
    # ---- Input Section ----
    st.markdown("---")
    st.markdown("### 📝 Enter Your Requirement")
    
    # Example requirements for quick selection
    examples = {
        "Custom (type your own)": "",
        "Battery Health Monitor": "Create a battery health monitoring service that tracks state of charge, predicts remaining EV range, and generates alerts when SOC drops below critical thresholds",
        "Tyre Pressure Monitor": "Create a tyre pressure monitoring service that reads pressure from all four tyres, detects slow leaks by analyzing pressure trends, and alerts the driver",
        "Motor Temperature Guard": "Create a motor temperature monitoring service that tracks motor and coolant temperatures, predicts overheating events, and triggers cooling system alerts",
        "Speed Limiter Service": "Create a vehicle speed limiter service that monitors current speed, enforces configurable speed limits, and logs speed violations",
        "Driving Efficiency Analyzer": "Create a driving efficiency service that analyzes throttle and brake patterns, calculates energy consumption rates, and provides driving tips for better range",
    }
    
    selected_example = st.selectbox(
        "Quick Start — Pick an example or write your own:",
        options=list(examples.keys()),
        key="example_selector"
    )
    
    default_text = examples[selected_example]
    
    requirement = st.text_area(
        "Requirement (describe the service you want to generate):",
        value=default_text,
        height=120,
        placeholder="e.g., Create a battery health monitoring service that tracks SOC and predicts range...",
        key="requirement_input"
    )
    
    # Language selection
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        language = st.selectbox(
            "Target Language",
            ["cpp", "rust", "kotlin"],
            format_func=lambda x: {"cpp": "🔧 C++", "rust": "🦀 Rust", "kotlin": "📱 Kotlin"}[x],
            key="language_selector"
        )
    with col2:
        st.markdown("")  # spacer
        st.caption(f"Code will be generated in **{language.upper()}**")
    with col3:
        st.markdown("")
    
    # Generate button
    st.markdown("---")
    
    generate_clicked = st.button(
        "🚀 Generate Service Code",
        type="primary",
        disabled=not requirement.strip(),
        use_container_width=True
    )
    
    # ---- Generation Process ----
    if generate_clicked and requirement.strip():
        _run_pipeline(requirement.strip(), language)
    
    # ---- Show Previously Generated Services ----
    st.markdown("---")
    st.markdown("### 📂 Generated Services")
    _show_generated_services()


def _run_pipeline(requirement: str, language: str):
    """Run the full AutoForge pipeline and display results in real-time."""
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        st.error("❌ **API Key not set!** Please add your GEMINI_API_KEY or OPENAI_API_KEY to the `.env` file.")
        return
    
    # Initialize progress
    progress_bar = st.progress(0, text="Starting pipeline...")
    status_container = st.container()
    
    try:
        # Phase 0: Requirement Refinement
        progress_bar.progress(5, text="📋 Phase 0: Refining requirement...")
        with status_container:
            with st.expander("📋 Phase 0: Requirement Refinement", expanded=True):
                with st.spinner("Analyzing and refining your requirement..."):
                    from autoforge.rag.retriever import RAGRetriever
                    from autoforge.agents.requirement_agent import RequirementAgent
                    from autoforge.config import load_config, get_llm_client
                    
                    config = load_config()
                    llm_client = get_llm_client()
                    rag_retriever = RAGRetriever(str(config['chroma_db_path']))
                    
                    req_agent = RequirementAgent(
                        llm_client=llm_client,
                        rag_retriever=rag_retriever,
                        model_name=config['model_name'],
                        max_tokens=config['max_tokens']
                    )
                    
                    spec = req_agent.refine(requirement)
                    refined_text = req_agent.format_spec(spec)
                    st.text(refined_text)
                    st.success("✅ Requirement refined successfully")
        
        refined_requirement = spec.get('refined_requirement', requirement)
        
        # Phase 1: Code Generation
        progress_bar.progress(25, text="📝 Phase 1: Generating code...")
        with status_container:
            with st.expander("📝 Phase 1: Code Generation", expanded=True):
                with st.spinner(f"Generating {language.upper()} service code..."):
                    from autoforge.agents.dev_agent import DevAgent
                    
                    dev_agent = DevAgent(
                        llm_client=llm_client,
                        rag_retriever=rag_retriever,
                        prompt_template_path=Path('prompts/dev_agent_prompt.txt'),
                        model_name=config['model_name'],
                        max_tokens=config['max_tokens']
                    )
                    
                    dev_output = dev_agent.generate(refined_requirement, language=language)
                    service_name = dev_output['service_name']
                    
                    st.info(f"Service name: **{service_name}**")
                    st.code(dev_output['full_code'], language=language)
                    st.success(f"✅ Generated {len(dev_output['full_code'].split(chr(10)))} lines of {language.upper()} code")
        
        # Save code
        outputs_dir = Path(config.get('outputs_dir', 'autoforge/outputs'))
        output_dir = outputs_dir / service_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        ext = {"cpp": ".cpp", "rust": ".rs", "kotlin": ".kt"}.get(language, ".cpp")
        code_path = output_dir / f"{service_name}{ext}"
        code_path.write_text(dev_output['full_code'], encoding='utf-8')
        
        # Save refined spec
        spec_path = output_dir / 'refined_spec.txt'
        spec_path.write_text(refined_text, encoding='utf-8')
        
        # Phase 2: Build Pipeline (C++ only)
        build_result = None
        if language == "cpp":
            progress_bar.progress(45, text="🔨 Phase 2: Compiling code...")
            with status_container:
                with st.expander("🔨 Phase 2: Self-Healing Build", expanded=True):
                    with st.spinner("Compiling and auto-fixing..."):
                        from autoforge.build_pipeline import BuildPipeline
                        
                        build_pipeline = BuildPipeline(
                            llm_client=llm_client,
                            model_name=config['model_name'],
                            max_tokens=config['max_tokens']
                        )
                        
                        build_result = build_pipeline.build(
                            code=dev_output['full_code'],
                            service_name=service_name
                        )
                        
                        if build_result.success:
                            st.success(f"✅ Build PASSED (iterations: {build_result.total_iterations})")
                            if build_result.total_iterations > 1:
                                dev_output['full_code'] = build_result.final_code
                                code_path.write_text(build_result.final_code, encoding='utf-8')
                                st.info("Code was auto-fixed during compilation!")
                        else:
                            st.warning(f"⚠️ Build failed after {build_result.total_iterations} attempts")
                        
                        # Show build log
                        for it in build_result.iterations:
                            with st.expander(f"Iteration {it.iteration} — {'✅' if it.success else '❌'}"):
                                st.code(it.compiler_output or "(clean)", language="text")
                        
                        # Save build log
                        log_lines = []
                        for it in build_result.iterations:
                            log_lines.append(f"=== Iteration {it.iteration} === {'PASS' if it.success else 'FAIL'}")
                            log_lines.append(it.compiler_output or "(clean)")
                        (output_dir / "build_log.txt").write_text('\n'.join(log_lines), encoding='utf-8')
        
        # Phase 3: Static Analysis (C++ only)
        analysis_result = None
        if language == "cpp":
            progress_bar.progress(60, text="📋 Phase 3: MISRA static analysis...")
            with status_container:
                with st.expander("📋 Phase 3: Static Analysis (MISRA Check)", expanded=True):
                    with st.spinner("Running cppcheck..."):
                        from autoforge.static_analyzer import StaticAnalyzer
                        
                        analyzer = StaticAnalyzer()
                        analysis_result = analyzer.analyze(
                            code=dev_output['full_code'],
                            service_name=service_name
                        )
                        
                        report = analyzer.format_report(analysis_result)
                        st.code(report, language="text")
                        
                        if analysis_result.success:
                            st.success("✅ Static analysis PASSED — no errors")
                        else:
                            st.warning(f"⚠️ Found {analysis_result.total_violations} violation(s)")
                        
                        (output_dir / "static_analysis_report.txt").write_text(report, encoding='utf-8')
        
        # Phase 4: Test Generation
        progress_bar.progress(75, text="🧪 Phase 4: Generating tests...")
        qa_output = None
        with status_container:
            with st.expander("🧪 Phase 4: Test Generation", expanded=True):
                with st.spinner("Generating test suite..."):
                    try:
                        from autoforge.agents.qa_agent import QAAgent
                        
                        qa_agent = QAAgent(
                            llm_client=llm_client,
                            prompt_template_path=Path('prompts/qa_agent_prompt.txt'),
                            model_name=config['model_name'],
                            max_tokens=config['max_tokens']
                        )
                        
                        qa_output = qa_agent.generate_tests(
                            requirement=requirement,
                            generated_code=dev_output['full_code'],
                            service_name=service_name
                        )
                        
                        test_path = output_dir / qa_output['test_file_name']
                        test_path.write_text(qa_output['test_code'], encoding='utf-8')
                        
                        st.code(qa_output['test_code'], language=language)
                        st.success("✅ Test suite generated successfully")
                    except Exception as e:
                        st.warning(f"⚠️ Test generation failed: {e}")
        
        # Phase 5: OTA Registration
        progress_bar.progress(90, text="📡 Phase 5: Registering service...")
        with status_container:
            with st.expander("📡 Phase 5: OTA Service Registration", expanded=True):
                from autoforge.ota_registry import OTAServiceRegistry
                
                if "ota_registry" not in st.session_state:
                    st.session_state.ota_registry = OTAServiceRegistry()
                
                registry = st.session_state.ota_registry
                entry = registry.register_service(
                    name=service_name,
                    description=requirement[:200],
                    language=language,
                    code_path=str(code_path),
                    test_path=str(test_path) if qa_output else None,
                    signals_used=dev_output.get('vss_signals_used', [])
                )
                
                st.success(f"✅ Registered: **{entry.name}** v{entry.version}")
        
        # Save metadata
        end_time = datetime.now()
        metadata = {
            'requirement': requirement,
            'refined_requirement': refined_requirement,
            'service_name': service_name,
            'language': language,
            'vss_signals_used': dev_output.get('vss_signals_used', []),
            'timestamp': datetime.now().isoformat(),
            'model_used': config['model_name'],
            'kpi_metrics': {
                'generation_time_seconds': 0,  # Approximate
                'code_lines': len(dev_output['full_code'].split('\n')),
                'build_success': build_result.success if build_result else None,
                'build_iterations': build_result.total_iterations if build_result else 0,
                'static_analysis_pass': analysis_result.success if analysis_result else None,
                'static_analysis_violations': analysis_result.total_violations if analysis_result else 0,
                'static_analysis_errors': analysis_result.errors if analysis_result else 0,
                'test_generated': qa_output is not None,
            }
        }
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Final status
        progress_bar.progress(100, text="✅ Pipeline complete!")
        
        st.markdown("---")
        st.markdown("### 🎉 Generation Complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Code Lines", len(dev_output['full_code'].split('\n')))
        with col2:
            if build_result:
                st.metric("🔨 Build", "✅ PASS" if build_result.success else "❌ FAIL")
            else:
                st.metric("🔨 Build", "N/A")
        with col3:
            if analysis_result:
                st.metric("📋 MISRA Violations", analysis_result.total_violations)
            else:
                st.metric("📋 MISRA", "N/A")
        
        st.info(f"📁 Files saved to: `{output_dir}`")
        
    except Exception as e:
        progress_bar.progress(0, text="❌ Pipeline failed")
        st.error(f"❌ Pipeline error: {e}")
        st.exception(e)


def _show_generated_services():
    """Show previously generated services."""
    outputs_path = Path("autoforge/outputs")
    
    if not outputs_path.exists():
        st.info("No services generated yet. Enter a requirement above and click Generate!")
        return
    
    services = [d for d in outputs_path.iterdir() if d.is_dir()]
    
    if not services:
        st.info("No services generated yet. Enter a requirement above and click Generate!")
        return
    
    for svc_dir in sorted(services, key=lambda x: x.stat().st_mtime, reverse=True):
        meta_path = svc_dir / "metadata.json"
        
        with st.expander(f"📦 {svc_dir.name}", expanded=False):
            # Show metadata if available
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Language: {meta.get('language', 'cpp').upper()}")
                    with col2:
                        st.caption(f"Model: {meta.get('model_used', 'N/A')}")
                    with col3:
                        st.caption(f"Generated: {meta.get('timestamp', 'N/A')[:19]}")
                    
                    st.markdown(f"**Requirement:** {meta.get('requirement', 'N/A')[:200]}")
                except Exception:
                    pass
            
            # List files
            files = [f for f in svc_dir.iterdir() if f.is_file()]
            if files:
                selected = st.selectbox(
                    "View file",
                    [f.name for f in files],
                    key=f"file_select_{svc_dir.name}"
                )
                if selected:
                    filepath = svc_dir / selected
                    content = filepath.read_text(encoding='utf-8')
                    ext = filepath.suffix
                    lang_map = {".cpp": "cpp", ".h": "cpp", ".rs": "rust", 
                               ".kt": "kotlin", ".json": "json", ".txt": "text"}
                    st.code(content, language=lang_map.get(ext, "text"))


# ============================================================
# Streamlit page auto-discovery calls this file directly.
# The function below must be called at the top level.
# ============================================================
render_code_generator()
