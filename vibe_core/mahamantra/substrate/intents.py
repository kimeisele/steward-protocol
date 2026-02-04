"""
INTENTS - Die zentrale Intent-Registry (SSOT)
=============================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
— Bhagavad Gita 10.8

DYNAMIC LOADING from knowledge/guardian_intents.yaml.
NO HARDCODED PYTHON DICTS. Prompt as Infrastructure.

STRUKTUR:
    Position (0-15) → Liste von Keywords die dieser Guardian handhabt

WATERTIGHT: No hardcoded intents in mahajana files.
"""
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA, QUARTERS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0x50f34ca4"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import Dict, Optional, Tuple

# =============================================================================
# YAML LOADER - Runtime Intent Loading
# =============================================================================
# "Prompt as Infrastructure" - NO STATIC DICTS

_INTENT_CACHE: Optional[Dict[int, Tuple[str, ...]]] = None
_YAML_PATH = Path(__file__).parent.parent.parent.parent / "knowledge" / "guardian_intents.yaml"


def _load_intents_from_yaml() -> Dict[int, Tuple[str, ...]]:
    """
    Load intents from YAML at runtime.

    CONSTITUTION COMPLIANCE:
        - Single Source of Truth: knowledge/guardian_intents.yaml
        - No hardcoded dicts in Python
        - Cached after first load
    """
    global _INTENT_CACHE

    if _INTENT_CACHE is not None:
        return _INTENT_CACHE

    try:
        import yaml

        if not _YAML_PATH.exists():
            # Fallback: empty map (graceful degradation)
            _INTENT_CACHE = {}
            return _INTENT_CACHE

        with open(_YAML_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        positions = data.get("positions", {})
        result: Dict[int, Tuple[str, ...]] = {}

        for pos_str, pos_data in positions.items():
            pos = int(pos_str)
            keywords = pos_data.get("keywords", [])
            result[pos] = tuple(keywords)

        _INTENT_CACHE = result
        return _INTENT_CACHE

    except Exception:
        # ARJUNA PATTERN: Graceful degradation
        _INTENT_CACHE = {}
        return _INTENT_CACHE


def _get_intent_map() -> Dict[int, Tuple[str, ...]]:
    """Get the intent map (lazy loaded from YAML)."""
    return _load_intents_from_yaml()


# =============================================================================
# BACKWARD COMPATIBLE INTERFACE
# =============================================================================
# INTENT_MAP is now a property-like access via function
# For code that does `from intents import INTENT_MAP`, we provide a module-level reference
# that gets populated on first access.


class _IntentMapProxy:
    """Proxy that loads YAML on first access."""

    def __getitem__(self, key: int) -> Tuple[str, ...]:
        return _get_intent_map().get(key, ())

    def get(self, key: int, default: Tuple[str, ...] = ()) -> Tuple[str, ...]:
        return _get_intent_map().get(key, default)

    def items(self):
        return _get_intent_map().items()

    def keys(self):
        return _get_intent_map().keys()

    def values(self):
        return _get_intent_map().values()

    def __iter__(self):
        return iter(_get_intent_map())

    def __len__(self):
        return len(_get_intent_map())

    def __contains__(self, key: int) -> bool:
        return key in _get_intent_map()


INTENT_MAP = _IntentMapProxy()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_intents(position: int) -> Tuple[str, ...]:
    """Get intents for a position. Returns empty tuple if invalid."""
    return INTENT_MAP.get(position, ())


def get_position_for_intent(intent: str) -> int:
    """Find which position handles an intent. Returns -1 if not found."""
    intent_lower = intent.lower()
    for pos, intents in INTENT_MAP.items():
        if intent_lower in intents:
            return pos
    return -KSETRAJNA


# =============================================================================
# RUNTIME FUNCTIONS
# =============================================================================


def reload_intents() -> Dict[int, Tuple[str, ...]]:
    """
    Force reload intents from YAML.

    Use this after modifying knowledge/guardian_intents.yaml at runtime.
    """
    global _INTENT_CACHE
    _INTENT_CACHE = None
    return _load_intents_from_yaml()


def get_yaml_path() -> Path:
    """Get the path to the YAML file (for debugging/tooling)."""
    return _YAML_PATH


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "INTENT_MAP",
    "get_intents",
    "get_position_for_intent",
    "reload_intents",
    "get_yaml_path",
]
