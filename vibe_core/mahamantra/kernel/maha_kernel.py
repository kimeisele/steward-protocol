"""
MAHA KERNEL - The Clean Kernel Using Existing Infrastructure
============================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

This kernel USES the existing Mahamantra infrastructure from singularity.py.
NO reinvention. NO duplication. JUST wiring.

WHAT IT USES:
    - Mahamantra.mod → ModuleRouter (services via BalaramaProxy)
    - Mahamantra.cells → CellRouter (O(1) cell lookup)
    - Mahamantra.shadow → ShadowReactor (parallel processing)
    - Mahamantra.tick() → Heartbeat
    - Mahamantra.governance → Protocol ownership

WHAT IT ADDS:
    - Ledger integration (the only thing missing in singularity.py)
    - Service wiring with ledger injection

USAGE:
    from vibe_core.mahamantra.kernel.maha_kernel import MahaKernel

    kernel = MahaKernel()
    kernel.brahma  # → via mahamantra.mod.brahma (BalaramaProxy wrapped)
    kernel.tick()  # → via mahamantra.tick()
"""

from __future__ import annotations

__mahajana__ = "vishnu"
__position__ = 0
__genesis__ = "0x00000000"

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vibe_core.mahamantra.kernel.singularity import Mahamantra, TickState

logger = logging.getLogger("MAHA_KERNEL")


class MahaKernel:
    """
    The Clean Kernel.

    USES Mahamantra from singularity.py for EVERYTHING.
    ADDS only ledger integration.
    """

    __slots__ = ("_mahamantra", "_ledger")

    def __init__(self, ledger_path: str = ":memory:") -> None:
        """
        Initialize kernel.

        Args:
            ledger_path: Path to SQLite ledger, or ":memory:" for in-memory
        """
        # 1. THE MAHAMANTRA (from singularity.py - the REAL one)
        from vibe_core.mahamantra.kernel.singularity import Mahamantra

        self._mahamantra = Mahamantra()

        # 2. LEDGER (the only thing we add)
        from vibe_core.mahamantra import InMemoryLedger, SQLiteLedger

        if ledger_path == ":memory:":
            self._ledger = InMemoryLedger()
        else:
            self._ledger = SQLiteLedger(ledger_path)

        # 3. INJECT LEDGER to services that need it
        self._inject_ledger()

        logger.info("🕉️ MahaKernel initialized (using singularity.py infrastructure)")

    def _inject_ledger(self) -> None:
        """Inject ledger to services via mahamantra.mod."""
        # Services that need ledger: brahma, bhishma, yamaraja
        for guardian in ["brahma", "bhishma", "yamaraja"]:
            try:
                service = getattr(self._mahamantra.mod, guardian)
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
    def mahamantra(self) -> "Mahamantra":
        """The underlying Mahamantra singleton."""
        return self._mahamantra

    # --- Position Access ---

    def __getitem__(self, index: int):
        """kernel[5] → mahamantra[5]"""
        return self._mahamantra[index]

    def __len__(self) -> int:
        return len(self._mahamantra)

    def __iter__(self):
        return iter(self._mahamantra)

    # --- Guardian Access (via mod with BalaramaProxy) ---

    def __getattr__(self, name: str) -> Any:
        """
        kernel.brahma → mahamantra.mod.brahma (BalaramaProxy wrapped)

        This routes ALL guardian access through ModuleRouter.
        """
        if name.startswith("_"):
            raise AttributeError(name)

        # Try mahamantra.mod first (services)
        try:
            return getattr(self._mahamantra.mod, name)
        except AttributeError:
            pass

        # Try mahamantra directly (positions, etc.)
        try:
            return getattr(self._mahamantra, name)
        except AttributeError:
            pass

        raise AttributeError(f"MahaKernel has no attribute '{name}'")

    # --- Core Operations ---

    def tick(self) -> "TickState":
        """Advance one position in the 16-word mantra."""
        return self._mahamantra.tick()

    def chant(self, separator: str = " ") -> str:
        """Chant the complete Mahamantra (16 words)."""
        return self._mahamantra.chant(separator)

    def verify(self, value: int) -> bool:
        """Verify connection to Parampara."""
        return self._mahamantra.verify(value)

    # --- Infrastructure Access ---

    @property
    def mod(self):
        """ModuleRouter (services via BalaramaProxy)."""
        return self._mahamantra.mod

    @property
    def cells(self):
        """CellRouter (O(1) cell lookup)."""
        return self._mahamantra.cells

    @property
    def shadow(self):
        """ShadowReactorFactory."""
        return self._mahamantra.shadow

    @property
    def governance(self):
        """Protocol governance bridge."""
        return self._mahamantra.governance

    @property
    def kala(self):
        """TimeKeeper."""
        return self._mahamantra.kala

    @property
    def registry(self):
        """ProtocolRegistry."""
        return self._mahamantra.registry

    # --- Convenience ---

    def compression(self):
        """Create MahaCompression engine."""
        return self._mahamantra.compression()

    def network(self):
        """Create LotusIPRouter."""
        return self._mahamantra.network()

    def cell_from_content(self, content: str, *, register: bool = True):
        """Create MahaCell from content."""
        return self._mahamantra.cell_from_content(content, register=register)

    def __repr__(self) -> str:
        return f"MahaKernel(tick={self._mahamantra._tick_counter})"


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
