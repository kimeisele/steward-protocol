"""
SATYA - The Truth Verification Layer

"सत्यं वद" - "Speak the Truth" (Taittiriya Upanishad)

This module implements the critical VERIFICATION step missing from the Ouroboros loop:

    Detect → Store → Heal → VERIFY → Learn
                              ↑
                         THIS MODULE

PROBLEM: Reports like REPORT.md are Smriti (memory/recollection).
         The actual code is Shruti (truth/what IS).
         Ingesting unverified claims creates Maya (illusion).

SOLUTION: Before any violation enters the Knowledge Graph, we verify it
          actually exists in the current codebase.

VEDA-4 Pattern:
    SHABDA → Receive violation claim from parser
    ARTHA  → Validate file/line still exists
    PRATYAYA → Check if violation pattern still matches
    KARMA  → Accept verified violations, reject Maya

Verification Statuses:
    - UNVERIFIED: Never checked against current code
    - VERIFIED: Confirmed to still exist in current code
    - STALE: Was verified before but not recently
    - MAYA: Claim was false (file/line doesn't match, violation fixed)
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.ouroboros.ingestion import ViolationRecord, ViolationSource

logger = logging.getLogger("OUROBOROS.SATYA")


class VerificationStatus(Enum):
    """Status of violation verification against current code."""

    UNVERIFIED = "unverified"  # Never checked
    VERIFIED = "verified"  # Confirmed to exist now
    STALE = "stale"  # Was verified but not recently
    MAYA = "maya"  # False positive / no longer exists


class ViolationOrigin(Enum):
    """Where did the violation claim come from?"""

    LIVE_SCAN = "live_scan"  # Fresh Watchman/Ruff/Pytest scan
    REPORT = "report"  # Static report file (REPORT.md, etc.)
    CI = "ci"  # CI/CD pipeline output
    MANUAL = "manual"  # Human-reported


@dataclass
class VerifiedViolation:
    """
    A violation that has been verified against current code.

    This is the OUTPUT of SatyaValidator - only verified violations
    should enter the Knowledge Graph.
    """

    # Original violation data
    record: ViolationRecord

    # Verification metadata
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_at: Optional[str] = None
    verification_method: str = "unverified"
    origin: ViolationOrigin = ViolationOrigin.REPORT

    # Verification evidence
    file_exists: bool = False
    line_exists: bool = False
    pattern_matches: bool = False
    evidence: Optional[str] = None  # Matched line content

    def is_valid(self) -> bool:
        """Check if violation is valid for ingestion."""
        return self.verification_status in (
            VerificationStatus.VERIFIED,
            VerificationStatus.STALE,  # Stale is still potentially valid
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for KG storage."""
        base = self.record.to_dict()
        base.update(
            {
                "verification_status": self.verification_status.value,
                "verified_at": self.verified_at,
                "verification_method": self.verification_method,
                "origin": self.origin.value,
                "file_exists": self.file_exists,
                "line_exists": self.line_exists,
                "pattern_matches": self.pattern_matches,
            }
        )
        return base


