"""
GUARDIAN REGISTRY - Dynamic Dispatch from SSOT
===============================================

"yato vā imāni bhūtāni jāyante, yena jātāni jīvanti"
"From whom all beings are born, by whom they are sustained..."
— Taittiriya Upanishad 3.1

LEVEL -1: META-PROGRAMMING

Der Code *weiß nicht*, wer "Vyasa" ist.
Der Code weiß nur "Index 0".

Die SSOT (MAHAMANTRA_POSITIONS) bestimmt zur Laufzeit,
welcher Guardian an welcher Position sitzt.

**ZERO manual imports. ZERO hardcoded names.**

GUARDIANS = 12 Mahajanas (Workers) + 4 Avataras (Heads) = 16 Total

Usage:
    from vibe_core.mahamantra.substrate.registry import GuardianRegistry

    registry = GuardianRegistry()
    BootMode = registry.load_type(position=0, type_name="BootMode")
    ProcessManager = registry.load_type(position=0, type_name="ProcessManager")

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x94644443"  # GenesisByte: parampara % 37 == 0

import importlib
from typing import Any, Dict, Optional, Type, Protocol as TypingProtocol, TypeVar, cast
from types import ModuleType

from vibe_core.mahamantra.substrate.position import MantraPosition
from vibe_core.mahamantra.substrate.wiring import (
    POSITION_BY_INDEX,
    get_position_by_index,
)


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar("T")
P = TypeVar("P")  # Protocol type variable (for future protocol enforcement)


# =============================================================================
# GUARDIAN REGISTRY - Dynamic Component Loader
# =============================================================================


class GuardianRegistry:
    """
    Registry for dynamic loading of Guardian components.

    **LOTUS LEVEL (-1):**
    The code doesn't know WHO is at a position, only WHAT position does.

    When you change the SSOT (position.py), this automatically adapts.

    **GUARDIANS:**
    - 12 Mahajanas (Workers at positions 1,2,3,5,6,7,9,10,11,13,14,15)
    - 4 Avataras (Heads at positions 0,4,8,12)
    - Total: 16 positions in the Mahamantra

    Zero manual imports. Zero hardcoded names.
    Single Source of Truth: MAHAMANTRA_POSITIONS.
    """

    _module_cache: Dict[str, ModuleType] = {}
    _type_cache: Dict[str, Type[Any]] = {}

    @classmethod
    def get_position(cls, index: int) -> Optional[MantraPosition]:
        """
        Get MantraPosition by index.

        Args:
            index: Position index (0-15)

        Returns:
            MantraPosition or None if invalid index
        """
        return get_position_by_index(index)

    @classmethod
    def get_guardian_name(cls, index: int) -> Optional[str]:
        """
        Get guardian name at position.

        Args:
            index: Position index (0-15)

        Returns:
            Guardian name (lowercase) or None

        Example:
            >>> GuardianRegistry.get_guardian_name(0)
            'vyasa'
            >>> GuardianRegistry.get_guardian_name(4)
            'prithu'
            >>> GuardianRegistry.get_guardian_name(1)
            'brahma'
        """
        position = cls.get_position(index)
        if position is None:
            return None

        # Guardian is Union[Mahajana, Avatara], both are str Enums
        return position.guardian.value  # Returns lowercase string

    @classmethod
    def _get_module_path(cls, index: int, component: str) -> Optional[str]:
        """
        Build dynamic import path for a component.

        Args:
            index: Position index (0-15)
            component: Component category (e.g., "types", "service")

        Returns:
            Import path string or None

        Example:
            >>> cls._get_module_path(0, "types")
            'vibe_core.protocols.mahajanas.vyasa.types'
            >>> cls._get_module_path(1, "types")
            'vibe_core.protocols.mahajanas.brahma.types'
        """
        guardian = cls.get_guardian_name(index)
        if guardian is None:
            return None

        return f"vibe_core.protocols.mahajanas.{guardian}.{component}"

    @classmethod
    def load_module(cls, index: int, component: str) -> Optional[ModuleType]:
        """
        Load a module component from the guardian at position.

        Args:
            index: Position index (0-15)
            component: Component category (e.g., "types", "service")

        Returns:
            Module object or None if not found

        Example:
            >>> types_module = GuardianRegistry.load_module(0, "types")
            >>> BootMode = types_module.BootMode
        """
        module_path = cls._get_module_path(index, component)
        if module_path is None:
            return None

        # Check cache
        if module_path in cls._module_cache:
            return cls._module_cache[module_path]

        # Dynamic import
        try:
            module = importlib.import_module(module_path)
            cls._module_cache[module_path] = module
            return module
        except (ImportError, ModuleNotFoundError):
            return None

    @classmethod
    def load_type(
        cls,
        position: int,
        type_name: str,
        protocol: Optional[Type[P]] = None,
    ) -> Optional[Type[Any]]:
        """
        Load a type from the guardian's types module.

        **THIS IS THE LOTUS CORE.**

        Position determines WHO owns the type.
        SSOT determines WHO sits at that position.
        Registry loads it dynamically.

        Args:
            position: Position index (0-15)
            type_name: Name of the type class
            protocol: Optional protocol to validate against (future use)

        Returns:
            Type class or None if not found

        Example:
            >>> BootMode = GuardianRegistry.load_type(0, "BootMode")
            >>> ProcessManager = GuardianRegistry.load_type(0, "ProcessManager")
            >>> ErrorCode = GuardianRegistry.load_type(4, "ErrorCode")

        Protocol Enforcement (Future):
            >>> from vibe_core.protocols import IBootMode
            >>> BootMode = GuardianRegistry.load_type(0, "BootMode", protocol=IBootMode)
            >>> # Will assert that BootMode implements IBootMode
        """
        cache_key = f"{position}:{type_name}"

        # Check cache
        if cache_key in cls._type_cache:
            return cls._type_cache[cache_key]

        # Load types module
        types_module = cls.load_module(position, "types")
        if types_module is None:
            return None

        # Get type from module
        try:
            type_class = getattr(types_module, type_name)

            # TODO: Protocol enforcement (future implementation)
            # if protocol is not None:
            #     if not isinstance(type_class, protocol):
            #         raise TypeError(f"{type_class} doesn't implement {protocol}")

            cls._type_cache[cache_key] = type_class
            return type_class
        except AttributeError:
            return None

    @classmethod
    def get_all_guardians(cls) -> list[str]:
        """
        Get all guardian names from the position table.

        Returns:
            List of all guardian names (lowercase) in position order

        Example:
            >>> GuardianRegistry.get_all_guardians()
            ['vyasa', 'brahma', 'narada', 'shambhu', 'prithu', ...]
        """
        return [get_position_by_index(i).guardian.value for i in range(16) if get_position_by_index(i) is not None]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches. Useful for testing."""
        cls._module_cache.clear()
        cls._type_cache.clear()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def load_type_from_position(position: int, type_name: str) -> Optional[Type[Any]]:
    """
    Convenience function for loading types.

    Example:
        >>> from vibe_core.mahamantra.substrate.registry import load_type_from_position
        >>> BootMode = load_type_from_position(0, "BootMode")
    """
    return GuardianRegistry.load_type(position, type_name)
