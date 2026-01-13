"""
Contract Verification Types for STEWARD Protocol.

OPUS-032: Shared schema for @HARNESS verification failures.

This module lives in the SHARED CORE (governance) so that:
- Plugins (opus_assistant) can generate typed failures
- Core (verification engine) can consume them
- No circular dependencies (Dependency Inversion Principle)

Key concepts:
- ContractFailureType: Enum of all possible @HARNESS failure types
- Severity: Determines auto-fix eligibility
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x5ba9c813"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class ContractFailureType(Enum):
    """
    OPUS-032: Explicit failure types for @HARNESS verification.

    Severity determines auto-fix eligibility:
    - FATAL: System halt, require human intervention
    - ERROR: Generate intent, require approval
    - WARNING: Generate intent, can auto-fix if karma high
    - INFO: Log only, no action

    Usage:
        from vibe_core.governance.contracts import ContractFailureType, ContractFailure

        failure = ContractFailure(
            type=ContractFailureType.FILE_MISSING,
            path="vibe_core/plugins/foo/bar.py",
            message="Required file not found"
        )

        if failure.type.auto_fixable:
            # Can attempt auto-fix with high karma
    """

    # File-level failures
    FILE_MISSING = auto()  # Required file doesn't exist
    FILE_EXTRA = auto()  # Absent file exists (shouldn't)

    # Pattern-level failures
    PATTERN_MISSING = auto()  # Required wiring not found
    PATTERN_BROKEN = auto()  # Pattern exists but syntax error

    # Doc-level failures
    DOC_STALE = auto()  # Doc references old paths
    DOC_INCOMPLETE = auto()  # Doc missing required sections

    # Semantic failures (OPUS-026)
    SEMANTIC_IMPORT_FAIL = auto()  # Module can't be imported
    SEMANTIC_TEST_FAIL = auto()  # Test doesn't pass

    @property
    def severity(self) -> str:
        """
        Map failure type to severity level.

        Returns:
            One of: "FATAL", "ERROR", "WARNING", "INFO"
        """
        fatal = {ContractFailureType.SEMANTIC_IMPORT_FAIL}
        error = {
            ContractFailureType.FILE_MISSING,
            ContractFailureType.PATTERN_MISSING,
            ContractFailureType.PATTERN_BROKEN,
        }
        warning = {
            ContractFailureType.DOC_STALE,
            ContractFailureType.DOC_INCOMPLETE,
            ContractFailureType.FILE_EXTRA,
        }

        if self in fatal:
            return "FATAL"
        elif self in error:
            return "ERROR"
        elif self in warning:
            return "WARNING"
        return "INFO"

    @property
    def auto_fixable(self) -> bool:
        """
        Can this be auto-fixed with high karma?

        Only WARNING and INFO severity can be auto-fixed.
        ERROR and FATAL always require human approval.
        """
        return self.severity in ("WARNING", "INFO")

    @property
    def intent_type(self) -> str:
        """
        Get the intent type to generate for this failure.

        Returns:
            Intent type string for IntentGenerator
        """
        mapping = {
            ContractFailureType.FILE_MISSING: "contract_file_create",
            ContractFailureType.FILE_EXTRA: "contract_file_remove",
            ContractFailureType.PATTERN_MISSING: "contract_pattern_fix",
            ContractFailureType.PATTERN_BROKEN: "contract_pattern_fix",
            ContractFailureType.DOC_STALE: "contract_doc_update",
            ContractFailureType.DOC_INCOMPLETE: "contract_doc_complete",
            ContractFailureType.SEMANTIC_IMPORT_FAIL: "contract_import_fix",
            ContractFailureType.SEMANTIC_TEST_FAIL: "contract_test_fix",
        }
        return mapping.get(self, "contract_unknown")


@dataclass
class ContractFailure:
    """
    A typed failure from @HARNESS verification.

    Attributes:
        type: The type of failure (determines severity and auto-fix)
        path: File path related to the failure
        message: Human-readable description
        harness_source: Path to the OPUS doc containing the @HARNESS
        details: Additional context (e.g., expected pattern, actual value)
    """

    type: ContractFailureType
    path: str
    message: str
    harness_source: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @property
    def severity(self) -> str:
        """Delegate to type's severity."""
        return self.type.severity

    @property
    def auto_fixable(self) -> bool:
        """Delegate to type's auto_fixable."""
        return self.type.auto_fixable

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON storage."""
        return {
            "type": self.type.name,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
            "harness_source": self.harness_source,
            "details": self.details,
            "auto_fixable": self.auto_fixable,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContractFailure":
        """Deserialize from JSON storage."""
        return cls(
            type=ContractFailureType[data["type"]],
            path=data["path"],
            message=data["message"],
            harness_source=data.get("harness_source"),
            details=data.get("details"),
        )
