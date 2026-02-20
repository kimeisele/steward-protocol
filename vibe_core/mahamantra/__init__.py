"""
MAHAMANTRA - The Sovereign Singularity (Level -2)
================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

SIKSASTAKAM ARCHITECTURE (O(1) Import):
    This module uses PURE LAZY LOADING via FRACTAL DISCOVERY.
    Import time: <20ms (vs 200ms+ before)

    Effect #1: ceto-darpaṇa-mārjanaṁ (Cache) - Only load what's accessed
    Effect #2: bhava-mahā-dāvāgni (Zero Entropy) - No eager imports

USAGE:
    from vibe_core.mahamantra import MahamantraLotus
    m = MahamantraLotus()
    m.bootstrap()
    result = m.execute("analyze this")
"""

from __future__ import annotations

__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"

# LOTUS FINDER: Install import-level routing BEFORE any substrate imports.
# This makes Python's import system go through the Lotus principle:
# FOLDER = EXISTENCE = WIRING. Files can be moved without breaking imports.
from vibe_core.mahamantra.substrate.lotus_finder import install as _install_lotus_finder
_install_lotus_finder()

from vibe_core.mahamantra.substrate.wiring import enable_universal_discovery

# =============================================================================
# UNIVERSAL DISCOVERY (The "Semantic Router" for Code)
# =============================================================================
# Instead of hardcoded "Legacy Maps", we define the CORE MODULES of the system.
# The Wiring Protocol dynamically scans these modules to resolve symbols.
#
# RULE: If a symbol is in a Core Module, it is available at Root.
# ENTROPY REDUCTION: 100+ manual lines replaced by 12 module definitions.

CORE_MODULES = [
    # === SEED (The DNA) ===
    "vibe_core.mahamantra.seed.types",
    "vibe_core.mahamantra.protocols._seed_cell",

    # === SUBSTRATE (The Engine) ===
    "vibe_core.mahamantra.substrate.lotus_core",    # MahamantraLotus, mahamantra, lotus
    "vibe_core.mahamantra.substrate.lotus_types",   # LotusNode
    "vibe_core.mahamantra.substrate.mahajana",      # Enums
    "vibe_core.mahamantra.substrate.opcode",        # MantraOpCode
    "vibe_core.mahamantra.substrate.protocol",      # Base Protocols
    "vibe_core.mahamantra.substrate.errors",        # Error Codes
    "vibe_core.mahamantra.substrate.position",      # Position Logic
    "vibe_core.mahamantra.substrate.cell",          # MahaCellUnified
    "vibe_core.mahamantra.substrate.config",        # PhoenixConfig
    "vibe_core.mahamantra.substrate.boot",          # BootMode
    "vibe_core.mahamantra.substrate.event_types",   # EventType, EventColor (zero-dep leaf)
    "vibe_core.mahamantra.substrate.event_bus",     # EventBus
    "vibe_core.mahamantra.substrate.ledger",        # SQLiteLedger
    "vibe_core.mahamantra.substrate.lineage",       # LineageChain, LineageBlock, LineageEventType
    "vibe_core.mahamantra.substrate.shuddhi",       # ShuddhiProtocol, ShuddhiStatus, ShuddhiResult
    "vibe_core.mahamantra.substrate.process_manager",  # ProcessManager, AgentProcessInfo, ProcessStatus
    "vibe_core.mahamantra.substrate.maha_state",      # MahaState, StateEntry, get_maha_state, pierce
    
    # === PROTOCOLS (The Standard) ===
    "vibe_core.mahamantra.protocols._gad",          # GADBase
    "vibe_core.mahamantra.protocols._header",       # MahaHeader
    "vibe_core.mahamantra.protocols._payload",      # PayloadType
]

# Enable Universal Discovery (Fractal + Core Modules)
enable_universal_discovery(globals(), __file__, CORE_MODULES)

# =============================================================================
# EXPLICIT ALIASES (variables that universal discovery can't resolve)
# =============================================================================
# lotus is an alias for the mahamantra singleton (from lotus_core.py)
# Universal discovery only resolves classes/functions, not module-level variables.
_original_getattr = globals().get("__getattr__")

def __getattr__(name):
    if name == "lotus":
        from vibe_core.mahamantra.substrate.lotus_core import lotus
        return lotus
    if _original_getattr is not None:
        return _original_getattr(name)
    raise AttributeError(f"module 'vibe_core.mahamantra' has no attribute {name!r}")

def __dir__():
    """Module-level __dir__ so lazy __getattr__ names appear in dir()."""
    names = set(globals().keys())
    names.update(__all__)
    return sorted(n for n in names if not n.startswith("_"))


# =============================================================================
# EXPORTS (for IDE support - hints only)
# =============================================================================

__all__ = [
    "MahamantraLotus", "mahamantra", "AkashState", "ExecuteResult", "PhoenixConfig",
    "genesis", "dharma", "karma", "moksha",
    "substrate", "protocols", "adapters", "kernel",
]
