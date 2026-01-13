"""
MANU Types - Position 5 (DHARMA Quarter, SYNC_PULSE)
=====================================================

MANU - The Lawgiver.
Types for pulse/sync operations.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xc5704348"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.manu.types.pulse import (
    SystemState,
    PulseFrequency,
    PulsePacket,
    PulseManager,
    get_pulse_manager,
)

from vibe_core.protocols.mahajanas.manu.types.kernel_ops import (
    check_system_health,
    sync_resource_quotas,
    grant_repo_access,
    pulse,
    execute_playbook,
    narasimha_destroy_agent,
)

__all__ = [
    # pulse.py
    "SystemState",
    "PulseFrequency",
    "PulsePacket",
    "PulseManager",
    "get_pulse_manager",
    # kernel_ops.py
    "check_system_health",
    "sync_resource_quotas",
    "grant_repo_access",
    "pulse",
    "execute_playbook",
    "narasimha_destroy_agent",
]
