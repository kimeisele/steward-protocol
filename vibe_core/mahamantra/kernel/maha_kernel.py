"""
MAHA KERNEL - The Protocol-Based Resonance Kernel
=================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

PROTOCOL-BASED ARCHITECTURE:
    1. Implements PanchaTattvaProtocol (5 Questions)
    2. Uses MahamantraLotus for RESONANCE routing (NOT if/else!)
    3. __call__ enables: kernel("text") → READS. COMPUTES. RESPONDS.

RESONANCE ROUTING (9 NavaBhakti):
    1. SRAVANAM:       Input empfangen
    2. KIRTANAM:       MahaCompression → seed
    3. SMARANAM:       MahaKirtan → vibration
    4. PADA_SEVANAM:   MahaResonator → attractor
    5. ARCANAM:        Parampara verification
    6. VANDANAM:       GitaResonance → verse match
    7. DASYAM:         Position/Quarter determination
    8. SAKHYAM:        MahaCell creation
    9. ATMA_NIVEDANAM: Complete response

USAGE:
    from vibe_core.mahamantra.kernel.maha_kernel import MahaKernel

    kernel = MahaKernel()
    kernel("analyze this")  # → Resonance-based routing
    kernel.brahma           # → via mahamantra.mod (BalaramaProxy)
"""

from __future__ import annotations

__mahajana__ = "vishnu"
__position__ = 0
__genesis__ = "0x00000000"

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict

if TYPE_CHECKING:
    from vibe_core.mahamantra.kernel.singularity import TickState
    from vibe_core.mahamantra.protocols._header import MahaCell

logger = logging.getLogger("MAHA_KERNEL")


