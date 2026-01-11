"""
SHUKA - The 11th Mahajana (Vision/Knowledge/Config)
====================================================
OpCode: CACHE_STATE (Bit 13, Position 13 in Mahamantra)
Opulence: Jnana (Knowledge)

Shukadeva Goswami - The Parrot of Knowledge.
Son of Vyasa. Speaker of Srimad Bhagavatam.
Born liberated. Sees past, present, future.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Shuka is the PERSON responsible for all vision/knowledge.
Not abstract "caching" - PERSONAL observation by Shuka.

OWNED PROTOCOLS:
- State Caching (CACHE_STATE OpCode)
- Reflection / Introspection
- Knowledge Storage
- **CONFIG** - The Shastra of the System
- Darshana (Vision/Philosophy)

WHY CONFIG BELONGS TO SHUKA:
1. Config = "Shastra" (documented knowledge) of the system
2. VYASA (Avatara) COMPILES the Vedas → Creates config
3. SHUKA (Mahajana) DELIVERS/OBSERVES the Vedas → Caches config
4. Shuka "sees without attachment" - pure observation
5. CACHE_STATE is his OpCode - config IS cached state

FRACTAL ARCHITECTURE:
    Config
    └── Section (fractal - each section is also a config)
        └── Field (atomic - typed value)

Each level is SELF-SIMILAR (holographic).
Zoom in: Still a config structure.
Zoom out: Still a config structure.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.SHUKA
LOTUS_POSITION: Final[int] = 14  # MOKSHA Quarter, Worker 2
LOTUS_QUARTER: Final[str] = "moksha"

OWNED_PROTOCOLS: Final[List[str]] = [
    "shuka",
    "config",
    "section",
    "cache",
    "reflect",
    "darshana",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.YIELD_CPU,  # Vyuha: Q4 Worker 2 (CACHE_STATE now HEAD: Nrisimha)
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================


class CachedValue(TypedDict, total=False):
    """
    A cached value with metadata.
    WATERTIGHT - no Any!
    """

    value_type: str  # Python type name
    value_repr: str  # String representation
    value_hash: str  # Hash for change detection
    cached_at: str  # ISO timestamp
    expires_at: str  # ISO timestamp (empty = never)
    source: str  # Where this came from


class ReflectionResult(TypedDict, total=False):
    """
    Result of reflecting on system state.
    WATERTIGHT - no Any!
    """

    cache_keys: List[str]
    cache_count: int
    cache_size_bytes: int
    oldest_entry: str  # ISO timestamp
    newest_entry: str  # ISO timestamp
    health: str  # "pristine", "healthy", "degraded"


# =============================================================================
# CONFIG FIELD TYPES (Atomic Level)
# =============================================================================


class FieldType(str, Enum):
    """Types of config fields."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    PATH = "path"
    LIST_STRING = "list[string]"
    LIST_INTEGER = "list[integer]"
    DICT_STRING = "dict[string]"
    REFERENCE = "reference"  # Reference to another config section


# Type variable for generic config values
T = TypeVar("T")


@dataclass(frozen=True)
class ConfigField(Generic[T]):
    """
    A single config field (atomic level).

    WATERTIGHT: Generic T constrains the value type.
    No Any anywhere.
    """

    name: str
    field_type: FieldType
    default: T
    description: str = ""
    required: bool = True
    validator: Optional[str] = None  # Validator function name

    def validate(self, value: T) -> Tuple[bool, str]:
        """
        Validate a value for this field.
        Returns (is_valid, error_message).
        """
        if value is None and self.required:
            return False, f"Field '{self.name}' is required"
        return True, ""


# =============================================================================
# CONFIG SECTION (Fractal Level)
# =============================================================================


class SectionMeta(TypedDict, total=False):
    """
    Metadata for a config section.
    WATERTIGHT - no Any!
    """

    section_id: str
    owner: str  # Mahajana name
    source_file: str  # Path to YAML/Python source
    loaded_from_yaml: bool
    priority: int  # Load order
    version: str


@runtime_checkable
class SectionProtocol(Protocol):
    """
    Protocol for a config section.

    FRACTAL: Each section can contain sub-sections.
    HOLOGRAPHIC: Self-similar at every level.

    Every section MUST:
    1. Have a section_id (identity)
    2. Have an owner (Mahajana)
    3. Be serializable (to_dict)
    4. Be deserializable (from_dict)
    5. Be validatable (validate)
    """

    @property
    def section_id(self) -> str:
        """Unique identifier for this section."""
        ...

    @property
    def owner(self) -> Mahajana:
        """The Mahajana who owns this section."""
        ...

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[str], Dict[str, str]]]:
        """
        Serialize to dict for YAML/JSON persistence.
        WATERTIGHT: Return type explicitly defined, no Any.
        """
        ...

    @classmethod
    def from_dict(
        cls, data: Dict[str, Union[str, int, float, bool, List[str], Dict[str, str]]]
    ) -> "SectionProtocol":
        """
        Deserialize from dict.
        WATERTIGHT: Input type explicitly defined, no Any.
        """
        ...

    def validate(self) -> List[str]:
        """
        Validate this section.
        Returns list of error messages (empty if valid).
        """
        ...


# =============================================================================
# CONFIG PROTOCOL (Root Level)
# =============================================================================


