"""
Dev Agent for generating MISRA-compliant service code in multiple languages.

This agent uses LLM capabilities combined with RAG-retrieved automotive domain knowledge
to generate production-ready services for Software Defined Vehicles.
Supports C++, Rust, and Kotlin code generation.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
import openai


# Language-specific configurations
LANGUAGE_CONFIG = {
    "cpp": {
        "name": "C++",
        "extension": ".cpp",
        "header_extension": ".h",
        "code_block_tag": "cpp",
        "standards": "MISRA-C++ 2008/2023, AUTOSAR C++14",
        "build_system": "CMake",
    },
    "rust": {
        "name": "Rust",
        "extension": ".rs",
        "header_extension": None,
        "code_block_tag": "rust",
        "standards": "Rust Safety Guidelines, MISRA-equivalent patterns",
        "build_system": "Cargo",
    },
    "kotlin": {
        "name": "Kotlin",
        "extension": ".kt",
        "header_extension": None,
        "code_block_tag": "kotlin",
        "standards": "Android Automotive AIDL, Kotlin coding conventions",
        "build_system": "Gradle",
    }
}


class DevAgent:
    """AI agent responsible for generating service code from requirements."""
    
    def __init__(self, llm_client: OpenAI, rag_retriever, 
                 prompt_template_path: Path, model_name: str, max_tokens: int):
        """Initialize Dev Agent.
        
        Args:
            llm_client: OpenAI client instance
            rag_retriever: RAG retriever for automotive context
            prompt_template_path: Path to prompt template file
            model_name: LLM model name (e.g., "gpt-4o-mini")
            max_tokens: Maximum tokens for generation
        """
        self.llm_client = llm_client
        self.rag_retriever = rag_retriever
        self.prompt_template_path = prompt_template_path
        self.model_name = model_name
        self.max_tokens = max_tokens
    
    def generate(self, requirement: str, language: str = "cpp") -> Dict[str, Any]:
        """Generate service code from requirement.
        
        Args:
            requirement: Natural language requirement string
            language: Target language ("cpp", "rust", "kotlin")
            
        Returns:
            Dictionary containing:
            - service_name: Derived snake_case service name
            - header_code: .h file content (C++ only)
            - source_code: .cpp/.rs/.kt file content
            - full_code: Combined code
            - requirement: Original requirement
            - vss_signals_used: List of VSS signals referenced
            - language: Target language used
        """
        lang_config = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["cpp"])
        
        # Derive service name
        service_name = self._derive_service_name(requirement)
        
        print(f"🤖 Dev Agent generating {service_name} ({lang_config['name']})...")
        
        # Retrieve automotive context from RAG
        rag_context = self.rag_retriever.retrieve_context(requirement)
        
        # Build the prompt (use template if exists, otherwise use built-in)
        filled_prompt = self._build_prompt(requirement, rag_context, lang_config)
        
        # Make OpenAI API call
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": filled_prompt}],
                max_tokens=self.max_tokens
            )
            
            llm_response = response.choices[0].message.content
            
        except openai.AuthenticationError as e:
            raise Exception(
                f"OpenAI authentication failed: Invalid or missing API key. {e}"
            )
        except openai.RateLimitError as e:
            raise Exception(f"OpenAI rate limit exceeded: {e}")
        except openai.APIConnectionError as e:
            raise Exception(f"OpenAI connection failed: {e}")
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
        
        # Parse LLM response to extract code
        full_code = self._parse_llm_response(llm_response, lang_config['code_block_tag'])
        
        # Split into header and source (C++ only)
        header_code = ""
        source_code = full_code
        if language == "cpp":
            header_code, source_code = self._split_header_source(full_code)
        
        # Extract VSS signals used
        vss_signals_used = self._extract_vss_signals(full_code)
        
        return {
            'service_name': service_name,
            'header_code': header_code,
            'source_code': source_code,
            'full_code': full_code,
            'requirement': requirement,
            'vss_signals_used': vss_signals_used,
            'language': language
        }
    
    def _build_prompt(self, requirement: str, rag_context: Dict[str, List[str]], 
                      lang_config: Dict) -> str:
        """Build the prompt using template file or built-in template.
        
        Args:
            requirement: User requirement string
            rag_context: RAG-retrieved context dictionary
            lang_config: Language configuration
            
        Returns:
            Filled prompt string
        """
        # Format RAG context sections
        vss_context = '\n'.join(rag_context.get('vss_signals', ['No VSS signals found']))
        misra_context = '\n'.join(rag_context.get('misra_rules', ['No MISRA rules found']))
        aspice_context = '\n'.join(rag_context.get('aspice_items', ['No ASPICE items found']))
        
        # Try to load from prompt template file
        if self.prompt_template_path.exists():
            try:
                template = self._load_prompt_template()
                filled = template.format(
                    requirement=requirement,
                    vss_context=vss_context,
                    misra_context=misra_context,
                    aspice_context=aspice_context,
                    language=lang_config['name'],
                    standards=lang_config['standards']
                )
                return filled
            except (KeyError, ValueError):
                pass  # Fall through to built-in template
        
        # Built-in prompt template
        return self._builtin_prompt(requirement, vss_context, misra_context, 
                                    aspice_context, lang_config)
    
    def _builtin_prompt(self, requirement: str, vss_context: str, 
                        misra_context: str, aspice_context: str,
                        lang_config: Dict) -> str:
        """Built-in prompt template for code generation."""
        lang_name = lang_config['name']
        standards = lang_config['standards']
        
        return f"""You are an expert automotive software engineer specializing in {lang_name} development 