class MahaKernel(PanchaTattvaProtocol):
    """
    The Protocol-Based Resonance Kernel.

    IMPLEMENTS: PanchaTattvaProtocol (the 5 Questions)
    USES: MahamantraLotus for resonance routing
    ADDS: Ledger integration
    """

    # NAGA BLESSING: MahaKernel IS mahamantra - absolute sovereignty
    _naga_flooded: bool = True

    __slots__ = ("_lotus", "_singularity", "_ledger")

    def __init__(self, ledger_path: str = ":memory:") -> None:
        """
        Initialize kernel.

        Args:
            ledger_path: Path to SQLite ledger, or ":memory:" for in-memory
        """
        # 1. MAHAMANTRA LOTUS (for __call__ resonance routing)
        from vibe_core.mahamantra._mahamantra_lotus import get_mahamantra

        self._lotus = get_mahamantra()

        # 2. MAHAMANTRA SINGULARITY (for infrastructure: mod, registry, etc.)
        from vibe_core.mahamantra.kernel.singularity import Mahamantra

        self._singularity = Mahamantra()

        # 3. LEDGER (the only thing we add)
        from vibe_core.mahamantra import InMemoryLedger, SQLiteLedger

        if ledger_path == ":memory:":
            self._ledger = InMemoryLedger()
        else:
            self._ledger = SQLiteLedger(ledger_path)

        # 4. INJECT LEDGER to services that need it
        self._inject_ledger()

        logger.info("🕉️ MahaKernel initialized (Protocol-based, Resonance routing)")

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of MahaKernel."""
        return {
            "chaitanya": "MahaKernel - The Protocol-Based Resonance Kernel",
            "nityananda": "MahamantraLotus (9 NavaBhakti Flow)",
            "advaita": "kernel('text') → Resonance Routing",
            "gadadhara": "Input → Seed → Attractor → Position → Response",
            "srivasa": "PanchaTattvaProtocol Governance",
        }

    # =========================================================================
    # RESONANCE ROUTING (__call__)
    # =========================================================================

    def __call__(self, input_data: Union[str, "MahaCell"]) -> Dict[str, object]:
        """
        RESONANCE-BASED ROUTING.

        kernel("anything") → READS. UNDERSTANDS. COMPUTES. RESPONDS.

        Delegates to MahamantraLotus.__call__ which implements
        the 9 NavaBhakti flow for pure resonance computation.

        Args:
            input_data: String or MahaCell to process

        Returns:
            ExecuteResult with position, guardian, quarter, guna, output
        """
        return self._lotus(input_data)

    def _inject_ledger(self) -> None:
        """Inject ledger to services via singularity.mod."""
        # Services that need ledger: brahma, bhishma, yamaraja
        for guardian in ["brahma", "bhishma", "yamaraja"]:
            try:
                service = getattr(self._singularity.mod, guardian)
                # Check if it has inject_ledger or accepts ledger
                if hasattr(service, "inject_ledger"):
                    service.inject_ledger(self._ledger)
                elif hasattr(service, "ledger"):
                    service.ledger = self._ledger
            except Exception as e:
                logger.debug(f"Could not inject ledger to {guardian}: {e}")

    # =========================================================================
    # DELEGATE EVERYTHING TO MAHAMANTRA
    # =========================================================================

    @property
    def ledger(self):
        """The immutable event ledger."""
        return self._ledger

    @property
    def lotus(self):
        """The MahamantraLotus (resonance routing)."""
        return self._lotus

    @property
    def singularity(self):
        """The Mahamantra singularity (infrastructure)."""
        return self._singularity

    # --- Position Access (via singularity) ---

    def __getitem__(self, index: int):
        """kernel[5] → singularity[5]"""
        return self._singularity[index]

    def __len__(self) -> int:
        return len(self._singularity)

    def __iter__(self):
        return iter(self._singularity)

    # --- Guardian Access (Delegate to Lotus) ---

    def __getattr__(self, name: str) -> Any:
        """
        kernel.brahma → Delegates to MahamantraLotus

        MahamantraLotus handles routing via:
        - LotusNode (folder-based auto-discovery)
        - DeclarationRegistry (cross-codebase routing)

        NO if/else chains here. Pure delegation.
        """
        if name.startswith("_"):
            raise AttributeError(name)

        # DELEGATE to MahamantraLotus - it knows how to route
        return getattr(self._lotus, name)

    # --- Core Operations (via singularity) ---

    def tick(self) -> "TickState":
        """Advance one position in the 16-word mantra."""
        return self._singularity.tick()

    def chant(self, separator: str = " ") -> str:
        """Chant the complete Mahamantra (16 words)."""
        return self._singularity.chant(separator)

    def verify(self, value: int) -> bool:
        """Verify connection to Parampara."""
        return self._singularity.verify(value)

    # --- Infrastructure Access (via singularity) ---

    @property
    def mod(self):
        """ModuleRouter (services via BalaramaProxy)."""
        return self._singularity.mod

    @property
    def cells(self):
        """CellRouter (O(1) cell lookup)."""
        return self._lotus.cells  # Lotus has cells

    @property
    def shadow(self):
        """ShadowReactorFactory."""
        return self._lotus.shadow  # Lotus has shadow

    @property
    def governance(self):
        """Protocol governance bridge."""
        return self._singularity.governance

    @property
    def kala(self):
        """TimeKeeper."""
        return self._singularity.kala

    @property
    def registry(self):
        """ProtocolRegistry."""
        return self._singularity.registry

    # --- Convenience (via singularity) ---

    def compression(self):
        """Create MahaCompression engine."""
        return self._singularity.compression()

    def network(self):
        """Create LotusIPRouter."""
        return self._singularity.network()

    def cell_from_content(self, content: str, *, register: bool = True):
        """Create MahaCell from content."""
        return self._singularity.cell_from_content(content, register=register)

    def __repr__(self) -> str:
        return "MahaKernel(resonance=active)"


# =============================================================================
# SINGLETON
# =============================================================================

_kernel: Optional[MahaKernel] = None


def get_kernel(ledger_path: str = ":memory:") -> MahaKernel:
    """Get the singleton MahaKernel."""
    global _kernel
    if _kernel is None:
        _kernel = MahaKernel(ledger_path)
    return _kernel


def reset_kernel() -> None:
    """Reset the singleton (for testing)."""
    global _kernel
    _kernel = None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaKernel",
    "get_kernel",
    "reset_kernel",
]
