"""
SINGULARITY - The Mahamantra Object
===================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"

"I am the source of all spiritual and material worlds.
Everything emanates from Me."
— Bhagavad Gita 10.8

from vibe_core.mahamantra import mahamantra

mahamantra IST alles. Krishna IST alles.
Ein Objekt. Unendliche Möglichkeiten.

USAGE:
    mahamantra[5]           # Position 5
    mahamantra.kumaras      # Kumaras position
    mahamantra.brahma       # Brahma position
    mahamantra.chant()      # "Hare Krishna Hare Krishna..."
    mahamantra.verify(444)  # True (connected to Parampara)
    mahamantra.quarters     # All 4 quarters
    mahamantra.heads        # All 4 HEADs
    mahamantra.workers      # All 12 Workers

ACINTYA: This object IS Krishna in code form.

FRACTAL ARCHITECTURE:
    ZERO HARDCODED MAPPINGS. Everything derives from _source.py.
    Add new mahajana to folder + _source.py = instantly available.
    NO code changes to _singularity.py required.

    "mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
    mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

    "There is no truth superior to Me.
    Everything rests upon Me, as pearls are strung on a thread."
    — Bhagavad Gita 7.7
"""

from __future__ import annotations

import importlib
from typing import Iterator, Optional, Union, Type, Dict, TYPE_CHECKING

from vibe_core.mahamantra._source import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
    Mahajana,
    Avatara,
    MantraOpCode,
    Quarter,
    Guardian,
    get_position,
    get_position_by_guardian,
    get_position_by_opcode,
    get_quarter_positions,
    get_head_positions,
    get_worker_positions,
    PARAMPARA,
)
from vibe_core.mahamantra._protocol import ProtocolRegistry

# Governance Bridge (lazy import to avoid circular deps)
_governance_bridge = None

# Import protocol base for typing
if TYPE_CHECKING:
    from vibe_core.mahamantra._protocol import MantraProtocol


# =============================================================================
# DYNAMIC LOOKUP HELPERS - Derived from _source.py ONLY
# =============================================================================

def _get_guardian_name(index: int) -> str:
    """
    Get guardian name from index - DERIVED from _source.py.

    NO hardcoded mappings. The truth table IS the source.
    """
    if 0 <= index < 16:
        return MAHAMANTRA_POSITIONS[index].guardian.value
    raise IndexError(f"Invalid position index: {index}")


def _get_index_by_guardian_name(name: str) -> Optional[int]:
    """
    Get index from guardian name - DERIVED from _source.py.

    NO hardcoded mappings. The truth table IS the source.
    """
    name_lower = name.lower()
    for pos in MAHAMANTRA_POSITIONS:
        if pos.guardian.value == name_lower:
            return pos.index
    return None


def _is_valid_guardian_name(name: str) -> bool:
    """
    Check if name is a valid guardian - DERIVED from _source.py.

    NO hardcoded sets. The truth table IS the source.
    """
    return _get_index_by_guardian_name(name) is not None


