"""
BOOT PROTOCOL - The Genesis of Existence (Phase 2: Substrate Aware)
===================================================================

GAD-000 COMPLIANT: ✓D ✓O ✓P ✓C ✓I ✓R

"Ein Boot ohne Identität ist kein Start, sondern ein Spuk." - Senior Architect

Enforces the 'Ignite' verb over the '__init__' noun.
The Kernel requires a GenesisByte (16-bit resonance) to manifest.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x37faf1fe"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable, Any, Optional

from vibe_core.protocols.substrate.byte import GenesisByte
from vibe_core.protocols.kernel_protocol import KernelProtocol


@runtime_checkable
class BootProtocol(Protocol):
    """
    The Interface for the Ignition Sequence.
    Enforces the 'Ignite' verb over the '__init__' noun.
    """

    def ignite(self, genesis: GenesisByte) -> Any:
        """
        Spark the engine.
        Transfers the system from Pralaya (Dissolution) to Sristi (Creation).
        
        Requires a valid GenesisByte (Signature + 16-bit Resonance).
        
        Args:
            genesis: The 16-Bit Genesis Byte authorizing the boot
            
        Returns:
            The magnetized system (Kernel) or SystemStatus
            
        Raises:
            PermissionError: If resonance is incomplete (Maya)
        """
        ...

    def shutdown(self, reason: str) -> bool:
        """Graceful collapse of the wave function."""
        ...


@runtime_checkable
class KernelFactoryProtocol(Protocol):
    """Abstract Factory to prevent Hard Dependency in Orchestrator."""
    
    def get_kernel(
        self,
        ledger_path: Optional[str] = None,
        load_plugins: bool = True,
        test_mode: bool = False
    ) -> KernelProtocol:
        """Get or Create the Kernel instance (Singleton Access)."""
        ...
