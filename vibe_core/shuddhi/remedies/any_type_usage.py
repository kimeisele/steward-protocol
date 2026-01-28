"""
OPUS-XXX: AnyTypeRemedy - Heals Any Type Violations.

Detection: watertight.py (rule: any_type_usage)
Surgery: This CSTRemedy

SAFE TRANSFORMATIONS:
1. Remove unused `Any` imports (from typing import Any where Any never used)
2. Mark actual Any usage as OUT_OF_SCOPE (requires manual type inference)

Philosophy:
"Na tv evāhaṁ jātu nāsaṁ" - Types are eternal. Any is impersonalism.

WATERTIGHT: This remedy does NOT blindly replace Any.
It only removes UNUSED imports safely.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xa3f7b2c1"  # GenesisByte: parampara % 37 == 0

from typing import List, Set, Union

import libcst as cst
import libcst.matchers as m

from vibe_core.shuddhi.remedies.base import CSTRemedy


class AnyTypeRemedy(CSTRemedy):
    """
    Heals Any type violations by removing unused imports.

    SAFE TRANSFORMATION ONLY:
    - If `Any` is imported but never used -> remove from import
    - If `Any` is actually used -> OUT_OF_SCOPE (manual intervention needed)

    This follows the principle of "first, do no harm" - we only
    make changes we can verify are safe.
    """

    # Required for get_metadata() to work with PositionProvider
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    @property
    def rule_id(self) -> str:
        return "any_type_usage"

    def requirements(self) -> List[str]:
        return []  # No special requirements

    def __init__(self) -> None:
        super().__init__()
        self._any_imported = False
        self._any_import_node: cst.ImportFrom | None = None
        self._any_usages: Set[int] = set()  # Line numbers where Any is used
        self._any_import_line: int = 0
        self._other_typing_imports: List[str] = []

    # =========================================================================
    # PASS 1: Detect Any imports and usages
    # =========================================================================

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        """Track imports from typing module."""
        if isinstance(node.module, cst.Attribute):
            # Handle typing.Any style
            return True

        if isinstance(node.module, cst.Name) and node.module.value == "typing":
            if isinstance(node.names, cst.ImportStar):
                return True

            for name in node.names:
                if isinstance(name, cst.ImportAlias):
                    name_value = name.name.value if isinstance(name.name, cst.Name) else None
                    if name_value == "Any":
                        self._any_imported = True
                        self._any_import_node = node
                        # Get position from metadata if available
                        pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
                        if pos:
                            self._any_import_line = pos.start.line
                    elif name_value:
                        self._other_typing_imports.append(name_value)

        return True

    def visit_Name(self, node: cst.Name) -> bool:
        """Track usages of Any (not just imports)."""
        if node.value == "Any":
            # Get position
            pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
            if pos:
                # Only count non-import usages
                if pos.start.line != self._any_import_line:
                    self._any_usages.add(pos.start.line)
        return True

    def visit_Subscript(self, node: cst.Subscript) -> bool:
        """Track Any in generic types like Dict[str, Any]."""
        # This is handled by visit_Name for the Any identifier
        return True

    # =========================================================================
    # PASS 2: Transform (remove unused imports)
    # =========================================================================
    #
    # NOTE: We can't use leave_ImportFrom because it's called BEFORE the rest
    # of the code is visited, so _any_usages would be empty.
    #
    # Instead, we override leave_Module to do a second pass AFTER all info
    # has been collected.
    # =========================================================================

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """
        Transform the module AFTER collecting all usage info.

        This is called after the entire module is visited, so _any_usages
        is fully populated.
        """
        if not self._any_imported:
            return updated_node

        # If Any is actually used, mark as found but don't remove
        if self._any_usages:
            self.violation_found = True
            # Don't transform - Any is used, needs manual intervention
            return updated_node

        # Any is imported but not used - safe to remove!
        self.violation_found = True
        self.applied = True

        # Find and transform the import statement
        new_body = []
        for statement in updated_node.body:
            if isinstance(statement, cst.SimpleStatementLine):
                new_stmts = []
                for stmt in statement.body:
                    if isinstance(stmt, cst.ImportFrom):
                        # Check if this is the Any import
                        if (isinstance(stmt.module, cst.Name) and
                            stmt.module.value == "typing" and
                            not isinstance(stmt.names, cst.ImportStar)):

                            # Filter out Any from imports
                            new_names = []
                            for name in stmt.names:
                                if isinstance(name, cst.ImportAlias):
                                    name_val = name.name.value if isinstance(name.name, cst.Name) else None
                                    if name_val != "Any":
                                        new_names.append(name)

                            if not new_names:
                                # All names removed, skip this statement
                                continue
                            else:
                                # Rebuild with remaining names
                                rebuilt_names = []
                                for i, name in enumerate(new_names):
                                    if i < len(new_names) - 1:
                                        rebuilt_names.append(name.with_changes(
                                            comma=cst.Comma(whitespace_after=cst.SimpleWhitespace(" "))))
                                    else:
                                        rebuilt_names.append(name.with_changes(
                                            comma=cst.MaybeSentinel.DEFAULT))

                                new_stmts.append(stmt.with_changes(names=rebuilt_names))
                                continue

                    new_stmts.append(stmt)

                if new_stmts:
                    new_body.append(statement.with_changes(body=new_stmts))
            else:
                new_body.append(statement)

        return updated_node.with_changes(body=new_body)


class AnyTypeUsageDetector(CSTRemedy):
    """
    Detection-only remedy for Any type usage.

    Unlike AnyTypeRemedy which removes unused imports,
    this remedy DETECTS all Any usages for reporting.

    Use this to generate a report of all Any violations
    that need manual intervention.
    """

    # Required for get_metadata() to work with PositionProvider
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    @property
    def rule_id(self) -> str:
        return "any_type_detection"

    def requirements(self) -> List[str]:
        return []

    def __init__(self) -> None:
        super().__init__()
        self._any_locations: List[tuple[int, int, str]] = []  # (line, col, context)

    def visit_Name(self, node: cst.Name) -> bool:
        """Track all Any usages."""
        if node.value == "Any":
            pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
            if pos:
                self._any_locations.append((pos.start.line, pos.start.column, "bare Any"))
                self.violation_found = True
        return True

    def visit_Subscript(self, node: cst.Subscript) -> bool:
        """Track Any in generic subscripts."""
        # Check slice for Any
        if isinstance(node.slice, list):
            for element in node.slice:
                if isinstance(element.slice, cst.Index):
                    if isinstance(element.slice.value, cst.Name):
                        if element.slice.value.value == "Any":
                            pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
                            if pos:
                                self._any_locations.append((pos.start.line, pos.start.column, "generic Any"))
                                self.violation_found = True
        return True

    @property
    def locations(self) -> List[tuple[int, int, str]]:
        """Get all detected Any locations."""
        return self._any_locations