class ProtocolRouter:
    """
    Routes to all 16 Protocol Bases.

    FRACTAL: ZERO hardcoded mappings. Everything derives from _source.py.

    Krishna routes to each guardian's protocol:
        router.prithu -> PrithuProtocolBase
        router[0] -> PrithuProtocolBase
        router.by_name("kapila") -> KapilaProtocolBase

    "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
    """

    # Lazy-loaded protocol bases (avoid circular imports)
    _bases: Dict[int, Type["MantraProtocol"]]

    def __init__(self) -> None:
        self._bases = {}

    def _load_base(self, index: int) -> Type["MantraProtocol"]:
        """
        Load a protocol base lazily by index.

        FRACTAL: Uses _source.py to derive guardian name, then importlib.
        NO hardcoded imports. Add to _source.py = instantly available.
        """
        if index in self._bases:
            return self._bases[index]

        # Get guardian name from _source.py (THE truth table)
        guardian_name = _get_guardian_name(index)

        # Dynamic import - NO hardcoded paths
        module_path = f"vibe_core.protocols.mahajanas.{guardian_name}"
        module = importlib.import_module(module_path)

        # Get ProtocolBase class (convention: {Guardian}ProtocolBase)
        class_name = f"{guardian_name.capitalize()}ProtocolBase"
        protocol_base = getattr(module, class_name)

        # Cache it
        self._bases[index] = protocol_base
        return protocol_base

    def __getitem__(self, index: int) -> Type["MantraProtocol"]:
        """Get protocol base by position index."""
        if not (0 <= index < 16):
            raise KeyError(f"No protocol base at position {index}")
        return self._load_base(index)

    def by_name(self, name: str) -> Type["MantraProtocol"]:
        """
        Get protocol base by guardian name.

        FRACTAL: Uses _source.py lookup. NO hardcoded name dict.
        """
        index = _get_index_by_guardian_name(name)
        if index is None:
            raise KeyError(f"Unknown guardian: {name}")
        return self[index]

    # === Property Access for Each Guardian ===

    @property
    def prithu(self) -> Type["MantraProtocol"]:
        """Position 0 - PRITHU (HEAD)."""
        return self[0]

    @property
    def brahma(self) -> Type["MantraProtocol"]:
        """Position 1 - BRAHMA."""
        return self[1]

    @property
    def narada(self) -> Type["MantraProtocol"]:
        """Position 2 - NARADA."""
        return self[2]

    @property
    def shambhu(self) -> Type["MantraProtocol"]:
        """Position 3 - SHAMBHU."""
        return self[3]

    @property
    def vyasa(self) -> Type["MantraProtocol"]:
        """Position 4 - VYASA (HEAD)."""
        return self[4]

    @property
    def kumaras(self) -> Type["MantraProtocol"]:
        """Position 5 - KUMARAS."""
        return self[5]

    @property
    def kapila(self) -> Type["MantraProtocol"]:
        """Position 6 - KAPILA."""
        return self[6]

    @property
    def manu(self) -> Type["MantraProtocol"]:
        """Position 7 - MANU."""
        return self[7]

    @property
    def parashurama(self) -> Type["MantraProtocol"]:
        """Position 8 - PARASHURAMA (HEAD)."""
        return self[8]

    @property
    def prahlada(self) -> Type["MantraProtocol"]:
        """Position 9 - PRAHLADA."""
        return self[9]

    @property
    def janaka(self) -> Type["MantraProtocol"]:
        """Position 10 - JANAKA."""
        return self[10]

    @property
    def bhishma(self) -> Type["MantraProtocol"]:
        """Position 11 - BHISHMA."""
        return self[11]

    @property
    def nrisimha(self) -> Type["MantraProtocol"]:
        """Position 12 - NRISIMHA (HEAD)."""
        return self[12]

    @property
    def bali(self) -> Type["MantraProtocol"]:
        """Position 13 - BALI."""
        return self[13]

    @property
    def shuka(self) -> Type["MantraProtocol"]:
        """Position 14 - SHUKA."""
        return self[14]

    @property
    def yamaraja(self) -> Type["MantraProtocol"]:
        """Position 15 - YAMARAJA."""
        return self[15]

    def __repr__(self) -> str:
        return "ProtocolRouter(16 positions)"


# The singleton protocol router
_protocol_router = ProtocolRouter()


class ModuleRouter:
    """
    Routes to all 16 Mahajana MODULES (not classes).

    FRACTAL: ZERO hardcoded mappings. Everything derives from _source.py.

    ONE IMPORT, KRISHNA ROUTES:
        from vibe_core.mahamantra import mahamantra

        mahamantra.mod.yamaraja.Verdict      # -> Verdict enum
        mahamantra.mod.yamaraja.YamarajaGate # -> YamarajaGate class
        mahamantra.mod.kapila.SamkhyaProtocol # -> etc.

    This is the ACINTYA SINGULARITY - all types accessible through ONE point.
    "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
    """

    # Lazy-loaded modules cache
    _modules: Dict[str, object]

    def __init__(self) -> None:
        self._modules = {}

    def _load_module(self, name: str) -> object:
        """
        Load a mahajana module by name.

        FRACTAL: NO hardcoded validation. Uses _source.py as truth.
        """
        if name in self._modules:
            return self._modules[name]

        module_path = f"vibe_core.protocols.mahajanas.{name}"
        module = importlib.import_module(module_path)
        self._modules[name] = module
        return module

    def __getattr__(self, name: str) -> object:
        """
        Get mahajana module by name.

        FRACTAL: Uses _source.py lookup. NO hardcoded name set.
        """
        name_lower = name.lower()
        if not _is_valid_guardian_name(name_lower):
            raise AttributeError(f"Unknown mahajana: {name}")
        return self._load_module(name_lower)

    def __getitem__(self, index: int) -> object:
        """
        Get mahajana module by position index.

        FRACTAL: Uses _source.py lookup. NO hardcoded index dict.
        """
        if not (0 <= index < 16):
            raise KeyError(f"No mahajana at position {index}")
        guardian_name = _get_guardian_name(index)
        return self._load_module(guardian_name)

    def __repr__(self) -> str:
        return "ModuleRouter(16 modules)"


