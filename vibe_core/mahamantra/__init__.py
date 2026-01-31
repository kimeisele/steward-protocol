"""
MAHAMANTRA - The Sovereign Singularity (Level -2)
================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

SIKSASTAKAM ARCHITECTURE (O(1) Import):
    This module uses PURE LAZY LOADING.
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

# =============================================================================
# ZERO EAGER IMPORTS - Everything via __getattr__
# =============================================================================
# This is the Siksastakam way: Only manifest what is requested.
# Import time should be <20ms now.


def __getattr__(name: str):
    """
    Lazy load EVERYTHING only when accessed.

    This eliminates the 200ms+ package chain overhead.
    """
    # === MahamantraLotus (the main class) ===
    if name == "MahamantraLotus":
        from vibe_core.mahamantra._mahamantra_lotus import MahamantraLotus
        return MahamantraLotus

    # === Singleton instance ===
    if name == "mahamantra":
        from vibe_core.mahamantra._mahamantra_lotus import get_mahamantra
        return get_mahamantra()

    # === Alias: lotus ===
    if name == "lotus":
        from vibe_core.mahamantra._mahamantra_lotus import get_mahamantra
        return get_mahamantra()

    # === Constants (from fast _seed_cell) ===
    if name in ("WORDS", "TRINITY", "QUARTERS", "PANCHA", "HALVES",
                "HARE_COUNT", "KRISHNA_COUNT", "RAMA_COUNT",
                "KSETRAJNA", "HALF_SIZE", "LILA", "KSHETRA", "NAVA", "SHARANAGATI",
                "SEVEN", "TEN", "MAHAJANA_COUNT", "QUALITIES", "MALA",
                "MAHA_QUANTUM", "GITA_CHAPTERS", "PARAMPARA"):
        from vibe_core.mahamantra.protocols import _seed_cell
        return getattr(_seed_cell, name)

    # === Types ===
    if name in ("AkashState", "ExecuteResult", "GitaRoute", "RouteResult", "VibrationState"):
        from vibe_core.mahamantra import _types
        return getattr(_types, name)

    # === Lotus ===
    if name in ("LotusNode", "LotusPath"):
        from vibe_core.mahamantra import _lotus
        return getattr(_lotus, name)

    # === GAD ===
    if name in ("GADBase", "GADProtocol"):
        from vibe_core.mahamantra.protocols import _gad
        return getattr(_gad, name)

    # === MahaCell ===
    if name in ("MahaCell", "MahaHeader"):
        from vibe_core.mahamantra.protocols import _header
        return getattr(_header, name)

    # === Payload ===
    if name in ("PayloadType", "PayloadQuarter", "SiksastakamOp"):
        from vibe_core.mahamantra.protocols import _payload
        return getattr(_payload, name)

    # === MahaCompute ===
    if name in ("get_gita_chapter", "get_gita_insight", "ATTRACTOR_FIXED", "ATTRACTOR_CYCLE"):
        from vibe_core.mahamantra.protocols import _maha_compute
        return getattr(_maha_compute, name)

    # === Position ===
    if name == "get_position":
        from vibe_core.mahamantra.substrate import position
        return position.get_position

    # === CLI Auto ===
    if name == "cli_auto":
        from vibe_core.mahamantra.cli import auto
        return auto.cli_auto

    # === ALL_GUARDIANS ===
    if name == "ALL_GUARDIANS":
        from vibe_core.mahamantra.substrate import seed
        return seed.ALL_GUARDIANS

    # === Substrate exports (for backwards compat) ===
    if name == "WorkerProtocol":
        from vibe_core.mahamantra.substrate.protocol import WorkerProtocol
        return WorkerProtocol

    if name == "HeadProtocol":
        from vibe_core.mahamantra.substrate.protocol import HeadProtocol
        return HeadProtocol

    if name == "MantraProtocol":
        from vibe_core.mahamantra.substrate.protocol import MantraProtocol
        return MantraProtocol

    if name == "ProtocolRegistry":
        from vibe_core.mahamantra.substrate.protocol import ProtocolRegistry
        return ProtocolRegistry

    if name == "Mahajana":
        from vibe_core.mahamantra.substrate.mahajana import Mahajana
        return Mahajana

    if name == "Avatara":
        from vibe_core.mahamantra.substrate.mahajana import Avatara
        return Avatara

    if name == "MantraOpCode":
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        return MantraOpCode

    # === Kernel Singularity ===
    if name == "kernel_singularity":
        from vibe_core.mahamantra.kernel import singularity
        return singularity

    # === BootMode (Vyasa) ===
    if name == "BootMode":
        from vibe_core.mahamantra.substrate import boot
        return boot.BootMode

    # === ProcessManager (Vyasa) ===
    if name in ("ProcessManager", "ProcessStatus"):
        from vibe_core.mahamantra.substrate import process_manager
        return getattr(process_manager, name)

    # === Errors (Prithu) ===
    if name in ("ErrorCode", "StructuredError", "ErrorCategory", "kernel_fault"):
        from vibe_core.mahamantra.substrate import errors
        return getattr(errors, name)

    # === Lineage (Prithu) ===
    if name in ("LineageBlock", "LineageChain", "LineageEventType"):
        from vibe_core.mahamantra.substrate import lineage
        return getattr(lineage, name)

    # === Ledger (Prithu) ===
    if name in ("VibeLedger", "InMemoryLedger", "SQLiteLedger"):
        from vibe_core.mahamantra.substrate import ledger
        return getattr(ledger, name)

    # === EventBus (Narada) ===
    if name in ("EventBus", "Event", "EventType", "EventColor", "EventBusProtocol", "get_event_bus"):
        from vibe_core.mahamantra.substrate import event_bus
        return getattr(event_bus, name)

    # === Shuddhi (Kapila/Kumaras) ===
    if name in ("ShuddhiProtocol", "ShuddhiStatus", "ShuddhiResult", "RemedyProtocol", "NullShuddhi", "ShuddhiProtocolBase"):
        from vibe_core.mahamantra.substrate import shuddhi
        return getattr(shuddhi, name)

    # === Config (Brahma) ===
    if name in ("PhoenixConfig", "get_config", "reset_config", "set_config"):
        from vibe_core.mahamantra.substrate import config
        return getattr(config, name)

    # === Samskara (Prithu) ===
    if name in ("SamskaraProtocol", "Phase", "PhaseStatus", "PhaseResult", "PipelineContext", "PipelineExecutor"):
        from vibe_core.mahamantra.substrate import samskara
        return getattr(samskara, name)

    # === Grace & Tulasi (Research -> Production) ===
    if name == "GraceProtocol":
        from vibe_core.mahamantra.protocols.offering import GraceProtocol
        return GraceProtocol

    if name == "TulasiGate":
        from vibe_core.mahamantra.adapters.tulasi_gate import TulasiGate
        return TulasiGate

    if name == "MahaModularSynth":
        from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
        return MahaModularSynth

    if name == "OfferingPipeline":
        from vibe_core.mahamantra.research.tulasi_lila import OfferingPipeline
        return OfferingPipeline

    raise AttributeError(f"module 'vibe_core.mahamantra' has no attribute '{name}'")


# =============================================================================
# EXPORTS (for IDE support and * import)
# =============================================================================

__all__ = [
    # Main class
    "MahamantraLotus",
    "mahamantra",
    # Constants
    "WORDS", "TRINITY", "QUARTERS", "PANCHA", "HALVES",
    "MAHA_QUANTUM", "PARAMPARA", "SEVEN",
    # Types
    "AkashState", "ExecuteResult", "VibrationState",
    # Lotus
    "LotusNode", "LotusPath",
    # GAD
    "GADBase", "GADProtocol",
    # MahaCell
    "MahaCell", "MahaHeader",
    # Substrate (for backwards compat)
    "HeadProtocol", "MantraProtocol", "WorkerProtocol",
    "ProtocolRegistry", "Mahajana", "Avatara", "MantraOpCode",
    # Substrate (SSOT)
    "BootMode", "ProcessManager", "ProcessStatus",
    "ErrorCode", "StructuredError", "ErrorCategory",
    "LineageBlock", "LineageChain", "LineageEventType",
    "VibeLedger", "InMemoryLedger", "SQLiteLedger",
    "EventBus", "Event", "EventType", "EventColor",
    "EventBusProtocol", "get_event_bus",
    "ShuddhiProtocol", "ShuddhiStatus", "ShuddhiResult", "RemedyProtocol",
    "NullShuddhi", "ShuddhiProtocolBase",
    "PhoenixConfig", "get_config", "reset_config", "set_config",
    "SamskaraProtocol", "Phase", "PhaseStatus", "PhaseResult", "PipelineContext", "PipelineExecutor",
    # Tulasi
    "TulasiGate", "GraceProtocol", "MahaModularSynth", "OfferingPipeline",
]

