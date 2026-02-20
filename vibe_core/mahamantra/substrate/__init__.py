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
    # ACINTYA
    from vibe_core.mahamantra.substrate.acintya import (
        ACINTYA_ACCEPTED,
        GURU_ENTROPY,
        KRISHNA,
        KRISHNA_ASPECT,
        KRISHNA_LARGEST,
        KRISHNA_SMALLEST,
        PARAMPARA,
        PARAMPARA_VECTOR,
        PHASES,
        PURUSHA,
        SYSTEM_MANIFESTATION,
        TRINITY,
        AcintyaAspect,
        AcintyaAware,
        JivaCondition,
        JivaState,
        KrishnaPresence,
        ParamparaConnection,
        ParamparaProtocol,
        ProtocolLevel,
        PurushaTattva,
    )

    # BYTE
    from vibe_core.mahamantra.substrate.byte import (
        GenesisByte,
        HolyName,
        MantraByte,
        MantraTrit,
    )

    # GUNA
    from vibe_core.mahamantra.substrate.guna import (
        OPCODE_GUNA,
        RAJAS_OPCODES,
        SATTVA_OPCODES,
        TAMAS_OPCODES,
        VISHUDDHA_SATTVA,
        Guna,
        GunaQoS,
    )
    from vibe_core.mahamantra.substrate.mahajana import (
        AVATARA_COUNT,
        MAHAJANA_COUNT,
        TOTAL_POSITIONS,
        Avatara,
        Mahajana,
        Quarter,
        Sampradaya,
    )

    # OPCODE
    from vibe_core.mahamantra.substrate.opcode import (
        DHARMA_OPCODES,
        GENESIS_OPCODES,
        KARMA_OPCODES,
        MAHAJANA_OPCODES,
        MOKSHA_OPCODES,
        OPCODE_NAMES,
        OPCODE_PARAMPARA,
        QUARTER_OPCODES,
        MantraOpCode,
    )

    # POSITION
    from vibe_core.mahamantra.substrate.position import (
        MAHAMANTRA_POSITIONS,
        Guardian,
        MantraPosition,
    )

    # PROTOCOL
    from vibe_core.mahamantra.substrate.protocol import (
        HeadProtocol,
        MantraAware,
        MantraProtocol,
        ProtocolRegistry,
        WorkerProtocol,
    )

    # TATTVA
    from vibe_core.mahamantra.substrate.tattva import (
        JIVA,
        PURUSHOTTAMA,
        GuruConnection,
        GuruTattva,
        KshetraElement,
        Purushottama,
    )

    # WIRING
    from vibe_core.mahamantra.substrate.wiring import (
        FOLDER_IS_WIRING,
        FRACTAL_BASE,
        NO_FOLDER_NO_EXISTENCE,
        POSITION_BY_FOLDER,
        POSITION_BY_INDEX,
        POSITION_BY_NAME,
        POSITION_MAPPINGS,
        POSITIONS_PER_QUARTER,
        QUARTER_COUNT,
        PositionMapping,
        WiringProtocol,
        WiringVerification,
    )

    # YAJNA
    from vibe_core.mahamantra.substrate.yajna import (
        MAHA_POSITIONS,
        MALA_ROUNDS,
        PRIME_SIGNATURE,
        STD_MANTRA_PATTERN,
        Bhoga,
        DissonanceError,
        ParamparaBreakError,
        Prasadam,
        TamasBlockError,
        Yajna,
        YajnaProtocol,
    )


# =============================================================================
# SYMBOL DISCOVERY (replaces 280-entry _LAZY_IMPORTS dict)
# =============================================================================
# The LotusFinder (lotus_finder.py) handles MODULE-level discovery via
# sys.meta_path. This __getattr__ handles SYMBOL-level discovery:
#   from vibe_core.mahamantra.substrate import Mahajana
# → scans substrate modules' __all__ to find which module exports "Mahajana"
#
# CONFLICT TABLE: When multiple modules export the same symbol name,
# this table picks the canonical winner. Only ~20 entries needed.
# Everything else is auto-discovered from __all__ lists.
# =============================================================================

