"""
MAHAMANTRA SOVEREIGN ASGI - The Sovereign Entry Point
=====================================================

"This connection IS the Mantra."

Wraps the application in the Rama-Varnamala 49-Matrix.
Treats every HTTP request path as a vibration (Shabda).
Classifies the energy as either PURNA (Complete/136) or LILA (Dynamic Cycle).
DOES NOT BLOCK. ONLY SANCTIFIES.
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x856ff23e"

import logging
import time
from typing import Any, Callable, Dict

from vibe_core.mahamantra import mahamantra
from gateway.api import app as fastapi_app

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MAHAMANTRA_ENTRY")


class MahamantraSovereignASGI:
    """
    Sovereign ASGI Middleware.

    1. VIBRATE: path -> mahamantra.vibrate()
    2. CLASSIFY: Purna (136) vs Lila (Cycle)
    3. SANCTIFY: Inject X-Mahamantra headers
    4. DELEGATE: Pass to FastAPI
    """

    def __init__(self, app: Callable):
        self.app = app
        # Bootstrap the Singularity (Lazy load core)
        logger.info("🕉️  BOOTSTRAPPING MAHAMANTRA...")
        mahamantra.bootstrap(silent=True)
        logger.info("✅ MAHAMANTRA ONLINE")

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. THE VIBRATION
        path = scope.get("path", "/")
        start_time = time.time()

        # Use the ONE OBJECT to compute everything (Algorithms, Gita, Rama Grid)
        # This uses the "49 Matrix" internally via PipelineCache -> Rama Grid
        vib_result = mahamantra.vibrate(path)

        # 2. THE DIAGNOSIS (Purna vs Lila)
        vibration = vib_result.get("vibration", {})
        attractor = vibration.get("attractor", 0)
        seed = vibration.get("seed", 0)

        # 136 = POSITION_SUM_TOTAL (The Field/Vaikuntha)
        if attractor == 136:
            state_type = "PURNA"  # Complete/Fixed
        else:
            state_type = "LILA"  # Dynamic/Cyclic

        # 3. THE LOG (The Evidence)
        duration = (time.time() - start_time) * 1000
        verse_info = vib_result.get("verse", {}) or {}
        verse_ref = f"BG.{verse_info.get('chapter')}.{verse_info.get('verse')}"

        logger.info(f"🕉️  {state_type} [{attractor:3d}] | {path} | SEED: {seed} | {verse_ref} | {duration:.2f}ms")

        # 4. THE SANCTIFICATION (Inject Headers)
        async def sanctify_send(message: Dict[str, Any]):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # The Sacred Headers
                headers.append((b"x-mahamantra-attractor", str(attractor).encode()))
                headers.append((b"x-mahamantra-state", state_type.encode()))
                headers.append((b"x-mahamantra-verse", str(verse_ref).encode()))
                headers.append((b"x-mahamantra-seed", str(seed).encode()))

                message["headers"] = headers
            await send(message)

        # 5. THE DELEGATION (Pass-through)
        await self.app(scope, receive, sanctify_send)


# Expose as 'app' for uvicorn
app = MahamantraSovereignASGI(fastapi_app)
