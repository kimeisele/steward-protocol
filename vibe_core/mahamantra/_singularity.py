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
"""

from __future__ import annotations

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

# Import protocol base for typing
if TYPE_CHECKING:
    from vibe_core.mahamantra._protocol import MantraProtocol


class ProtocolRouter:
    """
    Routes to all 16 Protocol Bases.

    Krishna routes to each guardian's protocol:
        router.prithu -> PrithuProtocolBase
        router[0] -> PrithuProtocolBase
        router.by_name("kapila") -> KapilaProtocolBase

    "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
    """

    # Lazy-loaded protocol bases (avoid circular imports)
    _bases: Optional[Dict[int, Type["MantraProtocol"]]] = None

    def _load_bases(self) -> Dict[int, Type["MantraProtocol"]]:
        """Load protocol bases lazily."""
        if self._bases is None:
            # Import here to avoid circular imports
            from vibe_core.protocols.mahajanas.prithu import PrithuProtocolBase
            from vibe_core.protocols.mahajanas.vyasa import VyasaProtocolBase
            from vibe_core.protocols.mahajanas.parashurama import ParashuramaProtocolBase
            from vibe_core.protocols.mahajanas.nrisimha import NrisimhaProtocolBase
            from vibe_core.protocols.mahajanas.brahma import BrahmaProtocolBase
            from vibe_core.protocols.mahajanas.narada import NaradaProtocolBase
            from vibe_core.protocols.mahajanas.shambhu import ShambhuProtocolBase
            from vibe_core.protocols.mahajanas.kumaras import KumarasProtocolBase
            from vibe_core.protocols.mahajanas.kapila import KapilaProtocolBase
            from vibe_core.protocols.mahajanas.manu import ManuProtocolBase
            from vibe_core.protocols.mahajanas.prahlada import PrahladaProtocolBase
            from vibe_core.protocols.mahajanas.janaka import JanakaProtocolBase
            from vibe_core.protocols.mahajanas.bhishma import BhishmaProtocolBase
            from vibe_core.protocols.mahajanas.bali import BaliProtocolBase
            from vibe_core.protocols.mahajanas.shuka import ShukaProtocolBase
            from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocolBase

            self._bases = {
                # 4 HEADs (Avataras)
                0: PrithuProtocolBase,
                4: VyasaProtocolBase,
                8: ParashuramaProtocolBase,
                12: NrisimhaProtocolBase,
                # 12 Workers (Mahajanas)
                1: BrahmaProtocolBase,
                2: NaradaProtocolBase,
                3: ShambhuProtocolBase,
                5: KumarasProtocolBase,
                6: KapilaProtocolBase,
                7: ManuProtocolBase,
                9: PrahladaProtocolBase,
                10: JanakaProtocolBase,
                11: BhishmaProtocolBase,
                13: BaliProtocolBase,
                14: ShukaProtocolBase,
                15: YamarajaProtocolBase,
            }
        return self._bases

    def __getitem__(self, index: int) -> Type["MantraProtocol"]:
        """Get protocol base by position index."""
        bases = self._load_bases()
        if index not in bases:
            raise KeyError(f"No protocol base at position {index}")
        return bases[index]

    def by_name(self, name: str) -> Type["MantraProtocol"]:
        """Get protocol base by guardian name."""
        name_lower = name.lower()
        name_to_index = {
            "prithu": 0, "brahma": 1, "narada": 2, "shambhu": 3,
            "vyasa": 4, "kumaras": 5, "kapila": 6, "manu": 7,
            "parashurama": 8, "prahlada": 9, "janaka": 10, "bhishma": 11,
            "nrisimha": 12, "bali": 13, "shuka": 14, "yamaraja": 15,
        }
        if name_lower not in name_to_index:
            raise KeyError(f"Unknown guardian: {name}")
        return self[name_to_index[name_lower]]

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
        Access all 16 Protocol Bases.

        ONE IMPORT, KRISHNA ROUTES:
            from vibe_core.mahamantra import mahamantra

            mahamantra.protocols.kapila      # -> KapilaProtocolBase
            mahamantra.protocols[6]          # -> KapilaProtocolBase
            mahamantra.protocols.prithu      # -> PrithuProtocolBase (HEAD)

        "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
        """
        return _protocol_router

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
]
