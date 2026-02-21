"""
Configuration module for AutoForge Phase 2 Multi-Agent Code Generation System.

This module manages environment variables, system settings, and LLM client initialization.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env file
load_dotenv()


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Returns:
        Dictionary containing configuration settings:
        - llm_provider: LLM provider name (default: "openai")
        - openai_api_key: OpenAI API key from environment
        - model_name: Model name (default: "gpt-4o-mini")
        - max_tokens: Maximum tokens for generation (default: 2048)
        - chroma_db_path: Path to ChromaDB database (default: "autoforge/data/chroma_db")
        - outputs_dir: Path to outputs directory (default: "autoforge/outputs")
    """
    config = {
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'model_name': os.getenv('MODEL_NAME', 'gpt-4o-mini'),
        'max_tokens': int(os.getenv('MAX_TOKENS', '2048')),
        'chroma_db_path': Path(os.getenv('CHROMA_DB_PATH', 'autoforge/data/chroma_db')),
        'outputs_dir': Path(os.getenv('OUTPUTS_DIR', 'autoforge/outputs'))
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration values.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If MODEL_NAME is empty or MAX_TOKENS is not positive
        FileNotFoundError: If CHROMA_DB_PATH does not exist
    """
    # Validate MODEL_NAME
    if not config['model_name'] or not isinstance(config['model_name'], str):
        raise ValueError("MODEL_NAME must be a non-empty string")
    
    # Validate MAX_TOKENS
    if not isinstance(config['max_tokens'], int) or config['max_tokens'] <= 0:
        raise ValueError("MAX_TOKENS must be a positive integer")
    
    # Validate CHROMA_DB_PATH exists
    if not config['chroma_db_path'].exists():
        raise FileNotFoundError(
            f"RAG database not initialized at {config['chroma_db_path']}. "
            "Please run Phase 1 setup first."
        )


def get_llm_client() -> OpenAI:
    """Initialize and return OpenAI client instance.
    
    Returns:
        Initialized OpenAI client
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set in environment
        FileNotFoundError: If CHROMA_DB_PATH does not exist
    """
    # Load configuration
    config = load_config()
    
    # Validate OPENAI_API_KEY
    if not config['openai_api_key']:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Validate configuration
    validate_config(config)
    
    # Initialize and return OpenAI client
    return OpenAI(api_key=config['openai_api_key'])
