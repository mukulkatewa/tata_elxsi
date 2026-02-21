"""
QA Agent for generating comprehensive C++ test code.

This agent generates test suites that validate service behavior across
normal operations, boundary conditions, and failure scenarios.
"""

import re
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
import openai


class QAAgent:
    """AI agent responsible for generating C++ test code for services."""
    
    def __init__(self, llm_client: OpenAI, prompt_template_path: Path, 
                 model_name: str, max_tokens: int):
        """Initialize QA Agent.
        
        Args:
            llm_client: OpenAI client instance
            prompt_template_path: Path to prompt template file
            model_name: LLM model name (e.g., "gpt-4o-mini")
            max_tokens: Maximum tokens for generation
        """
        self.llm_client = llm_client
        self.prompt_template_path = prompt_template_path
        self.model_name = model_name
        self.max_tokens = max_tokens
        
        # Verify prompt template exists
        if not self.prompt_template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {self.prompt_template_path}"
            )
    
    def generate_tests(self, requirement: str, generated_code: str, 
                      service_name: str) -> Dict[str, Any]:
        """Generate test code for service.
        
        Args:
            requirement: Original requirement string
            generated_code: Generated service code from Dev Agent
            service_name: Service name in snake_case
            
        Returns:
            Dictionary containing:
            - test_code: Complete test file content
            - service_name: Service name
            - test_file_name: Formatted as "test_[service_name].cpp"
            
        Raises:
            FileNotFoundError: If prompt template is missing
            Exception: If OpenAI API call fails
        """
        print(f"🧪 QA Agent generating tests for {service_name}...")
        
        # Load and fill prompt template
        template = self._load_prompt_template()
        filled_prompt = self._fill_prompt_template(
            template, requirement, generated_code, service_name
        )
        
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
        
        # Parse LLM response to extract test code
        test_code = self._parse_llm_response(llm_response)
        
        # Format test filename
        test_file_name = f"test_{service_name}.cpp"
        
        return {
            'test_code': test_code,
            'service_name': service_name,
            'test_file_name': test_file_name
        }
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file with UTF-8 encoding.
        
        Returns:
            Template content as string
        """
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _fill_prompt_template(self, template: str, requirement: str, 
                             generated_code: str, service_name: str) -> str:
        """Fill template placeholders with values.
        
        Args:
            template: Prompt template with placeholders
            requirement: Original requirement string
            generated_code: Generated service code
            service_name: Service name
            
        Returns:
            Filled prompt string
            
        Raises:
            KeyError: If placeholder variable is missing
        """
        try:
            filled = template.format(
                requirement=requirement,
                generated_code=generated_code,
                service_name=service_name
            )
            return filled
        except KeyError as e:
            raise KeyError(f"Missing placeholder variable in template: {e}")
    
    def _parse_llm_response(self, response: str) -> str:
        """Parse LLM response to extract C++ test code.
        
        Handles markdown code blocks and raw code.
        
        Args:
            response: LLM response string
            
        Returns:
            Extracted C++ test code
        """
        # Try to extract markdown code blocks
        code_blocks = re.findall(r'```(?:cpp|c\+\+)?\s*\n(.*?)```', response, re.DOTALL)
        
        if code_blocks:
            # Concatenate all code blocks
            return '\n\n'.join(block.strip() for block in code_blocks)
        
        # No markdown blocks, treat entire response as code
        return response.strip()
