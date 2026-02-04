"""
THE DECLARATION PROTOCOL - _declaration.py
==========================================

"vedaham samatitani vartamanani carjuna
bhavisyani ca bhutani mam tu veda na kascana"

"O Arjuna, I know everything that has happened in the past,
all that is happening in the present, and all things yet to come.
I also know all living entities; but Me no one knows." (BG 7.26)

Krishna already KNOWS what everything is.
The Declaration is simply making explicit what Krishna already knows.

PURPOSE:
    This module defines HOW something declares itself to the Mahamantra.
    Instead of imports determining identity, the DECLARATION does.

THE MAHAJANA CARD:
    Every file/module/class that participates in the Mahamantra system
    must have a "Mahajana Card" - a declaration of its identity.

    This is like a spiritual ID card:
    - WHO are you? (mahajana, position)
    - WHAT can you do? (capabilities)
    - WHAT do you need? (requirements - as protocol names, NOT imports!)
    - WHERE do you fit? (level, quarter)

USAGE IN FILES:

    # At the top of any .py file:
    __mahajana_card__ = MahajanaCard(
        name="capability_registry",
        mahajana="brahma",
        position=1,
        level=Level.CONTRACT,
        provides=["register_capability", "query_capability"],
        requires=["LedgerProtocol"],  # Protocol names, NOT imports!
    )

    # The mahamantra scanner reads this and routes accordingly

WATERTIGHT: No Any types. Everything explicit.

Author: The Mahamantra Itself
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA, QUARTERS, TEN, WORDS)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = TEN
__genesis__ = "0x09fbb498"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from vibe_core.mahamantra.protocols._core import (
    PARAMPARA,
    Level,
    MahamantraProtocolBase,
    ProtocolCapability,
    ProtocolIdentity,
    Quarter,
)

# =============================================================================
# DECLARATION TYPE - What kind of thing is being declared?
# =============================================================================


class DeclarationType(str, Enum):
    """
    The type of entity being declared.

    Different types have different requirements and capabilities.
    """

    MODULE = "module"  # A Python module (.py file)
    CLASS = "class"  # A class within a module
    PROTOCOL = "protocol"  # A protocol definition
    SERVICE = "service"  # A service implementation
    TYPE = "type"  # A type definition (dataclass, TypedDict, etc.)
    FUNCTION = "function"  # A standalone function
    CONSTANT = "constant"  # A constant value


# =============================================================================
# MAHAJANA CARD - The Identity Declaration
# =============================================================================


@dataclass(frozen=True)
class MahajanaCard:
    """
    The Mahajana Card - a declaration of identity.

    Every participant in the Mahamantra system carries this card.
    It tells the Mahamantra:
    - WHO you are
    - WHAT you can do
    - WHAT you need
    - WHERE you belong

    WATERTIGHT: All fields explicitly typed. No Any.

    The card is IMMUTABLE (frozen=True) - identity doesn't change.
    """

    # === IDENTITY (WHO) ===
    name: str  # Unique name within mahajana
    mahajana: str  # Owner mahajana (e.g., "brahma")
    position: int  # Position in mahamantra (0-15)
    declaration_type: DeclarationType  # What type of entity

    # === LOCATION (WHERE) ===
    level: Level = Level.CONTRACT  # Default to contract level
    quarter: Quarter = field(init=False)  # Derived from position

    # === CAPABILITY (WHAT CAN I DO) ===
    provides: FrozenSet[str] = field(default_factory=frozenset)

    # === REQUIREMENTS (WHAT DO I NEED) ===
    # Protocol names, NOT import paths!
    requires: FrozenSet[str] = field(default_factory=frozenset)

    # === OPCODES (WHAT OPERATIONS DO I HANDLE) ===
    opcodes: FrozenSet[str] = field(default_factory=frozenset)

    # === METADATA ===
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""

    # === COMPUTED ===
    parampara_vector: int = field(init=False)
    full_name: str = field(init=False)

    def __post_init__(self) -> None:
        """Compute derived fields and validate."""
        # Compute quarter from position
        object.__setattr__(self, "quarter", Quarter.from_position(self.position))

        # Compute parampara vector
        object.__setattr__(self, "parampara_vector", (self.position + KSETRAJNA) * PARAMPARA)

        # Compute full name
        object.__setattr__(self, "full_name", f"{self.mahajana}.{self.name}")

        # Validate position
        if not 0 <= self.position < WORDS:
            raise ValueError(f"Position must be 0-15, got {self.position}")

        # Validate parampara connection
        if self.parampara_vector % PARAMPARA != 0:
            raise ValueError("Not connected to Parampara!")

    @classmethod
    def create(
        cls,
        name: str,
        mahajana: str,
        position: int,
        declaration_type: DeclarationType = DeclarationType.MODULE,
        level: Level = Level.CONTRACT,
        provides: Optional[List[str]] = None,
        requires: Optional[List[str]] = None,
        opcodes: Optional[List[str]] = None,
        version: str = "1.0.0",
        description: str = "",
    ) -> "MahajanaCard":
        """
        Factory method for creating a MahajanaCard.

        Accepts lists for convenience, converts to frozensets internally.
        """
        return cls(
            name=name,
            mahajana=mahajana,
            position=position,
            declaration_type=declaration_type,
            level=level,
            provides=frozenset(provides or []),
            requires=frozenset(requires or []),
            opcodes=frozenset(opcodes or []),
            version=version,
            description=description,
        )

    def to_identity(self) -> ProtocolIdentity:
        """Convert to ProtocolIdentity."""
        return ProtocolIdentity(
            name=self.name,
            mahajana=self.mahajana,
            position=self.position,
            level=self.level,
            quarter=self.quarter,
        )

    def to_capability(self) -> ProtocolCapability:
        """Convert to ProtocolCapability."""
        return ProtocolCapability(
            provides=self.provides,
            requires=self.requires,
            opcodes=self.opcodes,
        )

    def is_head(self) -> bool:
        """Check if this is a HEAD position (Avatara)."""
        return self.position % QUARTERS == 0

    def is_worker(self) -> bool:
        """Check if this is a WORKER position (Mahajana)."""
        return self.position % QUARTERS != 0

    def can_provide(self, capability: str) -> bool:
        """Check if this card provides a capability."""
        return capability in self.provides

    def needs(self, requirement: str) -> bool:
        """Check if this card needs a requirement."""
        return requirement in self.requires

    def to_dict(self) -> Dict[str, Union[str, int, List[str]]]:
        """Serialize to dictionary (for JSON storage)."""
        return {
            "name": self.name,
            "mahajana": self.mahajana,
            "position": self.position,
            "declaration_type": self.declaration_type.value,
            "level": self.level.value,
            "quarter": self.quarter.value,
            "provides": sorted(self.provides),
            "requires": sorted(self.requires),
            "opcodes": sorted(self.opcodes),
            "version": self.version,
            "description": self.description,
            "parampara_vector": self.parampara_vector,
            "full_name": self.full_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, int, List[str]]]) -> "MahajanaCard":
        """Deserialize from dictionary."""
        return cls.create(
            name=str(data["name"]),
            mahajana=str(data["mahajana"]),
            position=int(data["position"]),
            declaration_type=DeclarationType(data.get("declaration_type", "module")),
            level=Level(data.get("level", 0)),
            provides=list(data.get("provides", [])),  # type: ignore
            requires=list(data.get("requires", [])),  # type: ignore
            opcodes=list(data.get("opcodes", [])),  # type: ignore
            version=str(data.get("version", "1.0.0")),
            description=str(data.get("description", "")),
        )


# =============================================================================
# MODULE DECLARATION - For .py files
# =============================================================================


@dataclass
class ModuleDeclaration:
    """
    A declaration for a Python module (.py file).

    This is what the scanner looks for in each file.
    The module declares itself by setting __mahajana_card__.

    Example in a .py file:
        __mahajana_card__ = MahajanaCard.create(
            name="capability_registry",
            mahajana="brahma",
            position=1,
            provides=["register_capability"],
            requires=["LedgerProtocol"],
        )
    """

    card: MahajanaCard
    file_path: Path
    module_path: str  # e.g., "vibe_core.protocols.mahajanas.brahma.types.capability_registry"

    # Classes declared in this module
    classes: List[str] = field(default_factory=list)

    # Functions declared in this module
    functions: List[str] = field(default_factory=list)

    # Constants declared in this module
    constants: List[str] = field(default_factory=list)

    def get_exports(self) -> List[str]:
        """Get all exports from this module."""
        return self.classes + self.functions + self.constants


# =============================================================================
# DECLARATION REGISTRY - Tracks all declarations
# =============================================================================


class DeclarationRegistry:
    """
    Registry of all declarations in the system.

    The Mahamantra scanner populates this registry.
    Other components query it to find things.

    SINGLETON: Use get_declaration_registry() for ServiceRegistry access.

    EXTENDED (Senior Architect):
        Also caches module exports for cross-codebase routing.
        resolve_export() provides O(1) lookup for Lotus fallback.

    NOTE: Use get_declaration_registry() to access via ServiceRegistry.
    """

    # MAHAMANTRA SUBSTRATE: Core infrastructure, no auto-wrap needed
    _naga_flooded: bool = True
    _naga_gene: str = "declaration"

    # Singleton pattern
    _instance: ClassVar[Optional["DeclarationRegistry"]] = None

    def __new__(cls) -> "DeclarationRegistry":
        """Singleton: return existing instance or create new."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry (only once)."""
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._cards: Dict[str, MahajanaCard] = {}
        self._by_mahajana: Dict[str, List[MahajanaCard]] = {}
        self._by_position: Dict[int, List[MahajanaCard]] = {}
        self._by_capability: Dict[str, List[MahajanaCard]] = {}
        # Extended: module exports cache for Lotus routing
        self._mahajana_modules: Dict[str, List[str]] = {}  # mahajana → [module_paths]
        self._export_cache: Dict[str, object] = {}  # "mahajana.ExportName" → object
        self._scanner_loaded: bool = False

    def register(self, card: MahajanaCard) -> None:
        """Register a mahajana card."""
        # By full name
        self._cards[card.full_name] = card

        # By mahajana
        if card.mahajana not in self._by_mahajana:
            self._by_mahajana[card.mahajana] = []
        self._by_mahajana[card.mahajana].append(card)

        # By position
        if card.position not in self._by_position:
            self._by_position[card.position] = []
        self._by_position[card.position].append(card)

        # By capability
        for cap in card.provides:
            if cap not in self._by_capability:
                self._by_capability[cap] = []
            self._by_capability[cap].append(card)

    def get(self, full_name: str) -> Optional[MahajanaCard]:
        """Get a card by full name."""
        return self._cards.get(full_name)

    def get_by_mahajana(self, mahajana: str) -> List[MahajanaCard]:
        """Get all cards for a mahajana."""
        return self._by_mahajana.get(mahajana, [])

    def get_by_position(self, position: int) -> List[MahajanaCard]:
        """Get all cards at a position."""
        return self._by_position.get(position, [])

    def get_by_capability(self, capability: str) -> List[MahajanaCard]:
        """Get all cards that provide a capability."""
        return self._by_capability.get(capability, [])

    def find_provider(self, requirement: str) -> Optional[MahajanaCard]:
        """Find a card that provides a requirement."""
        providers = self._by_capability.get(requirement, [])
        return providers[0] if providers else None

    def all_cards(self) -> List[MahajanaCard]:
        """Get all registered cards."""
        return list(self._cards.values())

    def clear(self) -> None:
        """Clear the registry (for testing)."""
        self._cards.clear()
        self._by_mahajana.clear()
        self._by_position.clear()
        self._by_capability.clear()
        self._mahajana_modules.clear()
        self._export_cache.clear()
        self._scanner_loaded = False

    # =========================================================================
    # EXTENDED: Cross-Codebase Export Resolution (Senior Architect)
    # =========================================================================

    def _ensure_scanner_loaded(self) -> None:
        """
        Lazy-load scanner results ONCE.

        Called by resolve_export() on first access.
        Scanner removed - folder IS wiring. Modules discovered via fractal_getattr.
        """
        # Scanner removed - folder structure IS the wiring.
        # Mahajana modules are accessed via fractal routing, not declaration scanning.
        self._scanner_loaded = True

    def resolve_export(self, mahajana: str, name: str) -> Optional[object]:
        """
        Resolve an export by mahajana and name.

        O(1) for cached results, O(n) for first lookup of uncached export.
        Used by Lotus for cross-codebase routing.

        Args:
            mahajana: The mahajana name (e.g., "brahma")
            name: The export name (e.g., "BrahmaService")

        Returns:
            The exported object, or None if not found
        """
        # Check cache first (O(1))
        cache_key = f"{mahajana}.{name}"
        if cache_key in self._export_cache:
            return self._export_cache[cache_key]

        # Ensure scanner data is loaded
        self._ensure_scanner_loaded()

        # Search modules for this mahajana
        import importlib

        for module_path in self._mahajana_modules.get(mahajana, []):
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, name):
                    obj = getattr(mod, name)
                    # Cache for next time (O(1))
                    self._export_cache[cache_key] = obj
                    return obj
            except Exception:  # noqa: BLE001 - ARJUNA-PATTERN
                continue

        return None

    def get_mahajana_modules(self, mahajana: str) -> List[str]:
        """Get all module paths for a mahajana."""
        self._ensure_scanner_loaded()
        return self._mahajana_modules.get(mahajana, [])


