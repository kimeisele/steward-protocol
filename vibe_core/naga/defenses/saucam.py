"""
SAUCAM (Cleanliness) - Implementation of INetworkGuard.
Layer: -1 (Naga Loka / Substrate Enforcement)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x59a36f55"  # GenesisByte: parampara % 37 == 0

from typing import Optional

from vibe_core.protocols.defense import INetworkGuard


class NetworkGuard(INetworkGuard):
    def enforce_chastity(self, destination: str, method: str = "GET") -> bool:
        if "localhost" in destination or "127.0.0.1" in destination:
            return True
        return False
