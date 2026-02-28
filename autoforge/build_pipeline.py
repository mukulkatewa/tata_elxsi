"""
Self-Healing Build Pipeline for AutoForge.

This module provides an iterative compile-fix loop:
1. Write generated C++ code to a temp workspace
2. Attempt compilation with g++ (or inside Docker if available)
3. If compilation fails, feed compiler errors back to the LLM for auto-fix
4. Retry up to MAX_RETRIES times
5. Return build result with pass/fail status and all iteration logs
"""

import os
import re
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BuildIteration:
    """Record of a single build attempt."""
    iteration: int
    success: bool
    compiler_output: str
    error_count: int
    code_snapshot: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BuildResult:
    """Final result of the build pipeline."""
    success: bool
    total_iterations: int
    final_code: str
    iterations: List[BuildIteration]
    binary_path: Optional[str] = None
    static_analysis: Optional[Dict[str, Any]] = None


class BuildPipeline:
    """
    Self-healing build pipeline that compiles C++ code and auto-fixes errors.
    
    Supports both local compilation (g++) and Docker-based compilation.
    """
    
    MAX_RETRIES = 3
    
    def __init__(self, llm_client=None, model_name: str = "gpt-4o-mini",
                 max_tokens: int = 2048, use_docker: bool = False):
        """
        Initialize the build pipeline.
        
        Args:
            llm_client: OpenAI client for error-fixing (None = no auto-fix)
            model_name: LLM model name for fix generation
            max_tokens: Max tokens for fix generation
            use_docker: Whether to compile inside Docker container
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.use_docker = use_docker
        self._workspace = None
    
    def build(self, code: str, service_name: str) -> BuildResult:
        """
        Execute the self-healing build pipeline.
        
        Args:
            code: C++ source code to compile
            service_name: Name of the service (used for filenames)
            
        Returns:
            BuildResult with success/fail status and iteration history
        """
        iterations: List[BuildIteration] = []
        current_code = code
        
        # Create temporary workspace
        self._workspace = Path(tempfile.mkdtemp(prefix="autoforge_build_"))
        
        try:
            for attempt in range(1, self.MAX_RETRIES + 1):
                print(f"🔨 Build attempt {attempt}/{self.MAX_RETRIES}...")
                
                # Write code to file
                source_path = self._workspace / f"{service_name}.cpp"
                source_path.write_text(current_code, encoding='utf-8')
                
                # Attempt compilation
                success, compiler_output = self._compile(source_path, service_name)
                
                # Count errors
                error_count = self._count_errors(compiler_output)
                
                # Record iteration
                iteration = BuildIteration(
                    iteration=attempt,
                    success=success,
                    compiler_output=compiler_output,
                    error_count=error_count,
                    code_snapshot=current_code
                )
                iterations.append(iteration)
                
                if success:
                    print(f"✅ Build succeeded on attempt {attempt}!")
                    binary_path = str(self._workspace / service_name)
                    return BuildResult(
                        success=True,
                        total_iterations=attempt,
                        final_code=current_code,
                        iterations=iterations,
                        binary_path=binary_path
                    )
                
                # If we have more retries and an LLM client, attempt auto-fix
                if attempt < self.MAX_RETRIES and self.llm_client:
                    print(f"⚠️  Build failed with {error_count} error(s). Auto-fixing...")
                    current_code = self._auto_fix(current_code, compiler_output, service_name)
                else:
                    if attempt < self.MAX_RETRIES:
                        print("⚠️  No LLM client available for auto-fix. Skipping retries.")
                        break
                    else:
                        print(f"❌ Build failed after {self.MAX_RETRIES} attempts.")
            
            return BuildResult(
                success=False,
                total_iterations=len(iterations),
                final_code=current_code,
                iterations=iterations
            )
        finally:
            # Cleanup workspace (keep on failure for debugging)
            pass
    
    def _compile(self, source_path: Path, service_name: str) -> tuple:
        """
        Compile C++ source file.
        
        Args:
            source_path: Path to .cpp file
            service_name: Service name for output binary
            
        Returns:
            Tuple of (success: bool, compiler_output: str)
        """
        output_path = self._workspace / service_name
        
        if self.use_docker and self._docker_available():
            return self._compile_docker(source_path, output_path)
        else:
            return self._compile_local(source_path, output_path)
    
    def _compile_local(self, source_path: Path, output_path: Path) -> tuple:
        """Compile using local g++ compiler."""
        cmd = [
            "g++",
            "-std=c++14",
            "-Wall", "-Wextra", "-Werror",
            "-o", str(output_path),
            str(source_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            compiler_output = result.stderr if result.stderr else result.stdout
            success = result.returncode == 0
            
            return success, compiler_output
            
        except FileNotFoundError:
            return False, "ERROR: g++ compiler not found. Install g++ to enable compilation."
        except subprocess.TimeoutExpired:
            return False, "ERROR: Compilation timed out after 30 seconds."
        except Exception as e:
            return False, f"ERROR: Compilation failed: {e}"
    
    def _compile_docker(self, source_path: Path, output_path: Path) -> tuple:
        """Compile inside Docker container."""
        workspace_dir = str(source_path.parent)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{workspace_dir}:/workspace",
            "autoforge-builder",
            "g++", "-std=c++14", "-Wall", "-Wextra", "-Werror",
            "-o", f"/workspace/{output_path.name}",
            f"/workspace/{source_path.name}"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            compiler_output = result.stderr if result.stderr else result.stdout
            success = result.returncode == 0
            
            return success, compiler_output
            
        except Exception as e:
            return False, f"ERROR: Docker compilation failed: {e}"
    
    def _docker_available(self) -> bool:
        """Check if Docker is available and the builder image exists."""
        try:
            result = subprocess.run(
                ["docker", "images", "-q", "autoforge-builder"],
                capture_output=True, text=True, timeout=5
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def _count_errors(self, compiler_output: str) -> int:
        """Count the number of error lines in compiler output."""
        error_pattern = re.compile(r'error:', re.IGNORECASE)
        return len(error_pattern.findall(compiler_output))
    
    def _auto_fix(self, code: str, compiler_errors: str, service_name: str) -> str:
        """
        Use LLM to automatically fix compilation errors.
        
        Args:
            code: Current C++ code with errors
            compiler_errors: Compiler error output
            service_name: Service name for context
            
        Returns:
            Fixed C++ code
        """
        fix_prompt = f"""You are an expert C++ developer specializing in automotive/embedded systems.
