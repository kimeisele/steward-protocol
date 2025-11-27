"""
Governance layer for Vibe Agency.

This module implements the "Soul" of the system - invariant rules and constraints
that ensure safe and correct agent behavior.

Key components:
- InvariantChecker: Validates tool calls against safety rules
- SoulResult: Encapsulates validation results
"""

from vibe_core.governance.invariants import InvariantChecker, SoulResult

__all__ = ["InvariantChecker", "SoulResult"]