_CONFLICT_WINNERS = {
    # Symbol → canonical module (when multiple modules export the same name)
    "FRACTAL_BASE": "wiring",
    "Guna": "guna",
    "HolyName": "byte",
    "MAHAJANA_COUNT": "mahajana",
    "PARAMPARA": "acintya",
    "PHASES": "acintya",
    "Phase": "_legacy",
    "PhaseResult": "sankirtan",
    "PipelineContext": "_legacy",
    "Quarter": "mahajana",
    "SYSTEM_MANIFESTATION": "acintya",
    "Sampradaya": "mahajana",
    "TRINITY": "acintya",
    "get_position": "parampara",
    "get_position_by_guardian": "position",
    "get_position_by_index": "position",
    "get_quarter": "parampara",
    "offer": "yajna",
    "verify_parampara": "acintya",
}

# Aliases: symbol_name → (module_name, real_attr_name)
_ALIASES = {
    "YAJNA_TRINITY": ("yajna", "TRINITY"),
    "YajnaGuna": ("yajna", "Guna"),
    "YajnaHolyName": ("yajna", "HolyName"),
    "YajnaMantraByte": ("yajna", "MantraByte"),
    "get_mahajana_position": ("scanner", "get_position"),
    "get_mahajana_name": ("scanner", "get_name"),
    "get_wiring_by_index": ("wiring", "get_position_by_index"),
    "SankirtanPipelineContext": ("sankirtan", "PipelineContext"),
}

# Symbol cache: populated incrementally as symbols are resolved.
# Maps symbol_name → module_name. Grows over time, never shrinks.
_SYMBOL_CACHE: dict[str, str] = {}

# AST-based symbol index: built lazily on first cache miss.
# Extracts __all__ from source files WITHOUT importing them.
_AST_INDEX: dict[str, str] | None = None


def _build_ast_index() -> dict[str, str]:
    """
    Extract __all__ from substrate .py files using AST (no imports).

    Uses LotusFinder's module map for file paths, so this works even
    after files are moved into subdirectories.

    ~50ms vs ~1800ms for import-based scanning. Zero side effects.
    """
    import ast
    from vibe_core.mahamantra.substrate.lotus_finder import _get_module_map

    index: dict[str, str] = {}
    module_map = _get_module_map()

    for mod_name, py_file in sorted(module_map.items()):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(), filename=str(py_file))
        except SyntaxError:
            continue
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    sym = elt.value
                                    if sym not in index:
                                        index[sym] = mod_name

    # Apply conflict winners (override first-found with canonical choice)
    for sym, mod_name in _CONFLICT_WINNERS.items():
        index[sym] = mod_name

    return index


def _get_ast_index() -> dict[str, str]:
    """Get or build the AST-based symbol index."""
    global _AST_INDEX
    if _AST_INDEX is None:
        _AST_INDEX = _build_ast_index()
    return _AST_INDEX


def __getattr__(name: str):
    """
    Auto-discover symbols from substrate modules.

    Resolution order:
    1. Aliases (renamed symbols) — O(1)
    2. Symbol cache (previously resolved) — O(1)
    3. Conflict winners (explicit disambiguation) — O(1)
    4. AST index (extracted from __all__ without importing) — O(1) after first build
    5. Fractal fallback (subpackages and .py files by name)
    """
    import importlib

    # 1. Aliases
    if name in _ALIASES:
        mod_name, attr_name = _ALIASES[name]
        module = importlib.import_module(f".{mod_name}", __package__)
        return getattr(module, attr_name)

    # 2. Symbol cache (previously resolved)
    if name in _SYMBOL_CACHE:
        mod_name = _SYMBOL_CACHE[name]
        module = importlib.import_module(f".{mod_name}", __package__)
        return getattr(module, name)

    # 3. AST index (zero-import scan of __all__ declarations)
    index = _get_ast_index()
    if name in index:
        mod_name = index[name]
        _SYMBOL_CACHE[name] = mod_name
        module = importlib.import_module(f".{mod_name}", __package__)
        return getattr(module, name)

    # 4. Fractal fallback: subpackage or .py file by name
    from pathlib import Path

    substrate_root = Path(__file__).parent

    subpkg_path = substrate_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    module_path = substrate_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# EXPORTS (auto-discovered, not manually maintained)
# =============================================================================

def _get_all():
    """Build __all__ from the AST index."""
    return list(_get_ast_index().keys()) + list(_ALIASES.keys())

# Lazy __all__ — computed on first access by Python's import machinery
__all__ = property(lambda self: _get_all())
