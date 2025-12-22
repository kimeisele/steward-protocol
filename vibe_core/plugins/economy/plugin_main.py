"""
Economy Plugin - CivicBank and CivicVault as a Service

OPUS-209 Phase 3: Extracted from kernel_impl.py

This plugin encapsulates the economic substrate (CivicBank and CivicVault),
removing the last direct cartridge imports from the kernel.

Philosophy:
    "Credits are not numbers in a database. Credits are CPU cycles and memory bytes.
    The economy is the operating system."
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols.economy import BankProtocol, VaultProtocol

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("ECONOMY")


def _get_config():
    """Get PhoenixConfig with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config()
    except Exception:
        return None


class EconomyPlugin(KernelPlugin):
    """
    Economic Substrate Plugin.

    Manages:
    - CivicBank: Credit/debit transactions, balance management
    - CivicVault: Secure secret storage

    The kernel no longer imports from cartridges directly.
    Instead, it accesses the bank/vault via:
        bank = ServiceRegistry.get(BankProtocol)
        vault = ServiceRegistry.get(VaultProtocol)

    Or via backward-compatible:
        kernel.get_bank()
        kernel.get_vault()
    """

    plugin_id = "economy"

    def __init__(self):
        self._bank = None
        self._vault = None
        self._db_path: Optional[Path] = None

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Boot the economy services.

        Lazy-load pattern: We don't create the bank/vault immediately,
        but set up the paths and register factories in ServiceRegistry.
        """
        try:
            # Resolve database path
            phoenix_config = _get_config()
            if phoenix_config and hasattr(phoenix_config, "paths"):
                self._db_path = Path(phoenix_config.paths.data.resolve("economy_db"))
            else:
                self._db_path = Path("/tmp") / "vibe_os" / "kernel" / "economy.db"

            self._db_path.parent.mkdir(parents=True, exist_ok=True)

            # Register factories for lazy loading
            ServiceRegistry.register_factory(BankProtocol, self._create_bank)
            ServiceRegistry.register_factory(VaultProtocol, self._create_vault)

            logger.info("🏦 Economy Plugin booted - Bank/Vault factories registered")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"Economy Plugin failed to boot: {e}")
            return HookResult.error(str(e))

    def _create_bank(self):
        """Factory for creating CivicBank instance."""
        if self._bank is None:
            try:
                from vibe_core.cartridges.system.civic.tools.economy import CivicBank

                self._bank = CivicBank(db_path=str(self._db_path))
                logger.info("🏦 CivicBank created (lazy load)")
            except ImportError as e:
                logger.warning(f"CivicBank not available: {e}")
                return None
        return self._bank

    def _create_vault(self):
        """Factory for creating CivicVault instance."""
        if self._vault is None:
            try:
                from vibe_core.cartridges.system.civic.tools.vault import CivicVault

                bank = self._create_bank()
                if bank:
                    self._vault = CivicVault(bank.conn)
                    logger.info("🔐 CivicVault created (lazy load)")
            except ImportError as e:
                logger.warning(f"CivicVault not available: {e}")
                return None
        return self._vault

    def get_bank(self):
        """Get the bank instance (creates if needed)."""
        return self._create_bank()

    def get_vault(self):
        """Get the vault instance (creates if needed)."""
        return self._create_vault()

    def get_api(self) -> Dict[str, Any]:
        """Return economy services for direct access."""
        return {
            "bank": self.get_bank(),
            "vault": self.get_vault(),
        }
