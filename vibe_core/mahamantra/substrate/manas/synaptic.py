"""
SYNAPTIC — Hebbian Learning for Manas
=======================================

"Neurons that fire together wire together."

Success: w += 0.1 * (1 - w)  [asymptotic to 1.0]
Failure: w -= 0.1 * w        [asymptotic to 0.0]

Extracted from opus_assistant/manas/action_manager.py (_update_synapses).
File-backed JSON persistence for cross-session learning.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("MAHAMANTRA.MANAS.SYNAPTIC")

# Learning rate — matches opus_assistant Hebbian rate
_LEARNING_RATE = 0.1

# Default weight for unknown trigger→action pairs
_DEFAULT_WEIGHT = 0.5


class HebbianSynaptic:
    """Hebbian synaptic learning — file-backed JSON persistence."""

    def __init__(self, state_dir: Optional[Path] = None) -> None:
        self._weights: Dict[str, float] = {}
        self._state_file: Optional[Path] = None
        self._dirty = False

        if state_dir is not None:
            self.set_state_dir(state_dir)

    def set_state_dir(self, state_dir: Path) -> None:
        """Set persistence directory and load existing weights."""
        state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = state_dir / "synaptic_weights.json"
        self._load()

    def get_weight(self, trigger: str, action: str) -> float:
        """Get current synaptic weight for trigger→action pair."""
        key = f"{trigger}→{action}"
        return self._weights.get(key, _DEFAULT_WEIGHT)

    def update(self, trigger: str, action: str, success: bool) -> float:
        """Update weight via Hebbian rule.

        Success: w += 0.1 * (1 - w)  → asymptotic to 1.0
        Failure: w -= 0.1 * w        → asymptotic to 0.0
        """
        key = f"{trigger}→{action}"
        w = self._weights.get(key, _DEFAULT_WEIGHT)

        if success:
            w += _LEARNING_RATE * (1.0 - w)
        else:
            w -= _LEARNING_RATE * w

        # Clamp to [0, 1]
        w = max(0.0, min(1.0, w))
        self._weights[key] = w
        self._dirty = True

        logger.debug("synapse %s: %s → %.3f", "+" if success else "-", key, w)
        return w

    def flush(self) -> None:
        """Persist weights to disk if dirty."""
        if not self._dirty or self._state_file is None:
            return

        try:
            self._state_file.write_text(json.dumps(self._weights, indent=2), encoding="utf-8")
            self._dirty = False
            logger.debug("Synaptic weights persisted: %d entries", len(self._weights))
        except Exception as e:
            logger.warning("Synaptic persist failed: %s", e)

    def _load(self) -> None:
        """Load weights from disk."""
        if self._state_file is None or not self._state_file.exists():
            return

        try:
            data = json.loads(self._state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._weights = {k: float(v) for k, v in data.items()}
                logger.info("Synaptic weights loaded: %d entries", len(self._weights))
        except Exception as e:
            logger.warning("Synaptic load failed: %s", e)

    @property
    def weight_count(self) -> int:
        """Number of learned synaptic connections."""
        return len(self._weights)

    def snapshot(self) -> Dict[str, float]:
        """Return copy of current weights."""
        return dict(self._weights)

    def restore(self, weights: Dict[str, float]) -> None:
        """Restore weights from a dict (counterpart to snapshot()).

        Replaces all current weights. Values are clamped to [0, 1].
        """
        self._weights = {k: max(0.0, min(1.0, float(v))) for k, v in weights.items()}
        self._dirty = True

    def decay(self, factor: float = 0.01) -> int:
        """Apply temporal decay: all weights regress toward 0.5 (default).

        w = w + factor * (0.5 - w)

        Prevents rigidity. Old patterns fade. New patterns dominate.
        Returns count of weights decayed.
        """
        count = 0
        for key in list(self._weights.keys()):
            w = self._weights[key]
            w += factor * (_DEFAULT_WEIGHT - w)
            w = max(0.0, min(1.0, w))
            self._weights[key] = w
            count += 1

        if count:
            self._dirty = True
            logger.debug("Synaptic decay: %d weights regressed by %.3f", count, factor)
        return count

    def trim(self, max_entries: int = 500) -> int:
        """Remove weakest synapses when over capacity.

        Keeps weights closest to 0.0 or 1.0 (most learned).
        Removes weights closest to 0.5 (least decisive).
        """
        if len(self._weights) <= max_entries:
            return 0

        # Sort by decisiveness: |w - 0.5| (high = keep, low = forget)
        scored = sorted(
            self._weights.items(),
            key=lambda kv: abs(kv[1] - _DEFAULT_WEIGHT),
        )
        # Remove least decisive
        to_remove = len(scored) - max_entries
        for key, _w in scored[:to_remove]:
            del self._weights[key]
        self._dirty = True
        logger.info("Synaptic trim: removed %d weak synapses", to_remove)
        return to_remove
