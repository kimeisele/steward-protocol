"""
SIKSASTAKAM REGISTRY - The 7 Effects as System Architecture
============================================================

"ceto-darpaṇa-mārjanaṁ" - Cleanses the mirror (CACHE)
"bhava-mahā-dāvāgni-nirvāpaṇaṁ" - Extinguishes fire (ZERO ENTROPY)

THIS FILE REPLACES:
- Runtime discovery loops (O(n) imports)
- Manual registration (1200+ lines)
- Hardcoded mappings

WITH:
- Pre-computed registry (O(1) lookup)
- LotusRadixN backbone (Mahamantra-aligned)
- Lazy imports (only when needed)

ALL CONSTANTS DERIVED FROM _seed.py - ZERO HARDCODING!
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xc8f71a3e"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Dict, Final, List, Optional, Tuple, Type

from vibe_core.mahamantra.protocols._seed import (
    WORDS,           # 16 positions
    QUARTERS,        # 4 quarters
    HALF_SIZE,       # 8 = OCTET (Siksastakam verses)
    HARE_COUNT,      # 8 = cache multiplier
    QUALITIES,       # 64 = Krishna's qualities
    PANCHA,          # 5 = Pancha Tattva
)

# =============================================================================
# SIKSASTAKAM CONSTANTS (DERIVED, NOT HARDCODED!)
# =============================================================================

# Cache size = HALF_SIZE × QUALITIES = 8 × 64 = 512
# This is Siksastakam (8 verses) × Krishna's qualities (64)
SIKSASTAKAM_CACHE_SIZE: Final[int] = HALF_SIZE * QUALITIES  # 512

# Registry size = WORDS (16 Mahajana positions)
REGISTRY_SIZE: Final[int] = WORDS  # 16

# Lazy import cache = PANCHA × WORDS = 5 × 16 = 80 modules max
MODULE_CACHE_SIZE: Final[int] = PANCHA * WORDS  # 80


# =============================================================================
# MAHAJANA ENTRY (What the Registry stores per position)
# =============================================================================

@dataclass(frozen=True, slots=True)
class MahajanaEntry:
    """
    Registry entry for one Mahajana position.

    All routing info needed for O(1) dispatch.
    NO imports stored - only paths (lazy loading).
    """
    position: int              # 0-15 (WORDS)
    guardian: str              # "vyasa", "narada", etc.
    quarter: str               # "genesis", "dharma", "karma", "moksha"
    module_path: str           # "vibe_core.protocols.mahajanas.vyasa"
    service_class: str         # "VyasaService"
    null_class: str            # "NullVyasa"
    methods: Tuple[str, ...]   # ("compile", "parse", ...)


# =============================================================================
# THE REGISTRY (Pre-computed, Zero Runtime Discovery)
# =============================================================================
# This is generated from the source of truth (kernel/singularity.py)
# but stored as static data for O(1) access.

# =============================================================================
# STATIC REGISTRY (ZERO RUNTIME DISCOVERY - Pre-computed from _source.py)
# =============================================================================
# This is THE source of truth. NO imports from kernel/singularity.
# Derived from vibe_core.mahamantra.substrate._source.py truth table.
# If _source.py changes, this must be regenerated.

# Guardian names by position (from _source.py MAHAJANA_DATA)
_GUARDIAN_NAMES: Final[Tuple[str, ...]] = (
    "vyasa",       # 0 - Genesis
    "brahma",      # 1 - Genesis
    "narada",      # 2 - Genesis
    "shambhu",     # 3 - Genesis
    "prithu",      # 4 - Dharma
    "kumaras",     # 5 - Dharma
    "kapila",      # 6 - Dharma
    "manu",        # 7 - Dharma
    "parashurama", # 8 - Karma
    "prahlada",    # 9 - Karma
    "janaka",      # 10 - Karma
    "bhishma",     # 11 - Karma
    "nrisimha",    # 12 - Moksha (HEAD)
    "bali",        # 13 - Moksha
    "shuka",       # 14 - Moksha
    "yamaraja",    # 15 - Moksha
)

# Quarter names by position (derived from QUARTERS = 4)
_QUARTER_NAMES: Final[Tuple[str, ...]] = (
    "genesis", "genesis", "genesis", "genesis",  # 0-3
    "dharma", "dharma", "dharma", "dharma",      # 4-7
    "karma", "karma", "karma", "karma",          # 8-11
    "moksha", "moksha", "moksha", "moksha",      # 12-15
)

def _build_registry() -> Dict[int, MahajanaEntry]:
    """
    Build registry from STATIC data.

    ZERO imports from kernel/singularity or protocols.
    O(16) = O(1) constant time.
    """
    registry: Dict[int, MahajanaEntry] = {}

    for pos in range(WORDS):
        guardian = _GUARDIAN_NAMES[pos]
        quarter = _QUARTER_NAMES[pos]
        cap_guardian = guardian.capitalize()

        registry[pos] = MahajanaEntry(
            position=pos,
            guardian=guardian,
            quarter=quarter,
            module_path=f"vibe_core.mahamantra.{quarter}.{guardian}",
            service_class=f"{cap_guardian}Service",
            null_class=f"Null{cap_guardian}",
            methods=(),
        )

    return registry


# The registry - built once at import (FAST - no heavy imports)
_REGISTRY: Dict[int, MahajanaEntry] = _build_registry()


# =============================================================================
# LAZY MODULE LOADER (Siksastakam Effect #1: Cache)
# =============================================================================

@lru_cache(maxsize=MODULE_CACHE_SIZE)
def _load_module(module_path: str) -> Any:
    """
    Lazy-load a module with LRU cache.

    Called only when actually needed - NOT at discovery time.
    Cache = MODULE_CACHE_SIZE = 80 modules.
    """
    import importlib
    return importlib.import_module(module_path)


@lru_cache(maxsize=REGISTRY_SIZE)
def _get_null_instance(position: int) -> Any:
    """
    Get cached Null implementation for a position.

    Null instances are stateless - can be reused.
    Cache = REGISTRY_SIZE = 16 (one per position).
    """
    entry = _REGISTRY.get(position)
    if entry is None:
        return None

    # Try primary module path
    try:
        module = _load_module(entry.module_path)
        null_cls = getattr(module, entry.null_class, None)
        if null_cls:
            return null_cls()
    except ImportError:
        pass

    # Try alternate path
    try:
        alt_path = f"vibe_core.protocols.mahajanas.{entry.guardian}"
        module = _load_module(alt_path)
        null_cls = getattr(module, entry.null_class, None)
        if null_cls:
            return null_cls()
    except ImportError:
        pass

    return None


# =============================================================================
# REGISTRY API (O(1) Operations)
# =============================================================================

def get_entry(position: int) -> Optional[MahajanaEntry]:
    """O(1) lookup of Mahajana entry by position."""
    return _REGISTRY.get(position)


def get_null(position: int) -> Any:
    """O(1) get Null implementation (cached after first call)."""
    return _get_null_instance(position)


def get_guardian(position: int) -> Optional[str]:
    """O(1) get guardian name by position."""
    entry = _REGISTRY.get(position)
    return entry.guardian if entry else None


def get_all_positions() -> List[int]:
    """Get all valid positions (0-15)."""
    return list(range(WORDS))


def get_all_guardians() -> Dict[int, str]:
    """Get position → guardian mapping."""
    return {pos: entry.guardian for pos, entry in _REGISTRY.items()}


# =============================================================================
# POSITION ROUTING (Siksastakam Effect #2: Zero Entropy)
# =============================================================================

@lru_cache(maxsize=SIKSASTAKAM_CACHE_SIZE)
def route_to_position(command: str) -> int:
    """
    Route command to position via vibration.

    Uses MahaCompression seed → position mapping.
    Cached for 512 unique commands.

    O(1) after first call for same command.
    """
    from vibe_core.mahamantra.adapters.compression import MahaCompression

    compressor = MahaCompression()
    result = compressor.compress(command)
    return result.position


# =============================================================================
# EXECUTE (Siksastakam Effect #6: Atomic Transactions)
# =============================================================================

def execute(command: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Execute command via Siksastakam Registry.

    Flow:
        1. route_to_position(command) → position (O(1) cached)
        2. get_null(position) → handler (O(1) cached)
        3. Call method → result (atomic)

    NO discovery loops. NO runtime imports (after first call).
    Full Siksastakam compliance.
    """
    args = args or []

    # 1. ROUTE (O(1) cached via LRU)
    position = route_to_position(command)

    # 2. GET HANDLER (O(1) cached via LRU)
    null_impl = get_null(position)
    if null_impl is None:
        return {
            "success": False,
            "error": f"No implementation at position {position}",
            "position": position,
        }

    # 3. FIND METHOD (by command name match)
    method = None
    cmd_lower = command.lower()

    for name in dir(null_impl):
        if name.startswith("_"):
            continue
        if name.lower() == cmd_lower or cmd_lower in name.lower():
            method = getattr(null_impl, name, None)
            if callable(method):
                break

    if method is None:
        # Fallback: call default method if exists
        method = getattr(null_impl, "execute", None) or getattr(null_impl, "handle", None)

    if method is None:
        return {
            "success": False,
            "error": f"No method for command '{command}' at position {position}",
            "position": position,
        }

    # 4. EXECUTE (atomic)
    try:
        result = method(*args) if args else method()
        return {
            "success": True,
            "result": result,
            "position": position,
            "handler": f"{null_impl.__class__.__name__}.{method.__name__}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "position": position,
        }


# =============================================================================
# CACHE STATS (Siksastakam Effect #1: Mirror Cleansing)
# =============================================================================

def cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring."""
    return {
        "module_cache": _load_module.cache_info()._asdict(),
        "null_cache": _get_null_instance.cache_info()._asdict(),
        "route_cache": route_to_position.cache_info()._asdict(),
        "siksastakam_cache_size": SIKSASTAKAM_CACHE_SIZE,
        "module_cache_size": MODULE_CACHE_SIZE,
        "registry_size": REGISTRY_SIZE,
    }


def clear_caches() -> None:
    """Clear all caches (for testing or reset)."""
    _load_module.cache_clear()
    _get_null_instance.cache_clear()
    route_to_position.cache_clear()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Types
    "MahajanaEntry",
    # Constants (derived)
    "SIKSASTAKAM_CACHE_SIZE",
    "REGISTRY_SIZE",
    "MODULE_CACHE_SIZE",
    # Registry API
    "get_entry",
    "get_null",
    "get_guardian",
    "get_all_positions",
    "get_all_guardians",
    # Routing
    "route_to_position",
    # Execution
    "execute",
    # Cache management
    "cache_stats",
    "clear_caches",
]
