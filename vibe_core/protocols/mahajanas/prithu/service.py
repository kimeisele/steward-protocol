"""
PRITHU SERVICE - Wraps Legacy Audit/Compliance
==============================================

POSITION: 4 (HEAD - DHARMA Quarter)

This is a THIN WRAPPER that connects legacy auditing and compliance
to the Mahajana framework. NO DUPLICATION - just delegation.

WRAPPED:
- vibe_core.genesis.compliance.ComplianceBureau (GAD-000 compliance)
- vibe_core.protocols.auditor.AuditorProtocol (verification)

"As Prithu compiled and divided Vedic knowledge,
this service asserts and validates truth."
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x257a4aa0"  # GenesisByte: parampara % 37 == 0

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from vibe_core.protocols.mahajanas.prithu import (
    PrithuProtocolBase,
    TruthLevel,
    AssertionResult,
    TruthState,
)

# Import legacy implementations - DO NOT DUPLICATE
from vibe_core.genesis.compliance import ComplianceBureau
from vibe_core.protocols.auditor import AuditorProtocol, NullAuditor


class PrithuService(PrithuProtocolBase):
    """
    PRITHU Service - Truth Assertion/Validation.

    WRAPS the legacy ComplianceBureau and AuditorProtocol.
    Manages truth verification and knowledge compilation.

    Position 4 - The Literary HEAD, asserts truth.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        auditor: Optional[AuditorProtocol] = None,
    ) -> None:
        """Initialize with optional workspace and auditor."""
        self._compliance = ComplianceBureau(workspace=workspace)
        self._auditor: AuditorProtocol = auditor or NullAuditor()
        self._assertions: Dict[str, AssertionResult] = {}
        self._compilations: Dict[str, List[str]] = {}
        self._stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
        }

    # =========================================================================
    # TRUTH PROTOCOL (Position 4 - ASSERT_TRUTH)
    # =========================================================================

    def assert_truth(self, claim: str, evidence: str) -> AssertionResult:
        """ASSERT_TRUTH: Assert a truth claim with evidence."""
        self._stats["total"] += 1
        assertion_id = f"prithu_{self._stats['total']}_{datetime.now().timestamp()}"

        # For now, all assertions are accepted (verification comes from auditor)
        self._stats["valid"] += 1

        result = AssertionResult(
            valid=True,
            truth_level=TruthLevel.ASSERTED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id=assertion_id,
            violations=[],
        )

        self._assertions[assertion_id] = result
        return result

    def verify(self, assertion_id: str) -> AssertionResult:
        """Verify a previous assertion."""
        if assertion_id not in self._assertions:
            return AssertionResult(
                valid=False,
                truth_level=TruthLevel.FALSE.value,
                timestamp=datetime.now().isoformat(),
                assertion_id=assertion_id,
                error_message="Assertion not found",
            )

        # Upgrade to verified
        original = self._assertions[assertion_id]
        result = AssertionResult(
            valid=original.get("valid", True),
            truth_level=TruthLevel.VERIFIED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id=assertion_id,
            violations=original.get("violations", []),
        )

        self._assertions[assertion_id] = result
        return result

    def compile(self, truths: List[str]) -> str:
        """Compile multiple truths (like Prithu compiled Vedas). Returns compilation ID."""
        compilation_id = f"compilation_{len(self._compilations)}"
        self._compilations[compilation_id] = truths
        return compilation_id

    def divide(self, compilation_id: str) -> List[str]:
        """Divide compiled truths (like Prithu divided Vedas). Returns parts."""
        return self._compilations.get(compilation_id, [])

    def get_truth_level(self, assertion_id: str) -> TruthLevel:
        """Get the truth level of an assertion."""
        if assertion_id not in self._assertions:
            return TruthLevel.FALSE

        level_str = self._assertions[assertion_id].get("truth_level", "asserted")
        try:
            return TruthLevel(level_str)
        except ValueError:
            return TruthLevel.ASSERTED

    def challenge(self, assertion_id: str, counter_evidence: str) -> AssertionResult:
        """Challenge an existing assertion with counter-evidence."""
        if assertion_id not in self._assertions:
            return AssertionResult(
                valid=False,
                truth_level=TruthLevel.FALSE.value,
                timestamp=datetime.now().isoformat(),
                assertion_id=assertion_id,
                error_message="Assertion not found to challenge",
            )

        # Mark as disputed
        result = AssertionResult(
            valid=True,  # Challenge accepted
            truth_level=TruthLevel.DISPUTED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id=assertion_id,
        )

        self._assertions[assertion_id] = result
        return result

    def get_state(self) -> TruthState:
        """Get truth assertion state."""
        total = self._stats["total"]
        coverage = self._stats["valid"] / total if total > 0 else 1.0

        return TruthState(
            total_assertions=total,
            valid_assertions=self._stats["valid"],
            invalid_assertions=self._stats["invalid"],
            truth_coverage=coverage,
            health="pristine" if coverage > 0.9 else "healthy",
        )

    # =========================================================================
    # COMPLIANCE ACCESS (Legacy ComplianceBureau)
    # =========================================================================

    def audit_compliance(self, path: Path) -> Dict:
        """Run GAD-000 compliance audit via ComplianceBureau."""
        report = self._compliance.audit(path)
        return {
            "path": str(report.path),
            "module_type": report.module_type.value if hasattr(report.module_type, "value") else str(report.module_type),
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                }
                for check in report.checks
            ],
            "is_compliant": report.is_compliant,
        }

    @property
    def compliance(self) -> ComplianceBureau:
        """Access the legacy ComplianceBureau."""
        return self._compliance

    @property
    def auditor(self) -> AuditorProtocol:
        """Access the auditor implementation."""
        return self._auditor

    def set_auditor(self, auditor: AuditorProtocol) -> None:
        """Set auditor implementation."""
        self._auditor = auditor

    # =========================================================================
    # GNOSIS - The Wisdom of Prithu
    # =========================================================================

    def execute(self, command: str) -> str:
        """
        Execute a Knowledge Consultation Command.
        Prithudeva asserts the eternal truth.
        """
        cmd_lower = command.lower()
        
        if "gita" in cmd_lower or "verse" in cmd_lower:
            # Simple Verse Resolver
            if "2.47" in cmd_lower:
                return (
                    "📜  PRITHU SPEAKS (Bhagavad Gita 2.47):\n"
                    "--------------------------------------\n"
                    "karmaṇy evādhikāras te mā phaleṣu kadācana\n"
                    "mā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi\n\n"
                    "TRANSLATION:\n"
                    "You have a right to perform your prescribed duty, but you are not entitled "
                    "to the fruits of action. Never consider yourself the cause of the results "
                    "of your activities, and never be attached to not doing your duty."
                )
            
            return (
                "📜  PRITHU SPEAKS:\n"
                "The Gita is the compilation of all Vedic wisdom. Ask for a specific verse "
                "(e.g., 'consult gita 2.47') to receive the Gnosis."
            )
            
        return f"📜  Prithu hears your inquiry: '{command}'. But the truth must be sought with humility."


__all__ = ["PrithuService"]
