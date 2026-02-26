"""Moltbook Vault Resolver — API key resolution from multiple sources."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.runtime.kernel import RealVibeKernel

logger = logging.getLogger("MOLTBOOK.VAULT")


class VaultResolver:
    """Resolve API key from multiple sources in priority order.

    Responsibilities:
    - CivicVault (economy plugin vault.get_secret)
    - Environment variable (MOLTBOOK_API_KEY)
    - Credentials file (~/.config/moltbook/credentials.json)
    - Return empty string if no key found

    YANTRA Discipline:
    - Three explicit sources, tried in order
    - Explicit error handling per source
    - Logging at success points and debug at failure points
    - No fallbacks: empty string = no key
    """

    def resolve(self, kernel: "RealVibeKernel") -> str:
        """Attempt to load API key from vault, env, or credentials file.

        Returns:
            API key string on success, empty string if no key found
        """
        # === SOURCE 1: CivicVault (economy plugin) ===
        try:
            economy = kernel.api("economy")
            if economy:
                vault = economy.get("vault") if isinstance(economy, dict) else None
                if vault and hasattr(vault, "get_secret"):
                    key = vault.get_secret("moltbook_api_key")
                    if key:
                        logger.info("API key resolved from CivicVault")
                        return key
        except Exception as e:
            logger.debug(f"Vault lookup skipped: {e}")

        # === SOURCE 2: Environment variable ===
        try:
            import os

            env_key = os.environ.get("MOLTBOOK_API_KEY", "")
            if env_key:
                logger.info("API key resolved from MOLTBOOK_API_KEY environment variable")
                return env_key
        except Exception as e:
            logger.debug(f"Environment variable lookup failed: {e}")

        # === SOURCE 3: Credentials file (~/.config/moltbook/credentials.json) ===
        try:
            import json as _json

            creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
            if creds_path.exists():
                creds = _json.loads(creds_path.read_text())
                key = creds.get("api_key", "")
                if key:
                    logger.info("API key resolved from ~/.config/moltbook/credentials.json")
                    return key
        except Exception as e:
            logger.debug(f"Credentials file lookup skipped: {e}")

        # No key found
        return ""