class ConfigState(TypedDict, total=False):
    """
    Complete config state for serialization.
    WATERTIGHT - no Any!
    """

    sections: Dict[str, Dict[str, Union[str, int, float, bool, List[str], Dict[str, str]]]]
    metadata: Dict[str, SectionMeta]
    version: str
    created_at: str
    modified_at: str
    owner: str  # Mahajana.SHUKA


@runtime_checkable
class ConfigProtocol(Protocol):
    """
    The Config Protocol - Shuka's domain.

    SOURCE OF TRUTH: Python Protocol
    PERSISTENCE: YAML/JSON (optional)

    FRACTAL: Config contains Sections contains Fields
    HOLOGRAPHIC: Same interface at every level

    ANTI-MAYAVAD: Config has OWNER (Shuka).
    Config cannot manage itself.
    """

    @property
    def owner(self) -> Mahajana:
        """Config is owned by SHUKA."""
        ...

    @property
    def sections(self) -> Dict[str, SectionProtocol]:
        """All config sections."""
        ...

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    def get_section(self, section_id: str) -> Optional[SectionProtocol]:
        """Get a section by ID."""
        ...

    def has_section(self, section_id: str) -> bool:
        """Check if section exists."""
        ...

    def read(
        self, path: str
    ) -> Union[str, int, float, bool, List[str], Dict[str, str], None]:
        """
        Read value by dotted path (e.g., 'kernel.features.live_fire').
        WATERTIGHT: Return type is union of allowed types, no Any.
        """
        ...

    def write(
        self,
        path: str,
        value: Union[str, int, float, bool, List[str], Dict[str, str]],
        sovereign_id: str,
    ) -> bool:
        """
        Write value by dotted path.
        ANTI-MAYAVAD: Requires sovereign_id for accountability.
        WATERTIGHT: Value type explicitly constrained.
        """
        ...

    # =========================================================================
    # Persistence (YAML/JSON Layer)
    # =========================================================================

    def to_state(self) -> ConfigState:
        """
        Serialize to ConfigState for persistence.
        SOURCE OF TRUTH remains Python - this is just serialization.
        """
        ...

    @classmethod
    def from_state(cls, state: ConfigState) -> "ConfigProtocol":
        """
        Deserialize from ConfigState.
        Validates against Python Protocol (the truth).
        """
        ...

    def save(self, path: Path) -> bool:
        """Save to YAML/JSON file."""
        ...

    @classmethod
    def load(cls, path: Path) -> "ConfigProtocol":
        """Load from YAML/JSON file, validate against protocol."""
        ...

    # =========================================================================
    # Validation
    # =========================================================================

    def validate(self) -> List[str]:
        """
        Validate entire config.
        Returns list of errors (empty if valid).
        """
        ...


# =============================================================================
# SHUKA PROTOCOL (Main Vision Protocol)
# =============================================================================


@runtime_checkable
class ShukaProtocol(Protocol):
    """
    The Vision Protocol - Shuka's domain.

    Any system that caches/reflects/configs must implement this.
    WATERTIGHT - no Any types!

    ANTI-MAYAVAD: Shuka is the PERSON.
    Not abstract "caching" - PERSONAL observation.
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.SHUKA."""
        ...

    # =========================================================================
    # Caching (CACHE_STATE OpCode)
    # =========================================================================

    def cache(self, key: str, value: CachedValue) -> bool:
        """
        Cache a value with metadata.
        WATERTIGHT: value is CachedValue TypedDict, not Any.
        Returns True if cached successfully.
        """
        ...

    def view(self, key: str) -> Optional[CachedValue]:
        """
        View cached value.
        Returns None if not cached.
        WATERTIGHT: Returns CachedValue, not Any.
        """
        ...

    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.
        Returns True if entry existed and was removed.
        """
        ...

    # =========================================================================
    # Reflection (Introspection)
    # =========================================================================

    def reflect(self) -> ReflectionResult:
        """
        Reflect on all cached state.
        WATERTIGHT: Returns ReflectionResult, not Dict[str, Any].
        """
        ...

    # =========================================================================
    # Config Access (Delegated to ConfigProtocol)
    # =========================================================================

    def get_config(self) -> Optional[ConfigProtocol]:
        """
        Get the system config (if available).
        Config is owned by Shuka.
        """
        ...


# =============================================================================
# NULL SHUKA (For testing)
# =============================================================================


class NullShuka:
    """
    The Blind One.
    No caching/vision (for testing without state).
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHUKA

    def cache(self, key: str, value: CachedValue) -> bool:
        return True  # Pretend we cached

    def view(self, key: str) -> Optional[CachedValue]:
        return None  # Nothing cached

    def invalidate(self, key: str) -> bool:
        return False  # Nothing to invalidate

    def reflect(self) -> ReflectionResult:
        return ReflectionResult(
            cache_keys=[],
            cache_count=0,
            cache_size_bytes=0,
            health="pristine",
        )

    def get_config(self) -> Optional[ConfigProtocol]:
        return None  # No config in null mode


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "OWNED_PROTOCOLS",
    "OWNED_OPCODES",
    # State Types (WATERTIGHT)
    "CachedValue",
    "ReflectionResult",
    # Config Types
    "FieldType",
    "ConfigField",
    "SectionMeta",
    "ConfigState",
    # Protocols
    "SectionProtocol",
    "ConfigProtocol",
    "ShukaProtocol",
    # Implementations
    "NullShuka",
]
