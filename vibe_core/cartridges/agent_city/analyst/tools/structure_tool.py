"""
Structure Analysis Tool - Project architecture analysis.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Module boundaries and organization
- File co-change patterns (coupling)
- Package structure analysis
- Entry points and main modules
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xc61b1be2"  # GenesisByte: parampara % 37 == 0

import logging
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("ANALYST_STRUCTURE_TOOL")


class StructureAnalysisTool(Tool):
    """
    Tool for analyzing project structure and architecture.

    This provides STRUCTURAL dimension - how code is organized.
    Reveals hidden coupling and architectural patterns.
    """

    def __init__(self, root_dir: str = "."):
        """
        Initialize structure analysis tool.

        Args:
            root_dir: Repository root directory
        """
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
        return "analyst.structure"

    @property
    def description(self) -> str:
        return "Analyze project structure, module boundaries, and file coupling patterns"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Analysis action: 'modules', 'coupling', 'hotspots', 'full'",
            },
            "days": {
                "type": "integer",
                "required": False,
                "description": "Days of history for coupling analysis (default: 30)",
            },
            "min_correlation": {
                "type": "integer",
                "required": False,
                "description": "Minimum co-changes for coupling (default: 3)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["modules", "coupling", "hotspots", "full"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute structure analysis."""
        try:
            action = parameters["action"]
            days = parameters.get("days", 30)
            min_correlation = parameters.get("min_correlation", 3)

            if action == "modules":
                result = self._analyze_modules()
            elif action == "coupling":
                result = self._analyze_coupling(days, min_correlation)
            elif action == "hotspots":
                result = self._find_hotspots(days)
            elif action == "full":
                result = {
                    "modules": self._analyze_modules(),
                    "coupling": self._analyze_coupling(days, min_correlation),
                    "hotspots": self._find_hotspots(days),
                    "metadata": {
                        "root_dir": str(self.root_dir),
                        "days": days,
                    },
                }
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"analyst.structure: {action} analysis complete")

            return ToolResult(
                success=True,
                output=result,
                metadata={"action": action},
            )

        except Exception as e:
            error_msg = f"Structure analysis failed: {type(e).__name__}: {e!s}"
            logger.error(f"StructureAnalysisTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _run_git(self, cmd: str) -> str:
        """Run git command."""
        result = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=str(self.root_dir),
        )
        return result.stdout.strip()

    def _analyze_modules(self) -> dict[str, Any]:
        """Analyze module structure and boundaries."""
        modules = []

        for item in self.root_dir.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                is_package = (item / "__init__.py").exists()
                has_pyproject = (item / "pyproject.toml").exists()

                if is_package or has_pyproject:
                    py_files = list(item.rglob("*.py"))
                    yaml_files = list(item.rglob("*.yaml")) + list(item.rglob("*.yml"))
                    md_files = list(item.rglob("*.md"))

                    # Calculate size
                    total_lines = 0
                    for f in py_files:
                        try:
                            total_lines += len(f.read_text().split("\n"))
                        except Exception as _exc:
                            logger.exception("Unexpected error: %s", _exc)

                    # Submodules
                    submodules = [
                        d.name
                        for d in item.iterdir()
                        if d.is_dir() and (d / "__init__.py").exists() and not d.name.startswith("_")
                    ]

                    modules.append(
                        {
                            "name": item.name,
                            "is_package": is_package,
                            "python_files": len(py_files),
                            "yaml_files": len(yaml_files),
                            "doc_files": len(md_files),
                            "total_lines": total_lines,
                            "submodules": submodules,
                        }
                    )

        # Sort by size
        modules.sort(key=lambda x: -x["total_lines"])

        # Find entry points
        entry_points = []
        for pattern in ["main.py", "cli.py", "__main__.py", "app.py"]:
            for f in self.root_dir.rglob(pattern):
                entry_points.append(str(f.relative_to(self.root_dir)))

        return {
            "modules": modules,
            "total_modules": len(modules),
            "entry_points": entry_points[:10],
            "largest_module": modules[0]["name"] if modules else None,
        }

    def _analyze_coupling(self, days: int = 30, min_correlation: int = 3) -> dict[str, Any]:
        """Analyze file co-change patterns to find coupling."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get commits with files
        output = self._run_git(f"log --pretty=format:COMMIT --name-only --since={since}")

        commits: list[set[str]] = []
        current_files: set[str] = set()

        for line in output.split("\n"):
            if line == "COMMIT":
                if current_files:
                    commits.append(current_files)
                current_files = set()
            elif line.strip() and not line.startswith("."):
                current_files.add(line.strip())

        if current_files:
            commits.append(current_files)

        # Find co-occurrences
        co_changes: dict[tuple[str, str], int] = defaultdict(int)
        for file_set in commits:
            files = sorted(file_set)
            for i, f1 in enumerate(files):
                for f2 in files[i + 1 :]:
                    co_changes[(f1, f2)] += 1

        # Filter and sort
        significant = {k: v for k, v in co_changes.items() if v >= min_correlation}
        sorted_pairs = sorted(significant.items(), key=lambda x: -x[1])[:30]

        # Build coupling clusters
        clusters: dict[str, set[str]] = defaultdict(set)
        for (f1, f2), count in sorted_pairs:
            clusters[f1].add(f2)
            clusters[f2].add(f1)

        coupling_scores = [(f, len(related)) for f, related in clusters.items()]
        coupling_scores.sort(key=lambda x: -x[1])

        return {
            "co_change_pairs": [{"files": f"{a} <-> {b}", "count": c} for (a, b), c in sorted_pairs[:20]],
            "coupling_hotspots": [{"file": f, "coupled_files": s} for f, s in coupling_scores[:15]],
            "total_commits_analyzed": len(commits),
        }

    def _find_hotspots(self, days: int = 30) -> dict[str, Any]:
        """Find files with high change frequency."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        output = self._run_git(f"log --pretty=format: --name-only --since={since}")
        file_counts: dict[str, int] = defaultdict(int)

        for line in output.split("\n"):
            if line.strip() and not line.startswith("."):
                file_counts[line.strip()] += 1

        # Sort by frequency
        sorted_files = sorted(file_counts.items(), key=lambda x: -x[1])

        # Categorize by module
        module_activity: dict[str, int] = defaultdict(int)
        for path, count in file_counts.items():
            parts = path.split("/")
            if parts:
                module_activity[parts[0]] += count

        sorted_modules = sorted(module_activity.items(), key=lambda x: -x[1])

        return {
            "hot_files": [{"file": f, "changes": c} for f, c in sorted_files[:20]],
            "module_activity": [{"module": m, "changes": c} for m, c in sorted_modules[:10]],
            "total_changes": sum(file_counts.values()),
        }
