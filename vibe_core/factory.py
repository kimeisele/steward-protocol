"""
VIBE FACTORY - The Origin of Instances (YONI)
=============================================

Enforces Dependency Inversion Principle (DIP).
Only this file is allowed to import concrete implementations.

"Der Kernel darf nicht direkt angefasst werden." - Senior Architect

Usage:
    from vibe_core.factory import VibeFactory
    kernel = VibeFactory.get_kernel()
    ledger = VibeFactory.create_ledger()
"""

from typing import Optional

# =============================================================================
# Protocols (Public Interface) - These are the ONLY exports that matter
# =============================================================================
from vibe_core.protocols.kernel_protocol import KernelProtocol
from vibe_core.protocols.ledger import VibeLedger

# =============================================================================
# Concrete Implementations (Hidden Details)
# HIER UND NUR HIER sind diese Imports legal!
# =============================================================================
# Concrete Implementations are Lazy Loaded to prevent circular imports
from vibe_core.ledger import SQLiteLedger, InMemoryLedger


class VibeFactory:
    """
    The Singleton Factory for Vibe System Components.
    
    All entry points (CLI, boot, services) MUST use this factory.
    Direct import of RealVibeKernel is a Protocol violation.
    """
    
    _kernel_instance: Optional[KernelProtocol] = None
    
    @classmethod
    def get_kernel(
        cls,
        ledger_path: Optional[str] = None,
        load_plugins: bool = True,
        test_mode: bool = False,
    ) -> KernelProtocol:
        """
        Singleton Access to the Kernel.
        
        Ensures we don't spawn multiple kernels in one process.
        The kernel is born HERE, with its full anatomy (__init__ is complete).
        
        Args:
            ledger_path: Path to SQLite ledger (None = use config default)
            load_plugins: Whether to load plugins (default True)
            test_mode: Disable git persistence (default False)
            
        Returns:
            KernelProtocol - the living, breathing kernel
        """
        if cls._kernel_instance is None:
            # Hier findet die "Geburt" statt
            # Lazy Import to break Ouroboros
            from vibe_core.kernel_impl import RealVibeKernel
            
            cls._kernel_instance = RealVibeKernel(
                ledger_path=ledger_path,
                load_plugins=load_plugins,
                test_mode=test_mode,
            )
        return cls._kernel_instance
    
    @classmethod
    def reset_kernel(cls) -> None:
        """
        Reset the singleton (for testing only).
        
        WARNING: This kills the current kernel instance.
        Use only in test teardown.
        """
        cls._kernel_instance = None
    
    @staticmethod
    def create_ledger(path: str = ":memory:") -> VibeLedger:
        """
        Create a new Ledger instance.
        
        Args:
            path: ":memory:" for in-memory, or file path for SQLite
            
        Returns:
            VibeLedger implementation
        """
        if path == ":memory:":
            return InMemoryLedger()
        return SQLiteLedger(path)
    
    @classmethod
    def get_test_kernel(cls) -> KernelProtocol:
        """
        Shorthand for test mode kernel.
        
        Equivalent to get_kernel(ledger_path=":memory:", load_plugins=False, test_mode=True)
        """
        return cls.get_kernel(
            ledger_path=":memory:",
            load_plugins=False,
            test_mode=True,
        )


# =============================================================================
# Convenience re-exports (Protocol-only)
# =============================================================================
__all__ = [
    "VibeFactory",
    "KernelProtocol",
    "VibeLedger",
]