for Software Defined Vehicles (SDV). Generate production-ready service code following {standards}.

## Requirement:
{requirement}

## Vehicle Signal Specification (VSS) Context:
{vss_context}

## MISRA/Safety Coding Rules:
{misra_context}

## ASPICE Process Requirements:
{aspice_context}

## Instructions:
1. Generate a complete, compilable {lang_name} service implementation
2. Follow {standards} coding guidelines strictly
3. Use the VSS signal definitions provided above for data types and naming
4. Include proper error handling and input validation
5. Add comprehensive inline documentation
6. Include a main() function or entry point for standalone compilation
7. Use only standard libraries (no external dependencies)

## Code Structure Requirements:
- Service class/struct with clear interface
- Signal reading/processing functions
- Threshold-based alert generation
- Proper initialization and cleanup
- Thread-safe where applicable

Return ONLY the complete {lang_name} source code wrapped in ```{lang_config['code_block_tag']} ... ``` markers.
No explanations outside the code.
"""
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file with UTF-8 encoding."""
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _derive_service_name(self, requirement: str) -> str:
        """Derive snake_case service name from requirement."""
        stop_words = {
            'create', 'a', 'an', 'the', 'that', 'when', 'which', 
            'who', 'where', 'why', 'how', 'is', 'are', 'was', 'were',
            'for', 'to', 'in', 'on', 'with', 'from', 'by', 'and', 'or'
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', requirement.lower())
        meaningful_words = [w for w in words if w not in stop_words]
        selected_words = meaningful_words[:4] if len(meaningful_words) >= 4 else meaningful_words[:3]
        
        return '_'.join(selected_words)
    
    def _extract_vss_signals(self, code: str) -> List[str]:
        """Extract VSS signal references from generated code."""
        pattern = r'Vehicle\.[A-Za-z0-9.]+'
        matches = re.findall(pattern, code)
        return sorted(list(set(matches)))
    
    def _parse_llm_response(self, response: str, code_tag: str = "cpp") -> str:
        """Parse LLM response to extract code."""
        # Try to extract markdown code blocks with specific language tag
        patterns = [
            rf'```{re.escape(code_tag)}\s*\n(.*?)```',
            r'```c\+\+\s*\n(.*?)```',
            r'```\s*\n(.*?)```'
        ]
        
        for pattern in patterns:
            code_blocks = re.findall(pattern, response, re.DOTALL)
            if code_blocks:
                return '\n\n'.join(block.strip() for block in code_blocks)
        
        # No markdown blocks, treat entire response as code
        return response.strip()
    
    def _split_header_source(self, full_code: str) -> tuple:
        """Split full code into header and source files."""
        header_marker = re.search(r'//\s*=+\s*HEADER FILE', full_code, re.IGNORECASE)
        source_marker = re.search(r'//\s*=+\s*SOURCE FILE', full_code, re.IGNORECASE)
        
        if header_marker and source_marker:
            header_start = header_marker.end()
            source_start = source_marker.end()
            header_code = full_code[header_start:source_marker.start()].strip()
            source_code = full_code[source_start:].strip()
            return header_code, source_code
        
        return full_code, full_code
