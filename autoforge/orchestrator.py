"""
AutoForge Orchestrator — The Compliant GenAI Pipeline for SDV.

Full pipeline: Requirement Refinement → Code Generation → Self-Healing Build →
Static Analysis (MISRA) → Test Generation → OTA Registration.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from autoforge.rag.retriever import RAGRetriever
from autoforge.agents.dev_agent import DevAgent
from autoforge.agents.qa_agent import QAAgent
from autoforge.agents.requirement_agent import RequirementAgent
from autoforge.build_pipeline import BuildPipeline, BuildResult
from autoforge.static_analyzer import StaticAnalyzer
from autoforge.ota_registry import OTAServiceRegistry
from autoforge.config import get_llm_client, load_config


class AutoForgeOrchestrator:
    """Orchestrator that coordinates multi-agent code generation workflow."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with configuration.
        
        Args:
            config: Configuration dictionary (if None, loads from environment)
        """
        # Load configuration
        if config is None:
            config = load_config()
        
        self.config = config
        self.outputs_dir = config['outputs_dir']
        self.model_name = config['model_name']
        
        # Initialize LLM client
        self.llm_client = get_llm_client()
        
        # Initialize RAG retriever
        self.rag_retriever = RAGRetriever(str(config['chroma_db_path']))
        
        # Initialize agents
        dev_prompt_path = Path('prompts/dev_agent_prompt.txt')
        qa_prompt_path = Path('prompts/qa_agent_prompt.txt')
        
        self.dev_agent = DevAgent(
            llm_client=self.llm_client,
            rag_retriever=self.rag_retriever,
            prompt_template_path=dev_prompt_path,
            model_name=self.model_name,
            max_tokens=config['max_tokens']
        )
        
        self.qa_agent = QAAgent(
            llm_client=self.llm_client,
            prompt_template_path=qa_prompt_path,
            model_name=self.model_name,
            max_tokens=config['max_tokens']
        )
        
        # Initialize Build Pipeline (self-healing compile loop)
        self.build_pipeline = BuildPipeline(
            llm_client=self.llm_client,
            model_name=self.model_name,
            max_tokens=config['max_tokens'],
            use_docker=config.get('use_docker', False)
        )
        
        # Initialize Static Analyzer (cppcheck MISRA check)
        self.static_analyzer = StaticAnalyzer(
            use_docker=config.get('use_docker', False)
        )
        
        # Initialize Requirement Agent
        self.requirement_agent = RequirementAgent(
            llm_client=self.llm_client,
            rag_retriever=self.rag_retriever,
            model_name=self.model_name,
            max_tokens=config['max_tokens']
        )
        
        # Initialize OTA Service Registry
        self.ota_registry = OTAServiceRegistry()
    
    def run(self, requirement: str, language: str = "cpp") -> Dict[str, Any]:
        """Execute complete code generation workflow.
        
        Pipeline: Requirement → DevAgent → Build → Static Analysis → QAAgent → Output
        
        Args:
            requirement: Natural language requirement string
            language: Target language ("cpp", "rust", "kotlin")
            
        Returns:
            Dictionary containing all outputs and metadata
        """
        start_time = datetime.now()
        
        # Phase 0: Requirement Refinement
        print("\n" + "=" * 60)
        print("📋 Phase 0: Requirement Refinement")
        print("=" * 60)
        spec = self.requirement_agent.refine(requirement)
        refined_spec_text = self.requirement_agent.format_spec(spec)
        print(refined_spec_text)
        
        # Use refined requirement for code generation
        refined_requirement = spec.get('refined_requirement', requirement)
        
        # Phase 1: Generate service code with Dev Agent
        print("\n" + "=" * 60)
        print("📝 Phase 1: Code Generation")
        print("=" * 60)
        dev_output = self.dev_agent.generate(refined_requirement, language=language)
        service_name = dev_output['service_name']
        
        # Create output directory
        output_dir = self._create_output_directory(service_name)
        
        # Save refined spec
        spec_path = output_dir / 'refined_spec.txt'
        spec_path.write_text(refined_spec_text, encoding='utf-8')
        
        # Save initial generated code
        ext = {"cpp": ".cpp", "rust": ".rs", "kotlin": ".kt"}.get(language, ".cpp")
        code_file_path = output_dir / f"{service_name}{ext}"
        self._save_code_file(code_file_path, dev_output['full_code'])
        
        # Phase 2: Self-Healing Build Pipeline (C++ only for now)
        build_result = None
        if language == "cpp":
            print("\n" + "=" * 60)
            print("🔨 Phase 2: Self-Healing Build Pipeline")
            print("=" * 60)
            build_result = self.build_pipeline.build(
                code=dev_output['full_code'],
                service_name=service_name
            )
            
            # If build succeeded with a fix, save the fixed code
            if build_result.success and build_result.total_iterations > 1:
                self._save_code_file(code_file_path, build_result.final_code)
                dev_output['full_code'] = build_result.final_code
                print(f"   📄 Updated code file with fixed version (iteration {build_result.total_iterations})")
            
            # Save build log
            build_log = self._format_build_log(build_result)
            build_log_path = output_dir / "build_log.txt"
            build_log_path.write_text(build_log, encoding='utf-8')
        
        # Phase 3: Static Analysis (C++ only for now)
        analysis_result = None
        if language == "cpp":
            print("\n" + "=" * 60)
            print("📋 Phase 3: Static Analysis (MISRA Check)")
            print("=" * 60)
            analysis_result = self.static_analyzer.analyze(
                code=dev_output['full_code'],
                service_name=service_name
            )
            
            # Print report
            report = self.static_analyzer.format_report(analysis_result)
            print(report)
            
            # Save analysis report
            report_path = output_dir / "static_analysis_report.txt"
            report_path.write_text(report, encoding='utf-8')
        
        # Phase 4: Generate test code with QA Agent (with graceful degradation)
        print("\n" + "=" * 60)
        print("🧪 Phase 4: Test Generation")
        print("=" * 60)
        qa_output = None
        test_file_path = None
        error_message = None
        
        try:
            qa_output = self.qa_agent.generate_tests(
                requirement=requirement,
                generated_code=dev_output['full_code'],
                service_name=service_name
            )
            
            test_file_path = output_dir / qa_output['test_file_name']
            self._save_code_file(test_file_path, qa_output['test_code'])
            
        except Exception as e:
            error_message = f"QA Agent failed: {e}"
            print(f"⚠️  {error_message}")
            print("✅ Service code saved successfully despite test generation failure")
        
        # Calculate metrics
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        # Phase 5: Register in OTA Service Registry
        print("\n" + "=" * 60)
        print("📡 Phase 5: OTA Service Registration")
        print("=" * 60)
        self.ota_registry.register_service(
            name=service_name,
            description=requirement[:200],
            language=language,
            code_path=str(code_file_path),
            test_path=str(test_file_path) if test_file_path else None,
            signals_used=dev_output.get('vss_signals_used', []),
        )
        
        # Save metadata with KPI metrics
        metadata = {
            'requirement': requirement,
            'refined_requirement': refined_requirement,
            'service_name': service_name,
            'language': language,
            'vss_signals_used': dev_output['vss_signals_used'],
            'timestamp': datetime.now().isoformat(),
            'model_used': self.model_name,
            'kpi_metrics': {
                'generation_time_seconds': round(generation_time, 2),
                'code_lines': len(dev_output['full_code'].split('\n')),
                'build_success': build_result.success if build_result else None,
                'build_iterations': build_result.total_iterations if build_result else 0,
                'static_analysis_pass': analysis_result.success if analysis_result else None,
                'static_analysis_violations': analysis_result.total_violations if analysis_result else 0,
                'static_analysis_errors': analysis_result.errors if analysis_result else 0,
                'test_generated': qa_output is not None,
            }
        }
        metadata_file_path = self._save_metadata(output_dir, metadata)
        
        # Print summary
        self._print_summary(service_name, code_file_path, test_file_path, 
                           metadata_file_path, build_result, analysis_result,
                           generation_time)
        
        return {
            'service_name': service_name,
            'language': language,
            'code_file_path': code_file_path,
            'test_file_path': test_file_path,
            'metadata_file_path': metadata_file_path,
            'dev_agent_output': dev_output,
            'qa_agent_output': qa_output,
            'build_result': build_result,
            'analysis_result': analysis_result,
            'error': error_message,
            'kpi_metrics': metadata['kpi_metrics']
        }
    
    def run_interactive(self) -> None:
        """Run interactive mode with continuous requirement input.
        
        Displays welcome message and continuously prompts for requirements
        until user enters 'quit' or 'exit'.
        """
        print("\n" + "=" * 70)
        print("🚀 AutoForge: Compliant GenAI Pipeline for SDV")
        print("=" * 70)
        print("\nWelcome to AutoForge interactive mode!")
        print("Enter your requirements to generate automotive services.")
        print("Supported languages: C++ (default), Rust, Kotlin")
        print("Type 'quit' or 'exit' to terminate.\n")
        
        while True:
            try:
                # Prompt for requirement
                requirement = input("\n📝 Enter requirement: ").strip()
                
                # Check for exit commands
                if requirement.lower() in ['quit', 'exit']:
                    print("\n👋 Exiting AutoForge. Goodbye!")
                    break
                
                # Skip empty inputs
                if not requirement:
                    print("⚠️  Please enter a valid requirement.")
                    continue
                
                # Ask for language
                lang_input = input("🔤 Language [cpp/rust/kotlin] (default: cpp): ").strip().lower()
                language = lang_input if lang_input in ['cpp', 'rust', 'kotlin'] else 'cpp'
                
                # Execute workflow
                print()
                self.run(requirement, language=language)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting AutoForge.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different requirement.\n")
    
    def _create_output_directory(self, service_name: str) -> Path:
        """Create output directory for service."""
        output_dir = self.outputs_dir / service_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _save_code_file(self, file_path: Path, content: str) -> None:
        """Save code file with UTF-8 encoding."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to save file {file_path}: {e}")
    
    def _save_metadata(self, output_dir: Path, metadata: Dict[str, Any]) -> Path:
        """Save metadata JSON with indentation for readability."""
        metadata_path = output_dir / 'metadata.json'
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save metadata {metadata_path}: {e}")
        return metadata_path
    
    def _format_build_log(self, build_result: BuildResult) -> str:
        """Format build result as a text log."""
        lines = [
            "=" * 60,
            "AutoForge Self-Healing Build Log",
            "=" * 60,
            f"Result: {'PASS' if build_result.success else 'FAIL'}",
            f"Total Iterations: {build_result.total_iterations}",
            ""
        ]
        
        for iteration in build_result.iterations:
            lines.extend([
                f"--- Iteration {iteration.iteration} ---",
                f"Status: {'✅ PASS' if iteration.success else '❌ FAIL'}",
                f"Error Count: {iteration.error_count}",
                f"Compiler Output:",
                iteration.compiler_output if iteration.compiler_output else "(clean)",
                ""
            ])
        
        lines.append("=" * 60)
        return '\n'.join(lines)
    
    def _print_summary(self, service_name: str, code_path: Path, 
                      test_path: Optional[Path], metadata_path: Path,
                      build_result: Optional[BuildResult] = None,
                      analysis_result=None,
                      generation_time: float = 0) -> None:
        """Print generation summary with file paths and KPIs."""
        print("\n" + "=" * 70)
        print(f"✅ Generation Complete: {service_name}")
        print("=" * 70)
        print(f"📄 Service Code:      {code_path}")
        if test_path:
            print(f"🧪 Test Code:         {test_path}")
        print(f"📋 Metadata:          {metadata_path}")
        
        # KPI Summary
        print("\n📊 KPI Metrics:")
        print(f"   ⏱  Generation Time:    {generation_time:.1f}s")
        if build_result:
            status = "✅ PASS" if build_result.success else "❌ FAIL"
            print(f"   🔨 Build Status:       {status} (iterations: {build_result.total_iterations})")
        if analysis_result:
            status = "✅ PASS" if analysis_result.success else f"❌ {analysis_result.total_violations} violations"
            print(f"   📋 Static Analysis:    {status}")
        
        print("=" * 70)
