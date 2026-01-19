"""
SHUKA - The 11th Mahajana (Vision/Knowledge/Config)
====================================================

POSITION: 14 (MOKSHA Quarter, YIELD_CPU OpCode)

Shukadeva Goswami - The Parrot of Knowledge.
Son of Vyasa. Speaker of Srimad Bhagavatam.
Born liberated. Sees past, present, future.

DERIVED FROM MAHAMANTRA:
    Position 14 -> guardian=SHUKA, opcode=YIELD_CPU, quarter=MOKSHA
    All properties derived from truth table. No manual wiring.

Shuka "sees without attachment" - pure observation.
Config IS cached state.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 14

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    ClassVar,
    Dict,
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

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# SHUKA PROTOCOL BASE - Derives from MantraPosition 14
# =============================================================================


@ProtocolRegistry.register
class ShukaProtocolBase(WorkerProtocol):
    """
    Shuka protocol ownership - DERIVED from Mahamantra position 14.

    NO MANUAL WIRING:
        _position_index = 14 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.SHUKA
        opcode()    -> MantraOpCode.LOG_EMIT
        quarter()   -> Quarter.MOKSHA
        is_head()   -> False (Worker position)
        parampara_vector() -> 555 (% 37 == 0)
    """

    _position_index: ClassVar[int] = 14  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[14]


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


class ViewCliResult(TypedDict):
    """Result of CLI view operation. WATERTIGHT - no Any!"""

    success: bool
    key: str
    cached: bool
    cache_count: int
    health: str


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
    def from_dict(cls, data: Dict[str, Union[str, int, float, bool, List[str], Dict[str, str]]]) -> "SectionProtocol":
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

    def read(self, path: str) -> Union[str, int, float, bool, List[str], Dict[str, str], None]:
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

    DERIVED: Position 14 -> SHUKA, YIELD_CPU, MOKSHA
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 14 in the Mahamantra."""
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

    def view(self, target_id: str) -> str:
        """View a target from a high perspective."""
        ...

    def render_file(self, content: str, path: str) -> bool:
        """Render markdown content to file."""
        ...

    def check_manifest_health(self) -> dict[str, object]:
        """Check manifestation system health."""
        ...

    def get_state(self) -> dict[str, object]:
        """Get state."""
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


class NullShuka(ShukaProtocolBase):
    """
    The Blind One.
    No caching/vision (for testing without state).

    Inherits from ShukaProtocolBase -> position 14 -> SHUKA.
    """

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

    def view_cli(self, key: str = "status") -> ViewCliResult:
        """CLI: View cached state. WATERTIGHT."""
        reflection = self.reflect()
        cached_value = self.view(key)
        return ViewCliResult(
            success=True,
            key=key,
            cached=cached_value is not None,
            cache_count=reflection.get("cache_count", 0),
            health=reflection.get("health", "pristine"),
        )


# =============================================================================
# REFLECT - System Introspection
# =============================================================================

from vibe_core.protocols.mahajanas.shuka.reflect import (
    HealthStatus,
    HealthCheck,
    Capability,
    Dependency,
    SystemMetrics,
    SystemSnapshot,
    HealthChecker,
    ReflectProtocol,
    Reflector,
    NullReflector,
    LOTUS_POSITION as REFLECT_POSITION,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "ShukaProtocolBase",
    # State Types (WATERTIGHT)
    "CachedValue",
    "ReflectionResult",
    "ViewCliResult",
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
    # Reflect (System Introspection)
    "HealthStatus",
    "HealthCheck",
    "Capability",
    "Dependency",
    "SystemMetrics",
    "SystemSnapshot",
    "HealthChecker",
    "ReflectProtocol",
    "Reflector",
    "NullReflector",
]
