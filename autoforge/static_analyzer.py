"""
Static Analysis Module for AutoForge.

Runs cppcheck (with optional MISRA addon) on generated C++ code and
returns structured violation reports.
"""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Violation:
    """A single static analysis violation."""
    rule_id: str
    severity: str  # error, warning, style, performance, portability
    message: str
    line: int
    column: int = 0
    file: str = ""


@dataclass 
class AnalysisResult:
    """Result of static analysis."""
    success: bool
    total_violations: int
    errors: int
    warnings: int
    style_issues: int
    performance_issues: int
    violations: List[Violation]
    raw_output: str
    misra_violations: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StaticAnalyzer:
    """
    Static analysis engine using cppcheck for MISRA-C++ compliance checking.
    """
    
    def __init__(self, use_docker: bool = False):
        """
        Initialize the static analyzer.
        
        Args:
            use_docker: Whether to run cppcheck inside Docker
        """
        self.use_docker = use_docker
    
    def analyze(self, code: str, service_name: str = "service") -> AnalysisResult:
        """
        Run static analysis on C++ code.
        
        Args:
            code: C++ source code to analyze
            service_name: Service name (used for temp file naming)
            
        Returns:
            AnalysisResult with violation details
        """
        # Write code to a temp file
        tmp_dir = Path(tempfile.mkdtemp(prefix="autoforge_analysis_"))
        source_path = tmp_dir / f"{service_name}.cpp"
        source_path.write_text(code, encoding='utf-8')
        
        try:
            # Run cppcheck
            raw_output = self._run_cppcheck(source_path)
            
            # Parse violations from output
            violations = self._parse_output(raw_output, source_path.name)
            
            # Categorize violations
            errors = sum(1 for v in violations if v.severity == "error")
            warnings = sum(1 for v in violations if v.severity == "warning")
            style_issues = sum(1 for v in violations if v.severity == "style")
            performance_issues = sum(1 for v in violations if v.severity == "performance")
            misra_count = sum(1 for v in violations if "misra" in v.rule_id.lower())
            
            return AnalysisResult(
                success=errors == 0,
                total_violations=len(violations),
                errors=errors,
                warnings=warnings,
                style_issues=style_issues,
                performance_issues=performance_issues,
                violations=violations,
                raw_output=raw_output,
                misra_violations=misra_count
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                total_violations=0,
                errors=0,
                warnings=0,
                style_issues=0,
                performance_issues=0,
                violations=[],
                raw_output=f"Analysis failed: {e}"
            )
    
    def _run_cppcheck(self, source_path: Path) -> str:
        """
        Execute cppcheck on a source file.
        
        Args:
            source_path: Path to .cpp file
            
        Returns:
            Raw cppcheck output string
        """
        cmd = [
            "cppcheck",
            "--enable=all",
            "--std=c++14",
            "--language=c++",
            "--suppress=missingIncludeSystem",
            "--template={file}:{line}:{column}: {severity}: {message} [{id}]",
            str(source_path)
        ]
        
        if self.use_docker and self._docker_available():
            workspace_dir = str(source_path.parent)
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{workspace_dir}:/workspace",
                "autoforge-builder",
            ] + [
                "cppcheck",
                "--enable=all",
                "--std=c++14",
                "--language=c++",
                "--suppress=missingIncludeSystem",
                f"--template={{file}}:{{line}}:{{column}}: {{severity}}: {{message}} [{{id}}]",
                f"/workspace/{source_path.name}"
            ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # cppcheck outputs findings to stderr
            output = result.stderr if result.stderr else result.stdout
            return output
            
        except FileNotFoundError:
            return "cppcheck not installed. Install with: sudo apt-get install cppcheck"
        except subprocess.TimeoutExpired:
            return "Analysis timed out after 30 seconds."
        except Exception as e:
            return f"Analysis error: {e}"
    
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
    
    def _parse_output(self, raw_output: str, filename: str) -> List[Violation]:
        """
        Parse cppcheck output into structured Violation objects.
        
        Args:
            raw_output: Raw cppcheck output
            filename: Source filename for filtering
            
        Returns:
            List of Violation objects
        """
        violations = []
        
        # Pattern: file:line:column: severity: message [id]
        pattern = re.compile(
            r'(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s*'
            r'(?P<severity>\w+):\s*(?P<message>.+?)\s*\[(?P<id>[^\]]+)\]'
        )
        
        for line in raw_output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            match = pattern.match(line)
            if match:
                violations.append(Violation(
                    rule_id=match.group('id'),
                    severity=match.group('severity'),
                    message=match.group('message'),
                    line=int(match.group('line')),
                    column=int(match.group('col')),
                    file=match.group('file')
                ))
        
        return violations
    
    def format_report(self, result: AnalysisResult) -> str:
        """
        Format analysis result as a human-readable report.
        
        Args:
            result: AnalysisResult to format
            
        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "📋 Static Analysis Report (cppcheck)",
            "=" * 60,
            f"Status: {'✅ PASS' if result.success else '❌ FAIL'}",
            f"Total Violations: {result.total_violations}",
            f"  Errors:       {result.errors}",
            f"  Warnings:     {result.warnings}",
            f"  Style:        {result.style_issues}",
            f"  Performance:  {result.performance_issues}",
            f"  MISRA:        {result.misra_violations}",
            ""
        ]
        
        if result.violations:
            lines.append("Violations:")
            lines.append("-" * 60)
            for v in result.violations:
                lines.append(
                    f"  Line {v.line}: [{v.severity.upper()}] {v.message} ({v.rule_id})"
                )
        
        lines.append("=" * 60)
        return '\n'.join(lines)
