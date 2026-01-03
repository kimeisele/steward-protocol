"""
OPUS-307: IterdirDiscoveryRemedy - Transforms TAMAS to SATTVA.

iterdir() is TAMAS - blind filesystem scanning.
Das System RATET statt zu WISSEN.

This remedy:
1. Detects iterdir() calls used for discovery patterns
2. Adds TODO comment for manual migration to ManifestRegistry
3. Skips allowed files (ManifestRegistry itself)

Detection: StandardsInspectionTool (iterdir_discovery)
Bridge: CSTLocator
Surgery: This CSTRemedy

Note: Full auto-heal requires semantic analysis (what type is being discovered).
This remedy adds TODO markers for engineer review.
"""

from typing import List, Optional, Set, Union

import libcst as cst

from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError


class IterdirDiscoveryRemedy(CSTRemedy):
    """
    Transforms iterdir() discovery antipattern.

    iterdir() = TAMAS (blind scanning)
    ManifestRegistry = SATTVA (knowing what's installed)

    This remedy:
    - Adds a deprecation comment above iterdir() calls
    - Preserves the code for manual review (semantic understanding needed)
    - Skips allowed files where iterdir is legitimate
    """

    # Files where iterdir IS allowed (the source of truth)
    ALLOWED_FILES: Set[str] = {
        "manifest_registry.py",
        "base_loader.py",  # Uses iterdir for initial scan
    }

    @property
    def rule_id(self) -> str:
        return "iterdir_discovery"

    @property
    def requirements(self) -> List[str]:
        return ["vibe_core.loaders.manifest_registry"]

    def __init__(self, file_path: Optional[str] = None):
        super().__init__()
        self._file_path = file_path
        self._iterdir_calls_found = 0

    def _is_allowed_file(self) -> bool:
        """Check if current file is in allowed list."""
        if not self._file_path:
            return False
        for allowed in self.ALLOWED_FILES:
            if self._file_path.endswith(allowed):
                return True
        return False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> Union[cst.Call, cst.BaseExpression]:
        """Detect iterdir() calls and mark for refactoring."""
        # Skip if in allowed file
        if self._is_allowed_file():
            return updated_node

        # Check for .iterdir() pattern
        if not self._is_iterdir_call(updated_node):
            return updated_node

        self._iterdir_calls_found += 1
        self.violation_found = True
        self.applied = True

        # Return unchanged - we add comment at statement level
        return updated_node

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        """Add TODO comment above lines containing iterdir()."""
        if not self.violation_found:
            return updated_node

        # Check if this line contains our iterdir call
        has_iterdir = False
        for stmt in updated_node.body:
            if isinstance(stmt, (cst.Expr, cst.Assign, cst.AnnAssign)):
                # Check if statement contains iterdir
                code = updated_node
                try:
                    code_str = code.body[0]
                    # Quick check via string matching (CST matching is complex)
                    if "iterdir" in str(code_str):
                        has_iterdir = True
                except Exception:
                    pass

        if not has_iterdir:
            return updated_node

        # Add TODO comment as leading line
        todo_comment = cst.EmptyLine(
            comment=cst.Comment("# TODO(SHUDDHI): Replace iterdir() with ManifestRegistry.get_by_type()")
        )

        # Prepend to existing leading lines
        new_leading = list(updated_node.leading_lines) + [todo_comment]
        return updated_node.with_changes(leading_lines=new_leading)

    def _is_iterdir_call(self, node: cst.Call) -> bool:
        """Check if node is a .iterdir() call."""
        if not isinstance(node.func, cst.Attribute):
            return False

        if not isinstance(node.func.attr, cst.Name):
            return False

        return node.func.attr.value == "iterdir"


class DirectRegistryInstantiationRemedy(CSTRemedy):
    """
    Heals direct instantiation of Registry classes.

    Transforms:
    - ToolRegistry() → ServiceRegistry.get(ToolRegistryProtocol)
    - UnifiedRegistry() → ServiceRegistry.get(UnifiedRegistryProtocol)

    Detection: StandardsInspectionTool (direct_registry_instantiation)
    """

    # Known registry to protocol mappings
    KNOWN_REGISTRIES = {
        "ToolRegistry": "ToolRegistryProtocol",
        "UnifiedRegistry": "UnifiedRegistryProtocol",
        "CartridgeRegistry": "CartridgeRegistryProtocol",
        "ManifestRegistry": "ManifestRegistryProtocol",
    }

    @property
    def rule_id(self) -> str:
        return "direct_registry_instantiation"

    @property
    def requirements(self) -> List[str]:
        return ["vibe_core.di"]

    def __init__(self):
        super().__init__()
        self._needs_service_registry_import = False
        self._has_service_registry_import = False
        self._transformed_registries: Set[str] = set()

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Check if ServiceRegistry is already imported."""
        if isinstance(node.module, cst.Attribute):
            module_name = self._get_full_module_name(node.module)
            if module_name == "vibe_core.di":
                if isinstance(node.names, cst.ImportStar):
                    self._has_service_registry_import = True
                elif isinstance(node.names, tuple):
                    for name in node.names:
                        if isinstance(name, cst.ImportAlias):
                            if isinstance(name.name, cst.Name) and name.name.value == "ServiceRegistry":
                                self._has_service_registry_import = True

    def _get_full_module_name(self, node: cst.BaseExpression) -> str:
        """Extract full module name from Attribute chain."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{self._get_full_module_name(node.value)}.{node.attr.value}"
        return ""

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> Union[cst.Call, cst.BaseExpression]:
        """Transform Registry() to ServiceRegistry.get(RegistryProtocol)."""
        # Check for direct Registry() instantiation
        if not isinstance(updated_node.func, cst.Name):
            return updated_node

        class_name = updated_node.func.value
        if class_name not in self.KNOWN_REGISTRIES:
            return updated_node

        # Skip if has arguments (might be intentional construction)
        if updated_node.args:
            return updated_node

        self.violation_found = True
        self.applied = True
        self._needs_service_registry_import = True
        self._transformed_registries.add(class_name)

        # Get protocol name
        protocol_name = self.KNOWN_REGISTRIES[class_name]

        # Build ServiceRegistry.get(RegistryProtocol)
        return cst.Call(
            func=cst.Attribute(
                value=cst.Name("ServiceRegistry"),
                attr=cst.Name("get"),
            ),
            args=[
                cst.Arg(value=cst.Name(protocol_name)),
            ],
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Add ServiceRegistry import if needed."""
        if not self._needs_service_registry_import or self._has_service_registry_import:
            return updated_node

        # Build import statement
        new_import = cst.SimpleStatementLine(
            body=[
                cst.ImportFrom(
                    module=cst.Attribute(
                        value=cst.Name("vibe_core"),
                        attr=cst.Name("di"),
                    ),
                    names=[
                        cst.ImportAlias(name=cst.Name("ServiceRegistry")),
                    ],
                )
            ]
        )

        # Find insertion point (after existing imports)
        new_body = list(updated_node.body)
        insert_idx = 0

        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    insert_idx = i + 1

        new_body.insert(insert_idx, new_import)
        return updated_node.with_changes(body=new_body)
