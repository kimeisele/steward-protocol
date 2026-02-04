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

from vibe_core.mahamantra.substrate.wiring import create_hybrid_getattr

# =============================================================================
# LEGACY EXPORTS (Backwards Compatibility)
# =============================================================================
# These are manual mappings for things that don't follow the fractal structure
# or need to be exposed at the root level for legacy reasons.

LEGACY_EXPORTS = {
    # === CORE ===
    "MahamantraLotus": ("vibe_core.mahamantra.substrate.lotus_core", "MahamantraLotus"),
    "mahamantra": ("vibe_core.mahamantra.substrate.lotus_core", "get_mahamantra"),
    "lotus": ("vibe_core.mahamantra.substrate.lotus_core", "get_mahamantra"),
    "AkashState": ("vibe_core.mahamantra.seed.types", "AkashState"),
    "ExecuteResult": ("vibe_core.mahamantra.seed.types", "ExecuteResult"),
    "GitaRoute": ("vibe_core.mahamantra.seed.types", "GitaRoute"),
    "RouteResult": ("vibe_core.mahamantra.seed.types", "RouteResult"),
    "VibrationState": ("vibe_core.mahamantra.seed.types", "VibrationState"),
    "LotusNode": ("vibe_core.mahamantra.substrate.lotus_types", "LotusNode"),
    "LotusPath": ("vibe_core.mahamantra.substrate.lotus_types", "LotusPath"),
    "PositionRegistry": ("vibe_core.mahamantra.lotus_projection", "PositionRegistry"),
    "cli_auto": ("vibe_core.mahamantra.cli.auto", "cli_auto"),

    # === SEED / CONSTANTS ===
    "ALL_GUARDIANS": ("vibe_core.mahamantra.substrate.seed", "ALL_GUARDIANS"),
    "WORDS": ("vibe_core.mahamantra.protocols._seed_cell", "WORDS"),
    "TRINITY": ("vibe_core.mahamantra.protocols._seed_cell", "TRINITY"),
    "QUARTERS": ("vibe_core.mahamantra.protocols._seed_cell", "QUARTERS"),
    "PANCHA": ("vibe_core.mahamantra.protocols._seed_cell", "PANCHA"),
    "HALVES": ("vibe_core.mahamantra.protocols._seed_cell", "HALVES"),
    "HARE_COUNT": ("vibe_core.mahamantra.protocols._seed_cell", "HARE_COUNT"),
    "KRISHNA_COUNT": ("vibe_core.mahamantra.protocols._seed_cell", "KRISHNA_COUNT"),
    "RAMA_COUNT": ("vibe_core.mahamantra.protocols._seed_cell", "RAMA_COUNT"),
    "KSETRAJNA": ("vibe_core.mahamantra.protocols._seed_cell", "KSETRAJNA"),
    "HALF_SIZE": ("vibe_core.mahamantra.protocols._seed_cell", "HALF_SIZE"),
    "LILA": ("vibe_core.mahamantra.protocols._seed_cell", "LILA"),
    "KSHETRA": ("vibe_core.mahamantra.protocols._seed_cell", "KSHETRA"),
    "NAVA": ("vibe_core.mahamantra.protocols._seed_cell", "NAVA"),
    "SHARANAGATI": ("vibe_core.mahamantra.protocols._seed_cell", "SHARANAGATI"),
    "SEVEN": ("vibe_core.mahamantra.protocols._seed_cell", "SEVEN"),
    "TEN": ("vibe_core.mahamantra.protocols._seed_cell", "TEN"),
    "MAHAJANA_COUNT": ("vibe_core.mahamantra.protocols._seed_cell", "MAHAJANA_COUNT"),
    "QUALITIES": ("vibe_core.mahamantra.protocols._seed_cell", "QUALITIES"),
    "MALA": ("vibe_core.mahamantra.protocols._seed_cell", "MALA"),
    "MAHA_QUANTUM": ("vibe_core.mahamantra.protocols._seed_cell", "MAHA_QUANTUM"),
    "GITA_CHAPTERS": ("vibe_core.mahamantra.protocols._seed_cell", "GITA_CHAPTERS"),
    "PARAMPARA": ("vibe_core.mahamantra.protocols._seed_cell", "PARAMPARA"),

    # === PROTOCOLS ===
    "GADBase": ("vibe_core.mahamantra.protocols._gad", "GADBase"),
    "GADProtocol": ("vibe_core.mahamantra.protocols._gad", "GADProtocol"),
    "MahaCell": ("vibe_core.mahamantra.protocols._header", "MahaCell"),
    "MahaHeader": ("vibe_core.mahamantra.protocols._header", "MahaHeader"),
    "PayloadType": ("vibe_core.mahamantra.protocols._payload", "PayloadType"),
    "PayloadQuarter": ("vibe_core.mahamantra.protocols._payload", "PayloadQuarter"),
    "SiksastakamOp": ("vibe_core.mahamantra.protocols._payload", "SiksastakamOp"),
    "ATTRACTOR_FIXED": ("vibe_core.mahamantra.protocols._maha_compute", "ATTRACTOR_FIXED"),
    "ATTRACTOR_CYCLE": ("vibe_core.mahamantra.protocols._maha_compute", "ATTRACTOR_CYCLE"),
    "get_gita_chapter": ("vibe_core.mahamantra.protocols._maha_compute", "get_gita_chapter"),
    "get_gita_insight": ("vibe_core.mahamantra.protocols._maha_compute", "get_gita_insight"),
    "GraceProtocol": ("vibe_core.mahamantra.protocols.offering", "GraceProtocol"),

    # === SUBSTRATE ===
    "WorkerProtocol": ("vibe_core.mahamantra.substrate.protocol", "WorkerProtocol"),
    "HeadProtocol": ("vibe_core.mahamantra.substrate.protocol", "HeadProtocol"),
    "MantraProtocol": ("vibe_core.mahamantra.substrate.protocol", "MantraProtocol"),
    "ProtocolRegistry": ("vibe_core.mahamantra.substrate.protocol", "ProtocolRegistry"),
    "Mahajana": ("vibe_core.mahamantra.substrate.mahajana", "Mahajana"),
    "Avatara": ("vibe_core.mahamantra.substrate.mahajana", "Avatara"),
    "MantraOpCode": ("vibe_core.mahamantra.substrate.opcode", "MantraOpCode"),
    "BootMode": ("vibe_core.mahamantra.substrate.boot", "BootMode"),
    "ProcessManager": ("vibe_core.mahamantra.substrate.process_manager", "ProcessManager"),
    "ProcessStatus": ("vibe_core.mahamantra.substrate.process_manager", "ProcessStatus"),
    "AgentProcessInfo": ("vibe_core.mahamantra.substrate.process_manager", "AgentProcessInfo"),
    "ErrorCode": ("vibe_core.mahamantra.substrate.errors", "ErrorCode"),
    "StructuredError": ("vibe_core.mahamantra.substrate.errors", "StructuredError"),
    "ErrorCategory": ("vibe_core.mahamantra.substrate.errors", "ErrorCategory"),
    "kernel_fault": ("vibe_core.mahamantra.substrate.errors", "kernel_fault"),
    "LineageBlock": ("vibe_core.mahamantra.substrate.lineage", "LineageBlock"),
    "LineageChain": ("vibe_core.mahamantra.substrate.lineage", "LineageChain"),
    "LineageEventType": ("vibe_core.mahamantra.substrate.lineage", "LineageEventType"),
    "VibeLedger": ("vibe_core.mahamantra.substrate.ledger", "VibeLedger"),
    "InMemoryLedger": ("vibe_core.mahamantra.substrate.ledger", "InMemoryLedger"),
    "SQLiteLedger": ("vibe_core.mahamantra.substrate.ledger", "SQLiteLedger"),
    "PhoenixConfig": ("vibe_core.mahamantra.substrate.config", "PhoenixConfig"),
    "get_config": ("vibe_core.mahamantra.substrate.config", "get_config"),
    "reset_config": ("vibe_core.mahamantra.substrate.config", "reset_config"),
    "set_config": ("vibe_core.mahamantra.substrate.config", "set_config"),
    "SamskaraProtocol": ("vibe_core.mahamantra.substrate.samskara", "SamskaraProtocol"),
    "Phase": ("vibe_core.mahamantra.substrate.samskara", "Phase"),
    "PhaseStatus": ("vibe_core.mahamantra.substrate.samskara", "PhaseStatus"),
    "PhaseResult": ("vibe_core.mahamantra.substrate.samskara", "PhaseResult"),
    "PipelineContext": ("vibe_core.mahamantra.substrate.samskara", "PipelineContext"),
    "PipelineExecutor": ("vibe_core.mahamantra.substrate.samskara", "PipelineExecutor"),
    "MahaModularSynth": ("vibe_core.mahamantra.substrate.algorithm.maha", "MahaModularSynth"),
    "MahaCluster": ("vibe_core.mahamantra.substrate.cluster", "MahaCluster"),
    "MahaCellUnified": ("vibe_core.mahamantra.substrate.cell", "MahaCellUnified"),
    "MahaFile": ("vibe_core.mahamantra.adapters.maha_format", "MahaFile"),
    "SankirtanChamber": ("vibe_core.mahamantra.substrate.chamber", "SankirtanChamber"),
    "MahaState": ("vibe_core.mahamantra.substrate.maha_state", "MahaState"),
    "StateEntry": ("vibe_core.mahamantra.substrate.maha_state", "StateEntry"),
    "get_maha_state": ("vibe_core.mahamantra.substrate.maha_state", "get_maha_state"),
    "pierce": ("vibe_core.mahamantra.substrate.maha_state", "pierce"),
    "get_position": ("vibe_core.mahamantra.substrate.position", "get_position"),
    
    # === ADAPTERS ===
    "TulasiGate": ("vibe_core.mahamantra.adapters.tulasi_gate", "TulasiGate"),
    
    # === KERNEL ===
    "kernel_singularity": ("vibe_core.mahamantra.kernel", "singularity"),
}

# =============================================================================
# HYBRID DISCOVERY (Fractal + Legacy)
# =============================================================================
# 1. Tries fractal discovery (folder structure)
# 2. Falls back to LEGACY_EXPORTS (backwards compatibility)
# 3. Raises AttributeError if not found

__getattr__ = create_hybrid_getattr(__file__, LEGACY_EXPORTS)

# =============================================================================
# EXPORTS (for IDE support)
# =============================================================================

__all__ = list(LEGACY_EXPORTS.keys()) + [
    # Explicitly list modules that are commonly star-imported or expected
    "genesis", "dharma", "karma", "moksha",
    "substrate", "protocols", "adapters", "kernel",
]
