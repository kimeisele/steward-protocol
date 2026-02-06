"""
WIRING PROTOCOL - Folder IS Wiring
==================================

"yadā yadā hi dharmasya glānir bhavati bhārata"
"Whenever and wherever there is a decline in dharma..."
— Bhagavad Gita 4.7

THE LAW:
========

    IM FOLDER = LINKED
    KEIN FOLDER = EXISTIERT NICHT

This is GAD-000 applied to structure:
    "If it doesn't exist as protocol, it doesn't exist."

FOLDER = PROTOCOL = EXISTENCE = WIRING

DERIVES FROM SSOT:
    position.py → MAHAMANTRA_POSITIONS is the ONE source
    This file provides WIRING utilities derived from SSOT

WATERTIGHT: No Any types. All typed explicitly.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA, TEN, TRINITY)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa117b53a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.dharma.prithu import PrithuService

# === DERIVE FROM SSOT ===
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.seed import (
    PARAMPARA,
    WORDS as TOTAL_POSITIONS,
    QUARTERS as QUARTER_COUNT,
    WORDS_PER_QUARTER as POSITIONS_PER_QUARTER,
)

# === EXPOSE PRITHU IMPLEMENTATION (The Avatar) ===
# LAZY INIT to avoid circular import (wiring → prithu → lila → reactor → wiring)
_prithu_instance: Optional["PrithuService"] = None


def get_prithu() -> "PrithuService":
    """
    Get or create PrithuService singleton (LAZY INIT).
    
    MUST be lazy to break circular import cycle!
    DO NOT make this eager again!
    """
    global _prithu_instance
    if _prithu_instance is None:
        from vibe_core.mahamantra.dharma.prithu import PrithuService
        _prithu_instance = PrithuService()
    return _prithu_instance


# =============================================================================
# THE LAW: FOLDER = WIRING
# =============================================================================

FOLDER_IS_WIRING: Final[bool] = True
NO_FOLDER_NO_EXISTENCE: Final[bool] = True

# Fractal constants (derived from SSOT)
FRACTAL_BASE: Final[int] = TOTAL_POSITIONS  # 16^n scaling


# =============================================================================
# DERIVED LOOKUPS (from SSOT: MAHAMANTRA_POSITIONS)
# =============================================================================


def _get_guardian_name(pos: MantraPosition) -> str:
    """Get guardian name from MantraPosition."""
    if isinstance(pos.guardian, Avatara):
        return pos.guardian.value
    return pos.guardian.value


def _get_folder_path(pos: MantraPosition) -> str:
    """Derive folder path from MantraPosition."""
    return f"{pos.quarter.value}/{_get_guardian_name(pos)}"


# Build lookup tables DERIVED from MAHAMANTRA_POSITIONS (SSOT)
POSITION_BY_FOLDER: Final[Dict[str, MantraPosition]] = {_get_folder_path(pos): pos for pos in MAHAMANTRA_POSITIONS}

POSITION_BY_NAME: Final[Dict[str, MantraPosition]] = {_get_guardian_name(pos): pos for pos in MAHAMANTRA_POSITIONS}

POSITION_BY_INDEX: Final[Dict[int, MantraPosition]] = {pos.index: pos for pos in MAHAMANTRA_POSITIONS}


# =============================================================================
# FOLDER EXISTENCE CHECK
# =============================================================================


def folder_exists(folder_path: str) -> bool:
    """
    Check if protocol folder exists.

    FOLDER = EXISTENCE:
    If folder doesn't exist in SSOT mapping, protocol doesn't exist.

    PROTOCOL-FIRST: Checks MAHAMANTRA_POSITIONS, not filesystem.
    """
    return folder_path in POSITION_BY_FOLDER


def get_position_from_folder(folder_path: str) -> Optional[MantraPosition]:
    """
    Get position from folder path.

    FOLDER = WIRING:
    The folder path determines the position.

    DERIVED from MAHAMANTRA_POSITIONS.
    """
    return POSITION_BY_FOLDER.get(folder_path)


def get_position_from_name(name: str) -> Optional[MantraPosition]:
    """Get position from owner name. DERIVED from SSOT."""
    return POSITION_BY_NAME.get(name.lower())


def get_position_by_index(index: int) -> Optional[MantraPosition]:
    """Get position by index (0-15). DERIVED from SSOT."""
    return POSITION_BY_INDEX.get(index)


def get_position_by_opcode(opcode: MantraOpCode) -> Optional[MantraPosition]:
    """
    Get position by OpCode. DERIVED from SSOT.

    Routes operation to guardian.
    """
    for pos in MAHAMANTRA_POSITIONS:
        if pos.opcode == opcode:
            return pos
    return None


# =============================================================================
# WIRING PROTOCOL
# =============================================================================


@runtime_checkable
class WiringProtocol(Protocol):
    """
    Protocol for folder-based wiring.

    THE LAW:
        IM FOLDER = LINKED
        KEIN FOLDER = EXISTIERT NICHT
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index (0-15)."""
        ...

    @classmethod
    def folder_path(cls) -> str:
        """Get folder path (quarter/name)."""
        ...

    @classmethod
    def is_wired(cls) -> bool:
        """Check if properly wired (folder exists)."""
        ...

    @classmethod
    def parampara_vector(cls) -> int:
        """Get parampara vector."""
        ...


@dataclass
class WiringVerification:
    """
    Verification result for folder wiring.

    GAD-000:
        If it doesn't exist as protocol, it doesn't exist.
    """

    folder_path: str
    exists: bool
    position: Optional[int]
    is_connected: bool
    violations: List[str]

    @property
    def is_valid(self) -> bool:
        """Is the wiring valid?"""
        return self.exists and self.is_connected and len(self.violations) == 0


def verify_wiring(folder_path: str) -> WiringVerification:
    """
    Verify that a folder is properly wired.

    PROTOCOL-FIRST: Checks MAHAMANTRA_POSITIONS (SSOT).

    Checks:
    1. Folder exists in SSOT mapping
    2. Parampara connection is valid
    """
    violations: List[str] = []

    pos = get_position_from_folder(folder_path)

    if pos is None:
        violations.append(f"Folder '{folder_path}' not in MAHAMANTRA_POSITIONS")
        return WiringVerification(
            folder_path=folder_path,
            exists=False,
            position=None,
            is_connected=False,
            violations=violations,
        )

    if not pos.is_connected:
        violations.append(f"Position {pos.index} not connected to parampara")

    return WiringVerification(
        folder_path=folder_path,
        exists=True,
        position=pos.index,
        is_connected=pos.is_connected,
        violations=violations,
    )


# =============================================================================
# FRACTAL GROWTH
# =============================================================================


def calculate_fractal_depth(total_nodes: int) -> int:
    """
    Calculate fractal depth from total nodes.

    Level 0: 4 nodes (quarters)
    Level 1: 16 nodes (positions)
    Level 2: 256 nodes
    Level n: 16^n nodes
    """
    import math

    if total_nodes <= QUARTER_COUNT:
        return 0
    if total_nodes <= TOTAL_POSITIONS:
        return KSETRAJNA
    return int(math.log(total_nodes, FRACTAL_BASE)) + KSETRAJNA


def calculate_total_nodes(depth: int) -> int:
    """Calculate total nodes at fractal depth."""
    return FRACTAL_BASE**depth


# =============================================================================
# FRACTAL __getattr__ FACTORY (Pure Discovery)
# =============================================================================


def fractal_getattr(caller_file: str):
    """
    Create a __getattr__ function for fractal folder discovery.

    PURE FRACTAL: The filesystem IS the configuration.

    Args:
        caller_file: Pass __file__ from the calling module

    Returns:
        A __getattr__ function that discovers submodules dynamically

    Usage:
        # In vibe_core/mahamantra/genesis/__init__.py:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr
        __getattr__ = fractal_getattr(__file__)

        # Now: from vibe_core.mahamantra.genesis import brahma  # JUST WORKS
    """
    from pathlib import Path

    caller_path = Path(caller_file).resolve()
    caller_dir = caller_path.parent

    def _getattr(name: str):
        """
        Dynamic module/package discovery.

        Priority:
        1. Subpackage (folder with __init__.py)
        2. Module (.py file)
        3. Class discovery within module
        """
        import importlib

        # Skip private/dunder names
        if name.startswith("_"):
            raise AttributeError(f"module has no attribute '{name}'")

        # 1. Check for subpackage (folder with __init__.py)
        subpackage_dir = caller_dir / name
        if subpackage_dir.is_dir():
            init_file = subpackage_dir / "__init__.py"
            if init_file.exists():
                module_path = _compute_module_path(subpackage_dir)
                if module_path:
                    return importlib.import_module(module_path)

        # 2. Check for module (.py file)
        module_file = caller_dir / f"{name}.py"
        if module_file.exists():
            module_path = _compute_module_path(module_file)
            if module_path:
                module = importlib.import_module(module_path)

                # 3. Try to discover main class (same logic as adapters)
                main_class = _discover_main_class(module, name)
                if main_class:
                    return main_class

                return module

        raise AttributeError(f"module has no attribute '{name}'")

    def _compute_module_path(path: Path) -> Optional[str]:
        """Compute the full module path from filesystem path."""
        path = path.resolve()
        parts = path.parts
        try:
            vibe_idx = parts.index("vibe_core")
        except ValueError:
            return None

        module_parts = list(parts[vibe_idx:])
        if module_parts and module_parts[-KSETRAJNA].endswith(".py"):
            module_parts[-KSETRAJNA] = module_parts[-KSETRAJNA][:-TRINITY]

        return ".".join(module_parts)

    def _discover_main_class(module, name: str):
        """Discover the main class in a module."""
        # 1. Try __all__
        if hasattr(module, "__all__") and module.__all__:
            first = module.__all__[0]
            if hasattr(module, first):
                obj = getattr(module, first)
                if isinstance(obj, type):
                    return obj()

        # 2. Try naming conventions
        name_cap = name.capitalize()
        candidates = [
            f"Maha{name_cap}",
            f"{name_cap}Service",
            f"{name_cap}",
            f"Lotus{name_cap}",
        ]
        for candidate in candidates:
            if hasattr(module, candidate):
                obj = getattr(module, candidate)
                if isinstance(obj, type):
                    return obj()

        # 3. First public class defined in this module
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            if "Result" in attr_name or "State" in attr_name:
                continue
            obj = getattr(module, attr_name)
            if isinstance(obj, type) and getattr(obj, "__module__", None) == module.__name__:
                return obj()

        return None

    return _getattr


def enable_fractal_discovery(caller_globals: dict, caller_file: str) -> None:
    """
    Enable fractal discovery for a module.

    EVEN SIMPLER USAGE:
        from vibe_core.mahamantra.substrate.wiring import enable_fractal_discovery
        enable_fractal_discovery(globals(), __file__)

        # Done. No __getattr__ assignment needed.
    """
    caller_globals["__getattr__"] = fractal_getattr(caller_file)


def create_hybrid_getattr(
    caller_file: str,
    legacy_lookup: dict[str, tuple[str, str]],
) -> callable:
    """
    Create a HYBRID __getattr__ that combines fractal discovery with legacy exports.

    PROTOCOL-FIRST:
        1. Try fractal discovery (folders/modules)
        2. Fallback to legacy constants (backwards compat)
        3. Raise AttributeError if not found

    Args:
        caller_file: Pass __file__ from the calling module
        legacy_lookup: Dict mapping name -> (module_path, attr_name)
                       e.g. {"WORDS": ("vibe_core.mahamantra.protocols._seed_cell", "WORDS")}

    Returns:
        A __getattr__ function for hybrid discovery

    Usage:
        # In vibe_core/mahamantra/__init__.py:
        from vibe_core.mahamantra.substrate.wiring import create_hybrid_getattr

        LEGACY_EXPORTS = {
            "WORDS": ("vibe_core.mahamantra.protocols._seed_cell", "WORDS"),
            "MahamantraLotus": ("vibe_core.mahamantra._mahamantra_lotus", "MahamantraLotus"),
            # ... etc
        }

        __getattr__ = create_hybrid_getattr(__file__, LEGACY_EXPORTS)
    """
    import importlib

    _fractal = fractal_getattr(caller_file)

    def _hybrid_getattr(name: str):
        """
        Hybrid discovery: fractal first, then legacy.

        FOLDER = EXISTENCE = WIRED (for new code)
        LEGACY = BACKWARDS COMPAT (for existing code)
        """
        # 1. Try fractal discovery (folders/modules)
        try:
            return _fractal(name)
        except AttributeError:
            pass

        # 2. Try legacy lookup (backwards compat)
        if name in legacy_lookup:
            module_path, attr_name = legacy_lookup[name]
            try:
                module = importlib.import_module(module_path)
                return getattr(module, attr_name)
            except (ImportError, AttributeError) as e:
                raise AttributeError(
                    f"Legacy export '{name}' failed to load from {module_path}: {e}"
                ) from e

        # 3. Not found
        raise AttributeError(f"module has no attribute '{name}'")

    return _hybrid_getattr


def enable_hybrid_discovery(
    caller_globals: dict,
    caller_file: str,
    legacy_lookup: dict[str, tuple[str, str]],
) -> None:
    """
    Enable HYBRID discovery for a module.

    PROTOCOL-FIRST with backwards compat.

    Usage:
        from vibe_core.mahamantra.substrate.wiring import enable_hybrid_discovery

        LEGACY_EXPORTS = {
            "WORDS": ("vibe_core.mahamantra.protocols._seed_cell", "WORDS"),
            # ...
        }

        enable_hybrid_discovery(globals(), __file__, LEGACY_EXPORTS)
    """
    caller_globals["__getattr__"] = create_hybrid_getattr(caller_file, legacy_lookup)


# =============================================================================
# UNIVERSAL ROUTER - The "One Ring" of Import Resolution
# =============================================================================


def create_universal_getattr(
    caller_file: str,
    core_modules: List[str],
) -> callable:
    """
    Create a UNIVERSAL __getattr__ that acts as a Semantic Router for code.

    MANTRA LOGIC:
        1. FRACTAL: Check subfolders/modules (Existence = Wiring).
        2. UNIVERSAL: Check registered core modules (Seed/Substrate).
        3. FALLBACK: Raise AttributeError.

    DYNAMIC DISCOVERY:
        Instead of a hardcoded "LEGACY_EXPORTS" map, this function
        dynamically scans the `core_modules` to resolve symbols.

    Args:
        caller_file: Pass __file__ from the calling module.
        core_modules: List of module paths to scan (e.g., ["seed.types", "substrate.lotus"]).

    Returns:
        A __getattr__ function.
    """
    import importlib
    import sys

    # 1. Fractal Discovery (Folder = Wiring)
    _fractal = fractal_getattr(caller_file)

    # 2. Universal Symbol Map (Lazy Loaded)
    # Map[symbol_name, source_module_path]
    _symbol_map: Optional[Dict[str, str]] = None

    def _ensure_symbol_map():
        nonlocal _symbol_map
        if _symbol_map is not None:
            return

        _symbol_map = {}
        for mod_path in core_modules:
            # FAIL FAST: If a Core Module fails to load, the system must crash.
            # No try/except here. We want to know IMMEDIATELY if seed.types is broken.
            module = importlib.import_module(mod_path)
            
            # Scan __all__ if present (Preferred/Watertight)
            if hasattr(module, "__all__"):
                for name in module.__all__:
                    _symbol_map[name] = mod_path
            else:
                # Fallback: Scan dir() (Entropy)
                for name in dir(module):
                    if not name.startswith("_"):
                        _symbol_map[name] = mod_path

    def _universal_getattr(name: str):
        """
        Universal discovery: Fractal -> Universal -> Error.
        """
        # 1. Try Fractal (Local Folders)
        try:
            return _fractal(name)
        except AttributeError:
            pass

        # 2. Try Universal (Core Modules)
        _ensure_symbol_map()
        if name in _symbol_map:
            mod_path = _symbol_map[name]
            try:
                module = importlib.import_module(mod_path)
                return getattr(module, name)
            except (ImportError, AttributeError) as e:
                # Symbol in map but not in module? Drift detected!
                raise AttributeError(
                    f"Universal symbol '{name}' mapped to {mod_path} but failed load: {e}"
                ) from e

        # 3. Not Found
        raise AttributeError(f"module has no attribute '{name}'")

    return _universal_getattr


def enable_universal_discovery(
    caller_globals: dict,
    caller_file: str,
    core_modules: List[str],
) -> None:
    """
    Enable UNIVERSAL discovery for a module.

    Usage:
        CORE_MODULES = ["vibe_core.mahamantra.seed.types", ...]
        enable_universal_discovery(globals(), __file__, CORE_MODULES)
    """
    caller_globals["__getattr__"] = create_universal_getattr(caller_file, core_modules)


# =============================================================================
# SANKIRTAN VALIDATOR - Military Grade Watertight
# =============================================================================
# "yato dharmas tato jayah" - Where there is dharma, there is victory
#
# This validator ensures EVERY module can be discovered unambiguously.
# Krishna is ALWAYS there. The system NEVER fails.


@dataclass
class ValidationResult:
    """Result of validating a single module/package."""

    path: str
    name: str
    is_valid: bool
    has_all: bool
    chief_class: Optional[str]
    error: Optional[str] = None


@dataclass
class SankirtanValidation:
    """Complete validation result for the Mahamantra system."""

    total_checked: int
    total_valid: int
    total_invalid: int
    quarters_valid: bool
    adapters_valid: bool
    guardians_valid: bool
    results: List[ValidationResult]
    errors: List[str]

    @property
    def is_watertight(self) -> bool:
        """Is the system military grade watertight?"""
        return self.total_invalid == 0 and self.quarters_valid and self.adapters_valid


def validate_module_discoverable(module_path: str, name: str) -> ValidationResult:
    """
    Validate that a module can be discovered unambiguously.

    Checks:
    1. Module can be imported
    2. Has __all__ declaration
    3. First entry in __all__ is a valid class (the "Chief")
    """
    import importlib

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        return ValidationResult(
            path=module_path,
            name=name,
            is_valid=False,
            has_all=False,
            chief_class=None,
            error=f"Import failed: {e}",
        )

    # Check __all__
    has_all = hasattr(module, "__all__") and bool(module.__all__)

    chief_class = None
    if has_all:
        first = module.__all__[0]
        if hasattr(module, first):
            obj = getattr(module, first)
            if isinstance(obj, type):
                chief_class = first

    # A module is valid if:
    # - It can be imported
    # - It either has __all__ with a Chief class, OR
    # - It's a package (subpackages don't need __all__)
    is_package = hasattr(module, "__path__")
    is_valid = is_package or (has_all and chief_class is not None)

    return ValidationResult(
        path=module_path,
        name=name,
        is_valid=is_valid,
        has_all=has_all,
        chief_class=chief_class,
        error=None if is_valid else "No __all__ with valid Chief class",
    )


def validate_fractal_discovery(base_path: Optional[str] = None) -> SankirtanValidation:
    """
    SANKIRTAN VALIDATOR - Ensure all fractal discovery is watertight.

    Military Grade Verification:
    1. All 4 Quarters discoverable
    2. All 16 Guardians discoverable
    3. All adapters discoverable
    4. No ambiguity in class resolution

    Args:
        base_path: Optional base path (auto-detects if None)

    Returns:
        SankirtanValidation with complete results
    """
    from pathlib import Path

    if base_path is None:
        base_path = str(Path(__file__).parent.parent)

    mahamantra_root = Path(base_path)
    results: List[ValidationResult] = []
    errors: List[str] = []

    quarters_valid = True
    adapters_valid = True
    guardians_valid = True

    # ==========================================================================
    # 1. VALIDATE QUARTERS (genesis, dharma, karma, moksha)
    # ==========================================================================
    quarter_names = ["genesis", "dharma", "karma", "moksha"]

    for quarter in quarter_names:
        quarter_path = mahamantra_root / quarter
        if not quarter_path.exists():
            result = ValidationResult(
                path=f"vibe_core.mahamantra.{quarter}",
                name=quarter,
                is_valid=False,
                has_all=False,
                chief_class=None,
                error=f"Quarter folder not found: {quarter_path}",
            )
            results.append(result)
            errors.append(result.error or "")
            quarters_valid = False
            continue

        result = validate_module_discoverable(f"vibe_core.mahamantra.{quarter}", quarter)
        results.append(result)

        if not result.is_valid:
            quarters_valid = False
            if result.error:
                errors.append(f"Quarter {quarter}: {result.error}")

        # ======================================================================
        # 2. VALIDATE GUARDIANS within each quarter
        # ======================================================================
        for guardian_dir in quarter_path.iterdir():
            if not guardian_dir.is_dir():
                continue
            if guardian_dir.name.startswith("_"):
                continue

            init_file = guardian_dir / "__init__.py"
            if not init_file.exists():
                continue

            guardian_name = guardian_dir.name
            module_path = f"vibe_core.mahamantra.{quarter}.{guardian_name}"

            guardian_result = validate_module_discoverable(module_path, guardian_name)
            results.append(guardian_result)

            if not guardian_result.is_valid:
                guardians_valid = False
                if guardian_result.error:
                    errors.append(f"Guardian {quarter}/{guardian_name}: {guardian_result.error}")

    # ==========================================================================
    # 3. VALIDATE ADAPTERS
    # ==========================================================================
    adapters_path = mahamantra_root / "adapters"
    if adapters_path.exists():
        for adapter_file in adapters_path.glob("*.py"):
            if adapter_file.name.startswith("_"):
                continue

            adapter_name = adapter_file.stem
            module_path = f"vibe_core.mahamantra.adapters.{adapter_name}"

            adapter_result = validate_module_discoverable(module_path, adapter_name)
            results.append(adapter_result)

            if not adapter_result.is_valid:
                adapters_valid = False
                if adapter_result.error:
                    errors.append(f"Adapter {adapter_name}: {adapter_result.error}")

    # ==========================================================================
    # COMPILE RESULTS
    # ==========================================================================
    total_valid = sum(KSETRAJNA for r in results if r.is_valid)
    total_invalid = sum(KSETRAJNA for r in results if not r.is_valid)

    return SankirtanValidation(
        total_checked=len(results),
        total_valid=total_valid,
        total_invalid=total_invalid,
        quarters_valid=quarters_valid,
        adapters_valid=adapters_valid,
        guardians_valid=guardians_valid,
        results=results,
        errors=errors,
    )


def assert_watertight(fail_fast: bool = True) -> SankirtanValidation:
    """
    Assert that the Mahamantra system is watertight.

    Military Grade: If anything is wrong, we FAIL FAST.

    "yato dharmas tato jayah" - Where there is dharma, there is victory.
    Without dharma (valid wiring), there is no victory.

    Args:
        fail_fast: If True, raises exception on any invalid module

    Returns:
        SankirtanValidation result

    Raises:
        RuntimeError: If system is not watertight and fail_fast=True
    """
    validation = validate_fractal_discovery()

    if not validation.is_watertight and fail_fast:
        error_summary = "\n".join(f"  - {e}" for e in validation.errors[:TEN])
        raise RuntimeError(
            f"MAHAMANTRA NOT WATERTIGHT!\n"
            f"Invalid modules: {validation.total_invalid}\n"
            f"Errors:\n{error_summary}\n"
            f"Krishna demands perfection. Fix the wiring."
        )

    return validation


def print_validation_report(validation: SankirtanValidation) -> None:
    """Print human-readable validation report."""
    status = "✅ WATERTIGHT" if validation.is_watertight else "❌ LEAKING"

    print(f"""
{'=' * 60}
  SANKIRTAN VALIDATOR - {status}
{'=' * 60}

  Total Checked:  {validation.total_checked}
  Valid:          {validation.total_valid}
  Invalid:        {validation.total_invalid}

  Quarters:       {'✅' if validation.quarters_valid else '❌'}
  Guardians:      {'✅' if validation.guardians_valid else '❌'}
  Adapters:       {'✅' if validation.adapters_valid else '❌'}
