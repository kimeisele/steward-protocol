import asyncio
import errno
import json
import logging
from pathlib import Path
from typing import Optional

from aiohttp import web

from vibe_core.protocols.network import NetworkGatewayProtocol
from vibe_core.state.prakriti import Prakriti

logger = logging.getLogger("NETWORK_GATEWAY")


class NetworkGateway(NetworkGatewayProtocol):
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
        self.app.router.add_get("/api/v1/union", self.handle_union_report)

        # Static files (if directory exists)
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.router.add_static("/static", static_dir)

        # Phase 19: Federation routes
        self._setup_federation_routes()

    async def start(self):
        """Start the API server non-blocking."""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            logger.info(f"🌐 Gateway listening at http://{self.host}:{self.port}")
        except OSError as e:
            if e.errno == errno.EADDRINUSE:  # Address already in use (works on Linux + macOS)
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
        """Return system state from Prakriti + Union Report."""
        try:
            # 1. Body: Base State from Prakriti
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, self.prakriti.get_system_status)

            # 2. Conscience: Union Report from Universal Protocol
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.universal import UnionProtocol

            union = ServiceRegistry.get(UnionProtocol)
            if union:
                status["union"] = union.get_union_summary()
            else:
                status["union"] = {"status": "NOT_AVAILABLE", "message": "UnionProtocol not found"}

            # Convert non-serializable objects (like sets) to lists
            return web.json_response(status, dumps=lambda x: json.dumps(x, default=str))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    # =========================================================================
    # Phase 19: Federation (Seed List API)
    # =========================================================================

    def _setup_federation_routes(self):
        """Register federation API routes."""
        self.app.router.add_get("/api/v1/federation/peers", self.handle_list_peers)
        self.app.router.add_post("/api/v1/federation/peers", self.handle_add_peer)
        self.app.router.add_delete("/api/v1/federation/peers/{peer_id}", self.handle_remove_peer)
        self.app.router.add_post("/api/v1/federation/forward/{peer_id}", self.handle_forward)

    async def handle_list_peers(self, request):
        """GET /api/v1/federation/peers - List all registered peers."""
        try:
            peers = self.prakriti.machine.list_peers()
            return web.json_response({"peers": peers})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_add_peer(self, request):
        """POST /api/v1/federation/peers - Add a peer to seed list."""
        try:
            data = await request.json()
            peer_id = data.get("peer_id")
            url = data.get("url")
            trust_level = data.get("trust_level", 1)

            if not peer_id or not url:
                return web.json_response({"error": "Missing peer_id or url"}, status=400)

            success = self.prakriti.machine.add_peer(peer_id, url, trust_level)
            if success:
                return web.json_response({"status": "registered", "peer_id": peer_id, "url": url})
            else:
                return web.json_response({"error": "Failed to add peer"}, status=500)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_remove_peer(self, request):
        """DELETE /api/v1/federation/peers/{peer_id} - Remove a peer."""
        try:
            peer_id = request.match_info.get("peer_id")
            success = self.prakriti.machine.remove_peer(peer_id)
            if success:
                return web.json_response({"status": "removed", "peer_id": peer_id})
            else:
                return web.json_response({"error": "Failed to remove peer"}, status=500)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_union_report(self, request):
        """GET /api/v1/union - Detailed State of the Union report."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.universal import UnionProtocol

            union = ServiceRegistry.get(UnionProtocol)
            if not union:
                return web.json_response({"error": "UnionProtocol not available"}, status=503)

            entities = union.get_living_entities()
            # Convert dataclasses to dicts for JSON
            from dataclasses import asdict

            data = [asdict(e) for e in entities]

            return web.json_response({"entities": data, "count": len(data)}, dumps=lambda x: json.dumps(x, default=str))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_forward(self, request):
        """
        POST /api/v1/federation/forward/{peer_id}
        Forward a request to a remote peer.

        Body: {"path": "/api/v1/health", "method": "GET", "payload": {...}}
        """
        import aiohttp as aiohttp_client  # local import to avoid namespace collision

        peer_id = request.match_info.get("peer_id")
        peer = self.prakriti.machine.get_peer(peer_id)

        if not peer:
            return web.json_response({"error": f"Peer '{peer_id}' not found"}, status=404)

        try:
            data = await request.json()
            path = data.get("path", "/api/v1/health")
            method = data.get("method", "GET").upper()
            payload = data.get("payload")

            target_url = f"{peer['url'].rstrip('/')}{path}"
            logger.info(f"[FEDERATION] Forwarding {method} to {target_url}")

            # SECURITY: SSL verification enabled by default (removed ssl=False)
            # For local dev with self-signed certs, configure SSLContext explicitly
            async with aiohttp_client.ClientSession() as session:
                if method == "GET":
                    async with session.get(target_url) as resp:
                        result = await resp.json()
                elif method == "POST":
                    async with session.post(target_url, json=payload) as resp:
                        result = await resp.json()
                else:
                    return web.json_response({"error": f"Unsupported method: {method}"}, status=400)

            # Update last_seen
            self.prakriti.machine.update_peer_last_seen(peer_id)

            return web.json_response({"peer_id": peer_id, "response": result})

        except Exception as e:
            logger.error(f"[FEDERATION] Forward failed: {e}")
            return web.json_response({"error": str(e)}, status=502)
