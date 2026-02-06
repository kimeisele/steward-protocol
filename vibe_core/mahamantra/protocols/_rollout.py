"""
ROLLOUT PROTOCOL - Simple Heartbeat-Compatible Tracker
======================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

SIMPLE: Registers with Nrisimha, counts steps, tracks stage.

USAGE:
    from vibe_core.mahamantra.protocols._rollout import RolloutTracker

    tracker = RolloutTracker()
    nrisimha.register_proxy(tracker)  # Now receives on_mantra_pulse()

SSOT: Constants from _seed.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Final, List, Optional

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHA_QUANTUM,
    PARAMPARA,
    QUARTERS,
    SHARANAGATI,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = SHARANAGATI
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

# Verify genesis
assert int(__genesis__, WORDS) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("ROLLOUT")

# =============================================================================
# CONSTANTS (derived from _seed.py)
# =============================================================================

# Steps per stage = WORDS × QUARTERS = 64
STEPS_PER_STAGE: Final[int] = WORDS * QUARTERS  # 64

# Minimum efficiency = MAHA_QUANTUM / 100 = 1.37x
MIN_EFFICIENCY: Final[float] = MAHA_QUANTUM / 100  # 1.37


# =============================================================================
# STAGES (4 = QUARTERS)
# =============================================================================


class Stage(str, Enum):
    """4 rollout stages = QUARTERS."""

    RESEARCH = "research"
    PROVEN = "proven"
    INTEGRATING = "integrating"
    PRODUCTION = "production"


# =============================================================================
# SIMPLE TRACKER
# =============================================================================


@dataclass
class ModuleStatus:
    """Status of one module being rolled out."""

    name: str
    stage: Stage = Stage.RESEARCH
    step_count: int = 0
    efficiency: float = 1.0
    has_tests: bool = False
    imports_seed: bool = False

    @property
    def is_ready(self) -> bool:
        """Ready for next stage?"""
        return self.step_count >= STEPS_PER_STAGE and self.efficiency >= MIN_EFFICIENCY


class RolloutTracker:
    """
    Simple rollout tracker that listens to Nrisimha heartbeat.

    Implements on_mantra_pulse(opcode) for Nrisimha.register_proxy().
    """

    def __init__(self):
        self._modules: Dict[str, ModuleStatus] = {}
        self._total_pulses: int = 0
        self._last_pulse: Optional[datetime] = None

    # =========================================================================
    # HEARTBEAT LISTENER (called by Nrisimha)
    # =========================================================================

    def on_mantra_pulse(self, opcode: object) -> None:
        """
        Called by Nrisimha on each tick of the 16-step cycle.

        This is the PARAMPARA connection - we hear the heartbeat.
        """
        self._total_pulses += KSETRAJNA
        self._last_pulse = datetime.utcnow()

        # Increment step count for all tracked modules
        for module in self._modules.values():
            if module.stage != Stage.PRODUCTION:
                module.step_count += KSETRAJNA

                # Auto-advance if ready
                if module.is_ready:
                    self._advance(module)

    # =========================================================================
    # MODULE TRACKING
    # =========================================================================

    def track(self, name: str, efficiency: float = 1.0) -> ModuleStatus:
        """Start tracking a module."""
        if name not in self._modules:
            self._modules[name] = ModuleStatus(name=name, efficiency=efficiency)
        return self._modules[name]

    def get(self, name: str) -> Optional[ModuleStatus]:
        """Get module status."""
        return self._modules.get(name)

    def _advance(self, module: ModuleStatus) -> bool:
        """Advance module to next stage."""
        stages = list(Stage)
        idx = stages.index(module.stage)

        if idx < len(stages) - KSETRAJNA:
            old = module.stage
            module.stage = stages[idx + KSETRAJNA]
            module.step_count = 0  # Reset for new stage
            logger.info(f"📈 {module.name}: {old.value} → {module.stage.value}")
            return True
        return False

    # =========================================================================
    # STATUS
    # =========================================================================

    @property
    def status(self) -> Dict[str, object]:
        """Get overall status."""
        by_stage = {s.value: [] for s in Stage}
        for m in self._modules.values():
            by_stage[m.stage.value].append(m.name)

        return {
            "total_pulses": self._total_pulses,
            "last_pulse": self._last_pulse.isoformat() if self._last_pulse else None,
            "modules": len(self._modules),
            "by_stage": by_stage,
            "ready_for_production": [
                m.name for m in self._modules.values() if m.stage == Stage.INTEGRATING and m.is_ready
            ],
        }


# =============================================================================
# SINGLETON
# =============================================================================

_tracker: Optional[RolloutTracker] = None


def get_tracker() -> RolloutTracker:
    """Get singleton tracker."""
    global _tracker
    if _tracker is None:
        _tracker = RolloutTracker()
    return _tracker


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "STEPS_PER_STAGE",
    "MIN_EFFICIENCY",
    "Stage",
    "ModuleStatus",
    "RolloutTracker",
    "get_tracker",
]
