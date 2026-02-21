"""
Quick validation script to verify AutoForge RAG setup.
Tests that all knowledge base files are valid and loadable.
"""

import json
import re
from pathlib import Path


def test_vss_signals():
    """Verify VSS signals JSON file."""
    print("Testing VSS signals...")
    path = Path("autoforge/knowledge_base/vss_signals.json")
    
    with open(path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    assert len(signals) == 30, f"Expected 30 signals, found {len(signals)}"
    
    required_fields = ['signal_name', 'datatype', 'unit', 'min_value', 'max_value', 'description']
    for signal in signals:
        for field in required_fields:
            assert field in signal, f"Signal missing field {field}: {signal.get('signal_name', 'unknown')}"
        
        # Check VSS dot notation
        assert '.' in signal['signal_name'], f"Signal name not in VSS format: {signal['signal_name']}"
    
    print(f"✓ VSS signals: {len(signals)} signals validated")


def test_misra_rules():
    """Verify MISRA rules markdown file."""
    print("Testing MISRA rules...")
    path = Path("autoforge/knowledge_base/misra_rules.md")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count rules (numbered items with "Rule" keyword)
    rules = re.findall(r'^\d+\.\s+\*\*Rule', content, re.MULTILINE)
    assert len(rules) >= 25, f"Expected at least 25 rules, found {len(rules)}"
    
    print(f"✓ MISRA rules: {len(rules)} rules validated")


def test_aspice_checklist():
    """Verify ASPICE checklist markdown file."""
    print("Testing ASPICE checklist...")
    path = Path("autoforge/knowledge_base/aspice_checklist.md")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count checkbox items
    items = re.findall(r'- \[ \]', content)
    assert len(items) >= 20, f"Expected at least 20 items, found {len(items)}"
    
    print(f"✓ ASPICE checklist: {len(items)} items validated")


def test_code_syntax():
    """Verify Python code syntax."""
    print("Testing Python code syntax...")
    import ast
    
    files = [
        "autoforge/rag/ingestor.py",
        "autoforge/rag/retriever.py",
        "autoforge/examples/query_example.py"
    ]
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        print(f"  ✓ {file_path}")


def main():
    print("=" * 60)
    print("AutoForge RAG Knowledge Base - Setup Validation")
    print("=" * 60)
    print()
    
    try:
        test_vss_signals()
        test_misra_rules()
        test_aspice_checklist()
        test_code_syntax()
        
        print()
        print("=" * 60)
        print("✓ All validation tests passed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run ingestion: python autoforge/rag/ingestor.py")
        print("3. Test queries: python autoforge/examples/query_example.py")
        
    except AssertionError as e:
        print(f"\n✗ Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
