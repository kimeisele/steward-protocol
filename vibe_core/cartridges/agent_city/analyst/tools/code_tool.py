"""
Code Analysis Tool - AST, complexity, and pattern analysis.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Code complexity metrics (classes, functions, nesting)
- Technical debt indicators (TODO, FIXME, HACK)
- Pattern detection (common anti-patterns)
- File-level analysis
"""

import ast
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("ANALYST_CODE_TOOL")


class CodeAnalysisTool(Tool):
    """
    Tool for analyzing code complexity and patterns.

    This provides SEMANTIC dimension - understanding code meaning.
    Not just commit messages, but actual CODE analysis.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, root_dir: str = "."):
        """
        Initialize code analysis tool.

        Args:
            services: Service registry for DI
            root_dir: Repository root directory
        """
        super().__init__(services)
        self.root_dir = Path(root_dir).resolve()
        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel = None

    def inject_kernel(self, kernel) -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        OPUS-070: Analyst tools MUST have kernel access for full context.
        Without kernel injection, they operate in "file-only mode" (limited).
        """
        self._vibe_kernel = kernel
        logger.info(f"⚡ {self.name}: Kernel injected - ledger binding ACTIVE")

    def _get_ledger(self):
        """Get kernel.ledger via VAJRA binding."""
        if self._vibe_kernel is None:
            return None
        if not hasattr(self._vibe_kernel, "ledger"):
            return None
        return self._vibe_kernel.ledger

    @property
    def name(self) -> str:
        return "analyst.code"

    @property
    def description(self) -> str:
        return "Analyze code complexity, technical debt, and patterns in Python files"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Analysis action: 'complexity', 'debt', 'patterns', 'full'",
            },
            "target_dirs": {
                "type": "array",
                "required": False,
                "description": "Directories to analyze (default: ['steward', 'vibe_core', 'agent_city'])",
            },
            "file_path": {
                "type": "string",
                "required": False,
                "description": "Specific file to analyze (for detailed analysis)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["complexity", "debt", "patterns", "full"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute code analysis."""
        try:
            action = parameters["action"]
            target_dirs = parameters.get("target_dirs", ["steward", "vibe_core", "agent_city"])
            # file_path parameter reserved for future single-file detailed analysis

            if action == "complexity":
                result = self._analyze_complexity(target_dirs)
            elif action == "debt":
                result = self._analyze_debt(target_dirs)
            elif action == "patterns":
                result = self._analyze_patterns(target_dirs)
            elif action == "full":
                result = {
                    "complexity": self._analyze_complexity(target_dirs),
                    "debt": self._analyze_debt(target_dirs),
                    "patterns": self._analyze_patterns(target_dirs),
                    "metadata": {
                        "analyzed_dirs": target_dirs,
                        "root_dir": str(self.root_dir),
                    },
                }
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"analyst.code: {action} analysis complete")

            return ToolResult(
                success=True,
                output=result,
                metadata={"action": action, "target_dirs": target_dirs},
            )

        except Exception as e:
            error_msg = f"Code analysis failed: {type(e).__name__}: {e!s}"
            logger.error(f"CodeAnalysisTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _get_python_files(self, target_dirs: list[str]) -> list[Path]:
        """Get all Python files in target directories."""
        files = []
        for dir_name in target_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                files.extend(dir_path.rglob("*.py"))
        return files

    def _analyze_complexity(self, target_dirs: list[str]) -> dict[str, Any]:
        """Analyze code complexity across files."""
        files = self._get_python_files(target_dirs)
        file_complexities = []
        total_classes = 0
        total_functions = 0
        total_lines = 0

        for py_file in files:
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                line_count = len(lines)
                total_lines += line_count

                # AST analysis for accurate counts
                try:
                    tree = ast.parse(content)
                    class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                    function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

                    # Nesting depth (approximation)
                    nested_ifs = len(re.findall(r"^\s{8,}if\s+", content, re.MULTILINE))
                    nested_loops = len(re.findall(r"^\s{8,}(for|while)\s+", content, re.MULTILINE))

                    total_classes += class_count
                    total_functions += function_count

                    # Complexity score
                    complexity = line_count // 50 + class_count * 3 + function_count + (nested_ifs + nested_loops) * 2

                    if complexity > 15:  # Only track complex files
                        rel_path = str(py_file.relative_to(self.root_dir))
                        file_complexities.append(
                            {
                                "file": rel_path,
                                "complexity": complexity,
                                "lines": line_count,
                                "classes": class_count,
                                "functions": function_count,
                                "nested_control": nested_ifs + nested_loops,
                            }
                        )

                except SyntaxError:
                    # Skip files with syntax errors
                    pass

            except Exception:
                pass

        # Sort by complexity
        file_complexities.sort(key=lambda x: -x["complexity"])

        return {
            "complex_files": file_complexities[:20],
            "total_files_analyzed": len(files),
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "average_lines_per_file": round(total_lines / len(files), 1) if files else 0,
        }

    def _analyze_debt(self, target_dirs: list[str]) -> dict[str, Any]:
        """Scan for technical debt indicators."""
        files = self._get_python_files(target_dirs)

        debt_patterns = [
            (r"\bTODO\b", "todo"),
            (r"\bFIXME\b", "fixme"),
            (r"\bHACK\b", "hack"),
            (r"\bXXX\b", "xxx"),
            (r"\bTEMP\b", "temp"),
            (r"\bDEPRECATED\b", "deprecated"),
            (r"\bBUG\b", "bug"),
            (r"\bWORKAROUND\b", "workaround"),
        ]

        debt_counts: dict[str, int] = {}
        debt_locations: dict[str, list[dict]] = {}

        for pattern, debt_type in debt_patterns:
            debt_counts[debt_type] = 0
            debt_locations[debt_type] = []

        for py_file in files:
            try:
                content = py_file.read_text()
                rel_path = str(py_file.relative_to(self.root_dir))

                for line_num, line in enumerate(content.split("\n"), 1):
                    for pattern, debt_type in debt_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            debt_counts[debt_type] += 1
                            if len(debt_locations[debt_type]) < 5:  # Limit examples
                                debt_locations[debt_type].append(
                                    {
                                        "file": rel_path,
                                        "line": line_num,
                                        "text": line.strip()[:80],
                                    }
                                )

            except Exception:
                pass

        total_debt = sum(debt_counts.values())

        # Calculate debt score (weighted)
        debt_score = (
            debt_counts.get("fixme", 0) * 3
            + debt_counts.get("hack", 0) * 5
            + debt_counts.get("todo", 0) * 1
            + debt_counts.get("deprecated", 0) * 2
            + debt_counts.get("bug", 0) * 4
            + debt_counts.get("workaround", 0) * 3
        )

        if debt_score < 10:
            debt_level = "LOW"
        elif debt_score < 50:
            debt_level = "MODERATE"
        elif debt_score < 100:
            debt_level = "HIGH"
        else:
            debt_level = "CRITICAL"

        return {
            "counts": debt_counts,
            "total_markers": total_debt,
            "debt_score": debt_score,
            "debt_level": debt_level,
            "locations": {k: v for k, v in debt_locations.items() if v},
        }

    def _analyze_patterns(self, target_dirs: list[str]) -> dict[str, Any]:
        """Detect code patterns and anti-patterns."""
        files = self._get_python_files(target_dirs)

        patterns_found = {
            "broad_exceptions": [],  # except Exception, except:
            "magic_numbers": [],  # hardcoded numeric literals
            "long_functions": [],  # functions > 50 lines
            "deep_nesting": [],  # > 4 levels of nesting
            "god_classes": [],  # classes with > 20 methods
        }

        for py_file in files:
            try:
                content = py_file.read_text()
                rel_path = str(py_file.relative_to(self.root_dir))

                # Broad exceptions
                broad_except = re.findall(r"except\s*(Exception|:)", content)
                if len(broad_except) > 3:
                    patterns_found["broad_exceptions"].append({"file": rel_path, "count": len(broad_except)})

                # AST-based analysis
                try:
                    tree = ast.parse(content)

                    # Long functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if hasattr(node, "end_lineno") and node.end_lineno:
                                func_length = node.end_lineno - node.lineno
                                if func_length > 50:
                                    patterns_found["long_functions"].append(
                                        {
                                            "file": rel_path,
                                            "function": node.name,
                                            "lines": func_length,
                                        }
                                    )

                        # God classes
                        if isinstance(node, ast.ClassDef):
                            methods = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                            if methods > 20:
                                patterns_found["god_classes"].append(
                                    {"file": rel_path, "class": node.name, "methods": methods}
                                )

                except SyntaxError:
                    pass

            except Exception:
                pass

        # Limit results
        for key in patterns_found:
            patterns_found[key] = patterns_found[key][:10]

        return {
            "anti_patterns": patterns_found,
            "files_analyzed": len(files),
        }
