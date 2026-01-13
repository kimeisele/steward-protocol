"""
THE KURUKSHETRA SHELL
=====================

"The Field of Righteousness where the war is fought."

This module implements the `EntropyShell`, a wrapper (Decorator) that
encapsulates the Immutable Kernel (Purusha) within the Field of Time (Prakriti/Kala).

THE LAW:
1. The Inner Kernel is NEVER modified (0 lines changed in kernel_impl.py).
2. The Shell intercepts interactions to apply the Law of Decay (entropy.py).
3. If Integrity Reaches Zero, the Shell enforces PRALAYA (System Death).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x9b250582"  # GenesisByte: parampara % 37 == 0

import time
import logging
from typing import Any, Optional, TYPE_CHECKING, Dict, List

from vibe_core.protocols.kernel_protocol import KernelProtocol, KernelStatusReport
from vibe_core.protocols.science.entropy import KaliYugaEngine, EntropyState
from vibe_core.protocols.kernel_types import SystemStatusReport
from vibe_core.protocols.substrate.byte import MantraBit

if TYPE_CHECKING:
    from vibe_core.protocols.agent import VibeAgent, AgentManifest
    from vibe_core.scheduling import Task
    from vibe_core.protocols.kernel_types import CapabilityResult, TaskResult

logger = logging.getLogger("ENTROPY_SHELL")

class EntropyShell:
    """
    The Kurukshetra Shell.
    Wraps the Immutable Kernel in the Field of Time (Kala).
    
    KERNEL IS UNTOUCHED. 
    The Shell handles the decay. The Kernel handles the Logic.
    
    Implements: KernelProtocol (via Delegation)
    """
    def __init__(self, real_kernel: KernelProtocol):
        self._inner = real_kernel  # The Immutable Core (Unchanged)
        # Kali Yuga Factor: 1.0 = Default Decay
        self.entropy = KaliYugaEngine(intensity=1.0)
        # Start fresh (Satya Yuga mode for the individual)
        self.state = EntropyState(decay_rate=0.1, integrity=1.0, last_refresh=time.time())
        
        logger.info("🛡️  KURUKSHETRA SHELL ACTIVE: Kernel wrapped in Time (Kala)")

    def _apply_entropy(self) -> None:
        """
        The Inevitable Decay.
        Calculates and updates integrity state.
        Raises SystemError if Pralaya (Death) is reached.
        """
        # 1. KALA (Time) Attacks the Shell
        current_integrity = self.state.integrity
        self.state.integrity = self.entropy.apply_decay(self.state)
        
        if self.state.integrity <= 0.0:
            logger.critical("💀 PRALAYA: System Integrity Reached Zero. The Kernel is Silent.")
            raise SystemError("PRALAYA: System Integrity Reached Zero. (Need Mantra!)")
            
        if current_integrity > 0.5 and self.state.integrity <= 0.5:
             logger.warning("⚠️  KALI YUGA WARNING: System Integrity < 50%")

    # --- INTERCEPTED METHODS (The "Tick") ---

    def get_status(self) -> KernelStatusReport:
        """
        Intercept status check to apply entropy and overlay integrity.
        """
        self._apply_entropy()
        
        # Delegate to inner
        status = self._inner.get_status()
        
        # Overlay Entropy State (The illusion of the material world overlaying the spiritual)
        if isinstance(status, dict):
            status['entropy_integrity'] = self.state.integrity
            status['kali_yuga_factor'] = self.entropy.intensity
            
        return status

    async def process_operator_input(
        self,
        input_text: str,
        session_id: Optional[str] = None,
        signed_input: Any = None,
    ) -> Any:
        """
        Intercept thinking to apply entropy.
        """
        self._apply_entropy()
        return await self._inner.process_operator_input(input_text, session_id, signed_input)

    # --- PASSTHROUGH DELEGATION ---
    # We forward everything else to the inner kernel
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate all other attribute access to the inner kernel.
        This makes the Shell transparently behave like the Kernel.
        """
        return getattr(self._inner, name)

    # Explicit properties to ensure Protocol compliance if __getattr__ isn't enough for static analysis tools
    # (Though runtime it works fine)
    
    @property
    def event_bus(self) -> Any:
        return self._inner.event_bus

    @property
    def agent_registry(self) -> Any:
        return self._inner.agent_registry
        
    @property
    def status(self) -> Any:
        return self._inner.status
        
    @property
    def config(self) -> Any:
        return self._inner.config
        
    @property
    def ledger(self) -> Any:
        return self._inner.ledger

    # --- UP-LINK: THE MANTRA INJECTOR ---
    
    def receive_mantra(self, gate: MantraBit) -> None:
        """
        The Up-Link (Grace).
        Called when the Orchestrator sequences the DNA correctly.
        
        Resonance Points:
        1. HARE_4 (Bit 7, 0x0080): PULSE_SYNC (The Midpoint)
        2. HARE_8 (Bit 15, 0x8000): PURNAM (The Conclusion)
        
        Only resonance points restore energy.
        """
        now = time.time()
        
        # RESONANCE CHECK
        if gate == MantraBit.HARE_4:
             # MIDPOINT RESET
             self.state.last_refresh = now
             self.state.integrity = 1.0 
             # logger.debug("🕉️  MANTRA PULSE: Energy Restored (HARE 4)")
             
        elif gate == MantraBit.HARE_8:
             # FORMAT COMPLETION RESET
             self.state.last_refresh = now
             self.state.integrity = 1.0
             # logger.debug("🕉️  MANTRA PURNAM: Cycle Sealed (HARE 8)")
             
        # All other bits are just structural DNA steps, they do not inject energy directly
        # but they are required to reach the resonance points.
