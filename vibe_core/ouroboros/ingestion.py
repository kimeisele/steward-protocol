"""
Violation Ingestion - Universal intake for all error sources.

Any source of violations (ruff, pytest, mypy, CI/CD, watchman) can feed
into the Knowledge Graph through this interface.

Pattern: Uses ServiceRegistry for KG access (injected by Prakriti on boot).

KARMA: All significant operations emit Ledger events.
YANTRA: duration_ms tracked for performance monitoring.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# YANTRA: Type aliases for JSON data structures
# These replace naked 'Any' with precise typing
ViolationJsonItem = Dict[str, object]  # Single violation record from JSON
ViolationJsonData = Union[List[ViolationJsonItem], Dict[str, object]]  # List or wrapper

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
    """
    A violation record from any source.

    SATYA Enhancement: Now includes verification metadata.
    Violations should be verified before ingestion to avoid Maya (illusion).
    """

    source: ViolationSource
    rule_id: str
    file_path: Optional[str] = None
    line: Optional[int] = None
    message: str = ""
    severity: str = "MEDIUM"
    has_remedy: bool = False
    context: Optional[Dict[str, Any]] = None

    # SATYA: Verification metadata (optional, populated by SatyaValidator)
    verification_status: str = "unverified"  # unverified | verified | stale | maya
    verified_at: Optional[str] = None
    origin: str = "unknown"  # live_scan | report | ci | manual

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
            # SATYA: Verification metadata
            "verification_status": self.verification_status,
            "verified_at": self.verified_at,
            "origin": self.origin,
        }

    def is_verified(self) -> bool:
        """Check if this violation has been verified to exist."""
        return self.verification_status in ("verified", "stale")

    def is_maya(self) -> bool:
        """Check if this violation is Maya (false positive / no longer exists)."""
        return self.verification_status == "maya"


class ViolationIngester:
    """
    Universal violation ingestion service.

    Accepts violations from any source and persists them to the Knowledge Graph.
    This is the "stomach" of Ouroboros - it digests all errors.

    SATYA Enhancement: Can optionally verify violations before ingestion.
    This prevents Maya (illusion) from entering the Knowledge Graph.
    """

    def __init__(
        self,
        kg: Optional[UnifiedKnowledgeGraph] = None,
        verify: bool = False,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize with optional Knowledge Graph injection.

        Args:
            kg: Optional Knowledge Graph instance
            verify: If True, verify violations before ingesting (via SatyaValidator)
            project_root: Root directory for verification
        """
        self._kg = kg
        self._verify = verify
        self._project_root = project_root

    @property
    def kg(self) -> UnifiedKnowledgeGraph:
        """Lazy-load Knowledge Graph from ServiceRegistry."""
        if self._kg is None:
            self._kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
        if self._kg is None:
            raise RuntimeError("Knowledge Graph not available in ServiceRegistry")
        return self._kg

    def ingest(
        self,
        violations: List[ViolationRecord],
        verify: Optional[bool] = None,
    ) -> int:
        """
        Ingest a batch of violations into the Knowledge Graph.

        SATYA: If verify=True, violations are verified against current code
        before ingestion. Maya (false positives) are discarded.

        KARMA: Emits VIOLATION_INGESTED ledger event for audit trail.
        YANTRA: Tracks duration_ms for performance monitoring.

        Args:
            violations: List of violation records
            verify: Override instance-level verify setting

        Returns:
            Number of violations ingested (excludes Maya)
        """
        start_time = time.perf_counter()
        should_verify = verify if verify is not None else self._verify

        if should_verify:
            violations = self._verify_violations(violations)

        count = 0
        maya_count = 0
        source = violations[0].source.value if violations else "unknown"

        for v in violations:
            # Skip Maya (false positives)
            if v.is_maya():
                maya_count += 1
                continue

            try:
                self.kg.add_violation(
                    file_path=v.file_path or "unknown",
                    line=v.line or 0,
                    rule_id=v.rule_id,
                    message=v.message,
                    has_remedy=v.has_remedy,
                    verification_status=v.verification_status,
                    verified_at=v.verified_at,
                    origin=v.origin,
                )
                count += 1
            except Exception as e:
                logger.warning(f"[OUROBOROS] Failed to ingest violation: {e}")

        # YANTRA: Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        if count > 0 or maya_count > 0:
            logger.info(
                f"[OUROBOROS] Ingested {count} violations from {source} "
                f"(Maya discarded: {maya_count}, duration: {duration_ms:.1f}ms)"
            )

            # KARMA: Record to Ledger (significant action = must be recorded)
            self._record_ingestion_event(
                source=source,
                count=count,
                maya_count=maya_count,
                duration_ms=duration_ms,
                verified=should_verify,
            )

        # YANTRA: Warn on slow operations (>100ms as per PROMPT.md)
        if duration_ms > 100:
            logger.warning(f"[OUROBOROS] Slow ingestion: {duration_ms:.1f}ms for {count} violations")

        return count

    def _record_ingestion_event(
        self,
        source: str,
        count: int,
        maya_count: int,
        duration_ms: float,
        verified: bool,
    ) -> None:
        """
        KARMA: Record violation ingestion to Ledger.

        This creates an immutable audit trail of all ingestion operations.
        """
        try:
            from vibe_core.protocols.ledger import VibeLedger

            ledger = ServiceRegistry.get(VibeLedger)
            if ledger is None:
                logger.debug("[OUROBOROS] Ledger not available, skipping event recording")
                return

            ledger.record_event(
                event_type="VIOLATION_INGESTED",
                agent_id="ouroboros",
                details={
                    "source": source,
                    "violations_ingested": count,
                    "maya_discarded": maya_count,
                    "duration_ms": round(duration_ms, 2),
                    "verified": verified,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.debug("[OUROBOROS] Recorded ingestion event to Ledger")
        except Exception as e:
            # DHARMA: Never crash on Ledger failure, but always log
            logger.warning(f"[OUROBOROS] Failed to record to Ledger: {e}")

    def _verify_violations(
        self,
        violations: List[ViolationRecord],
    ) -> List[ViolationRecord]:
        """
        Verify violations using SatyaValidator.

        Returns violations with updated verification_status.
        """
        from vibe_core.ouroboros.verification import (
            SatyaValidator,
            ViolationOrigin,
        )

        validator = SatyaValidator(project_root=self._project_root)
        result = validator.verify_batch(violations, origin=ViolationOrigin.REPORT)

        # Convert verified violations back to ViolationRecords
        verified_records = []

        for v in result.verified:
            record = v.record
            record.verification_status = v.verification_status.value
            record.verified_at = v.verified_at
            record.origin = v.origin.value
            verified_records.append(record)

        for v in result.maya:
            record = v.record
            record.verification_status = "maya"
            record.origin = v.origin.value
            verified_records.append(record)

        return verified_records

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

    def _parse_violations(self, data: ViolationJsonData, source: ViolationSource) -> List[ViolationRecord]:
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
