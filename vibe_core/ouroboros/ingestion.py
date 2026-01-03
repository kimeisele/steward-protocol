"""
Violation Ingestion - Universal intake for all error sources.

Any source of violations (ruff, pytest, mypy, CI/CD, watchman) can feed
into the Knowledge Graph through this interface.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

logger = logging.getLogger("OUROBOROS")


class ViolationSource(Enum):
    """Sources of violations that feed the Ouroboros loop."""

    # Local sources
    WATCHMAN = "watchman"  # AST-based code inspection
    RUFF = "ruff"  # Linter violations
    PYTEST = "pytest"  # Test failures
    MYPY = "mypy"  # Type errors

    # CI/CD sources
    CI_LINT = "ci/lint"  # CI linter failures
    CI_TEST = "ci/test"  # CI test failures
    CI_BUILD = "ci/build"  # CI build failures
    CI_SECURITY = "ci/security"  # CI security scan failures

    # Runtime sources
    RUNTIME_ERROR = "runtime"  # Production errors
    CRASH = "crash"  # System crashes


@dataclass
class ViolationRecord:
    """A violation record from any source."""

    source: ViolationSource
    rule_id: str
    file_path: Optional[str] = None
    line: Optional[int] = None
    message: str = ""
    severity: str = "MEDIUM"
    has_remedy: bool = False
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.value,
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line": self.line,
            "message": self.message,
            "severity": self.severity,
            "has_remedy": self.has_remedy,
            "context": self.context or {},
            "ingested_at": datetime.now().isoformat(),
        }


class ViolationIngester:
    """
    Universal violation ingestion service.

    Accepts violations from any source and persists them to the Knowledge Graph.
    This is the "stomach" of Ouroboros - it digests all errors.
    """

    def __init__(self, kg: Optional[UnifiedKnowledgeGraph] = None):
        """Initialize with optional Knowledge Graph injection."""
        self._kg = kg

    @property
    def kg(self) -> UnifiedKnowledgeGraph:
        """Lazy-load Knowledge Graph from ServiceRegistry."""
        if self._kg is None:
            self._kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
        if self._kg is None:
            raise RuntimeError("Knowledge Graph not available in ServiceRegistry")
        return self._kg

    def ingest(self, violations: List[ViolationRecord]) -> int:
        """
        Ingest a batch of violations into the Knowledge Graph.

        Args:
            violations: List of violation records

        Returns:
            Number of violations ingested
        """
        count = 0
        for v in violations:
            try:
                self.kg.add_violation(
                    file_path=v.file_path or "unknown",
                    line=v.line or 0,
                    rule_id=v.rule_id,
                    message=v.message,
                    has_remedy=v.has_remedy,
                )
                count += 1
            except Exception as e:
                logger.warning(f"[OUROBOROS] Failed to ingest violation: {e}")

        if count > 0:
            logger.info(
                f"[OUROBOROS] Ingested {count} violations from {violations[0].source.value if violations else 'unknown'}"
            )

        return count

    def ingest_from_json(self, json_path: Path, source: ViolationSource) -> int:
        """
        Ingest violations from a JSON file.

        Args:
            json_path: Path to violations JSON
            source: Source type for these violations

        Returns:
            Number of violations ingested
        """
        if not json_path.exists():
            logger.warning(f"[OUROBOROS] Violations file not found: {json_path}")
            return 0

        try:
            data = json.loads(json_path.read_text())
            violations = self._parse_violations(data, source)
            return self.ingest(violations)
        except Exception as e:
            logger.error(f"[OUROBOROS] Failed to parse violations file: {e}")
            return 0

    def ingest_ruff_output(self, ruff_output: str) -> int:
        """
        Ingest violations from ruff JSON output.

        Args:
            ruff_output: Raw ruff JSON output

        Returns:
            Number of violations ingested
        """
        try:
            data = json.loads(ruff_output)
            violations = []

            for item in data:
                violations.append(
                    ViolationRecord(
                        source=ViolationSource.RUFF,
                        rule_id=item.get("code", "UNKNOWN"),
                        file_path=item.get("filename"),
                        line=item.get("location", {}).get("row"),
                        message=item.get("message", ""),
                        severity=self._ruff_severity(item.get("code", "")),
                        has_remedy=True,  # ruff --fix can fix most issues
                    )
                )

            return self.ingest(violations)
        except Exception as e:
            logger.error(f"[OUROBOROS] Failed to parse ruff output: {e}")
            return 0

    def ingest_pytest_output(self, pytest_json: Dict[str, Any]) -> int:
        """
        Ingest violations from pytest JSON output.

        Args:
            pytest_json: Parsed pytest-json output

        Returns:
            Number of violations ingested
        """
        violations = []

        for test in pytest_json.get("tests", []):
            if test.get("outcome") == "failed":
                # Extract file path from nodeid (e.g., "tests/unit/test_foo.py::test_bar")
                nodeid = test.get("nodeid", "")
                file_path = nodeid.split("::")[0] if "::" in nodeid else nodeid

                violations.append(
                    ViolationRecord(
                        source=ViolationSource.PYTEST,
                        rule_id=f"TEST_FAILURE:{nodeid}",
                        file_path=file_path,
                        line=test.get("lineno"),
                        message=test.get("call", {}).get("longrepr", "Test failed"),
                        severity="HIGH",
                        has_remedy=False,  # Tests need human investigation
                        context={"nodeid": nodeid, "duration": test.get("duration")},
                    )
                )

        return self.ingest(violations)

    def _parse_violations(self, data: Any, source: ViolationSource) -> List[ViolationRecord]:
        """Parse violations from generic JSON data."""
        violations = []

        # Handle list of violations
        if isinstance(data, list):
            for item in data:
                violations.append(
                    ViolationRecord(
                        source=source,
                        rule_id=item.get("rule_id", item.get("code", "UNKNOWN")),
                        file_path=item.get("file_path", item.get("filename")),
                        line=item.get("line", item.get("line_number")),
                        message=item.get("message", ""),
                        severity=item.get("severity", "MEDIUM"),
                        has_remedy=item.get("has_remedy", False),
                    )
                )

        # Handle dict with violations key
        elif isinstance(data, dict) and "violations" in data:
            return self._parse_violations(data["violations"], source)

        return violations

    def _ruff_severity(self, code: str) -> str:
        """Map ruff error codes to severity levels."""
        if code.startswith("E9") or code.startswith("F"):
            return "CRITICAL"  # Syntax errors, undefined names
        elif code.startswith("E"):
            return "MEDIUM"  # Style errors
        elif code.startswith("W"):
            return "LOW"  # Warnings
        else:
            return "MEDIUM"
