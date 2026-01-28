"""
LEGACY BRIDGE - Balarama Pattern für Legacy-Types
=================================================

"Opfern (Wrappen): Lade das fremde System durch den Balarama Proxy."
— MAHAPROMPT

Diese Datei re-exportiert Legacy-Types aus protocols/substrate.
Alle Imports INNERHALB mahamantra/ sollten hierüber gehen.

NICHT NEU SCHREIBEN - nur wrappen.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nityananda"
__position__ = 1
__genesis__ = "0x3658b02f"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# RE-EXPORTS FROM protocols/substrate/scanner
# =============================================================================

from vibe_core.protocols.substrate.scanner import (
    Declaration,
    DeclarationType,
    FileStatus,
    ScanConfig,
    ScannedFile,
    ScannerProtocol,
    ScanProgress,
    ScanResult,
    extract_declarations,
    get_default_config,
    path_to_module,
)

# =============================================================================
# RE-EXPORTS FROM protocols/substrate/samskara
# =============================================================================

from vibe_core.protocols.substrate.samskara import (
    Phase,
    PhaseStatus,
    PipelineExecutor,
    SamskaraProtocol,
    PipelineContext,
)

# =============================================================================
# RE-EXPORTS FROM protocols/substrate/tattva
# =============================================================================

from vibe_core.protocols.substrate.tattva import (
    PURUSHOTTAMA as LEGACY_PURUSHOTTAMA,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # scanner
    "Declaration",
    "DeclarationType",
    "FileStatus",
    "ScanConfig",
    "ScannedFile",
    "ScannerProtocol",
    "ScanProgress",
    "ScanResult",
    "extract_declarations",
    "get_default_config",
    "path_to_module",
    # samskara
    "Phase",
    "PhaseStatus",
    "PipelineExecutor",
    "SamskaraProtocol",
    "PipelineContext",
    # tattva
    "LEGACY_PURUSHOTTAMA",
]
