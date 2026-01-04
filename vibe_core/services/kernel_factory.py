"""
KernelFactory - Factory for creating Kernel instances.

PHASE 3 OF OPERATION LASAGNE: EphemeralCities Extraction

This factory allows plugins to spawn child kernels WITHOUT importing
RealVibeKernel directly, breaking the circular dependency.

Usage:
    # In plugin (via ServiceRegistry):
    from vibe_core.protocols.kernel_protocol import KernelFactoryProtocol

    factory = ServiceRegistry.get(KernelFactoryProtocol)
    child = factory.create_kernel(config, parent=current_kernel)

    # NOT this (creates circular dependency):
    from vibe_core.kernel_impl import RealVibeKernel
    child = RealVibeKernel(config=config)

Registration:
    # In kernel __init__ or boot:
    from vibe_core.services.kernel_factory import KernelFactory
    ServiceRegistry.register(KernelFactoryProtocol, KernelFactory())
"""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vibe_core.phoenix import PhoenixConfig
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("KERNEL_FACTORY")


class KernelFactory:
    """
    Factory for creating RealVibeKernel instances.

    Registered in ServiceRegistry to allow plugins to create kernels
    without importing RealVibeKernel directly.

    This breaks the circular dependency between plugins and kernel.
    """

    def __init__(self):
        logger.info("🏭 KernelFactory initialized")

    def create_kernel(
        self,
        config: "PhoenixConfig",
        ledger_path: str = ":memory:",
        parent: Optional["KernelProtocol"] = None,
        load_plugins: bool = True,
        test_mode: bool = False,
    ) -> "KernelProtocol":
        """
        Create a new kernel instance.

        Args:
            config: PhoenixConfig for the kernel
            ledger_path: Path to ledger (":memory:" for ephemeral)
            parent: Optional parent kernel (for child kernels)
            load_plugins: Whether to auto-load plugins
            test_mode: Whether to run in test mode

        Returns:
            New KernelProtocol-compliant kernel instance
        """
        # Lazy import to avoid circular dependency at module level
        from vibe_core.kernel_impl import RealVibeKernel

        logger.info(f"🏭 Creating kernel (ephemeral: {parent is not None})")

        kernel = RealVibeKernel(
            ledger_path=ledger_path,
            config=config,
            parent=parent,
            load_plugins=load_plugins,
            test_mode=test_mode,
        )

        logger.info(f"🏭 Kernel created (id: {id(kernel)})")
        return kernel


__all__ = ["KernelFactory"]
