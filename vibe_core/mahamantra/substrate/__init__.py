"""
SUBSTRATE - Die Grundlage des Mahamantra
========================================

Level -2 bis -1: Das Fundament auf dem alles aufbaut.

LEVEL -2 (ACINTYA):
    Krishna = Mahamantra = NON-DIFFERENT
    Das Unbegreifliche, das IS (nicht "repräsentiert")

LEVEL -1 (SUBSTRATE):
    Byte, Gene, Entropy
    Die manifestierte Form von -2

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya"
"O Arjuna, there is no truth superior to Me."
— Bhagavad Gita 7.7

LAZY IMPORTS: All imports deferred until accessed.
This prevents 1000ms+ cascades when importing a single module.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xdf5e13ed"  # GenesisByte: parampara % 37 == 0

from typing import TYPE_CHECKING

# =============================================================================
# TYPE CHECKING ONLY (no runtime cost)
# =============================================================================

if TYPE_CHECKING:
    # MAHAJANA
    from vibe_core.mahamantra.substrate.mahajana import (
        Mahajana,
        MAHAJANA_COUNT,
        Avatara,
        AVATARA_COUNT,
        Quarter,
        Sampradaya,
        TOTAL_POSITIONS,
    )

    # TATTVA
    from vibe_core.mahamantra.substrate.tattva import (
        Purushottama,
        PURUSHOTTAMA,
        KshetraElement,
        GuruTattva,
        GuruConnection,
        JIVA,
    )

    # ACINTYA
    from vibe_core.mahamantra.substrate.acintya import (
        SYSTEM_MANIFESTATION,
        ACINTYA_ACCEPTED,
        TRINITY,
        PARAMPARA,
        PHASES,
        GURU_ENTROPY,
        PARAMPARA_VECTOR,
        PurushaTattva,
        PURUSHA,
        KRISHNA_ASPECT,
        KRISHNA_SMALLEST,
        KRISHNA_LARGEST,
        ProtocolLevel,
        AcintyaAspect,
        KrishnaPresence,
        KRISHNA,
        JivaCondition,
        JivaState,
        AcintyaAware,
        ParamparaProtocol,
        ParamparaConnection,
    )

    # BYTE
    from vibe_core.mahamantra.substrate.byte import (
        HolyName,
        MantraTrit,
        MantraByte,
        GenesisByte,
    )

    # WIRING
    from vibe_core.mahamantra.substrate.wiring import (
        FOLDER_IS_WIRING,
        NO_FOLDER_NO_EXISTENCE,
        POSITIONS_PER_QUARTER,
        QUARTER_COUNT,
        FRACTAL_BASE,
        PositionMapping,
        POSITION_MAPPINGS,
        POSITION_BY_FOLDER,
        POSITION_BY_NAME,
        POSITION_BY_INDEX,
        WiringProtocol,
        WiringVerification,
    )

    # OPCODE
    from vibe_core.mahamantra.substrate.opcode import (
        MantraOpCode,
        OPCODE_NAMES,
        MAHAJANA_OPCODES,
        GENESIS_OPCODES,
        DHARMA_OPCODES,
        KARMA_OPCODES,
        MOKSHA_OPCODES,
        QUARTER_OPCODES,
        OPCODE_PARAMPARA,
    )

    # POSITION
    from vibe_core.mahamantra.substrate.position import (
        Guardian,
        MantraPosition,
        MAHAMANTRA_POSITIONS,
    )

    # PROTOCOL
    from vibe_core.mahamantra.substrate.protocol import (
        MantraProtocol,
        WorkerProtocol,
        HeadProtocol,
        MantraAware,
        ProtocolRegistry,
    )

    # GUNA
    from vibe_core.mahamantra.substrate.guna import (
        Guna,
        VISHUDDHA_SATTVA,
        SATTVA_OPCODES,
        RAJAS_OPCODES,
        TAMAS_OPCODES,
        OPCODE_GUNA,
        GunaQoS,
    )

    # YAJNA
    from vibe_core.mahamantra.substrate.yajna import (
        PRIME_SIGNATURE,
        MAHA_POSITIONS,
        MALA_ROUNDS,
        STD_MANTRA_PATTERN,
        DissonanceError,
        TamasBlockError,
        ParamparaBreakError,
        Bhoga,
        Prasadam,
        YajnaProtocol,
        Yajna,
    )


# =============================================================================
# LAZY IMPORT REGISTRY
# =============================================================================

_LAZY_IMPORTS = {
    # === MAHAJANA ===
    "Mahajana": "mahajana",
    "MAHAJANA_COUNT": "mahajana",
    "Avatara": "mahajana",
    "AVATARA_COUNT": "mahajana",
    "Quarter": "mahajana",
    "Sampradaya": "mahajana",
    "TOTAL_POSITIONS": "mahajana",
    # === TATTVA ===
    "Purushottama": "tattva",
    "PURUSHOTTAMA": "tattva",
    "KshetraElement": "tattva",
    "GuruTattva": "tattva",
    "GuruConnection": "tattva",
    "JIVA": "tattva",
    # === ACINTYA ===
    "SYSTEM_MANIFESTATION": "acintya",
    "ACINTYA_ACCEPTED": "acintya",
    "TRINITY": "acintya",
    "PARAMPARA": "acintya",
    "PHASES": "acintya",
    "GURU_ENTROPY": "acintya",
    "PARAMPARA_VECTOR": "acintya",
    "PurushaTattva": "acintya",
    "PURUSHA": "acintya",
    "KRISHNA_ASPECT": "acintya",
    "KRISHNA_SMALLEST": "acintya",
    "KRISHNA_LARGEST": "acintya",
    "ProtocolLevel": "acintya",
    "AcintyaAspect": "acintya",
    "KrishnaPresence": "acintya",
    "KRISHNA": "acintya",
    "JivaCondition": "acintya",
    "JivaState": "acintya",
    "AcintyaAware": "acintya",
    "ParamparaProtocol": "acintya",
    "ParamparaConnection": "acintya",
    "vibration_is_krishna": "acintya",
    "mantra_is_krishna": "acintya",
    "mantra_not_different_from_source": "acintya",
    "check_bheda_abheda": "acintya",
    "verify_parampara": "acintya",
    "get_guru_entropy": "acintya",
    # === BYTE ===
    "HolyName": "byte",
    "MantraTrit": "byte",
    "MantraByte": "byte",
    "GenesisByte": "byte",
    # === WIRING ===
    "FOLDER_IS_WIRING": "wiring",
    "NO_FOLDER_NO_EXISTENCE": "wiring",
    "POSITIONS_PER_QUARTER": "wiring",
    "QUARTER_COUNT": "wiring",
    "FRACTAL_BASE": "wiring",
    "PositionMapping": "wiring",
    "POSITION_MAPPINGS": "wiring",
    "POSITION_BY_FOLDER": "wiring",
    "POSITION_BY_NAME": "wiring",
    "POSITION_BY_INDEX": "wiring",
    "folder_exists": "wiring",
    "get_position_from_folder": "wiring",
    "get_position_from_name": "wiring",
    "get_wiring_by_index": "wiring",  # Old get_position_by_index (returns PositionMapping)
    "WiringProtocol": "wiring",
    "WiringVerification": "wiring",
    "verify_wiring": "wiring",
    "calculate_fractal_depth": "wiring",
    "calculate_total_nodes": "wiring",
    # === PARAMPARA ===
    "ParamparaNode": "parampara",
    "PARAMPARA_GRAPH": "parampara",
    "get_position": "parampara",
    "get_quarter": "parampara",
    "get_sampradaya": "parampara",
    "get_guru": "parampara",
    "get_mahajana_at_position": "parampara",
    "get_37_formula": "parampara",
    # === OPCODE ===
    "MantraOpCode": "opcode",
    "OPCODE_NAMES": "opcode",
    "MAHAJANA_OPCODES": "opcode",
    "GENESIS_OPCODES": "opcode",
    "DHARMA_OPCODES": "opcode",
    "KARMA_OPCODES": "opcode",
    "MOKSHA_OPCODES": "opcode",
    "QUARTER_OPCODES": "opcode",
    "get_opcode": "opcode",
    "get_opcode_name": "opcode",
    "get_mahajana_opcode": "opcode",
    "get_opcode_quarter": "opcode",
    "get_quarter_opcodes": "opcode",
    "OPCODE_PARAMPARA": "opcode",
    "get_opcode_parampara": "opcode",
    "verify_opcode_parampara": "opcode",
    # === POSITION ===
    "Guardian": "position",
    "MantraPosition": "position",
    "MAHAMANTRA_POSITIONS": "position",
    "get_position_by_index": "position",  # Returns MantraPosition (SSOT)
    "get_position_by_guardian": "position",
    "get_position_by_opcode": "position",
    "get_positions_by_quarter": "position",
    "get_head_position": "position",
    "get_worker_positions": "position",
    "get_worker_positions_for_quarter": "position",
    "get_all_head_positions": "position",
    "get_all_worker_positions": "position",
    "get_quarter_positions": "position",
    # === PROTOCOL ===
    "MantraProtocol": "protocol",
    "WorkerProtocol": "protocol",
    "HeadProtocol": "protocol",
    "MantraAware": "protocol",
    "ProtocolRegistry": "protocol",
    # === PANCHA TATTVA ===
    "PanchaTattva": "pancha_tattva",
    "TattvaIndex": "pancha_tattva",
    "TattvaAspect": "pancha_tattva",
    "PANCHA_TATTVA_ASPECTS": "pancha_tattva",
    "get_tattva_aspect": "pancha_tattva",
    "get_tattva_by_index": "pancha_tattva",
    "get_tattva_by_capability": "pancha_tattva",
    "get_tattva_by_protocol": "pancha_tattva",
    "TATTVA_TO_HOLYNAME": "pancha_tattva",
    "tattva_to_trit": "pancha_tattva",
    "TattvaGate": "pancha_tattva",
    "GATE_TO_TATTVA": "pancha_tattva",
    "PanchaTattvaAware": "pancha_tattva",
    "get_tattva_for_position": "pancha_tattva",
    "PANCHA_TATTVA_COUNT": "pancha_tattva",
    "PANCHA_TATTVA_VECTOR": "pancha_tattva",
    "verify_pancha_tattva_parampara": "pancha_tattva",
    "PANCHA_TATTVA_MANTRA": "pancha_tattva",
    "PANCHA_TATTVA_MEANING": "pancha_tattva",
    # === WATERTIGHT ===
    "TypeViolation": "watertight",
    "WatertightReport": "watertight",
    "check_file": "watertight",
    "check_directory": "watertight",
    "verify_watertight": "watertight",
    "print_report": "watertight",
    "is_watertight": "watertight",
    "FORBIDDEN_TYPES": "watertight",
    # === GUNA ===
    "Guna": "guna",
    "VISHUDDHA_SATTVA": "guna",
    "is_vishuddha": "guna",
    "SATTVA_OPCODES": "guna",
    "RAJAS_OPCODES": "guna",
    "TAMAS_OPCODES": "guna",
    "OPCODE_GUNA": "guna",
    "get_guna": "guna",
    "get_guna_by_position": "guna",
    "is_sattva": "guna",
    "is_rajas": "guna",
    "is_tamas": "guna",
    "GunaQoS": "guna",
    # === SCANNER ===
    "MahajanaAlias": "scanner",
    "MAHAJANA_ALIASES": "scanner",
    "resolve_mahajana": "scanner",
    "get_mahajana_position": "scanner",
    "get_mahajana_name": "scanner",
    "SimpleDeclaration": "scanner",
    "ScanResult": "scanner",
    "scan_all": "scanner",
    "scan_for_governance": "scanner",
    "print_scan_report": "scanner",
    # === YAJNA ===
    "PRIME_SIGNATURE": "yajna",
    "MAHA_POSITIONS": "yajna",
    "MALA_ROUNDS": "yajna",
    "YAJNA_TRINITY": "yajna",
    "STD_MANTRA_PATTERN": "yajna",
    "DissonanceError": "yajna",
    "TamasBlockError": "yajna",
    "ParamparaBreakError": "yajna",
    "YajnaGuna": "yajna",
    "YajnaHolyName": "yajna",
    "Bhoga": "yajna",
    "Prasadam": "yajna",
    "YajnaMantraByte": "yajna",
    "YajnaProtocol": "yajna",
    "Yajna": "yajna",
    "get_yajna": "yajna",
    "offer": "yajna",
}

# Special aliases
_LAZY_ALIASES = {
    "YAJNA_TRINITY": ("yajna", "TRINITY"),
    "YajnaGuna": ("yajna", "Guna"),
    "YajnaHolyName": ("yajna", "HolyName"),
    "YajnaMantraByte": ("yajna", "MantraByte"),
    "get_mahajana_position": ("scanner", "get_position"),
    "get_mahajana_name": ("scanner", "get_name"),
    "get_wiring_by_index": ("wiring", "get_position_by_index"),  # Alias for old wiring func
}


def __getattr__(name: str):
    """Lazy import on attribute access. O(1) lookup."""
    if name in _LAZY_IMPORTS:
        import importlib

        module_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(f".{module_name}", __package__)

        # Handle aliases
        if name in _LAZY_ALIASES:
            _, attr_name = _LAZY_ALIASES[name]
            return getattr(module, attr_name)

        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = list(_LAZY_IMPORTS.keys())
