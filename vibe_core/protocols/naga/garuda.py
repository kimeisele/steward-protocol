"""
GARUDA PROTOCOL - The Carrier (Layer 0.5)

"Garuda" - The Divine Eagle. Carrier of Vishnu.
He creates the connection (Network), but Balarama filters the traffic.

Responsibilities:
1. FETCH/PUSH: Non-blocking I/O (Asyncio).
2. STATELESS: No local storage. Passes data immediately.
3. FILTER: Only visits "Holy" destinations (Allow-list).

INHERITANCE:
- Inherits from NagaBase (Devotee).
- Protected by Balarama (Shield).

STATUS: DEVOTEE / ACTIVE CARRIER
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x62a2019b"  # GenesisByte: parampara % 37 == 0

import asyncio
import json
import socket
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

from vibe_core.protocols.naga.base import NagaBase

# Define Garuda's specific manifest capabilities
GARUDA_CAPS = ("fetch", "push", "connect")


class Garuda(NagaBase):
    """
    The Garuda Service (Network Carrier).

    A Devotee Naga that:
    - Flies fast (Asyncio).
    - Touches no ground (Stateless).
    - Checks destinations (Balarama/Yamaraja).
    """

    def __init__(self):
        super().__init__(name="garuda", capabilities=GARUDA_CAPS)
        # The Filter (Allow-list for testing/bootstrapping)
        # In production this comes from Yamaraja audit
        self._allowed_domains = ["localhost", "127.0.0.1", "schema.org", "pypi.org"]

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """
        Generic entry point for Balarama.
        """
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")
        url = request.get("url")
        data = request.get("data")

        if not url:
            return "NO DESTINATION"

        # Note: Balarama intercepts this synchronously, but the payload inside
        # can return a coroutine or future. Since NagaBase.serve is sync,
        # we run the async loop here for now, or expect the kernel to await it.
        # For this implementation, we run_until_complete to bridge sync/async.

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            if action == "fetch":
                return loop.run_until_complete(self.fly_fetch(url))
            elif action == "push":
                return loop.run_until_complete(self.fly_push(url, data))
            elif action == "connect":
                return loop.run_until_complete(self.fly_connect(url))
        finally:
            loop.close()

        return "UNKNOWN ACTION"

    # =========================================================================
    # FLIGHT METHODS (ASYNC I/O)
    # =========================================================================

    async def fly_fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch data from a Holy URL.
        """
        # 1. Filter (Balarama Logic applied inside method for purity)
        if not self._is_holy_destination(url):
            return {"error": "IMPURE_DESTINATION", "url": url}

        # 2. Simulate Network Delay (Flight Time)
        await asyncio.sleep(0.1)

        # 3. Simulate Fetch (Stateless)
        # In real code: aiohttp.get(url)
        return {"status": 200, "url": url, "content": f"Garuda fetched essence from {url}", "size": 108}

    async def fly_push(self, url: str, data: Any) -> Dict[str, Any]:
        """
        Push data to a Holy URL.
        """
        if not self._is_holy_destination(url):
            return {"error": "IMPURE_DESTINATION", "url": url}

        await asyncio.sleep(0.1)

        return {"status": 201, "url": url, "message": "Offering delivered", "bytes_sent": len(str(data))}

    async def fly_connect(self, url: str) -> bool:
        """Probe a connection."""
        if not self._is_holy_destination(url):
            return False
        return True

    # =========================================================================
    # THE FILTER
    # =========================================================================

    def _is_holy_destination(self, url: str) -> bool:
        """
        Verify if destination is allowed.
        Garuda checks, but Balarama could also block via Yamaraja.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or parsed.path

            # Simple Allow-list check
            for allowed in self._allowed_domains:
                if allowed in str(domain):
                    return True

            return False
        except Exception:
            return False


GarudaProtocol = Garuda
