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

from vibe_core.governance.contracts import ContractFailure, ContractFailureType
from vibe_core.governance.invariants import InvariantChecker, SoulResult

__all__ = ["InvariantChecker", "SoulResult", "ContractFailureType", "ContractFailure"]
