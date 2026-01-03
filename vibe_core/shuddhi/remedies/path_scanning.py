"""
OPUS-307: PathScanningDiscoveryRemedy - Transforms TAMAS path scanning to SATTVA.

Path scanning (glob, scandir, listdir) is TAMAS - blind filesystem scanning.
ManifestRegistry-driven discovery is SATTVA - knowing what's installed.

Detection: StandardsInspectionTool (path_scanning_discovery)
"""

from typing import List, Set, Union

import libcst as cst

from vibe_core.shuddhi.remedies.base import CSTRemedy


class PathScanningDiscoveryRemedy(CSTRemedy):
    """
    Transforms path scanning antipatterns to manifest-driven discovery.

    Detects:
    - glob() calls for file discovery
    - os.scandir() / os.listdir()
    - pathlib.Path().glob()

    Adds TODO markers for manual migration to ManifestRegistry.
    """

    # Methods that indicate path scanning
    SCANNING_METHODS: Set[str] = {
        "glob",
        "rglob",
        "scandir",
        "listdir",
        "walk",
    }

    # Files where path scanning IS allowed
    ALLOWED_FILES: Set[str] = {
        "manifest_registry.py",
        "base_loader.py",
        "container_loader.py",
    }

    @property
    def rule_id(self) -> str:
        return "path_scanning_discovery"

    def requirements(self) -> List[str]:
        return ["vibe_core.loaders.manifest_registry"]

    def __init__(self, file_path: str | None = None):
        super().__init__()
        self._file_path = file_path

    def _is_allowed_file(self) -> bool:
        """Check if current file is in allowed list."""
        if not self._file_path:
            return False
        for allowed in self.ALLOWED_FILES:
            if self._file_path.endswith(allowed):
                return True
        return False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> Union[cst.Call, cst.BaseExpression]:
        """Detect path scanning calls."""
        if self._is_allowed_file():
            return updated_node

        if not self._is_scanning_call(updated_node):
            return updated_node

        self.violation_found = True
        self.applied = True
        return updated_node

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        """Add TODO comment above lines containing path scanning."""
        if not self.violation_found:
            return updated_node

        # Check if this line contains scanning call
        has_scanning = False
        try:
            code_str = str(updated_node)
            for method in self.SCANNING_METHODS:
                if f".{method}(" in code_str or f"{method}(" in code_str:
                    has_scanning = True
                    break
        except Exception:
            pass

        if not has_scanning:
            return updated_node

        # Add TODO comment
        todo_comment = cst.EmptyLine(
            comment=cst.Comment("# TODO(SHUDDHI): Replace path scanning with ManifestRegistry.get_by_type()")
        )

        new_leading = list(updated_node.leading_lines) + [todo_comment]
        return updated_node.with_changes(leading_lines=new_leading)

    def _is_scanning_call(self, node: cst.Call) -> bool:
        """Check if node is a path scanning call."""
        # Check for .glob(), .scandir(), etc.
        if isinstance(node.func, cst.Attribute):
            if isinstance(node.func.attr, cst.Name):
                if node.func.attr.value in self.SCANNING_METHODS:
                    return True

        # Check for os.scandir(), os.listdir(), etc.
        if isinstance(node.func, cst.Attribute):
            if isinstance(node.func.value, cst.Name):
                if node.func.value.value == "os":
                    if isinstance(node.func.attr, cst.Name):
                        if node.func.attr.value in {"scandir", "listdir", "walk"}:
                            return True

        return False