""")

    if validation.errors:
        print(f"  ERRORS ({len(validation.errors)}):")
        for err in validation.errors[:TEN]:
            print(f"    ❌ {err}")
        if len(validation.errors) > TEN:
            print(f"    ... and {len(validation.errors) - TEN} more")

    print(f"""
{'=' * 60}
  {"Krishna is always there." if validation.is_watertight else "Fix the wiring!"}
{'=' * 60}
""")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "FOLDER_IS_WIRING",
    "NO_FOLDER_NO_EXISTENCE",
    "POSITIONS_PER_QUARTER",
    "QUARTER_COUNT",
    "FRACTAL_BASE",
    # Lookup tables (DERIVED from SSOT)
    "POSITION_BY_FOLDER",
    "POSITION_BY_NAME",
    "POSITION_BY_INDEX",
    # Functions
    "folder_exists",
    "get_position_from_folder",
    "get_position_from_name",
    "get_position_by_index",
    # Protocol
    "WiringProtocol",
    "WiringVerification",
    "verify_wiring",
    # Fractal
    "calculate_fractal_depth",
    "calculate_total_nodes",
    # FRACTAL DISCOVERY
    "fractal_getattr",
    "enable_fractal_discovery",
    # HYBRID DISCOVERY (Protocol-First + Backwards Compat)
    "create_hybrid_getattr",
    "enable_hybrid_discovery",
    # UNIVERSAL DISCOVERY (Semantic Router for Code)
    "create_universal_getattr",
    "enable_universal_discovery",
    # SANKIRTAN VALIDATOR
    "ValidationResult",
    "SankirtanValidation",
    "validate_module_discoverable",
    "validate_fractal_discovery",
    "assert_watertight",
    "print_validation_report",
]
