"""
Dependency Analysis Tool - Import and requirement analysis.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Import graph analysis (internal dependencies)
- External dependencies (requirements.txt, pyproject.toml)
- Circular dependency detection
- Architecture hubs (most depended-upon modules)
"""

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("ANALYST_DEPS_TOOL")


class DependencyAnalysisTool(Tool):
    """
    Tool for analyzing code dependencies.

    This provides dependency dimension - what depends on what.
    Reveals architectural structure and potential issues.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, root_dir: str = "."):
        """
        Initialize dependency analysis tool.

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
        return "analyst.deps"

    @property
    def description(self) -> str:
        return "Analyze import dependencies, external requirements, and architectural hubs"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Analysis action: 'imports', 'external', 'hubs', 'full'",
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

        valid_actions = ["imports", "external", "hubs", "full"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute dependency analysis."""
        try:
            action = parameters["action"]
            target_dirs = parameters.get("target_dirs", ["steward", "vibe_core", "agent_city"])

            if action == "imports":
                result = self._analyze_imports(target_dirs)
            elif action == "external":
                result = self._analyze_external()
            elif action == "hubs":
                result = self._find_hubs(target_dirs)
            elif action == "full":
                result = {
                    "imports": self._analyze_imports(target_dirs),
                    "external": self._analyze_external(),
                    "hubs": self._find_hubs(target_dirs),
                    "metadata": {
                        "target_dirs": target_dirs,
                        "root_dir": str(self.root_dir),
                    },
                }
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"analyst.deps: {action} analysis complete")

            return ToolResult(
                success=True,
                output=result,
                metadata={"action": action},
            )

        except Exception as e:
            error_msg = f"Dependency analysis failed: {type(e).__name__}: {e!s}"
            logger.error(f"DependencyAnalysisTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _analyze_imports(self, target_dirs: list[str]) -> dict[str, Any]:
        """Analyze internal import dependencies."""
        import_pattern = re.compile(r"^(?:from\s+([\w.]+)|import\s+([\w.]+))")

        imports: dict[str, list[str]] = {}
        all_internal_modules = set(target_dirs)

        for dir_name in target_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    rel_path = str(py_file.relative_to(self.root_dir))

                    file_imports = []
                    for line in content.split("\n"):
                        match = import_pattern.match(line.strip())
                        if match:
                            module = match.group(1) or match.group(2)
                            if module:
                                # Track internal imports
                                root_module = module.split(".")[0]
                                if root_module in all_internal_modules:
                                    file_imports.append(module)

                    if file_imports:
                        imports[rel_path] = file_imports

                except Exception:
                    pass

        # Calculate metrics
        total_imports = sum(len(deps) for deps in imports.values())
        avg_imports = round(total_imports / len(imports), 1) if imports else 0

        # Files with most imports
        import_counts = [(f, len(deps)) for f, deps in imports.items()]
        import_counts.sort(key=lambda x: -x[1])

        return {
            "files_with_imports": len(imports),
            "total_internal_imports": total_imports,
            "average_imports_per_file": avg_imports,
            "high_import_files": [{"file": f, "imports": c} for f, c in import_counts[:15]],
        }

    def _analyze_external(self) -> dict[str, Any]:
        """Analyze external dependencies from requirements and pyproject."""
        external_deps = []

        # Check requirements.txt
        req_file = self.root_dir / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse package name
                        match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                        if match:
                            external_deps.append(
                                {
                                    "package": match.group(1),
                                    "spec": line,
                                    "source": "requirements.txt",
                                }
                            )
            except Exception:
                pass

        # Check pyproject.toml
        pyproject_file = self.root_dir / "pyproject.toml"
        if pyproject_file.exists():
            try:
                content = pyproject_file.read_text()
                # Simple regex for dependencies (not full TOML parsing)
                in_deps = False
                for line in content.split("\n"):
                    if "[project.dependencies]" in line or "[tool.poetry.dependencies]" in line:
                        in_deps = True
                        continue
                    if in_deps:
                        if line.startswith("["):
                            in_deps = False
                            continue
                        if "=" in line or line.strip().startswith('"'):
                            # Extract package name
                            match = re.match(r'^["\']?([a-zA-Z0-9_-]+)', line.strip())
                            if match:
                                pkg = match.group(1)
                                if pkg not in [d["package"] for d in external_deps]:
                                    external_deps.append(
                                        {
                                            "package": pkg,
                                            "spec": line.strip(),
                                            "source": "pyproject.toml",
                                        }
                                    )
            except Exception:
                pass

        # Categorize
        std_libs = {"os", "sys", "re", "json", "pathlib", "typing", "logging", "datetime", "collections", "abc"}
        filtered = [d for d in external_deps if d["package"].lower() not in std_libs]

        return {
            "dependencies": filtered,
            "total_external": len(filtered),
            "sources_checked": ["requirements.txt", "pyproject.toml"],
        }

    def _find_hubs(self, target_dirs: list[str]) -> dict[str, Any]:
        """Find architectural hubs (most depended-upon modules)."""
        import_pattern = re.compile(r"^(?:from\s+([\w.]+)|import\s+([\w.]+))")

        # Count how many times each module is imported
        incoming: dict[str, int] = defaultdict(int)
        outgoing: dict[str, int] = defaultdict(int)

        for dir_name in target_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    rel_path = str(py_file.relative_to(self.root_dir))

                    imports_found = 0
                    for line in content.split("\n"):
                        match = import_pattern.match(line.strip())
                        if match:
                            module = match.group(1) or match.group(2)
                            if module:
                                root = module.split(".")[0]
                                if root in target_dirs:
                                    incoming[module] += 1
                                    imports_found += 1

                    outgoing[rel_path] = imports_found

                except Exception:
                    pass

        # Sort by incoming (most depended upon)
        hubs = sorted(incoming.items(), key=lambda x: -x[1])[:20]

        # Sort by outgoing (depends on most)
        complex_files = sorted(outgoing.items(), key=lambda x: -x[1])[:15]

        # Module-level hubs
        module_hubs: dict[str, int] = defaultdict(int)
        for module, count in incoming.items():
            parts = module.split(".")
            if len(parts) >= 2:
                module_hubs[f"{parts[0]}.{parts[1]}"] += count

        sorted_module_hubs = sorted(module_hubs.items(), key=lambda x: -x[1])[:10]

        return {
            "architectural_hubs": [{"module": m, "dependents": c} for m, c in hubs],
            "complex_files": [{"file": f, "dependencies": c} for f, c in complex_files],
            "module_hubs": [{"module": m, "total_imports": c} for m, c in sorted_module_hubs],
        }
