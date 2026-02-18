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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xd4a989ae"  # GenesisByte: parampara % 37 == 0

from typing import Optional

# =============================================================================
# Concrete Implementations (Hidden Details)
# HIER UND NUR HIER sind diese Imports legal!
# =============================================================================
# Concrete Implementations are Lazy Loaded to prevent circular imports
from vibe_core.ledger import InMemoryLedger, SQLiteLedger

# =============================================================================
# Protocols (Public Interface) - These are the ONLY exports that matter
# =============================================================================
from vibe_core.protocols.kernel_protocol import KernelProtocol
from vibe_core.protocols.ledger import VibeLedger


class VibeFactory:
    """
    The Singleton Factory for Vibe System Components.

    All entry points (CLI, boot, services) MUST use this factory.
    Direct import of RealVibeKernel is a Protocol violation.

    NOTE: Kernel singleton is managed via ServiceRegistry.
    """

    @classmethod
    def get_kernel(
        cls,
        ledger_path: Optional[str] = None,
        load_plugins: bool = True,
        test_mode: bool = False,
    ) -> KernelProtocol:
        """
        Singleton Access to the Kernel via ServiceRegistry.

        Ensures we don't spawn multiple kernels in one process.
        The kernel is born HERE, with its full anatomy (__init__ is complete).

        Args:
            ledger_path: Path to SQLite ledger (None = use config default)
            load_plugins: Whether to load plugins (default True)
            test_mode: Disable git persistence (default False)

        Returns:
            KernelProtocol - the living, breathing kernel
        """
        from vibe_core.di import ServiceRegistry

        # Check ServiceRegistry first
        existing = ServiceRegistry.get(KernelProtocol)
        if existing is not None:
            return existing

        # Hier findet die "Geburt" statt
        # Lazy Import to break Ouroboros
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(
            ledger_path=ledger_path,
            load_plugins=load_plugins,
            test_mode=test_mode,
        )

        # =================================================================
        # LOTUS PROJECTION - Auto-Wire at Boot Time
        # =================================================================
        # "FOLDER = EXISTENCE = WIRED = GRAVITY"
        # Every mahajana in the folder structure gets discovered,
        # instantiated, and wired to the kernel automatically.
        try:
            from vibe_core.mahamantra.lotus_projection import project_lotus

            kernel._positions = project_lotus(kernel)

            # Upgrade module-stubs to real service instances (not proxies).
            # Uses _raw_* (direct) with fallback to proxy attributes.
            # This makes them visible to Balarama auto_wrap_services().
            _KERNEL_SERVICES = {
                1: ("_raw_brahma", "brahma", "brahma"),
                11: ("_raw_bhishma", "bhishma", "bhishma"),
                10: ("_raw_janaka", "janaka", "janaka"),
                13: ("_raw_bali", "bali", "bali"),
                6: ("_raw_kapila", "kapila", "kapila"),
            }
            for pos, (raw_attr, fallback_attr, guardian) in _KERNEL_SERVICES.items():
                svc = getattr(kernel, raw_attr, None) or getattr(kernel, fallback_attr, None)
                if svc is not None:
                    kernel._positions.register(pos, guardian, svc)

        except Exception as e:
            # Graceful degradation - kernel still works without projection
            import logging

            logging.getLogger("FACTORY").debug(f"Lotus projection skipped: {e}")

        # Register via ServiceRegistry (NAGA-observed!)
        ServiceRegistry.register(KernelProtocol, kernel)

        return ServiceRegistry.get(KernelProtocol)  # type: ignore

    @classmethod
    def reset_kernel(cls) -> None:
        """
        Reset the singleton (for testing only).

        WARNING: This kills the current kernel instance.
        Use only in test teardown.
        """
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.unregister(KernelProtocol)

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
