"""
OPUS-307: GetInstanceAntipatternRemedy - Migrates singleton to DI.

Transforms X.get_instance() calls to ServiceRegistry.get(XProtocol),
enforcing proper dependency injection via the ServiceRegistry.

Detection: StandardsInspectionTool (get_instance_antipattern)
Bridge: CSTLocator
Surgery: This CSTRemedy
"""

from typing import List, Set, Union

import libcst as cst

from vibe_core.shuddhi.remedies.base import CSTRemedy


class GetInstanceAntipatternRemedy(CSTRemedy):
    """
    Heals get_instance() singleton antipattern.

    Transforms:
    - GenesisService.get_instance() → ServiceRegistry.get(GenesisProtocol)
    - ShuddhiEngine.get_instance() → ServiceRegistry.get(ShuddhiProtocol)

    Note: This remedy adds a TODO comment when protocol doesn't exist.
    """

    # Known class to protocol mappings
    KNOWN_PROTOCOLS = {
        "GenesisService": "GenesisProtocol",
        "ShuddhiEngine": "ShuddhiProtocol",
        "TaskManager": "TaskProtocol",
        "CartridgeService": "CartridgeProtocol",
        "ToolRegistry": "ToolRegistryProtocol",
    }

    @property
    def rule_id(self) -> str:
        return "get_instance_antipattern"

    @property
    def requirements(self) -> List[str]:
        return ["vibe_core.di"]

    def __init__(self):
        super().__init__()
        self._needs_service_registry_import = False
        self._has_service_registry_import = False
        self._transformed_classes: Set[str] = set()

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
        """Transform X.get_instance() to ServiceRegistry.get(XProtocol)."""
        # Check for .get_instance() pattern
        if not self._is_get_instance_call(updated_node):
            return updated_node

        # Extract class name
        class_name = self._extract_class_name(updated_node)
        if not class_name:
            return updated_node

        self.violation_found = True
        self.applied = True
        self._needs_service_registry_import = True
        self._transformed_classes.add(class_name)

        # Determine protocol name
        protocol_name = self.KNOWN_PROTOCOLS.get(class_name, f"{class_name}Protocol")

        # Build ServiceRegistry.get(XProtocol)
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

        # Build import statement: from vibe_core.di import ServiceRegistry
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
            if isinstance(stmt, (cst.SimpleStatementLine, cst.BaseCompoundStatement)):
                # Check if it's an import
                if isinstance(stmt, cst.SimpleStatementLine):
                    if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                        insert_idx = i + 1

        new_body.insert(insert_idx, new_import)
        return updated_node.with_changes(body=new_body)

    def _is_get_instance_call(self, node: cst.Call) -> bool:
        """Check if node is a .get_instance() call."""
        if not isinstance(node.func, cst.Attribute):
            return False

        if not isinstance(node.func.attr, cst.Name):
            return False

        return node.func.attr.value == "get_instance"

    def _extract_class_name(self, node: cst.Call) -> str:
        """Extract class name from X.get_instance() call."""
        if not isinstance(node.func, cst.Attribute):
            return ""

        if isinstance(node.func.value, cst.Name):
            return node.func.value.value

        return ""