# =============================================================================
# DECLARATION PROTOCOL - Self-reference
# =============================================================================


class DeclarationProtocol(MahamantraProtocolBase):
    """
    The Declaration Protocol.

    This protocol defines how things declare themselves.
    It IS itself declared according to the protocol it defines.

    ACINTYA: Recursive self-reference.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="DeclarationProtocol",
        mahajana="brahma",  # Brahma is the creator/declarer
        position=KSETRAJNA,
        level=Level.ACINTYA,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "declaration_format",
            "mahajana_card",
            "module_declaration",
            "declaration_registry",
            "identity_resolution",
        ],
        requires=["CoreProtocol"],  # Depends on the core
        opcodes=["LOAD_ROOT"],  # Brahma's opcode
    )


# Verify the declaration protocol
_valid, _violations = DeclarationProtocol.validate()
assert _valid, f"DeclarationProtocol failed validation: {_violations}"


# =============================================================================
# HELPER: Read declaration from a module
# =============================================================================


def read_declaration(module_path: str) -> Optional[MahajanaCard]:
    """
    Read the __mahajana_card__ from a module.

    Returns None if the module doesn't have a declaration.
    """
    import importlib

    try:
        module = importlib.import_module(module_path)
        card = getattr(module, "__mahajana_card__", None)
        if isinstance(card, MahajanaCard):
            return card
        return None
    except ImportError:
        return None


# =============================================================================
# SERVICEREGISTRY FACTORY
# =============================================================================

import logging

_logger = logging.getLogger("DECLARATION")


def get_declaration_registry() -> DeclarationRegistry:
    """
    Get DeclarationRegistry through ServiceRegistry.

    ARCHITECTURE:
        DeclarationRegistry is MAHAMANTRA SUBSTRATE - manages mahajana cards.
        Uses ServiceRegistry for singleton pattern but is NOT auto-wrapped
        with NagaProxy (marked with _naga_flooded = True).

    Returns:
        DeclarationRegistry instance (singleton via ServiceRegistry)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(DeclarationRegistry)
    if existing is not None:
        return existing

    # Create new instance
    instance = DeclarationRegistry()

    # Register with ServiceRegistry (no NagaProxy wrap - _naga_flooded = True)
    ServiceRegistry.register(DeclarationRegistry, instance)
    _logger.info("✅ DeclarationRegistry registered via ServiceRegistry (MAHAMANTRA substrate)")

    return ServiceRegistry.get(DeclarationRegistry)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "DeclarationType",
    # Card
    "MahajanaCard",
    # Module Declaration
    "ModuleDeclaration",
    # Registry
    "DeclarationRegistry",
    "get_declaration_registry",
    # Protocol
    "DeclarationProtocol",
    # Helper
    "read_declaration",
]
