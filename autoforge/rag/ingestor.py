"""
Document ingestion pipeline for AutoForge RAG Knowledge Base.

This module loads automotive domain documents (VSS signals, MISRA rules, ASPICE checklists),
chunks them appropriately, generates embeddings, and stores them in ChromaDB.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb


def load_vss_signals(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load VSS signals from JSON file.
    
    Args:
        file_path: Path to the vss_signals.json file
        
    Returns:
        List of signal dictionaries with all required fields
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the JSON is malformed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")


def load_markdown_document(file_path: Path) -> str:
    """
    Load markdown content from file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        String content of the markdown file
        
    Raises:
        FileNotFoundError: If the file does not exist
        UnicodeDecodeError: If the file encoding is not UTF-8
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding, e.object, e.start, e.end,
            f"File {file_path} must be UTF-8 encoded"
        )


def chunk_vss_signals(signals: List[Dict]) -> List[str]:
    """
    Convert each VSS signal object to a text chunk.
    
    Args:
        signals: List of signal dictionaries
        
    Returns:
        List of formatted text chunks, one per signal
    """
    chunks = []
    required_fields = ['signal_name', 'datatype', 'unit', 'min_value', 'max_value', 'description']
    
    for signal in signals:
        # Validate required fields
        missing = [f for f in required_fields if f not in signal]
        if missing:
            print(f"Warning: Signal missing fields {missing}: {signal.get('signal_name', 'unknown')}")
            continue
            
        chunk = f"""Signal: {signal['signal_name']}
Type: {signal['datatype']}
Unit: {signal['unit']}
Range: {signal['min_value']} to {signal['max_value']}
Description: {signal['description']}"""
        chunks.append(chunk)
    
    return chunks


def chunk_markdown(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split markdown content by headings or fixed size with overlap.
    
    Args:
        content: Markdown text content
        chunk_size: Maximum characters per chunk (default 500)
        overlap: Character overlap between consecutive chunks (default 50)
        
    Returns:
        List of text chunks
    """
    if not content.strip():
        return []
    
    chunks = []
    
    # Try splitting by markdown headings first
    lines = content.split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        # Check if this is a heading
        if line.startswith('##'):
            # Save current chunk if it exists
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = len(line)
        else:
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
            
            # If chunk exceeds size, split it
            if current_size > chunk_size and len(current_chunk) > 1:
                chunks.append('\n'.join(current_chunk))
                # Keep overlap for next chunk
                overlap_text = '\n'.join(current_chunk)[-overlap:]
                current_chunk = [overlap_text]
                current_size = len(overlap_text)
    
    # Add final chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    # If no headings found or chunks are still too large, do fixed-size chunking
    if not chunks or any(len(c) > chunk_size * 2 for c in chunks):
        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap
    
    return [c.strip() for c in chunks if c.strip()]


def create_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Generate embeddings using sentence-transformers.
    
    Args:
        texts: List of text chunks to embed
        model_name: Name of the sentence-transformers model
        
    Returns:
        List of embedding vectors
        
    Raises:
        RuntimeError: If model fails to load
    """
    try:
        print(f"Loading embedding model: {model_name}...")
        model = SentenceTransformer(model_name)
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    except Exception as e:
        raise RuntimeError(
            f"Failed to load embedding model: {e}. "
            "Ensure internet connectivity for first download."
        )


def store_in_chromadb(
    collection_name: str,
    chunks: List[str],
    embeddings: List[List[float]],
    db_path: Path
):
    """
    Store chunks and embeddings in ChromaDB collection.
    
    Args:
        collection_name: Name of the collection to create/update
        chunks: List of text chunks
        embeddings: List of embedding vectors
        db_path: Path to ChromaDB persistent storage
        
    Raises:
        RuntimeError: If database initialization fails
    """
    # Create database directory if it doesn't exist
    db_path.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Connecting to ChromaDB at {db_path}...")
        client = chromadb.PersistentClient(path=str(db_path))
        
        # Delete collection if it exists (for fresh ingestion)
        try:
            client.delete_collection(name=collection_name)
        except:
            pass
        
        # Create collection
        collection = client.create_collection(name=collection_name)
        
        # Generate IDs
        ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
        
        # Store documents with embeddings
        print(f"Storing {len(chunks)} chunks in collection '{collection_name}'...")
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings
        )
        
        print(f"Successfully stored {len(chunks)} chunks in '{collection_name}'")
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize ChromaDB at {db_path}: {e}")


def ingest_all_documents(knowledge_base_path: Path, db_path: Path):
    """
    Main ingestion function that processes all documents.
    
    Args:
        knowledge_base_path: Path to knowledge_base directory
        db_path: Path to ChromaDB storage directory
    """
    print("=" * 60)
    print("AutoForge RAG Knowledge Base - Document Ingestion")
    print("=" * 60)
    
    # Process VSS signals
    print("\n[1/3] Processing VSS Signals...")
    vss_path = knowledge_base_path / "vss_signals.json"
    signals = load_vss_signals(vss_path)
    print(f"Loaded {len(signals)} VSS signals")
    
    vss_chunks = chunk_vss_signals(signals)
    print(f"Created {len(vss_chunks)} VSS signal chunks")
    
    vss_embeddings = create_embeddings(vss_chunks)
    store_in_chromadb("vss_signals", vss_chunks, vss_embeddings, db_path)
    
    # Process MISRA rules
    print("\n[2/3] Processing MISRA-C++ Rules...")
    misra_path = knowledge_base_path / "misra_rules.md"
    misra_content = load_markdown_document(misra_path)
    print(f"Loaded MISRA rules document ({len(misra_content)} characters)")
    
    misra_chunks = chunk_markdown(misra_content)
    print(f"Created {len(misra_chunks)} MISRA rule chunks")
    
    misra_embeddings = create_embeddings(misra_chunks)
    store_in_chromadb("misra_rules", misra_chunks, misra_embeddings, db_path)
    
    # Process ASPICE checklist
    print("\n[3/3] Processing ASPICE Checklist...")
    aspice_path = knowledge_base_path / "aspice_checklist.md"
    aspice_content = load_markdown_document(aspice_path)
    print(f"Loaded ASPICE checklist ({len(aspice_content)} characters)")
    
    aspice_chunks = chunk_markdown(aspice_content)
    print(f"Created {len(aspice_chunks)} ASPICE checklist chunks")
    
    aspice_embeddings = create_embeddings(aspice_chunks)
    store_in_chromadb("aspice_checklist", aspice_chunks, aspice_embeddings, db_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    print(f"VSS Signals: {len(vss_chunks)} chunks")
    print(f"MISRA Rules: {len(misra_chunks)} chunks")
    print(f"ASPICE Checklist: {len(aspice_chunks)} chunks")
    print(f"Total: {len(vss_chunks) + len(misra_chunks) + len(aspice_chunks)} chunks")
    print(f"Database location: {db_path}")
    print("=" * 60)


if __name__ == "__main__":
    # Use relative paths from script location
    script_dir = Path(__file__).parent.parent
    kb_path = script_dir / "knowledge_base"
    db_path = script_dir / "data" / "chroma_db"
    
    ingest_all_documents(kb_path, db_path)
