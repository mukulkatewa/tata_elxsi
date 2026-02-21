"""
AutoForge Orchestrator for multi-agent code generation workflow.

This orchestrator coordinates Dev Agent and QA Agent to generate complete
service implementations with tests, metadata, and graceful error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from autoforge.rag.retriever import RAGRetriever
from autoforge.agents.dev_agent import DevAgent
from autoforge.agents.qa_agent import QAAgent
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
    
    def run(self, requirement: str) -> Dict[str, Any]:
        """Execute complete code generation workflow.
        
        Args:
            requirement: Natural language requirement string
            
        Returns:
            Dictionary containing:
            - service_name: Derived service name
            - code_file_path: Path to generated service code
            - test_file_path: Path to generated test code (or None if QA failed)
            - metadata_file_path: Path to metadata JSON
            - dev_agent_output: Dev Agent output dictionary
            - qa_agent_output: QA Agent output dictionary (or None if failed)
            - error: Error message if QA Agent failed (or None)
        """
        # Generate service code with Dev Agent
        dev_output = self.dev_agent.generate(requirement)
        service_name = dev_output['service_name']
        
        # Create output directory
        output_dir = self._create_output_directory(service_name)
        
        # Save service code
        code_file_path = output_dir / f"{service_name}.cpp"
        self._save_code_file(code_file_path, dev_output['full_code'])
        
        # Generate test code with QA Agent (with graceful degradation)
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
        
        # Save metadata
        metadata = {
            'requirement': requirement,
            'service_name': service_name,
            'vss_signals_used': dev_output['vss_signals_used'],
            'timestamp': datetime.now().isoformat(),
            'model_used': self.model_name
        }
        metadata_file_path = self._save_metadata(output_dir, metadata)
        
        # Print summary
        self._print_summary(service_name, code_file_path, test_file_path, metadata_file_path)
        
        return {
            'service_name': service_name,
            'code_file_path': code_file_path,
            'test_file_path': test_file_path,
            'metadata_file_path': metadata_file_path,
            'dev_agent_output': dev_output,
            'qa_agent_output': qa_output,
            'error': error_message
        }
    
    def run_interactive(self) -> None:
        """Run interactive mode with continuous requirement input.
        
        Displays welcome message and continuously prompts for requirements
        until user enters 'quit' or 'exit'.
        """
        print("\n" + "="*70)
        print("🚀 AutoForge Phase 2: Multi-Agent Code Generation System")
        print("="*70)
        print("\nWelcome to AutoForge interactive mode!")
        print("Enter your requirements to generate automotive C++ services.")
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
                
                # Execute workflow
                print()
                self.run(requirement)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting AutoForge.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again with a different requirement.\n")
    
    def _create_output_directory(self, service_name: str) -> Path:
        """Create output directory for service.
        
        Args:
            service_name: Service name in snake_case
            
        Returns:
            Path to created directory
        """
        output_dir = self.outputs_dir / service_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _save_code_file(self, file_path: Path, content: str) -> None:
        """Save code file with UTF-8 encoding.
        
        Args:
            file_path: Path to save file
            content: Code content to save
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to save file {file_path}: {e}")
    
    def _save_metadata(self, output_dir: Path, metadata: Dict[str, Any]) -> Path:
        """Save metadata JSON with indentation for readability.
        
        Args:
            output_dir: Output directory path
            metadata: Metadata dictionary
            
        Returns:
            Path to saved metadata file
        """
        metadata_path = output_dir / 'metadata.json'
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save metadata {metadata_path}: {e}")
        
        return metadata_path
    
    def _print_summary(self, service_name: str, code_path: Path, 
                      test_path: Optional[Path], metadata_path: Path) -> None:
        """Print generation summary with file paths.
        
        Args:
            service_name: Service name
            code_path: Path to service code file
            test_path: Path to test code file (or None)
            metadata_path: Path to metadata file
        """
        print("\n" + "="*70)
        print(f"✅ Generation Complete: {service_name}")
        print("="*70)
        print(f"📄 Service Code: {code_path}")
        if test_path:
            print(f"🧪 Test Code: {test_path}")
        print(f"📋 Metadata: {metadata_path}")
        print("="*70)
