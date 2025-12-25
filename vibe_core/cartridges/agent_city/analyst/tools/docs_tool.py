"""
Documentation Analysis Tool - Doc coverage and quality analysis.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Documentation coverage (docstrings, README)
- Doc quality indicators
- API documentation status
- Missing documentation detection
"""

import ast
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("ANALYST_DOCS_TOOL")


class DocsAnalysisTool(Tool):
    """
    Tool for analyzing documentation coverage and quality.

    This provides DOCUMENTATION dimension - how well is code documented.
    Reveals gaps and quality issues in documentation.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, root_dir: str = "."):
        """
        Initialize docs analysis tool.

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
        return "analyst.docs"

    @property
    def description(self) -> str:
        return "Analyze documentation coverage, docstrings, and documentation quality"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Analysis action: 'coverage', 'quality', 'structure', 'full'",
            },
            "target_dirs": {
                "type": "array",
                "required": False,
                "description": "Directories to analyze (default: ['steward', 'vibe_core', 'agent_city'])",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["coverage", "quality", "structure", "full"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute docs analysis."""
        try:
            action = parameters["action"]
            target_dirs = parameters.get("target_dirs", ["steward", "vibe_core", "agent_city"])

            if action == "coverage":
                result = self._analyze_coverage(target_dirs)
            elif action == "quality":
                result = self._analyze_quality(target_dirs)
            elif action == "structure":
                result = self._analyze_structure()
            elif action == "full":
                result = {
                    "coverage": self._analyze_coverage(target_dirs),
                    "quality": self._analyze_quality(target_dirs),
                    "structure": self._analyze_structure(),
                    "metadata": {
                        "target_dirs": target_dirs,
                        "root_dir": str(self.root_dir),
                    },
                }
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"analyst.docs: {action} analysis complete")

            return ToolResult(
                success=True,
                output=result,
                metadata={"action": action},
            )

        except Exception as e:
            error_msg = f"Docs analysis failed: {type(e).__name__}: {e!s}"
            logger.error(f"DocsAnalysisTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _analyze_coverage(self, target_dirs: list[str]) -> dict[str, Any]:
        """Analyze docstring coverage in Python files."""
        total_classes = 0
        total_functions = 0
        documented_classes = 0
        documented_functions = 0
        undocumented = []

        for dir_name in target_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    rel_path = str(py_file.relative_to(self.root_dir))

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            total_classes += 1
                            if ast.get_docstring(node):
                                documented_classes += 1
                            else:
                                undocumented.append({"type": "class", "name": node.name, "file": rel_path})

                        elif isinstance(node, ast.FunctionDef):
                            # Skip private/magic methods for coverage
                            if not node.name.startswith("_"):
                                total_functions += 1
                                if ast.get_docstring(node):
                                    documented_functions += 1
                                else:
                                    undocumented.append({"type": "function", "name": node.name, "file": rel_path})

                except (SyntaxError, Exception):
                    pass

        # Calculate coverage
        class_coverage = round(documented_classes / total_classes * 100, 1) if total_classes > 0 else 0
        func_coverage = round(documented_functions / total_functions * 100, 1) if total_functions > 0 else 0
        overall = (
            round((documented_classes + documented_functions) / (total_classes + total_functions) * 100, 1)
            if (total_classes + total_functions) > 0
            else 0
        )

        # Coverage level
        if overall >= 80:
            level = "EXCELLENT"
        elif overall >= 60:
            level = "GOOD"
        elif overall >= 40:
            level = "FAIR"
        else:
            level = "POOR"

        return {
            "class_coverage": f"{class_coverage}%",
            "function_coverage": f"{func_coverage}%",
            "overall_coverage": f"{overall}%",
            "coverage_level": level,
            "total_classes": total_classes,
            "documented_classes": documented_classes,
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "undocumented_items": undocumented[:20],  # Limit
        }

    def _analyze_quality(self, target_dirs: list[str]) -> dict[str, Any]:
        """Analyze documentation quality indicators."""
        quality_issues = []
        good_examples = []

        for dir_name in target_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    rel_path = str(py_file.relative_to(self.root_dir))

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                # Quality checks
                                lines = docstring.split("\n")
                                word_count = len(docstring.split())

                                # Too short?
                                if word_count < 5:
                                    quality_issues.append(
                                        {
                                            "issue": "too_short",
                                            "name": node.name,
                                            "file": rel_path,
                                            "words": word_count,
                                        }
                                    )

                                # Has Args/Returns sections? (good pattern)
                                has_args = "Args:" in docstring or "Parameters:" in docstring
                                has_returns = "Returns:" in docstring or "Return:" in docstring

                                if isinstance(node, ast.FunctionDef):
                                    # Functions should document args/returns
                                    if len(lines) > 3 and has_args and has_returns:
                                        if len(good_examples) < 5:
                                            good_examples.append(
                                                {
                                                    "name": node.name,
                                                    "file": rel_path,
                                                    "reason": "Complete Args/Returns",
                                                }
                                            )

                except (SyntaxError, Exception):
                    pass

        return {
            "quality_issues": quality_issues[:15],
            "good_examples": good_examples,
            "total_issues": len(quality_issues),
        }

    def _analyze_structure(self) -> dict[str, Any]:
        """Analyze documentation file structure."""
        doc_files = []

        # Find markdown files
        for md_file in self.root_dir.rglob("*.md"):
            try:
                # Skip hidden directories
                if any(part.startswith(".") for part in md_file.parts):
                    continue

                content = md_file.read_text()
                rel_path = str(md_file.relative_to(self.root_dir))

                # Analyze structure
                lines = content.split("\n")
                headers = [line for line in lines if line.startswith("#")]
                links = len(re.findall(r"\[.+?\]\(.+?\)", content))
                code_blocks = len(re.findall(r"```", content)) // 2

                doc_files.append(
                    {
                        "file": rel_path,
                        "lines": len(lines),
                        "headers": len(headers),
                        "links": links,
                        "code_blocks": code_blocks,
                    }
                )

            except Exception:
                pass

        # Sort by size
        doc_files.sort(key=lambda x: -x["lines"])

        # Check for key docs
        key_docs = {
            "README.md": (self.root_dir / "README.md").exists(),
            "CONTRIBUTING.md": (self.root_dir / "CONTRIBUTING.md").exists(),
            "CHANGELOG.md": (self.root_dir / "CHANGELOG.md").exists(),
            "docs/": (self.root_dir / "docs").is_dir() if (self.root_dir / "docs").exists() else False,
        }

        return {
            "doc_files": doc_files[:20],
            "total_doc_files": len(doc_files),
            "key_docs_present": key_docs,
            "total_lines": sum(d["lines"] for d in doc_files),
        }
