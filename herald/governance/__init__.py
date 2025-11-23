"""
HERALD Governance Module - Rules as Code.

This module implements the governance layer for HERALD agents.
All governance rules are hardcoded as Python logic, not YAML configs.
This makes governance immutable and architecturally enforced.
"""

from herald.governance.constitution import (
    GovernanceContract,
    HeraldConstitution,
)

__all__ = [
    "GovernanceContract",
    "HeraldConstitution",
]
