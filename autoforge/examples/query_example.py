"""
Example usage of the AutoForge RAG Retriever.

This script demonstrates how to query the knowledge base and retrieve
relevant automotive domain context for code generation.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoforge.rag.retriever import RAGRetriever


def main():
    # Initialize retriever with database path
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / "data" / "chroma_db"
    
    print("Initializing RAG Retriever...")
    retriever = RAGRetriever(db_path)
    print("Retriever initialized successfully!\n")
    
    # Example queries
    queries = [
        "vehicle speed signal",
        "memory management rules",
        "unit test coverage requirements",
        "battery state of charge",
        "type safety and casting"
    ]
    
    print("=" * 70)
    print("AutoForge RAG Knowledge Base - Query Examples")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 70)
        
        # Retrieve context
        results = retriever.retrieve_context(query, top_k=3)
        
        # Display results by category
        if results['vss_signals']:
            print("\nVSS Signals Found:")
            for j, chunk in enumerate(results['vss_signals'], 1):
                print(f"  {j}. {chunk[:100]}...")
        
        if results['misra_rules']:
            print("\nMISRA Rules Found:")
            for j, chunk in enumerate(results['misra_rules'], 1):
                print(f"  {j}. {chunk[:100]}...")
        
        if results['aspice_items']:
            print("\nASPICE Items Found:")
            for j, chunk in enumerate(results['aspice_items'], 1):
                print(f"  {j}. {chunk[:100]}...")
    
    # Demonstrate build_prompt_context
    print("\n" + "=" * 70)
    print("Example: Building LLM Prompt Context")
    print("=" * 70)
    
    query = "Generate code for reading tire pressure sensors"
    print(f"\nQuery: {query}\n")
    
    prompt_context = retriever.build_prompt_context(query, top_k=2)
    print(prompt_context)


if __name__ == "__main__":
    main()
