"""
SAUCAM (Cleanliness) - Implementation of INetworkGuard.
Layer: -1 (Naga Loka / Substrate Enforcement)
"""

from typing import Optional

from vibe_core.protocols.defense import INetworkGuard


class NetworkGuard(INetworkGuard):
    def enforce_chastity(self, destination: str, method: str = "GET") -> bool:
        if "localhost" in destination or "127.0.0.1" in destination:
            return True
        return False
