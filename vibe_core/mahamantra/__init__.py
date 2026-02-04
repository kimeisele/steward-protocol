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
    "vibe_core.mahamantra.substrate.lotus_core",    # MahamantraLotus
    "vibe_core.mahamantra.substrate.lotus_types",   # LotusNode
    "vibe_core.mahamantra.substrate.mahajana",      # Enums
    "vibe_core.mahamantra.substrate.opcode",        # MantraOpCode
    "vibe_core.mahamantra.substrate.protocol",      # Base Protocols
    "vibe_core.mahamantra.substrate.errors",        # Error Codes
    "vibe_core.mahamantra.substrate.position",      # Position Logic
    "vibe_core.mahamantra.substrate.cell",          # MahaCellUnified
    
    # === PROTOCOLS (The Standard) ===
    "vibe_core.mahamantra.protocols._gad",          # GADBase
    "vibe_core.mahamantra.protocols._header",       # MahaHeader
    "vibe_core.mahamantra.protocols._payload",      # PayloadType
]

# Enable Universal Discovery (Fractal + Core Modules)
enable_universal_discovery(globals(), __file__, CORE_MODULES)

# =============================================================================
# EXPORTS (for IDE support - hints only)
# =============================================================================

__all__ = [
    "MahamantraLotus", "mahamantra", "AkashState", "ExecuteResult",
    "genesis", "dharma", "karma", "moksha",
    "substrate", "protocols", "adapters", "kernel",
]
