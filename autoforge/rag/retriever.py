"""
Context retrieval interface for AutoForge RAG Knowledge Base.

This module provides semantic search capabilities across automotive domain knowledge
stored in ChromaDB, returning relevant context for LLM prompt injection.
"""

from pathlib import Path
from typing import Dict, List
import chromadb


class RAGRetriever:
    """
    Retriever for querying automotive domain knowledge from ChromaDB.
    
    Provides semantic search across VSS signals, MISRA rules, and ASPICE checklists.
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize retriever with ChromaDB connection.
        
        Args:
            db_path: Path to ChromaDB persistent storage
            
        Raises:
            RuntimeError: If database cannot be loaded
        """
        try:
            self.client = chromadb.PersistentClient(path=str(db_path))
            
            # Load all collections
            self.vss_collection = self.client.get_collection("vss_signals")
            self.misra_collection = self.client.get_collection("misra_rules")
            self.aspice_collection = self.client.get_collection("aspice_checklist")
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to load ChromaDB from {db_path}: {e}. "
                "Ensure the database has been created by running ingestor.py first."
            )
    
    def retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, List[str]]:
        """
        Query all collections and return organized results.
        
        Args:
            query: Natural language query string
            top_k: Number of top results to return per collection (default 5)
            
        Returns:
            Dictionary with keys 'vss_signals', 'misra_rules', 'aspice_items',
            each mapping to a list of relevant document chunks
            
        Raises:
            ValueError: If query string is empty
        """
        if not query.strip():
            raise ValueError("Query string cannot be empty")
        
        results = {
            'vss_signals': [],
            'misra_rules': [],
            'aspice_items': []
        }
        
        try:
            # Query VSS signals collection
            vss_results = self.vss_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            if vss_results['documents'] and vss_results['documents'][0]:
                results['vss_signals'] = vss_results['documents'][0]
        except Exception as e:
            print(f"Warning: Query failed for vss_signals collection: {e}")
        
        try:
            # Query MISRA rules collection
            misra_results = self.misra_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            if misra_results['documents'] and misra_results['documents'][0]:
                results['misra_rules'] = misra_results['documents'][0]
        except Exception as e:
            print(f"Warning: Query failed for misra_rules collection: {e}")
        
        try:
            # Query ASPICE checklist collection
            aspice_results = self.aspice_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            if aspice_results['documents'] and aspice_results['documents'][0]:
                results['aspice_items'] = aspice_results['documents'][0]
        except Exception as e:
            print(f"Warning: Query failed for aspice_checklist collection: {e}")
        
        return results
    
    def build_prompt_context(self, query: str, top_k: int = 5) -> str:
        """
        Format retrieved context as clean string for LLM prompt injection.
        
        Args:
            query: Natural language query string
            top_k: Number of top results to return per collection (default 5)
            
        Returns:
            Formatted string with section headers for each document type
        """
        results = self.retrieve_context(query, top_k)
        
        context_parts = []
        
        # Add VSS signals section
        if results['vss_signals']:
            context_parts.append("=== Vehicle Signal Specifications ===\n")
            for i, chunk in enumerate(results['vss_signals'], 1):
                context_parts.append(f"{i}. {chunk}\n")
        
        # Add MISRA rules section
        if results['misra_rules']:
            context_parts.append("\n=== MISRA-C++ Coding Rules ===\n")
            for i, chunk in enumerate(results['misra_rules'], 1):
                context_parts.append(f"{i}. {chunk}\n")
        
        # Add ASPICE checklist section
        if results['aspice_items']:
            context_parts.append("\n=== ASPICE Compliance Requirements ===\n")
            for i, chunk in enumerate(results['aspice_items'], 1):
                context_parts.append(f"{i}. {chunk}\n")
        
        if not context_parts:
            return "No relevant context found for the query."
        
        return "".join(context_parts)
