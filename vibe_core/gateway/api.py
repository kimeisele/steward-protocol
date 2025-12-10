import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from aiohttp import web

from vibe_core.state.prakriti import Prakriti

logger = logging.getLogger("NETWORK_GATEWAY")


class NetworkGateway:
    """
    Phase 18: The Network (Sangha)
    Provides HTTP REST API for VibeOS.
    """

    def __init__(self, prakriti: Prakriti, host: str = "127.0.0.1", port: int = 8000):
        self.prakriti = prakriti
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

        # Routes
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/api/v1/health", self.handle_health)
        self.app.router.add_get("/api/v1/state", self.handle_state)

        # Static files (if directory exists)
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.router.add_static("/static", static_dir)

    async def start(self):
        """Start the API server non-blocking."""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            logger.info(f"🌐 Gateway listening at http://{self.host}:{self.port}")
        except OSError as e:
            if e.errno == 48:  # Address already in use
                logger.warning(f"⚠️ Port {self.port} in use. Gateway disabled (Graceful Degradation).")
            else:
                logger.error(f"❌ Gateway failed to start: {e}")
                raise e
        except Exception as e:
            logger.error(f"❌ Gateway failed to start: {e}")

    async def stop(self):
        """Stop the API server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Gateway stopped.")

    async def handle_index(self, request):
        """Serve index.html"""
        static_dir = Path(__file__).parent / "static"
        index_file = static_dir / "index.html"
        if index_file.exists():
            return web.FileResponse(index_file)
        return web.Response(text="VibeOS Gateway (Static content missing)", content_type="text/plain")

    async def handle_health(self, request):
        """Health check endpoint."""
        return web.json_response({"status": "alive", "phase": "18 (Sangha)", "system": "VibeOS"})

    async def handle_state(self, request):
        """Return system state from Prakriti."""
        try:
            # Offload blocking sync call (Git/IO) to thread pool
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, self.prakriti.get_system_status)

            # Convert non-serializable objects (like sets) to lists
            return web.json_response(status, dumps=lambda x: json.dumps(x, default=str))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
