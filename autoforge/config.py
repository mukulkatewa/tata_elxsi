"""
Configuration module for AutoForge.

Supports Google Gemini (native google-genai SDK) and OpenAI.
Uses a lightweight wrapper so all agents work with the same interface.
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# ============================================================
# Gemini Wrapper — makes Gemini look like OpenAI client
# ============================================================

@dataclass
class _Message:
    content: str
    role: str = "assistant"

@dataclass
class _Choice:
    message: _Message
    index: int = 0
    finish_reason: str = "stop"

@dataclass
class _Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

@dataclass
class _ChatCompletion:
    choices: List[_Choice] = field(default_factory=list)
    usage: _Usage = field(default_factory=_Usage)
    model: str = ""
    id: str = "gemini"


class _GeminiCompletions:
    """Mimics openai.chat.completions interface using google-genai SDK."""

    def __init__(self, api_key: str):
        from google import genai
        self._client = genai.Client(api_key=api_key)

    def create(self, model: str, messages: list,
               max_tokens: int = 4096, temperature: float = 0.7,
               **kwargs) -> _ChatCompletion:
        """Call Gemini and return an OpenAI-shaped response."""
        from google.genai import types

        # Convert OpenAI-style messages to Gemini format
        system_prompt = None
        contents = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_prompt = content
            elif role == "user":
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=content)]
                ))
            elif role == "assistant":
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=content)]
                ))

        # Build generation config
        gen_config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_prompt,
        )

        # Retry logic for rate limits
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=gen_config,
                )

                text = response.text or ""

                return _ChatCompletion(
                    choices=[_Choice(message=_Message(content=text))],
                    model=model,
                    usage=_Usage(
                        prompt_tokens=getattr(response.usage_metadata, 'prompt_token_count', 0) if response.usage_metadata else 0,
                        completion_tokens=getattr(response.usage_metadata, 'candidates_token_count', 0) if response.usage_metadata else 0,
                    )
                )

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = (attempt + 1) * 20  # 20s, 40s, 60s, 80s, 100s
                    print(f"  ⏳ Rate limited, waiting {wait_time}s... (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Gemini API error: {e}")

        raise Exception("Gemini API rate limit exceeded. Please wait a few minutes and try again.")


class _GeminiChat:
    """Mimics openai.chat interface."""
    def __init__(self, api_key: str):
        self.completions = _GeminiCompletions(api_key)


class GeminiClient:
    """Drop-in replacement for OpenAI client, using native Gemini SDK."""
    def __init__(self, api_key: str):
        self.chat = _GeminiChat(api_key)


# ============================================================
# Configuration
# ============================================================

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    provider = os.getenv('LLM_PROVIDER', 'gemini').lower()

    if provider == 'gemini':
        default_model = 'gemini-2.0-flash'
    else:
        default_model = 'gpt-4o-mini'

    config = {
        'llm_provider': provider,
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'model_name': os.getenv('MODEL_NAME', default_model),
        'max_tokens': int(os.getenv('MAX_TOKENS', '4096')),
        'chroma_db_path': Path(os.getenv('CHROMA_DB_PATH', 'autoforge/data/chroma_db')),
        'outputs_dir': Path(os.getenv('OUTPUTS_DIR', 'autoforge/outputs')),
        'use_docker': os.getenv('USE_DOCKER', 'false').lower() == 'true'
    }

    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration values."""
    if not config['model_name']:
        raise ValueError("MODEL_NAME must be a non-empty string")

    if not isinstance(config['max_tokens'], int) or config['max_tokens'] <= 0:
        raise ValueError("MAX_TOKENS must be a positive integer")

    if not config['chroma_db_path'].exists():
        raise FileNotFoundError(
            f"RAG database not initialized at {config['chroma_db_path']}. "
            "Run: python3 autoforge/rag/ingestor.py"
        )


def get_llm_client():
    """Initialize and return LLM client.

    Returns GeminiClient or OpenAI client based on LLM_PROVIDER config.
    Both share the same interface: client.chat.completions.create(...)
    """
    config = load_config()
    validate_config(config)

    provider = config['llm_provider']

    if provider == 'gemini':
        api_key = config['gemini_api_key']
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env file.")
        return GeminiClient(api_key=api_key)

    else:
        from openai import OpenAI
        api_key = config['openai_api_key']
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file.")
        return OpenAI(api_key=api_key)
