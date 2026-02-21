"""
Dev Agent for generating MISRA-compliant C++ service code.

This agent uses LLM capabilities combined with RAG-retrieved automotive domain knowledge
to generate production-ready C++ services for Software Defined Vehicles.
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
import openai


class DevAgent:
    """AI agent responsible for generating C++ service code from requirements."""
    
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
        
        # Verify prompt template exists
        if not self.prompt_template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {self.prompt_template_path}"
            )
    
    def generate(self, requirement: str) -> Dict[str, Any]:
        """Generate C++ service code from requirement.
        
        Args:
            requirement: Natural language requirement string
            
        Returns:
            Dictionary containing:
            - service_name: Derived snake_case service name
            - header_code: .h file content
            - source_code: .cpp file content
            - full_code: Combined header + source
            - requirement: Original requirement
            - vss_signals_used: List of VSS signals referenced
            
        Raises:
            FileNotFoundError: If prompt template is missing
            Exception: If OpenAI API call fails
        """
        # Derive service name
        service_name = self._derive_service_name(requirement)
        
        print(f"🤖 Dev Agent generating {service_name}...")
        
        # Retrieve automotive context from RAG
        rag_context = self.rag_retriever.retrieve_context(requirement)
        
        # Load and fill prompt template
        template = self._load_prompt_template()
        filled_prompt = self._fill_prompt_template(template, requirement, rag_context)
        
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
        full_code = self._parse_llm_response(llm_response)
        
        # Split into header and source
        header_code, source_code = self._split_header_source(full_code)
        
        # Extract VSS signals used
        vss_signals_used = self._extract_vss_signals(full_code)
        
        return {
            'service_name': service_name,
            'header_code': header_code,
            'source_code': source_code,
            'full_code': full_code,
            'requirement': requirement,
            'vss_signals_used': vss_signals_used
        }
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file with UTF-8 encoding.
        
        Returns:
            Template content as string
        """
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _fill_prompt_template(self, template: str, requirement: str, 
                             rag_context: Dict[str, List[str]]) -> str:
        """Fill template placeholders with requirement and RAG context.
        
        Args:
            template: Prompt template with placeholders
            requirement: User requirement string
            rag_context: RAG-retrieved context dictionary
            
        Returns:
            Filled prompt string
            
        Raises:
            KeyError: If placeholder variable is missing
        """
        # Format RAG context sections
        vss_context = '\n'.join(rag_context.get('vss_signals', ['No VSS signals found']))
        misra_context = '\n'.join(rag_context.get('misra_rules', ['No MISRA rules found']))
        aspice_context = '\n'.join(rag_context.get('aspice_items', ['No ASPICE items found']))
        
        try:
            filled = template.format(
                requirement=requirement,
                vss_context=vss_context,
                misra_context=misra_context,
                aspice_context=aspice_context
            )
            return filled
        except KeyError as e:
            raise KeyError(f"Missing placeholder variable in template: {e}")
    
    def _derive_service_name(self, requirement: str) -> str:
        """Derive snake_case service name from requirement.
        
        Extracts first 3-4 meaningful words, excludes stop words,
        converts to snake_case format.
        
        Args:
            requirement: Natural language requirement
            
        Returns:
            Service name in snake_case format
        """
        # Stop words to exclude
        stop_words = {
            'create', 'a', 'an', 'the', 'that', 'when', 'which', 
            'who', 'where', 'why', 'how', 'is', 'are', 'was', 'were'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]+\b', requirement.lower())
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Take first 3-4 words
        selected_words = meaningful_words[:4] if len(meaningful_words) >= 4 else meaningful_words[:3]
        
        # Join with underscores
        service_name = '_'.join(selected_words)
        
        return service_name
    
    def _extract_vss_signals(self, code: str) -> List[str]:
        """Extract VSS signal references from generated code.
        
        Searches for 'Vehicle.' pattern occurrences.
        
        Args:
            code: Generated C++ code
            
        Returns:
            List of unique VSS signal names
        """
        # Pattern to match Vehicle.* signal references
        pattern = r'Vehicle\.[A-Za-z0-9.]+'
        
        # Find all matches
        matches = re.findall(pattern, code)
        
        # Return unique signals, sorted
        return sorted(list(set(matches)))
    
    def _parse_llm_response(self, response: str) -> str:
        """Parse LLM response to extract C++ code.
        
        Handles markdown code blocks and raw code.
        
        Args:
            response: LLM response string
            
        Returns:
            Extracted C++ code
        """
        # Try to extract markdown code blocks
        code_blocks = re.findall(r'```(?:cpp|c\+\+)?\s*\n(.*?)```', response, re.DOTALL)
        
        if code_blocks:
            # Concatenate all code blocks
            return '\n\n'.join(block.strip() for block in code_blocks)
        
        # No markdown blocks, treat entire response as code
        return response.strip()
    
    def _split_header_source(self, full_code: str) -> tuple:
        """Split full code into header and source files.
        
        Args:
            full_code: Combined code content
            
        Returns:
            Tuple of (header_code, source_code)
        """
        # Look for header/source separators
        header_marker = re.search(r'//\s*=+\s*HEADER FILE', full_code, re.IGNORECASE)
        source_marker = re.search(r'//\s*=+\s*SOURCE FILE', full_code, re.IGNORECASE)
        
        if header_marker and source_marker:
            header_start = header_marker.end()
            source_start = source_marker.end()
            
            header_code = full_code[header_start:source_marker.start()].strip()
            source_code = full_code[source_start:].strip()
            
            return header_code, source_code
        
        # If no clear separation, return full code for both
        return full_code, full_code