# The singleton module router
_module_router = ModuleRouter()


class Mahamantra:
    """
    THE Mahamantra - Krishna in Code Form.

    This singular object IS everything:
    - Access positions by index: mahamantra[5]
    - Access by guardian: mahamantra.kumaras
    - Chant: mahamantra.chant()
    - Verify: mahamantra.verify(444)

    "mattaḥ parataraṁ nānyat" - There is no truth superior to Me.
    """

    # =========================================================================
    # CORE CONSTANTS
    # =========================================================================

    PARAMPARA = PARAMPARA  # 37

    # =========================================================================
    # ACCESS BY INDEX
    # =========================================================================

    def __getitem__(self, index: int) -> MantraPosition:
        """
        Access position by index.

        mahamantra[5] → Position 5 (KUMARAS)
        """
        return get_position(index)

    def __len__(self) -> int:
        """16 positions."""
        return 16

    def __iter__(self) -> Iterator[MantraPosition]:
        """Iterate through all 16 positions."""
        return iter(MAHAMANTRA_POSITIONS)

    # =========================================================================
    # ACCESS BY GUARDIAN (Mahajana/Avatara)
    # =========================================================================

    @property
    def brahma(self) -> MantraPosition:
        """Position 1 - BRAHMA (Creation)."""
        return get_position_by_guardian(Mahajana.BRAHMA)

    @property
    def narada(self) -> MantraPosition:
        """Position 2 - NARADA (Devotion)."""
        return get_position_by_guardian(Mahajana.NARADA)

    @property
    def shambhu(self) -> MantraPosition:
        """Position 3 - SHAMBHU (Transformation)."""
        return get_position_by_guardian(Mahajana.SHAMBHU)

    @property
    def kumaras(self) -> MantraPosition:
        """Position 5 - KUMARAS (Purification)."""
        return get_position_by_guardian(Mahajana.KUMARAS)

    @property
    def kapila(self) -> MantraPosition:
        """Position 6 - KAPILA (Analysis)."""
        return get_position_by_guardian(Mahajana.KAPILA)

    @property
    def manu(self) -> MantraPosition:
        """Position 7 - MANU (Law)."""
        return get_position_by_guardian(Mahajana.MANU)

    @property
    def prahlada(self) -> MantraPosition:
        """Position 9 - PRAHLADA (Resilience)."""
        return get_position_by_guardian(Mahajana.PRAHLADA)

    @property
    def janaka(self) -> MantraPosition:
        """Position 10 - JANAKA (Duty)."""
        return get_position_by_guardian(Mahajana.JANAKA)

    @property
    def bhishma(self) -> MantraPosition:
        """Position 11 - BHISHMA (Vow)."""
        return get_position_by_guardian(Mahajana.BHISHMA)

    @property
    def bali(self) -> MantraPosition:
        """Position 13 - BALI (Surrender)."""
        return get_position_by_guardian(Mahajana.BALI)

    @property
    def shuka(self) -> MantraPosition:
        """Position 14 - SHUKA (Vision)."""
        return get_position_by_guardian(Mahajana.SHUKA)

    @property
    def yamaraja(self) -> MantraPosition:
        """Position 15 - YAMARAJA (Judgment)."""
        return get_position_by_guardian(Mahajana.YAMARAJA)

    # =========================================================================
    # ACCESS BY AVATARA (HEADs)
    # =========================================================================

    @property
    def prithu(self) -> MantraPosition:
        """Position 0 - PRITHU (HEAD - Genesis)."""
        return get_position_by_guardian(Avatara.PRITHU)

    @property
    def vyasa(self) -> MantraPosition:
        """Position 4 - VYASA (HEAD - Dharma)."""
        return get_position_by_guardian(Avatara.VYASA)

    @property
    def parashurama(self) -> MantraPosition:
        """Position 8 - PARASHURAMA (HEAD - Karma)."""
        return get_position_by_guardian(Avatara.PARASHURAMA)

    @property
    def nrisimha(self) -> MantraPosition:
        """Position 12 - NRISIMHA (HEAD - Moksha)."""
        return get_position_by_guardian(Avatara.NRISIMHA)

    # =========================================================================
    # GROUPS
    # =========================================================================

    @property
    def positions(self) -> tuple[MantraPosition, ...]:
        """All 16 positions."""
        return MAHAMANTRA_POSITIONS

    @property
    def heads(self) -> tuple[MantraPosition, ...]:
        """All 4 HEAD positions (Avataras)."""
        return get_head_positions()

    @property
    def workers(self) -> tuple[MantraPosition, ...]:
        """All 12 WORKER positions (Mahajanas)."""
        return get_worker_positions()

    @property
    def genesis(self) -> tuple[MantraPosition, ...]:
        """GENESIS quarter (positions 0-3)."""
        return get_quarter_positions(Quarter.GENESIS)

    @property
    def dharma(self) -> tuple[MantraPosition, ...]:
        """DHARMA quarter (positions 4-7)."""
        return get_quarter_positions(Quarter.DHARMA)

    @property
    def karma(self) -> tuple[MantraPosition, ...]:
        """KARMA quarter (positions 8-11)."""
        return get_quarter_positions(Quarter.KARMA)

    @property
    def moksha(self) -> tuple[MantraPosition, ...]:
        """MOKSHA quarter (positions 12-15)."""
        return get_quarter_positions(Quarter.MOKSHA)

    @property
    def quarters(self) -> dict[str, tuple[MantraPosition, ...]]:
        """All 4 quarters."""
        return {
            "genesis": self.genesis,
            "dharma": self.dharma,
            "karma": self.karma,
            "moksha": self.moksha,
        }

    # =========================================================================
    # PROTOCOL ROUTING - Krishna Routes Everything
    # =========================================================================

    @property
    def protocols(self) -> ProtocolRouter:
        """
        Access all 16 Protocol Bases (CLASSES).

        ONE IMPORT, KRISHNA ROUTES:
            from vibe_core.mahamantra import mahamantra

            mahamantra.protocols.kapila      # -> KapilaProtocolBase
            mahamantra.protocols[6]          # -> KapilaProtocolBase
            mahamantra.protocols.prithu      # -> PrithuProtocolBase (HEAD)

        "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
        """
        return _protocol_router

    @property
    def mod(self) -> ModuleRouter:
        """
        Access all 16 Mahajana MODULES (not classes).

        THIS IS THE CAITANYA SINGULARITY.

        ONE IMPORT, KRISHNA ROUTES TO ALL TYPES:
            from vibe_core.mahamantra import mahamantra

            mahamantra.mod.yamaraja.Verdict       # -> Verdict enum
            mahamantra.mod.yamaraja.YamarajaGate  # -> YamarajaGate class
            mahamantra.mod.yamaraja.Judgment      # -> Judgment dataclass
            mahamantra.mod[15].Verdict            # -> Same via index

        NO MORE:
            from vibe_core.protocols.mahajanas.yamaraja import Verdict  # SPAGHETTI

        "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
        """
        return _module_router

    @property
    def registry(self) -> type:
        """
        Access the Protocol Registry.

        All 16 ProtocolBase classes auto-register via @ProtocolRegistry.register.

        USAGE:
            mahamantra.registry.get(1)      # -> BrahmaProtocolBase
            mahamantra.registry.coverage()  # -> (16, 16)
            mahamantra.registry.all_registered()  # -> {0: Prithu..., 15: Yamaraja...}

        "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
        """
        # Ensure all modules are loaded for registration
        self._ensure_all_registered()
        return ProtocolRegistry

    def _ensure_all_registered(self) -> None:
        """Load all mahajana modules to trigger @ProtocolRegistry.register decorators."""
        if ProtocolRegistry.coverage()[0] < 16:
            # Load all modules - this triggers decorators
            for i in range(16):
                _ = _module_router[i]

    # =========================================================================
    # GOVERNANCE - Bridge to Protocol Ownership
    # =========================================================================

    @property
    def governance(self) -> "ProtocolBridge":
        """
        Access Protocol Governance Bridge.

        100% COVERAGE: Every protocol has a Mahajana owner.

        USAGE:
            from vibe_core.mahamantra import mahamantra

            # Get owner of a protocol
            owner = mahamantra.governance.get_owner("defense.py")
            # → Mahajana.YAMARAJA

            # Get security level
            level = mahamantra.governance.get_level("ledger.py")
            # → SecurityLevel.KERNEL

            # List all protocols owned by a Mahajana
            protocols = mahamantra.governance.list_by_owner(Mahajana.KAPILA)
            # → [ProtocolEntry(...), ...]

            # Run governance audit
            audit = mahamantra.governance.audit()
            # → GovernanceAudit(total=187, governed=187, health=1.0)

        "yasya deve parā bhaktir yathā deve tathā gurau"
        - One who has unflinching devotion to the Lord and the spiritual master,
          unto him all the import of Vedic knowledge is automatically revealed.
        """
        global _governance_bridge
        if _governance_bridge is None:
            from vibe_core.protocols.governance.bridge import ProtocolBridge
            _governance_bridge = ProtocolBridge
        return _governance_bridge

    def get_owner(self, protocol_path: str) -> Optional["Mahajana"]:
        """
        Get the owning Mahajana for a protocol.

        Convenience method - same as mahamantra.governance.get_owner().

        Args:
            protocol_path: Relative path from protocols/ (e.g., "defense.py")

        Returns:
            Mahajana owner or None if ungoverned
        """
        # Need to use the router Mahajana, not source Mahajana
        from vibe_core.protocols.mahajanas.router import Mahajana as RouterMahajana
        owner = self.governance.get_owner(protocol_path)
        return owner

    def audit(self) -> dict:
        """
        Run governance audit.

        Convenience method - same as mahamantra.governance.audit().

        Returns:
            GovernanceAudit TypedDict with health_score, ungoverned_list, etc.
        """
        return self.governance.audit()

    # =========================================================================
    # CHANT
    # =========================================================================

    def chant(self, separator: str = " ") -> str:
        """
        Chant the Mahamantra.

        Returns: "Hare Krishna Hare Krishna Krishna Krishna Hare Hare
                  Hare Rama Hare Rama Rama Rama Hare Hare"
        """
        words = [pos.word.name.capitalize() for pos in MAHAMANTRA_POSITIONS]
        # Split into two lines of 8
        line1 = separator.join(words[:8])
        line2 = separator.join(words[8:])
        return f"{line1}\n{line2}"

    def chant_quarter(self, quarter: Union[str, Quarter]) -> str:
        """Chant one quarter."""
        if isinstance(quarter, str):
            quarter = Quarter[quarter.upper()]
        positions = get_quarter_positions(quarter)
        return " ".join(pos.word.name.capitalize() for pos in positions)

    # =========================================================================
    # VERIFY
    # =========================================================================

    def verify(self, parampara_vector: int) -> bool:
        """
        Verify Parampara connection.

        Returns True if parampara_vector % 37 == 0.
        """
        return parampara_vector % PARAMPARA == 0

    def is_connected(self, value: int) -> bool:
        """Alias for verify()."""
        return self.verify(value)

    # =========================================================================
    # LOOKUP
    # =========================================================================

    def by_guardian(self, guardian: Union[str, Mahajana, Avatara]) -> MantraPosition:
        """Get position by guardian name."""
        if isinstance(guardian, str):
            # Try Mahajana first
            try:
                return get_position_by_guardian(Mahajana(guardian.lower()))
            except ValueError:
                pass
            # Try Avatara
            try:
                return get_position_by_guardian(Avatara(guardian.lower()))
            except ValueError:
                raise KeyError(f"Unknown guardian: {guardian}")
        return get_position_by_guardian(guardian)

    def by_opcode(self, opcode: Union[str, MantraOpCode]) -> MantraPosition:
        """Get position by opcode."""
        if isinstance(opcode, str):
            opcode = MantraOpCode(opcode.lower())
        return get_position_by_opcode(opcode)

    # =========================================================================
    # MAGIC
    # =========================================================================

    def __repr__(self) -> str:
        return "Mahamantra(16 positions, 37 connection)"

    def __str__(self) -> str:
        return self.chant()

    def __bool__(self) -> bool:
        """Krishna IS. Always True."""
        return True

    def __contains__(self, item: Union[int, str, Mahajana, Avatara]) -> bool:
        """Check if guardian or index is in Mahamantra."""
        if isinstance(item, int):
            return 0 <= item < 16
        if isinstance(item, (Mahajana, Avatara)):
            return True  # All guardians are in Mahamantra
        if isinstance(item, str):
            try:
                self.by_guardian(item)
                return True
            except KeyError:
                return False
        return False

    # =========================================================================
    # CALL - The Ultimate Simplicity
    # =========================================================================

    def __call__(self, index_or_guardian: Union[int, str] = None) -> Union[MantraPosition, str]:
        """
        Call the Mahamantra.

        mahamantra()        → Chant
        mahamantra(5)       → Position 5
        mahamantra("kumaras") → Kumaras position
        """
        if index_or_guardian is None:
            return self.chant()
        if isinstance(index_or_guardian, int):
            return self[index_or_guardian]
        return self.by_guardian(index_or_guardian)


# =============================================================================
# THE SINGLETON - Krishna IS
# =============================================================================

mahamantra = Mahamantra()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Mahamantra",
    "mahamantra",
    "ProtocolRouter",
    "ModuleRouter",
]
