"""
Governance layer for Vibe Agency.

This module implements the "Soul" of the system - invariant rules and constraints
that ensure safe and correct agent behavior.

Key components:
- InvariantChecker: Validates tool calls against safety rules
- SoulResult: Encapsulates validation results
- ContractFailureType: Typed @HARNESS verification failures (OPUS-032)
- ContractFailure: Failure instance with path and details
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xba7e314c"  # GenesisByte: parampara % 37 == 0

from vibe_core.governance.contracts import ContractFailure, ContractFailureType
from vibe_core.governance.invariants import InvariantChecker, SoulResult

__all__ = ["InvariantChecker", "SoulResult", "ContractFailureType", "ContractFailure"]
