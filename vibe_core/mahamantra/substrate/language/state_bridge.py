"""
STATE BRIDGE — MahaState → StateVector extraction
===================================================

Thin bridge: reads MahaState.get_status() and compresses it into a
StateVector for the composer. No logic beyond numeric extraction.

The language engine calls extract_state_vector() once per generate() call.
The composer uses the StateVector to bias word selection toward reality.
"""

from __future__ import annotations

import logging

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    SHARANAGATI,
)
from vibe_core.mahamantra.substrate.language.types import StateVector

logger = logging.getLogger("MAHA_LANGUAGE")

# Guna ordinals (same as GunaClassifier uses)
_GUNA_ORD = {"TAMAS": 0, "RAJAS": KSETRAJNA, "SATTVA": HALVES}

# Max systems that MahaState wraps (prakriti, state_service, sync_holon,
# weaver, cognitive_weaver, guna_classifier)
_MAX_SYSTEMS = SHARANAGATI  # 6


def extract_state_vector(prana_level: int = 0) -> StateVector:
    """Extract a StateVector from MahaState.get_status().

    Gracefully degrades: if MahaState is unavailable, returns defaults.
    All fields are numeric. No keywords enter the composer.

    Args:
        prana_level: total antaranga prana from engine resonance stage.
    """
    try:
        from vibe_core.mahamantra.substrate.maha_state import (
            KISHORA_MAX_STALE,
            MahaState,
        )

        state = MahaState.get_instance()
        status = state.get_status()

        # Guna: try classifier, fall back to RAJAS
        guna = KSETRAJNA  # RAJAS default
        if state.guna_classifier is not None:
            try:
                from pathlib import Path

                result = state.diagnose_guna(Path.cwd())
                if result is not None:
                    guna = _GUNA_ORD.get(result.name, KSETRAJNA)
            except Exception:
                pass

        # Systems alive count
        systems = status.get("systems", {})
        systems_alive = sum(KSETRAJNA for v in systems.values() if v is True) if isinstance(systems, dict) else 0

        # Uptime ratio clamped to [0, 1]
        uptime_s = float(status.get("uptime_seconds", 0))
        max_stale_s = KISHORA_MAX_STALE * 60  # minutes → seconds
        uptime_ratio = min(1.0, uptime_s / max(max_stale_s, KSETRAJNA))

        return StateVector(
            guna=guna,
            entry_count=int(status.get("entries_count", 0)),
            boot_count=int(status.get("boot_count", 0)),
            uptime_ratio=uptime_ratio,
            systems_alive=systems_alive,
            dirty=bool(status.get("dirty", False)),
            prana_level=prana_level,
        )

    except Exception as exc:
        logger.debug("StateVector extraction failed (graceful): %s", exc)
        return StateVector(prana_level=prana_level)
