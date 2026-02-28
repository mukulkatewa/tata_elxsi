"""
Requirement Refinement Agent for AutoForge.

This agent takes a high-level natural language requirement and produces
a structured, refined technical specification before code generation begins.
It uses RAG context to enrich the specification with relevant VSS signals,
MISRA rules, and ASPICE requirements.
"""

import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
import openai


class RequirementAgent:
    """Agent that refines high-level requirements into structured technical specifications."""
    
    def __init__(self, llm_client: OpenAI, rag_retriever, 
                 model_name: str = "gpt-4o-mini", max_tokens: int = 2048):
        """Initialize Requirement Agent.
        
        Args:
            llm_client: OpenAI client instance
            rag_retriever: RAG retriever for automotive context
            model_name: LLM model name
            max_tokens: Maximum tokens for generation
        """
        self.llm_client = llm_client
        self.rag_retriever = rag_retriever
        self.model_name = model_name
        self.max_tokens = max_tokens
    
    def refine(self, raw_requirement: str) -> Dict[str, Any]:
        """
        Refine a high-level requirement into a structured technical specification.
        
        Args:
            raw_requirement: Natural language requirement from user
            
        Returns:
            Dictionary containing:
            - raw_requirement: Original input
            - refined_requirement: Structured technical specification
            - service_name: Suggested service name
            - vss_signals: Identified VSS signals needed
            - misra_rules: Applicable MISRA rules
            - aspice_requirements: Relevant ASPICE requirements
            - interfaces: Identified service interfaces
            - data_flow: Data flow description
        """
        print("📋 Requirement Agent: Analyzing and refining requirement...")
        
        # Retrieve automotive context from RAG
        rag_context = self.rag_retriever.retrieve_context(raw_requirement)
        
        # Format context
        vss_context = '\n'.join(rag_context.get('vss_signals', []))
        misra_context = '\n'.join(rag_context.get('misra_rules', []))
        aspice_context = '\n'.join(rag_context.get('aspice_items', []))
        
        # Build refinement prompt
        prompt = self._build_prompt(raw_requirement, vss_context, misra_context, aspice_context)
        
        # Call LLM
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens
            )
            
            llm_response = response.choices[0].message.content
            
        except Exception as e:
            # Graceful fallback: return basic spec
            return self._fallback_spec(raw_requirement, rag_context)
        
        # Parse structured output
        parsed = self._parse_response(llm_response, raw_requirement, rag_context)
        
        return parsed
    
    def format_spec(self, spec: Dict[str, Any]) -> str:
        """
        Format the refined specification as a human-readable document.
        
        Args:
            spec: Specification dictionary from refine()
            
        Returns:
            Formatted specification string
        """
        lines = [
            "=" * 70,
            "📋 REFINED TECHNICAL SPECIFICATION",
            "=" * 70,
            "",
            f"📝 Original Requirement:",
            f"   {spec['raw_requirement']}",
            "",
            f"🏷️  Service Name: {spec['service_name']}",
            "",
            "📄 Refined Specification:",
            spec['refined_requirement'],
            "",
        ]
        
        if spec.get('vss_signals'):
            lines.append("📡 VSS Signals Identified:")
            for signal in spec['vss_signals']:
                lines.append(f"   • {signal}")
            lines.append("")
        
        if spec.get('interfaces'):
            lines.append("🔌 Service Interfaces:")
            for iface in spec['interfaces']:
                lines.append(f"   • {iface}")
            lines.append("")
        
        if spec.get('data_flow'):
            lines.append("📊 Data Flow:")
            lines.append(f"   {spec['data_flow']}")
            lines.append("")
        
        if spec.get('misra_rules'):
            lines.append(f"🛡️  Applicable MISRA Rules: {len(spec['misra_rules'])} identified")
        
        if spec.get('aspice_requirements'):
            lines.append(f"📐 ASPICE Requirements: {len(spec['aspice_requirements'])} applicable")
        
        lines.append("")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def _build_prompt(self, requirement: str, vss_context: str, 
                      misra_context: str, aspice_context: str) -> str:
        """Build the refinement prompt."""
        return f"""You are an automotive systems engineer specializing in Software Defined Vehicle (SDV) 
service-oriented architecture. Your task is to refine a high-level requirement into a 
detailed technical specification.

## High-Level Requirement:
{requirement}

## Available VSS (Vehicle Signal Specification) Signals:
{vss_context}

## Applicable MISRA-C++ Rules:
{misra_context}

## ASPICE Process Requirements:
{aspice_context}

## Your Task:
Analyze the requirement and produce a structured technical specification with these sections:

### SERVICE_NAME
A snake_case name for this service (e.g., battery_health_monitor)

### REFINED_REQUIREMENT
A detailed, unambiguous technical specification (3-5 paragraphs) that includes:
- Exact functionality to implement
- Input signals and their data types
- Output signals and expected behavior
- Threshold values and boundary conditions
- Error handling requirements

### VSS_SIGNALS
List the exact VSS signal paths needed (e.g., Vehicle.Powertrain.Battery.StateOfCharge)

### INTERFACES
List service interfaces (methods/functions) to implement, each as:
- Name: description (input types → output type)

### DATA_FLOW
Describe the data flow in one paragraph: what data comes in, how it's processed, what goes out

Respond with ONLY these sections, using the exact headers above (### SECTION_NAME format).
"""

    def _parse_response(self, response: str, raw_requirement: str, 
                        rag_context: Dict) -> Dict[str, Any]:
        """Parse the LLM response into a structured dictionary."""
        
        # Extract sections using headers
        service_name = self._extract_section(response, "SERVICE_NAME").strip().lower().replace(' ', '_')
        if not service_name:
            service_name = self._derive_service_name(raw_requirement)
        
        refined_req = self._extract_section(response, "REFINED_REQUIREMENT")
        vss_signals = self._extract_list(response, "VSS_SIGNALS")
        interfaces = self._extract_list(response, "INTERFACES")
        data_flow = self._extract_section(response, "DATA_FLOW")
        
        return {
            'raw_requirement': raw_requirement,
            'refined_requirement': refined_req if refined_req else raw_requirement,
            'service_name': service_name,
            'vss_signals': vss_signals,
            'misra_rules': rag_context.get('misra_rules', []),
            'aspice_requirements': rag_context.get('aspice_items', []),
            'interfaces': interfaces,
            'data_flow': data_flow if data_flow else "N/A"
        }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract content of a named section from markdown-formatted text."""
        pattern = rf'###\s*{section_name}\s*\n(.*?)(?=###|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, text: str, section_name: str) -> List[str]:
        """Extract a list of items from a named section."""
        section_content = self._extract_section(text, section_name)
        if not section_content:
            return []
        
        # Parse bullet points or numbered lists
        items = []
        for line in section_content.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or 
                        re.match(r'^\d+\.', line)):
                # Remove bullet/number prefix
                clean = re.sub(r'^[-•\d.]+\s*', '', line).strip()
                if clean:
                    items.append(clean)
            elif line and not line.startswith('#'):
                items.append(line)
        
        return items
    
    def _derive_service_name(self, requirement: str) -> str:
        """Derive a service name from the requirement."""
        stop_words = {'create', 'a', 'an', 'the', 'that', 'when', 'which',
                      'for', 'to', 'in', 'on', 'with', 'from', 'by', 'and', 'or'}
        words = re.findall(r'\b[a-zA-Z]+\b', requirement.lower())
        meaningful = [w for w in words if w not in stop_words][:4]
        return '_'.join(meaningful)
    
    def _fallback_spec(self, raw_requirement: str, rag_context: Dict) -> Dict[str, Any]:
        """Generate a basic spec when LLM fails."""
        return {
            'raw_requirement': raw_requirement,
            'refined_requirement': raw_requirement,
            'service_name': self._derive_service_name(raw_requirement),
            'vss_signals': [],
            'misra_rules': rag_context.get('misra_rules', []),
            'aspice_requirements': rag_context.get('aspice_items', []),
            'interfaces': [],
            'data_flow': "N/A"
        }
