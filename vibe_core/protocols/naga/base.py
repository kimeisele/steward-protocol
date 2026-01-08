"""
NAGA BASE - The Standard Devotee Interface (Layer 0)

Every Naga (Service) is a Devotee.
It inherits from this base to ensure:
1. It is automatically protected by Balarama.
2. It chants continuously (Heartbeat).
3. It respects the Gene Lifecycle.

"Ekale ishvara krishna, ara saba bhritya"
- Only Krishna is the Controller; everyone else is a servant.
"""

import threading
import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from vibe_core.protocols.substrate import (
    GeneManifest,
    IGene,
    MantraOpCode,
)

from .balarama import BalaramaProxy


class NagaBase(IGene, ABC):
    """
    Standard Base for all Nagas.

    Features:
    - Auto-Proxy (Balarama) on bind.
    - Background Chanting (Heartbeat).
    - Gene Lifecycle management.
    """

    def __init__(self, name: str, capabilities: Tuple[str, ...]):
        self._name = name
        self._capabilities = capabilities
        self._host: Optional[Any] = None
        self._proxy: Optional[BalaramaProxy] = None
        self._chanting_thread: Optional[threading.Thread] = None
        self._stop_chanting = threading.Event()

    # =========================================================================
    # GENE IMPLEMENTATION
    # =========================================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def manifest(self) -> GeneManifest:
        return GeneManifest(name=self._name, capabilities=self._capabilities, requires=())

    def bind(self, host: Any) -> Any:
        """
        Bind to the host.

        THIS IS WHERE BALARAMA INTERVENES.
        We do NOT return 'self'. We return a BalaramaProxy wrapping 'self'.
        """
        # LAZY IMPORT to avoid circular dependency (Naga -> Base -> Yamaraja -> Naga)
        from vibe_core.protocols.universal.yamaraja import YamarajaProtocol

        self._host = host

        # Create the Shield
        self._proxy = BalaramaProxy(
            target=self,
            name=self._name,
            # Ideally we get Yamaraja from host, but for now we instantiate or reuse
            # In a real system, host should provide the singletons.
            yamaraja=YamarajaProtocol(),
            mantra_handler=self._emit_mantra,
        )

        # Start Chanting (Heartbeat)
        self._start_chanting()

        # Return the Proxy, not the raw object
        return self._proxy

    def activate(self) -> None:
        """Lifecycle hook: The Naga awakes."""
        pass

    def deactivate(self) -> None:
        """Lifecycle hook: The Naga sleeps."""
        self._stop_chanting.set()
        if self._chanting_thread:
            self._chanting_thread.join(timeout=1.0)

    # =========================================================================
    # CHANTING (HEARTBEAT)
    # =========================================================================

    def _start_chanting(self):
        """Start the background mantra loop."""
        self._stop_chanting.clear()
        self._chanting_thread = threading.Thread(target=self._chant_loop, name=f"naga_chant_{self._name}", daemon=True)
        self._chanting_thread.start()

    def _chant_loop(self):
        """
        The Heartbeat of Service.
        Emits PULSE_SYNC every few seconds.
        """
        while not self._stop_chanting.is_set():
            self._emit_mantra(MantraOpCode.PULSE_SYNC)
            time.sleep(5)  # 5 seconds breath execution

    def _emit_mantra(self, opcode: str):
        """Emit a mantra signal (Log/Heartbeat)."""
        # In a real system, this goes to the Kernel's event bus.
        # For now, we print or log to stdout as a proof of life.
        pass

    # =========================================================================
    # SERVICE INTERFACE
    # =========================================================================

    @abstractmethod
    def serve(self, request: Any) -> Any:
        """
        The Core Service Method.
        Must be implemented by concrete Nagas.
        """
        pass