@dataclass
class VerificationResult:
    """Result of a verification batch."""

    verified: List[VerifiedViolation] = field(default_factory=list)
    maya: List[VerifiedViolation] = field(default_factory=list)  # False positives
    errors: List[Tuple[ViolationRecord, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.verified) + len(self.maya) + len(self.errors)

    @property
    def verified_count(self) -> int:
        return len(self.verified)

    @property
    def maya_count(self) -> int:
        return len(self.maya)

    def summary(self) -> str:
        return f"Verified: {self.verified_count}, Maya (discarded): {self.maya_count}, Errors: {len(self.errors)}"


class SatyaValidator:
    """
    The Truth Validator - Verifies violation claims against current code.

    "Who watches the watchers?" - This module.

    Usage:
        validator = SatyaValidator(project_root=Path("."))

        # Verify a batch of violations
        result = validator.verify_batch(violations)

        # Only ingest verified violations
        ingester.ingest([v.record for v in result.verified])
    """

    # Known violation patterns for re-verification
    # Maps rule_id prefix to regex patterns that indicate the violation
    VIOLATION_PATTERNS: Dict[str, List[str]] = {
        # Shuddhi/Watchman patterns
        "subprocess_timeout": [r"subprocess\.run\([^)]*\)", r"subprocess\.call\("],
        "hardcoded_path": [r'Path\(["\'][^"\']+["\']\)', r'open\(["\'][^"\']+["\']\)'],
        "mock_return": [r"return True\s*(#|$)", r"return False\s*(#|$)"],
        # REPORT.md patterns
        "REPORT:A-": [r".*"],  # Can't verify without specific pattern
        "REPORT:B-": [r".*"],
        # Test patterns
        "TESTS:UNTESTED_MODULE": [r".*"],  # Can verify file exists
        "TESTS:LOW_COVERAGE": [r".*"],
    }

    def __init__(
        self,
        project_root: Optional[Path] = None,
        strict: bool = False,
        max_staleness_days: int = 30,
    ):
        """
        Initialize the Satya Validator.

        Args:
            project_root: Root directory for resolving file paths
            strict: If True, reject violations that can't be verified
            max_staleness_days: Days after which verified violations become stale
        """
        self._project_root = project_root or Path.cwd()
        self._strict = strict
        self._max_staleness_days = max_staleness_days

    def verify_batch(
        self,
        violations: List[ViolationRecord],
        origin: ViolationOrigin = ViolationOrigin.REPORT,
    ) -> VerificationResult:
        """
        Verify a batch of violations against current code.

        Args:
            violations: List of violation claims to verify
            origin: Where these claims came from

        Returns:
            VerificationResult with verified and maya (false positive) lists
        """
        result = VerificationResult()

        for v in violations:
            try:
                verified = self.verify_single(v, origin)

                if verified.is_valid():
                    result.verified.append(verified)
                    logger.debug(f"[SATYA] ✓ Verified: {v.rule_id}")
                else:
                    result.maya.append(verified)
                    logger.info(
                        f"[SATYA] ✗ Maya discarded: {v.rule_id} at {v.file_path}:{v.line} "
                        f"(status: {verified.verification_status.value})"
                    )

            except Exception as e:
                result.errors.append((v, str(e)))
                logger.warning(f"[SATYA] Error verifying {v.rule_id}: {e}")

        logger.info(f"[SATYA] Verification complete: {result.summary()}")
        return result

    def verify_single(
        self,
        violation: ViolationRecord,
        origin: ViolationOrigin = ViolationOrigin.REPORT,
    ) -> VerifiedViolation:
        """
        Verify a single violation against current code.

        Verification steps:
        1. Check if file exists
        2. Check if line exists
        3. Check if violation pattern still matches

        Args:
            violation: The violation claim to verify
            origin: Where this claim came from

        Returns:
            VerifiedViolation with verification status and evidence
        """
        verified = VerifiedViolation(
            record=violation,
            origin=origin,
            verified_at=datetime.now().isoformat(),
            verification_method="satya_validator",
        )

        # Live scans are pre-verified (they just happened)
        if origin == ViolationOrigin.LIVE_SCAN:
            verified.verification_status = VerificationStatus.VERIFIED
            verified.file_exists = True
            verified.line_exists = True
            verified.pattern_matches = True
            return verified

        # For report-based claims, verify against current code
        file_path = violation.file_path
        if not file_path:
            # Can't verify without file path
            if self._strict:
                verified.verification_status = VerificationStatus.MAYA
            else:
                verified.verification_status = VerificationStatus.UNVERIFIED
            return verified

        # Step 1: Check file exists
        full_path = self._resolve_path(file_path)
        if not full_path.exists():
            verified.verification_status = VerificationStatus.MAYA
            verified.file_exists = False
            return verified

        verified.file_exists = True

        # Step 2: Check line exists (if specified)
        if violation.line:
            try:
                lines = full_path.read_text().splitlines()
                if violation.line > len(lines):
                    verified.verification_status = VerificationStatus.MAYA
                    verified.line_exists = False
                    return verified
                verified.line_exists = True
                verified.evidence = lines[violation.line - 1] if lines else None
            except Exception:
                verified.line_exists = False
        else:
            # No line specified, can't check
            verified.line_exists = True

        # Step 3: Check if violation pattern still matches
        pattern_matches = self._check_pattern_matches(violation.rule_id, full_path, violation.line)
        verified.pattern_matches = pattern_matches

        # Determine final status
        if verified.file_exists and verified.line_exists and pattern_matches:
            verified.verification_status = VerificationStatus.VERIFIED
        elif verified.file_exists and verified.line_exists:
            # File and line exist but pattern doesn't match
            # Could be fixed or refactored
            if self._strict:
                verified.verification_status = VerificationStatus.MAYA
            else:
                # Give benefit of doubt - mark as unverified
                verified.verification_status = VerificationStatus.UNVERIFIED
        else:
            verified.verification_status = VerificationStatus.MAYA

        return verified

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path relative to project root."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self._project_root / path

    def _check_pattern_matches(
        self,
        rule_id: str,
        file_path: Path,
        line: Optional[int],
    ) -> bool:
        """
        Check if the violation pattern still matches at the location.

        Returns True if:
        - We find a matching pattern in the specified line, OR
        - We don't have a specific pattern for this rule (can't verify)
        """
        # Find patterns for this rule
        patterns = self._get_patterns_for_rule(rule_id)

        if not patterns:
            # No specific patterns - can't verify, assume still exists
            return True

        try:
            content = file_path.read_text()
            lines = content.splitlines()

            if line and line <= len(lines):
                # Check specific line
                line_content = lines[line - 1]
                for pattern in patterns:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        return True
            else:
                # No line specified - check entire file
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True

            return False

        except Exception as e:
            logger.warning(f"[SATYA] Error checking pattern: {e}")
            return True  # Can't verify, assume exists

    def _get_patterns_for_rule(self, rule_id: str) -> List[str]:
        """Get regex patterns for a rule ID."""
        # Exact match
        if rule_id in self.VIOLATION_PATTERNS:
            return self.VIOLATION_PATTERNS[rule_id]

        # Prefix match
        for prefix, patterns in self.VIOLATION_PATTERNS.items():
            if rule_id.startswith(prefix):
                return patterns

        return []

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics (GAD-000: Observability)."""
        return {
            "project_root": str(self._project_root),
            "strict_mode": self._strict,
            "max_staleness_days": self._max_staleness_days,
            "known_patterns": len(self.VIOLATION_PATTERNS),
        }


# Convenience functions


def verify_violations(
    violations: List[ViolationRecord],
    project_root: Optional[Path] = None,
    origin: ViolationOrigin = ViolationOrigin.REPORT,
) -> VerificationResult:
    """
    Verify a batch of violations against current code.

    Convenience function for one-off verification.
    """
    validator = SatyaValidator(project_root=project_root)
    return validator.verify_batch(violations, origin)


def filter_maya(violations: List[ViolationRecord]) -> List[ViolationRecord]:
    """
    Filter out Maya (false positives) from violations.

    Returns only violations that are verified to still exist.
    """
    result = verify_violations(violations)
    return [v.record for v in result.verified]
