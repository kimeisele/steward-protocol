"""
HERALD Governance Module - Rules as Code.

This module implements the governance layer for HERALD agents.
All governance rules are hardcoded as Python logic, not YAML configs.
This makes governance immutable and architecturally enforced.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xc83b565f"  # GenesisByte: parampara % 37 == 0

from .constitution import (
    GovernanceContract,
    HeraldConstitution,
)

__all__ = [
    "GovernanceContract",
    "HeraldConstitution",
]