The following C++ code failed to compile. Fix ALL compiler errors while maintaining the 
original functionality. Follow MISRA-C++ guidelines.

## Compiler Errors:
```
{compiler_errors}
```

## Current Code:
```cpp
{code}
```

## Instructions:
1. Fix ALL compiler errors shown above
2. Do NOT change the overall logic or architecture
3. Ensure the code follows MISRA-C++ best practices
4. Return ONLY the complete fixed C++ code, no explanations
5. Include all necessary #include directives
6. Ensure proper main() function exists for compilation

Return the complete fixed code wrapped in ```cpp ... ``` markers.
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": fix_prompt}],
                max_tokens=self.max_tokens
            )
            
            fixed_response = response.choices[0].message.content
            
            # Extract code from response
            code_blocks = re.findall(r'```(?:cpp|c\+\+)?\s*\n(.*?)```', 
                                     fixed_response, re.DOTALL)
            
            if code_blocks:
                fixed_code = '\n\n'.join(block.strip() for block in code_blocks)
                print(f"   ✅ Auto-fix generated ({len(fixed_code)} chars)")
                return fixed_code
            
            # Fallback: return the raw response
            return fixed_response.strip()
            
        except Exception as e:
            print(f"   ❌ Auto-fix failed: {e}")
            return code  # Return original code on failure

    def cleanup(self):
        """Remove temporary workspace."""
        if self._workspace and self._workspace.exists():
            shutil.rmtree(self._workspace, ignore_errors=True)
