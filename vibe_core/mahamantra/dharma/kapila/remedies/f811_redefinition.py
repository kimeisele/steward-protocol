"""
F811 REMEDY - Redefinition Of Unused Import
===========================================

Ruff F811 flags duplicate re-imports where the first binding is unused.

SAFE HEALING STRATEGY (subset):
1. Remove exact duplicate import aliases in the same import statement.
2. Remove later re-imports of the exact same alias from the exact same source.

This intentionally does NOT rewrite imports from different sources that bind
same symbol names (those can be semantic overrides).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x7e696b72"

from typing import List, Set, Tuple

import libcst as cst
from libcst import Attribute, BaseExpression, Name

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy

_ImportKey = Tuple[str, str, str, str]


class F811RedefinitionRemedy(CSTRemedy):
    """Removes exact duplicate imports that trigger Ruff F811."""

    @property
    def rule_id(self) -> str:
        return "F811"

    def requirements(self) -> List[str]:
        return []

    def __init__(self) -> None:
        super().__init__()
        self._seen: Set[_ImportKey] = set()

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.BaseStatement:
        if len(updated_node.body) != 1:
            return updated_node

        stmt = updated_node.body[0]
        if isinstance(stmt, cst.ImportFrom):
            return self._heal_import_from(updated_node, stmt)
        if isinstance(stmt, cst.Import):
            return self._heal_import(updated_node, stmt)
        return updated_node

    def _heal_import_from(
        self,
        parent: cst.SimpleStatementLine,
        stmt: cst.ImportFrom,
    ) -> cst.BaseStatement:
        if isinstance(stmt.names, cst.ImportStar):
            return parent

        module_name = self._import_from_module(stmt)
        kept: List[cst.ImportAlias] = []
        removed_any = False

        for alias in stmt.names:
            key = (
                "from",
                module_name,
                self._expr_to_dotted(alias.name),
                alias.asname.name.value if alias.asname else "",
            )
            if key in self._seen:
                removed_any = True
                self.violation_found = True
                continue

            self._seen.add(key)
            kept.append(alias)

        if not removed_any:
            return parent

        self.applied = True
        if not kept:
            return cst.RemoveFromParent()

        return parent.with_changes(body=(stmt.with_changes(names=tuple(kept)),))

    def _heal_import(
        self,
        parent: cst.SimpleStatementLine,
        stmt: cst.Import,
    ) -> cst.BaseStatement:
        kept: List[cst.ImportAlias] = []
        removed_any = False

        for alias in stmt.names:
            key = (
                "import",
                "",
                self._expr_to_dotted(alias.name),
                alias.asname.name.value if alias.asname else "",
            )
            if key in self._seen:
                removed_any = True
                self.violation_found = True
                continue

            self._seen.add(key)
            kept.append(alias)

        if not removed_any:
            return parent

        self.applied = True
        if not kept:
            return cst.RemoveFromParent()

        return parent.with_changes(body=(stmt.with_changes(names=tuple(kept)),))

    @staticmethod
    def _import_from_module(node: cst.ImportFrom) -> str:
        rel = "." * len(node.relative)
        if node.module is None:
            return rel
        return rel + F811RedefinitionRemedy._expr_to_dotted(node.module)

    @staticmethod
    def _expr_to_dotted(expr: BaseExpression) -> str:
        """Convert Name/Attribute import expressions to dotted string."""
        if isinstance(expr, Name):
            return expr.value
        if isinstance(expr, Attribute):
            left = F811RedefinitionRemedy._expr_to_dotted(expr.value)
            return f"{left}.{expr.attr.value}"
        # Defensive fallback for rare import expression shapes.
        return ""
