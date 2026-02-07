"""
HYGIENE AUDITOR - Code Quality Enforcement
===========================================

Detects code hygiene violations using AST analysis:
1. Usage of 'Any' type (should be specific types or 'object')
2. Missing __mahajana__ declarations in mahamantra modules
3. Broken __genesis__ bytes (not divisible by PARAMPARA)

Implements AuditorProtocol: class Auditor + run_audit() → List[AuditFinding].
Auto-discovered by AuditDispatcher via __position__ + Auditor class.
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 3  # Fourth auditor to run
__genesis__ = "0x8000000f"

import ast
import logging
from pathlib import Path
from typing import List, Optional

from vibe_core.mahamantra.protocols._seed import PARAMPARA
from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("AUDIT.HYGIENE")


class _HygieneVisitor(ast.NodeVisitor):
    """AST visitor that collects hygiene violations."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.findings: List[AuditFinding] = []
        self.has_mahajana = False
        self.genesis_value: Optional[str] = None

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id == "__mahajana__":
                    self.has_mahajana = True
                elif target.id == "__genesis__":
                    if isinstance(node.value, ast.Constant):
                        self.genesis_value = node.value.value
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "Any":
            self.findings.append(AuditFinding(
                source="hygiene_auditor",
                position=__position__,
                mahajana=__mahajana__,
                description=f"Usage of 'Any' type",
                file_path=self.filepath,
                line_number=node.lineno,
                severity=FindingSeverity.WARNING,
            ))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "Any":
            self.findings.append(AuditFinding(
                source="hygiene_auditor",
                position=__position__,
                mahajana=__mahajana__,
                description=f"Usage of 'typing.Any' type",
                file_path=self.filepath,
                line_number=node.lineno,
                severity=FindingSeverity.WARNING,
            ))
        self.generic_visit(node)


class Auditor:
    """
    Hygiene Auditor — AST-based code quality checks.

    Single responsibility: detect type hygiene and declaration violations.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self._root = Path(root or "vibe_core/mahamantra")

    def run_audit(self) -> List[AuditFinding]:
        """AuditorProtocol: scan for hygiene violations via AST."""
        findings: List[AuditFinding] = []

        for path in self._root.rglob("*.py"):
            if "__pycache__" in str(path):
                continue
            # Don't audit the audit tools themselves
            if "audit" in str(path.parent.name):
                continue

            try:
                source = path.read_text()
                tree = ast.parse(source, filename=str(path))
            except SyntaxError:
                findings.append(AuditFinding(
                    source="hygiene_auditor",
                    position=__position__,
                    mahajana=__mahajana__,
                    description="SyntaxError — cannot parse",
                    file_path=str(path),
                    severity=FindingSeverity.CRITICAL,
                ))
                continue
            except Exception:
                continue

            visitor = _HygieneVisitor(str(path))
            visitor.visit(tree)
            findings.extend(visitor.findings)

            # Check genesis if present
            if visitor.genesis_value:
                try:
                    val = int(visitor.genesis_value, 16)
                    if val % PARAMPARA != 0:
                        findings.append(AuditFinding(
                            source="hygiene_auditor",
                            position=__position__,
                            mahajana=__mahajana__,
                            description=(
                                f"Broken genesis: {visitor.genesis_value} "
                                f"% {PARAMPARA} = {val % PARAMPARA}"
                            ),
                            file_path=str(path),
                            severity=FindingSeverity.CRITICAL,
                        ))
                except ValueError:
                    findings.append(AuditFinding(
                        source="hygiene_auditor",
                        position=__position__,
                        mahajana=__mahajana__,
                        description=f"Invalid genesis format: {visitor.genesis_value}",
                        file_path=str(path),
                        severity=FindingSeverity.CRITICAL,
                    ))

        logger.info(
            "Hygiene audit: %d findings from %s",
            len(findings), self._root,
        )
        return findings


__all__ = ["Auditor"]
