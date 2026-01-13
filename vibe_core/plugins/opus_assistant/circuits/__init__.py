"""
OPUS Assistant Circuits - Cognitive Self-Management.

Phase 5: The system manages itself via declarative circuits.

Circuits:
- OPUS_AUTO_VERIFY: Triggered by GIT_COMMIT, detects drift
- OPUS_AUTO_HEAL: Triggered by persistent drift, suggests fixes
- OPUS_AUTO_REFRESH: Keeps OPUS.md always fresh (no stale docs!)

These circuits make the system SELF-AWARE and SELF-MAINTAINING:
1. GIT_COMMIT event → auto_verify circuit → drift detection
2. Drift detected → log observation → update context
3. Persistent drift → auto_heal circuit → suggest fix
4. Schedule/Boot → auto_refresh circuit → OPUS.md always fresh

Architecture:
    ┌─────────────────────────────────┐
    │         EventBus                │  ← GIT_COMMIT, KERNEL_TICK, BOOT
    └──────────────┬──────────────────┘
                   │ triggers
                   ▼
    ┌─────────────────────────────────┐
    │      OPUS_AUTO_REFRESH          │  ← Keep docs fresh
    │      (auto_refresh.yaml)        │
    └──────────────┬──────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────┐
    │      OPUS_AUTO_VERIFY           │  ← Drift detection
    │      (auto_verify.yaml)         │
    └──────────────┬──────────────────┘
                   │ if drift persists
                   ▼
    ┌─────────────────────────────────┐
    │      OPUS_AUTO_HEAL             │  ← Suggest fixes
    │      (auto_heal.yaml)           │     (human approval required)
    └─────────────────────────────────┘
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xbb43e6d7"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import Dict, List

# Circuit file locations
CIRCUITS_DIR = Path(__file__).parent
AUTO_VERIFY_PATH = CIRCUITS_DIR / "auto_verify.yaml"
AUTO_HEAL_PATH = CIRCUITS_DIR / "auto_heal.yaml"
AUTO_REFRESH_PATH = CIRCUITS_DIR / "auto_refresh.yaml"

# Circuit IDs for external reference
CIRCUIT_IDS = [
    "OPUS_AUTO_VERIFY",
    "OPUS_AUTO_HEAL",
    "OPUS_AUTO_REFRESH",
]


def get_circuit_paths() -> Dict[str, Path]:
    """
    Get paths to all OPUS circuits.

    Returns:
        Dict mapping circuit ID to file path
    """
    return {
        "OPUS_AUTO_VERIFY": AUTO_VERIFY_PATH,
        "OPUS_AUTO_HEAL": AUTO_HEAL_PATH,
        "OPUS_AUTO_REFRESH": AUTO_REFRESH_PATH,
    }


def list_circuits() -> List[str]:
    """
    List all available OPUS circuit IDs.

    Returns:
        List of circuit IDs
    """
    return CIRCUIT_IDS.copy()


__all__ = [
    "CIRCUIT_IDS",
    "CIRCUITS_DIR",
    "AUTO_VERIFY_PATH",
    "AUTO_HEAL_PATH",
    "AUTO_REFRESH_PATH",
    "get_circuit_paths",
    "list_circuits",
]
