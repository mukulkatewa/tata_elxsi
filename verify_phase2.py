#!/usr/bin/env python3
"""
Verification script for AutoForge Phase 2 implementation.

This script verifies that all modules can be imported and basic
configuration works correctly.
"""

import sys
from pathlib import Path


def verify_imports():
    """Verify all Phase 2 modules can be imported."""
    print("Verifying imports...")
    
    try:
        from autoforge.config import load_config, validate_config, get_llm_client
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config module: {e}")
        return False
    
    try:
        from autoforge.agents.dev_agent import DevAgent
        print("✅ DevAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DevAgent: {e}")
        return False
    
    try:
        from autoforge.agents.qa_agent import QAAgent
        print("✅ QAAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import QAAgent: {e}")
        return False
    
    try:
        from autoforge.orchestrator import AutoForgeOrchestrator
        print("✅ Orchestrator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Orchestrator: {e}")
        return False
    
    return True


def verify_file_structure():
    """Verify all required files exist."""
    print("\nVerifying file structure...")
    
    required_files = [
        'autoforge/config.py',
        'autoforge/agents/__init__.py',
        'autoforge/agents/dev_agent.py',
        'autoforge/agents/qa_agent.py',
        'autoforge/orchestrator.py',
        'prompts/dev_agent_prompt.txt',
        'prompts/qa_agent_prompt.txt',
        'run_phase2.py',
        'requirements.txt'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist


def verify_prompt_templates():
    """Verify prompt templates contain required placeholders."""
    print("\nVerifying prompt templates...")
    
    # Check Dev Agent prompt
    dev_prompt_path = Path('prompts/dev_agent_prompt.txt')
    if dev_prompt_path.exists():
        content = dev_prompt_path.read_text(encoding='utf-8')
        required_placeholders = ['{requirement}', '{vss_context}', '{misra_context}', '{aspice_context}']
        
        missing = [p for p in required_placeholders if p not in content]
        if missing:
            print(f"❌ Dev Agent prompt missing placeholders: {missing}")
            return False
        else:
            print("✅ Dev Agent prompt has all required placeholders")
    else:
        print("❌ Dev Agent prompt template not found")
        return False
    
    # Check QA Agent prompt
    qa_prompt_path = Path('prompts/qa_agent_prompt.txt')
    if qa_prompt_path.exists():
        content = qa_prompt_path.read_text(encoding='utf-8')
        required_placeholders = ['{requirement}', '{generated_code}', '{service_name}']
        
        missing = [p for p in required_placeholders if p not in content]
        if missing:
            print(f"❌ QA Agent prompt missing placeholders: {missing}")
            return False
        else:
            print("✅ QA Agent prompt has all required placeholders")
    else:
        print("❌ QA Agent prompt template not found")
        return False
    
    return True


def verify_config():
    """Verify configuration can be loaded."""
    print("\nVerifying configuration...")
    
    try:
        from autoforge.config import load_config
        config = load_config()
        
        required_keys = ['llm_provider', 'openai_api_key', 'model_name', 
                        'max_tokens', 'chroma_db_path', 'outputs_dir']
        
        missing = [k for k in required_keys if k not in config]
        if missing:
            print(f"❌ Config missing keys: {missing}")
            return False
        
        print("✅ Configuration loaded successfully")
        print(f"   - LLM Provider: {config['llm_provider']}")
        print(f"   - Model: {config['model_name']}")
        print(f"   - Max Tokens: {config['max_tokens']}")
        print(f"   - ChromaDB Path: {config['chroma_db_path']}")
        print(f"   - Outputs Dir: {config['outputs_dir']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False


def main():
    """Run all verification checks."""
    print("="*70)
    print("AutoForge Phase 2 Verification")
    print("="*70)
    
    checks = [
        ("File Structure", verify_file_structure),
        ("Module Imports", verify_imports),
        ("Prompt Templates", verify_prompt_templates),
        ("Configuration", verify_config)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("Verification Summary")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All verification checks passed!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Ensure Phase 1 RAG database is initialized")
        print("3. Run: python run_phase2.py --demo")
        return 0
    else:
        print("\n⚠️  Some verification checks failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
