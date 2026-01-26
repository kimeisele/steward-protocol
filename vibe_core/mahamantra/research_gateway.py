"""
RESEARCH GATEWAY - Bridge Research to Production
================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart"
— Bhagavad Gita 15.15

PURPOSE:
========

This module bridges the research folder to production code.
It connects research modules to the kernel's heartbeat system.

USAGE:
======

    # In kernel boot or plugin:
    from vibe_core.mahamantra.research_gateway import connect_research

    connect_research(kernel.chaitanya)  # Register with Nrisimha heartbeat

WHAT IT DOES:
=============

1. Creates singleton RolloutTracker
2. Registers with NrisimhaWatchdog.register_proxy()
3. Tracks research module rollout: RESEARCH → PROVEN → INTEGRATING → PRODUCTION
4. Counts heartbeat pulses per module

SSOT: All constants from _seed.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.mahamantra.protocols._seed import PARAMPARA

# Verify genesis
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

if TYPE_CHECKING:
    from vibe_core.services.nrisimha import NrisimhaWatchdog

logger = logging.getLogger("RESEARCH_GATEWAY")

# =============================================================================
# SINGLETON TRACKER
# =============================================================================

_rollout_tracker = None


def get_rollout_tracker():
    """Get singleton RolloutTracker (lazy import to avoid circular deps)."""
    global _rollout_tracker
    if _rollout_tracker is None:
        from vibe_core.mahamantra.protocols._rollout import get_tracker

        _rollout_tracker = get_tracker()
    return _rollout_tracker


# =============================================================================
# RESEARCH MODULES TO TRACK
# =============================================================================

RESEARCH_MODULES: List[Dict[str, Any]] = [
    # Core research with measured efficiency
    {"name": "lotus_radix_n", "efficiency": 1.5},  # Generalized N-level structure
    {"name": "lotus_acintya", "efficiency": 1.37},  # ACINTYA verification
    {"name": "lotus_full_spectrum", "efficiency": 1.6},  # Full spectrum analysis
    {"name": "lotus_tree", "efficiency": 1.4},  # Tree structure
    {"name": "research_lab", "efficiency": 1.37},  # Lab with Lotus structures
    {"name": "gap_analysis", "efficiency": 1.2},  # Gap detection
    {"name": "project_introspection", "efficiency": 1.3},  # Drishti - codebase scan
    {"name": "gut_synthesis", "efficiency": 1.37},  # GUT proof
    {"name": "research_chat", "efficiency": 1.2},  # Internal chat
    {"name": "classification", "efficiency": 1.4},  # Classification system
]


# =============================================================================
# CONNECT FUNCTION - The Bridge
# =============================================================================


def connect_research(nrisimha: "NrisimhaWatchdog") -> Dict[str, Any]:
    """
    Connect research modules to kernel heartbeat.

    This is the BRIDGE from research to production.

    Args:
        nrisimha: The NrisimhaWatchdog instance (kernel.chaitanya)

    Returns:
        Status dict with tracked modules
    """
    tracker = get_rollout_tracker()

    # Register tracker with Nrisimha heartbeat
    nrisimha.register_proxy(tracker)
    logger.info("📡 RolloutTracker registered with Nrisimha heartbeat")

    # Track all research modules
    for module in RESEARCH_MODULES:
        tracker.track(module["name"], efficiency=module["efficiency"])
        logger.debug(f"  + Tracking: {module['name']} (efficiency={module['efficiency']})")

    logger.info(f"🔬 Research Gateway: {len(RESEARCH_MODULES)} modules connected to heartbeat")

    return {
        "success": True,
        "modules_tracked": len(RESEARCH_MODULES),
        "tracker_status": tracker.status,
    }


def get_research_status() -> Dict[str, Any]:
    """Get current research rollout status."""
    tracker = get_rollout_tracker()
    return tracker.status


def is_production_ready(module_name: str) -> bool:
    """Check if a research module is ready for production."""
    tracker = get_rollout_tracker()
    module = tracker.get(module_name)
    if module is None:
        return False
    from vibe_core.mahamantra.protocols._rollout import Stage

    return module.stage == Stage.PRODUCTION


# =============================================================================
# AUTO-CONNECT (Optional - can be called during kernel boot)
# =============================================================================


def auto_connect() -> Optional[Dict[str, Any]]:
    """
    Auto-connect to kernel if available.

    Call this from kernel_impl.py boot sequence:
        from vibe_core.mahamantra.research_gateway import auto_connect
        auto_connect()  # Automatically finds and connects to Nrisimha
    """
    try:
        # Try to get kernel's Nrisimha from DI registry
        from vibe_core.di import ServiceRegistry
        from vibe_core.services.nrisimha import NrisimhaWatchdog

        nrisimha = ServiceRegistry.get(NrisimhaWatchdog)
        if nrisimha is not None:
            return connect_research(nrisimha)

        logger.warning("⚠️ NrisimhaWatchdog not in ServiceRegistry - manual connect required")
        return None

    except ImportError as e:
        logger.warning(f"⚠️ Auto-connect failed (import): {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Auto-connect failed: {e}")
        return None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "connect_research",
    "get_research_status",
    "is_production_ready",
    "auto_connect",
    "get_rollout_tracker",
    "RESEARCH_MODULES",
]
