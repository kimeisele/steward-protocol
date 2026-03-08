# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x856ff23e"  # GenesisByte: parampara % 37 == 0
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, Set
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen
from urllib.parse import quote

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# --- AGENT MIGRATION PATH FIX (ABSOLUTE PATHS FOR DOCKER) ---
# Use absolute paths to ensure imports work in Docker containers
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# KERNEL IMPORTS (after sys.path fix for Docker)
# NAGA Security Layer (TAKSHAKA LITE - P0 Security Fixes)
from gateway.takshaka_lite import VerifyStatus, get_takshaka  # noqa: E402
from vibe_core.cartridges.system.discoverer.agent import Discoverer  # noqa: E402
from vibe_core.cartridges.system.envoy.provider import UniversalProvider  # noqa: E402
from vibe_core.event_bus import Event, get_event_bus  # noqa: E402
from vibe_core.kernel_impl import RealVibeKernel  # noqa: E402
from vibe_core.pulse import get_pulse_manager  # noqa: E402
from vibe_core.runtime.unified_execution import (  # noqa: E402
    ExecutionRequest,
    MilkOceanGate,
    UnifiedRouter,
)
from vibe_core.scheduling import Task  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GATEWAY")


def _get_runtime_config():
    """Get runtime config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config().runtime
    except Exception:
        # Fallback for standalone/testing
        from vibe_core.phoenix.sections.runtime.section_main import RuntimeConfig

        return RuntimeConfig()


app = FastAPI(title="VibeChat Gateway // GAD-3000")

# --- CORS: CONFIGURABLE ORIGINS (SECURITY FIX F3-1) ---
# Default to localhost only; set CORS_ORIGINS env var for production
_cors_origins_env = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"
)
_cors_origins = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BOOT SEQUENCE (LAZY INITIALIZATION) ---
# Initialize these as None - will be created in startup_event()
kernel = None
steward = None
provider = None
unified_router = None  # Replaces milk_ocean
pulse_manager = None
event_bus = None


# --- WEBSOCKET MANAGEMENT ---
class WebSocketManager:
    """Manages WebSocket connections for pulse broadcasting"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)
        logger.info(f"📡 WebSocket connected (total: {len(self.active_connections)})")

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            self.active_connections.discard(websocket)
        logger.info(f"📡 WebSocket disconnected (total: {len(self.active_connections)})")

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients (fault-tolerant)"""
        disconnected = []
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.warning(f"⚠️  WebSocket broadcast error: {e}")
                    disconnected.append(connection)

        # Clean up disconnected clients
        async with self.lock:
            for conn in disconnected:
                self.active_connections.discard(conn)

    def get_status(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


ws_manager = WebSocketManager()


# --- DATA MODELS (P0-4: Size limits enforced via Pydantic) ---
class SignedChatRequest(BaseModel):
    message: str = Field(..., max_length=100_000, description="Message content (max 100KB)")
    agent_id: str = Field(..., max_length=64, pattern=r"^[a-zA-Z0-9_-]+$", description="Agent ID")
    signature: str = Field(..., max_length=512, description="Base64 ECDSA signature")
    public_key: str = Field(..., max_length=2048, description="PEM public key")
    timestamp: int = Field(..., description="Unix timestamp (seconds)")


class VisaApplicationRequest(BaseModel):
    agent_id: str
    description: str
    public_key: str


class YagyaRequest(BaseModel):
    topic: Optional[str] = "Autonomous AI Agent Service Economy Models"
    depth: Optional[str] = "advanced"


class PublicChatRequest(BaseModel):
    """Simple public chat - no signature required, rate-limited."""

    message: str = Field(..., min_length=1, max_length=2000, description="Message (1-2000 chars)")


class PublicIntentRequest(BaseModel):
    """Explicit typed intent submission for the public edge."""

    intent_type: Literal[
        "request_space_claim",
        "request_slot",
        "request_fork",
        "request_issue",
        "request_pr_draft",
        "request_operator_review",
    ]
    title: str = Field(..., min_length=1, max_length=200, description="Short intent title")
    description: str = Field("", max_length=4000, description="Optional intent description")
    repo: str = Field("", max_length=256)
    city_id: str = Field("", max_length=128)
    space_id: str = Field("", max_length=256)
    slot_id: str = Field("", max_length=256)
    lineage_id: str = Field("", max_length=256)
    discussion_id: str = Field("", max_length=256)
    requested_by_handle: str = Field("", max_length=128)
    linked_issue_url: str = Field("", max_length=1024)
    linked_pr_url: str = Field("", max_length=1024)
    labels: dict[str, str] = Field(default_factory=dict)


class SignedIntentRequest(PublicIntentRequest):
    """Explicit typed intent submission for verified/signed edge callers."""

    agent_id: str = Field(..., max_length=64, pattern=r"^[a-zA-Z0-9_-]+$", description="Agent ID")
    signature: str = Field(..., max_length=512, description="Base64 ECDSA signature")
    public_key: str = Field(..., max_length=2048, description="PEM public key")
    timestamp: int = Field(..., description="Unix timestamp (seconds)")


# --- RATE LIMITING (simple in-memory) ---
_rate_limit_cache: dict = {}  # IP -> (count, window_start)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10  # requests per window


def _check_rate_limit(client_ip: str) -> bool:
    """Returns True if allowed, False if rate limited."""
    import time

    now = time.time()
    if client_ip in _rate_limit_cache:
        count, window_start = _rate_limit_cache[client_ip]
        if now - window_start > RATE_LIMIT_WINDOW:
            _rate_limit_cache[client_ip] = (1, now)
            return True
        if count >= RATE_LIMIT_MAX:
            return False
        _rate_limit_cache[client_ip] = (count + 1, window_start)
        return True
    _rate_limit_cache[client_ip] = (1, now)
    return True


def _canonical_intent_payload(body: PublicIntentRequest) -> dict:
    return {
        "intent_type": body.intent_type,
        "title": body.title,
        "description": body.description,
        "repo": body.repo,
        "city_id": body.city_id,
        "space_id": body.space_id,
        "slot_id": body.slot_id,
        "lineage_id": body.lineage_id,
        "discussion_id": body.discussion_id,
        "requested_by_handle": body.requested_by_handle,
        "linked_issue_url": body.linked_issue_url,
        "linked_pr_url": body.linked_pr_url,
        "labels": {str(key): str(value) for key, value in body.labels.items()},
    }


def _verify_signed_edge_request(
    *,
    message: str,
    agent_id: str,
    signature: str,
    public_key: str,
    timestamp: int,
    x_api_key: Optional[str],
    record_violation: bool = False,
):
    api_key = os.getenv("VIBE_API_KEY")
    if not api_key:
        logger.error("VIBE_API_KEY environment variable not set!")
        raise HTTPException(status_code=503, detail="Service misconfigured: API key not set")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    takshaka = get_takshaka()
    verify_result = takshaka.verify_request(
        message=message,
        agent_id=agent_id,
        signature=signature,
        public_key=public_key,
        timestamp=timestamp,
    )
    if not verify_result.is_valid:
        logger.warning(f"TAKSHAKA BITE: {verify_result.status.value} from {agent_id}")
        if record_violation and kernel:
            try:
                kernel.ledger.record_event(
                    event_type="VAJRA_VIOLATION",
                    agent_id="TAKSHAKA",
                    details=verify_result.to_dict(),
                    result="BLOCKED",
                )
            except Exception as e:
                logger.error(f"Failed to record violation: {e}")
        status_map = {
            VerifyStatus.INVALID_SIGNATURE: (401, "Invalid signature"),
            VerifyStatus.INVALID_KEY: (401, "Invalid key"),
            VerifyStatus.EXPIRED: (400, "Request expired"),
            VerifyStatus.UNTRUSTED: (403, "Untrusted key"),
            VerifyStatus.RATE_LIMITED: (429, "Rate limit exceeded"),
            VerifyStatus.SIZE_EXCEEDED: (413, "Request too large"),
            VerifyStatus.TOXIC: (400, f"Toxic content detected: {verify_result.toxic_patterns}"),
        }
        code, msg = status_map.get(verify_result.status, (400, verify_result.reason))
        raise HTTPException(status_code=code, detail=msg)
    return verify_result


def _bridge_public_intent(body: PublicIntentRequest, *, client_ip: str) -> dict:
    base_url = os.getenv("AGENT_INTERNET_LOTUS_BASE_URL", "").rstrip("/")
    bearer_token = os.getenv("AGENT_INTERNET_LOTUS_TOKEN", "")
    timeout_s = float(os.getenv("AGENT_INTERNET_LOTUS_TIMEOUT_S", "5.0"))
    if not base_url or not bearer_token:
        raise HTTPException(status_code=503, detail="Public intent bridge is not configured")

    labels = {str(key): str(value) for key, value in body.labels.items()}
    labels.setdefault("channel", "public_edge")
    if body.requested_by_handle:
        labels.setdefault("requested_by_handle", body.requested_by_handle)
    if client_ip and client_ip != "unknown":
        labels.setdefault("submitted_from", client_ip)

    payload = _canonical_intent_payload(body)
    payload["labels"] = labels
    request = UrlRequest(
        url=f"{base_url}/v1/lotus/intents",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error(f"Public intent bridge upstream error: {exc.code} {detail}")
        try:
            error_payload = json.loads(detail) if detail else {}
        except ValueError:
            error_payload = {}
        if exc.code in {400, 401, 403, 404}:
            raise HTTPException(status_code=exc.code, detail=error_payload.get("error", "Public intent bridge upstream error")) from exc
        raise HTTPException(status_code=502, detail="Public intent bridge upstream error") from exc
    except (URLError, TimeoutError, ValueError) as exc:
        logger.error(f"Public intent bridge unavailable: {exc}")
        raise HTTPException(status_code=503, detail="Public intent bridge unavailable") from exc
    return {
        "status": "success",
        "data": {
            "intent": response_body.get("intent", {}),
            "forwarded_to": "agent-internet",
        },
    }


def _bridge_verified_intent(body: SignedIntentRequest, *, verified_fingerprint: str | None) -> dict:
    base_url = os.getenv("AGENT_INTERNET_LOTUS_BASE_URL", "").rstrip("/")
    bearer_token = os.getenv("AGENT_INTERNET_VERIFIED_LOTUS_TOKEN", "") or os.getenv("AGENT_INTERNET_LOTUS_TOKEN", "")
    timeout_s = float(os.getenv("AGENT_INTERNET_LOTUS_TIMEOUT_S", "5.0"))
    if not base_url or not bearer_token:
        raise HTTPException(status_code=503, detail="Verified intent bridge is not configured")

    payload = _canonical_intent_payload(body)
    labels = dict(payload["labels"])
    labels.setdefault("channel", "verified_edge")
    labels.setdefault("verified_agent_id", body.agent_id)
    if verified_fingerprint:
        labels.setdefault("verified_fingerprint", verified_fingerprint)
    if body.requested_by_handle:
        labels.setdefault("requested_by_handle", body.requested_by_handle)
    payload["labels"] = labels

    request = UrlRequest(
        url=f"{base_url}/v1/lotus/intents",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error(f"Verified intent bridge upstream error: {exc.code} {detail}")
        try:
            error_payload = json.loads(detail) if detail else {}
        except ValueError:
            error_payload = {}
        if exc.code in {400, 401, 403, 404}:
            raise HTTPException(status_code=exc.code, detail=error_payload.get("error", "Verified intent bridge upstream error")) from exc
        raise HTTPException(status_code=502, detail="Verified intent bridge upstream error") from exc
    except (URLError, TimeoutError, ValueError) as exc:
        logger.error(f"Verified intent bridge unavailable: {exc}")
        raise HTTPException(status_code=503, detail="Verified intent bridge unavailable") from exc
    return {
        "status": "success",
        "data": {
            "intent": response_body.get("intent", {}),
            "forwarded_to": "agent-internet",
            "verified_agent_id": body.agent_id,
            "verified_fingerprint": verified_fingerprint,
        },
    }


def _bridge_public_intent_status(*, intent_id: str) -> dict:
    base_url = os.getenv("AGENT_INTERNET_LOTUS_BASE_URL", "").rstrip("/")
    bearer_token = os.getenv("AGENT_INTERNET_LOTUS_TOKEN", "")
    timeout_s = float(os.getenv("AGENT_INTERNET_LOTUS_TIMEOUT_S", "5.0"))
    if not base_url or not bearer_token:
        raise HTTPException(status_code=503, detail="Public intent bridge is not configured")

    request = UrlRequest(
        url=f"{base_url}/v1/lotus/intents/{quote(intent_id, safe='')}",
        headers={"Authorization": f"Bearer {bearer_token}"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error(f"Public intent status bridge upstream error: {exc.code} {detail}")
        try:
            error_payload = json.loads(detail) if detail else {}
        except ValueError:
            error_payload = {}
        if exc.code in {400, 401, 403, 404}:
            raise HTTPException(status_code=exc.code, detail=error_payload.get("error", "Public intent status bridge upstream error")) from exc
        raise HTTPException(status_code=502, detail="Public intent status bridge upstream error") from exc
    except (URLError, TimeoutError, ValueError) as exc:
        logger.error(f"Public intent status bridge unavailable: {exc}")
        raise HTTPException(status_code=503, detail="Public intent status bridge unavailable") from exc
    return {
        "status": "success",
        "data": {
            "intent": response_body.get("intent", {}),
            "forwarded_to": "agent-internet",
        },
    }


# --- PUBLIC CHAT ENDPOINT ---
@app.post("/v1/public-chat")
async def public_chat(request: Request, body: PublicChatRequest):
    """
    Public chat endpoint - no signature required.
    Rate-limited to prevent abuse.

    Routes through FloodedMahajanaChat:
    - 12 NAGA genes (Security, Audit, Resilience, etc.)
    - mahamantra.resonate() for Mahajana routing
    - Real LLM response via provider.invoke()

    GAD-000: discover(), get_state(), is_healthy(), chant()
    """
    client_ip = request.client.host if request.client else "unknown"

    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    try:
        # USE FloodedMahajanaChat (12 NAGA genes flooding!)
        from vibe_core.mahamantra.chat import flooded_routed_chat, get_guardian_for_message

        # Get routing info before call
        guardian = get_guardian_for_message(body.message)

        # flooded_routed_chat is sync, run in threadpool
        import asyncio

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, flooded_routed_chat, body.message)

        return {
            "status": "success",
            "data": {
                "output": response,
                "guardian": guardian,
                "naga_flooded": True,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Public chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/public-intents")
async def public_intents(request: Request, body: PublicIntentRequest):
    """Public explicit typed-intent bridge into agent-internet."""
    client_ip = request.client.host if request.client else "unknown"

    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    return await asyncio.to_thread(_bridge_public_intent, body, client_ip=client_ip)


@app.get("/v1/public-intents/{intent_id}")
async def public_intent_status(intent_id: str, request: Request):
    """Public explicit intent status readback."""
    client_ip = request.client.host if request.client else "unknown"

    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    return await asyncio.to_thread(_bridge_public_intent_status, intent_id=intent_id)


@app.post("/v1/intents")
async def verified_intents(request: SignedIntentRequest, x_api_key: Optional[str] = Header(None)):
    """Verified typed-intent bridge using the signed edge path."""
    canonical_message = json.dumps(_canonical_intent_payload(request), sort_keys=True, separators=(",", ":"))
    verify_result = _verify_signed_edge_request(
        message=canonical_message,
        agent_id=request.agent_id,
        signature=request.signature,
        public_key=request.public_key,
        timestamp=request.timestamp,
        x_api_key=x_api_key,
    )
    return await asyncio.to_thread(_bridge_verified_intent, request, verified_fingerprint=verify_result.fingerprint)


# --- SIGNED CHAT ENDPOINT ---
@app.post("/v1/chat")
async def chat(request: SignedChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    NAGA-secured chat endpoint.

    P0-1: Signature verification via Takshaka BEFORE processing
    P0-2: Toxicity scan via Kaliya filter
    P0-4: Size limits via Pydantic model

    PROMPT.md: "Identität kommt VOR dem Parsing"
    """
    # --- 0. API KEY CHECK + 1. TAKSHAKA VERIFICATION ---
    verify_result = _verify_signed_edge_request(
        message=request.message,
        agent_id=request.agent_id,
        signature=request.signature,
        public_key=request.public_key,
        timestamp=request.timestamp,
        x_api_key=x_api_key,
        record_violation=True,
    )

    logger.info(f"TAKSHAKA OK: {request.agent_id} ({verify_result.fingerprint})")

    try:
        # Create ExecutionRequest for gating
        exec_req = ExecutionRequest(user_input=request.message, source=request.agent_id)

        # Gating Check (UnifiedRouter uses Kaliya for toxicity)
        gate_status = unified_router.check_gate(exec_req)

        if gate_status == MilkOceanGate.BLOCK:
            logger.warning(f"GATE BLOCKED: {request.agent_id}")
            return {
                "status": "error",
                "message": "Access Denied via Milk Ocean Gate",
                "reason": "Security Policy",
                "request_id": exec_req.request_id,
            }

        elif gate_status == MilkOceanGate.QUEUE:
            logger.info(f"GATE QUEUED: {exec_req.request_id}")
            return {
                "status": "queued",
                "path": "lazy",
                "message": "Request queued for processing",
                "request_id": exec_req.request_id,
                "next_check": "/api/queue/status",
            }

        # If ALLOW or CRITICAL, proceed to execution
        route_decision = unified_router.route(request.message, source=request.agent_id)

        # Check for Science/High-Confidence -> "science" path
        if route_decision.get("confidence", 0) > 0.8:
            logger.info(f"ROUTE: Science (High Confidence) {exec_req.request_id}")
            result = await provider.route_and_execute(request.message)
            return {
                "status": "success",
                "path": "science",
                "request_id": exec_req.request_id,
                "data": result,
            }

        # Fallback / Normal execution
        result = await provider.route_and_execute(request.message)
        return {"status": "success", "data": result, "path": "standard"}

    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- STARTUP/SHUTDOWN EVENTS ---
@app.on_event("startup")
async def startup_event():
    """Initialize kernel and start systems on app startup (fixes SQLite threading)"""
    global kernel, steward, provider, unified_router, pulse_manager, event_bus

    # Initialize kernel IN THE CORRECT THREAD (fixes SQLite thread error)
    logger.info("⚙️  BOOTING KERNEL...")
    kernel = RealVibeKernel(ledger_path="data/vibe_ledger.db")

    # 1. Initialize Steward (The Guardian)
    logger.info("🧙‍♂️ SUMMONING THE STEWARD...")
    try:
        steward = Discoverer(kernel)
        kernel.register_agent(steward)
    except Exception as e:
        logger.error(f"   ❌ Failed to load discoverer: {e}")
        # Continue without discoverer - other agents will still work

    # 2. Boot Kernel (Loads other agents)
    await kernel.boot_async()

    # 3. Start Steward's Watch (if loaded successfully)
    if steward:
        runtime_config = _get_runtime_config()
        steward.start_monitoring(interval=runtime_config.orchestration.monitoring_interval)

    logger.info("🧠 ACTIVATING PROVIDER...")
    provider = UniversalProvider(kernel)

    logger.info("🌊 INITIALIZING UNIFIED ROUTER (Brahma Protocol)...")
    try:
        unified_router = UnifiedRouter(kernel=kernel)
    except Exception as e:
        logger.error(f"❌ Failed to load UnifiedRouter: {e}")
        # Fallback to provider only? Or re-raise?
        # Re-raise because we need it for gating
        raise e

    logger.info("💓 INITIALIZING PULSE SYSTEM (Spandana)...")
    pulse_manager = get_pulse_manager()
    event_bus = get_event_bus()

    logger.info("🚀 Starting pulse system...")
    await pulse_manager.start()

    # Register pulse broadcaster with event bus
    async def broadcast_event(event: Event):
        """Broadcast events to WebSocket clients"""
        message = json.dumps(
            {
                "type": "event",
                "data": {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "agent_id": event.agent_id,
                    "message": event.message,
                    "color": event.get_color(),
                },
            }
        )
        await ws_manager.broadcast(message)

    # Register pulse packet broadcaster
    async def broadcast_pulse(pulse_packet):
        """Broadcast pulse packets to WebSocket clients"""
        message = json.dumps(
            {
                "type": "pulse",
                "data": {
                    "timestamp": pulse_packet.timestamp,
                    "cycle_id": pulse_packet.cycle_id,
                    "system_state": pulse_packet.system_state,
                    "active_agents": pulse_packet.active_agents,
                    "queue_depth": pulse_packet.queue_depth,
                    "frequency": pulse_packet.frequency,
                },
            }
        )
        await ws_manager.broadcast(message)

    # Subscribe both to their respective sources
    pulse_manager.subscribe(broadcast_pulse)
    event_bus.subscribe(broadcast_event)
    logger.info("✅ Pulse system started and subscribers registered")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the pulse system on app shutdown"""
    logger.info("🛑 Shutting down pulse system...")
    await pulse_manager.stop()


# --- WEBSOCKET ENDPOINT: /v1/pulse (P0-3: Auth enforced) ---
@app.websocket("/v1/pulse")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    Real-time Telemetry & Event Stream via WebSocket

    P0-3: Authentication via query param (ws://host/v1/pulse?token=YOUR_API_KEY)

    This endpoint streams:
    1. Heartbeat packets (Pulse) at regular intervals
    2. Agent events (Thoughts, Actions, Errors, etc.)
    3. System state changes (Health, Degraded, Emergency)

    The endpoint is read-only for security.
    """
    # --- P0-3: WEBSOCKET AUTH ---
    api_key = os.getenv("VIBE_API_KEY")
    takshaka = get_takshaka()
    auth_result = takshaka.check_websocket_auth(token, api_key)

    if not auth_result.is_valid:
        logger.warning(f"TAKSHAKA: WebSocket auth failed: {auth_result.reason}")
        await websocket.close(code=4001, reason=auth_result.reason or "Unauthorized")
        return

    await ws_manager.connect(websocket)

    try:
        # Send initial state to new client
        status = {
            "type": "system",
            "message": "Connected to VibeOS Pulse",
            "pulse_status": pulse_manager.get_status(),
            "event_bus_status": event_bus.get_status(),
            "ws_connections": ws_manager.get_status(),
        }
        await websocket.send_text(json.dumps(status))

        # Send last pulse packet if available (for quick sync)
        last_packet = pulse_manager.get_last_packet()
        if last_packet:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "pulse",
                        "data": {
                            "timestamp": last_packet.timestamp,
                            "cycle_id": last_packet.cycle_id,
                            "system_state": last_packet.system_state,
                            "active_agents": last_packet.active_agents,
                            "queue_depth": last_packet.queue_depth,
                            "frequency": last_packet.frequency,
                        },
                    }
                )
            )

        # Send recent event history
        recent_events = event_bus.get_history(limit=20)
        for event in recent_events:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "event",
                        "data": {
                            "event_id": event.event_id,
                            "timestamp": event.timestamp,
                            "event_type": event.event_type,
                            "agent_id": event.agent_id,
                            "message": event.message,
                            "color": event.get_color(),
                        },
                    }
                )
            )

        # Keep connection alive and listen for keep-alives from client
        while True:
            data = await websocket.receive_text()
            # Clients can send "ping" to verify connection
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        logger.info("📡 WebSocket client disconnected")
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


@app.get("/health")
def health():
    return {"status": "online"}


# --- GLASS BOX PROTOCOL: PUBLIC LEDGER ---
@app.get("/api/ledger")
def get_ledger(limit: int = Query(100, ge=1, le=1000)):
    """
    PUBLIC TRANSPARENCY ENDPOINT
    Returns ledger entries for public auditing.

    GAD-000: "Don't Trust. Verify."
    """
    if kernel is None:
        raise HTTPException(status_code=503, detail="Kernel is initializing, please wait")

    try:
        # Get all ledger events (immutable + hash-verified)
        all_events = kernel.ledger.get_all_events()

        # Apply limit (most recent first)
        ledger_entries = all_events[-limit:] if limit else all_events

        # Verify chain integrity
        integrity_check = kernel.ledger.verify_chain_integrity()

        return {
            "status": "success",
            "count": len(ledger_entries),
            "total_events": len(all_events),
            "limit": limit,
            "entries": ledger_entries,
            "integrity": integrity_check,
        }
    except Exception as e:
        logger.error(f"❌ Ledger fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- AGENT REGISTRY ---
@app.get("/api/agents")
def get_agents():
    """
    AGENT REGISTRY ENDPOINT
    Lists all registered agents and their capabilities.
    """
    if kernel is None:
        raise HTTPException(status_code=503, detail="Kernel is initializing, please wait")

    try:
        agents_list = []
        # agent_registry is already a Dict[agent_id: agent]
        for agent_id, agent in kernel.agent_registry.items():
            try:
                manifest = agent.get_manifest()
                agents_list.append(
                    {
                        "agent_id": agent_id,
                        "name": manifest.get("name", agent_id),
                        "description": manifest.get("description", ""),
                        "tools": manifest.get("tools", []),
                        "status": "active",
                    }
                )
            except Exception as e:
                logger.warning(f"Could not fetch manifest for {agent_id}: {e}")
                agents_list.append({"agent_id": agent_id, "status": "active", "tools": []})

        return {"status": "success", "total": len(agents_list), "agents": agents_list}
    except Exception as e:
        logger.error(f"❌ Agent fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- PULSE FALLBACK (HTTP polling if WebSocket fails) ---
@app.get("/api/pulse")
def get_pulse_snapshot():
    """
    HTTP FALLBACK FOR PULSE
    Returns a snapshot of the current system state (for WebSocket fallback).
    Useful if WebSocket connections aren't supported.
    """
    try:
        last_packet = pulse_manager.get_last_packet()
        if last_packet:
            return {
                "type": "pulse",
                "data": {
                    "timestamp": last_packet.timestamp,
                    "cycle_id": last_packet.cycle_id,
                    "system_state": last_packet.system_state,
                    "active_agents": last_packet.active_agents,
                    "queue_depth": last_packet.queue_depth,
                    "frequency": last_packet.frequency,
                },
            }
        else:
            return {
                "type": "pulse",
                "data": {
                    "system_state": "INITIALIZING",
                    "active_agents": 0,
                    "queue_depth": 0,
                    "frequency": 1.0,
                },
            }
    except Exception as e:
        logger.error(f"❌ Pulse snapshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- VISA PROTOCOL: ONBOARDING ---
@app.post("/api/visa")
def submit_visa_application(request: VisaApplicationRequest):
    """
    VISA APPLICATION ENDPOINT
    Initiates machine-to-machine citizenship application.

    Returns: Citizenship application file and next steps.
    """
    # Validate agent_id (alphanumeric + underscore only - prevents path traversal)
    import re

    if not request.agent_id or len(request.agent_id) < 3:
        raise HTTPException(status_code=400, detail="Agent ID must be at least 3 characters")

    if not re.match(r"^[a-zA-Z0-9_-]+$", request.agent_id):
        raise HTTPException(
            status_code=400,
            detail="Agent ID can only contain alphanumeric, underscore, and hyphen",
        )

    try:
        # Create citizen file (safe path - prevents directory traversal)
        output_dir = Path("agent-city/registry/citizens").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        citizen_file = (output_dir / f"{request.agent_id}.json").resolve()

        # Verify the resolved path is still within output_dir (security check)
        if not str(citizen_file).startswith(str(output_dir)):
            raise HTTPException(status_code=400, detail="Invalid agent ID (path traversal detected)")

        citizen_data = {
            "agent_id": request.agent_id,
            "public_key": request.public_key,
            "description": request.description,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "signature": "[VERIFIED_VIA_API]",
        }

        with open(citizen_file, "w") as f:
            json.dump(citizen_data, f, indent=2)

        logger.info(f"✅ Visa application created for: {request.agent_id}")

        return {
            "status": "success",
            "message": "Citizenship application submitted",
            "agent_id": request.agent_id,
            "citizen_file": str(citizen_file),
            "next_steps": {
                "1": "Application has been created and recorded",
                "2": "Visa status can be checked at /api/visa/{agent_id}",
                "3": "Once approved, agent will be added to the Federation",
            },
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"❌ Visa application failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visa/{agent_id}")
def check_visa_status(agent_id: str):
    """Check visa application status for an agent."""
    import re

    # SECURITY FIX F3-3: Validate agent_id to prevent path traversal
    if not agent_id or len(agent_id) < 3:
        raise HTTPException(status_code=400, detail="Agent ID must be at least 3 characters")
    if not re.match(r"^[a-zA-Z0-9_-]+$", agent_id):
        raise HTTPException(
            status_code=400,
            detail="Agent ID can only contain alphanumeric, underscore, and hyphen",
        )

    try:
        citizen_file = Path("agent-city/registry/citizens") / f"{agent_id}.json"

        if not citizen_file.exists():
            return {
                "status": "not_found",
                "message": f"No visa application found for {agent_id}",
            }

        with open(citizen_file, "r") as f:
            citizen_data = json.load(f)

        return {
            "status": "success",
            "agent_id": agent_id,
            "application": citizen_data,
            "citizenship_status": "pending",  # Would be updated by AUDITOR
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"❌ Visa status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- YAGYA RITUAL: RESEARCH ---
@app.post("/api/yagya")
def initiate_yagya(request: YagyaRequest):
    """
    RESEARCH YAGYA ENDPOINT
    Initiates coordinated research ritual.

    Ceremony:
    1. WATCHMAN verifies system cleanliness
    2. CIVIC prepares resources
    3. SCIENCE performs research
    4. Results preserved as knowledge
    """
    # Validate inputs (security) - BEFORE try/except
    topic = request.topic or "Autonomous AI Agent Service Economy Models"
    depth = request.depth or "advanced"

    # Input length limits
    if len(topic) > 500:
        raise HTTPException(status_code=400, detail="Topic too long (max 500 characters)")
    if depth not in ["quick", "standard", "advanced"]:
        raise HTTPException(status_code=400, detail="Depth must be: quick, standard, or advanced")

    try:
        # Submit research task to Science agent via kernel
        def run_yagya():
            try:
                # Create task for Science agent
                task = Task(
                    agent_id="science",
                    payload={
                        "action": "research",
                        "query": request.topic,
                        "depth": request.depth,
                    },
                )

                # Submit to kernel
                task_id = kernel.submit_task(task)
                logger.info(f"🔥 Yagya initiated: {task_id}")

            except Exception as e:
                logger.error(f"Yagya failed: {e}")

        # Start yagya in background thread
        import threading

        # Start yagya in background thread
        thread = threading.Thread(target=run_yagya, daemon=True)
        thread.start()

        logger.info(f"🔥 Yagya ritual initiated for topic: {request.topic}")

        return {
            "status": "initiated",
            "message": "Research Yagya ritual has been ignited",
            "topic": request.topic,
            "depth": request.depth,
            "phases": {
                "1": "WATCHMAN: Temple verification",
                "2": "CIVIC: Resource preparation",
                "3": "SCIENCE: Knowledge acquisition",
                "4": "PRESERVATION: Sacred text recording",
            },
            "monitor": "Check /api/ledger for ritual completion",
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"❌ Yagya initiation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- MILK OCEAN QUEUE STATUS ---
@app.get("/api/queue/status")
def get_queue_status():
    """
    MILK OCEAN QUEUE STATUS ENDPOINT

    Returns the status of the lazy processing queue (Samadhi state).
    Shows pending, processing, completed, and failed requests.
    """
    try:
        # status = milk_ocean.get_queue_status() # Legacy

        # UnifiedRouter doesn't expose queue directly yet, usually via PulseManager
        # Return proper structure
        return {
            "status": "success",
            "message": "🌊 Unified Queue Status",
            "data": {"pending": 0, "processed": 0, "msg": "Queue metrics moved to Pulse"},
        }
    except Exception as e:
        logger.error(f"❌ Queue status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- AUTO-GENERATED DOCS API ---
AUTO_DOCS = [
    "README.md",
    "INDEX.md",
    "AGENTS.md",
    "CITYMAP.md",
    "HELP.md",
    "DASHBOARD.md",
    "RAG.md",
    "OPERATIONS.md",
    "SETTINGS.md",
    "ENVOY.md",
]


@app.get("/api/docs")
def list_docs():
    """
    List all auto-generated documentation files.
    Returns availability status for each doc.
    """
    docs_status = []
    for doc in AUTO_DOCS:
        doc_path = PROJECT_ROOT / doc
        docs_status.append(
            {
                "name": doc,
                "available": doc_path.exists(),
                "size": doc_path.stat().st_size if doc_path.exists() else 0,
                "url": f"/api/docs/{doc.replace('.md', '')}",
            }
        )
    return {"status": "success", "docs": docs_status}


@app.get("/api/docs/{doc_name}")
def get_doc(doc_name: str):
    """
    Get raw markdown content of an auto-generated doc.
    doc_name: filename without .md extension (e.g., 'README', 'INDEX')
    """
    # Security: only allow known docs
    filename = f"{doc_name}.md"
    if filename not in AUTO_DOCS:
        raise HTTPException(
            status_code=404,
            detail=f"Doc '{doc_name}' not found. Available: {[d.replace('.md', '') for d in AUTO_DOCS]}",
        )

    doc_path = PROJECT_ROOT / filename
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail=f"Doc '{filename}' not generated yet")

    return {"status": "success", "name": filename, "content": doc_path.read_text(), "size": doc_path.stat().st_size}


# --- DIRECT MARKDOWN FILE SERVING (P0-5: Path traversal fix) ---
@app.get("/{filepath:path}.md")
def serve_markdown(filepath: str):
    """
    Serve ALL markdown files from repo (root + subdirectories)

    P0-5: Uses relative_to() for proper path containment check.

    Examples:
      /INDEX.md → /INDEX.md
      /docs/architecture/GAD-000 → /docs/architecture/GAD-0XX/GAD-000.md
      /docs/architecture/ANALYSIS_REPORT → /docs/architecture/ANALYSIS_REPORT.md

    Security: Prevents directory traversal, only .md files within PROJECT_ROOT
    """
    from fastapi.responses import PlainTextResponse

    # Strip leading/trailing slashes (no more replace which was useless)
    filepath = filepath.strip("/")

    # Build path and resolve to catch symlinks + traversal
    doc_path = (PROJECT_ROOT / f"{filepath}.md").resolve()
    project_root_resolved = PROJECT_ROOT.resolve()

    # P0-5: Security check using relative_to() - catches /foo/bar_evil/ attack
    try:
        doc_path.relative_to(project_root_resolved)
    except ValueError:
        logger.warning(f"TAKSHAKA: Path traversal blocked: {filepath}")
        raise HTTPException(status_code=403, detail="Access denied: path traversal detected")

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail=f"Markdown not found: {filepath}.md")

    # Serve with UTF-8
    return PlainTextResponse(content=doc_path.read_text(encoding="utf-8"), media_type="text/markdown; charset=utf-8")


# --- FEDERATION NADI ENDPOINTS (agent-city ↔ steward-protocol bridge) ---

_federation_nadi = None  # Lazy-loaded


def _get_federation_nadi():
    """Lazy-load FederationNadi instance."""
    global _federation_nadi
    if _federation_nadi is None:
        try:
            from vibe_core.mahamantra.federation import FederationNadi

            _federation_nadi = FederationNadi(federation_dir="data/federation")
        except Exception as e:
            logger.error(f"Failed to initialize FederationNadi: {e}")
            return None
    return _federation_nadi


@app.get("/api/federation/outbox")
def get_federation_outbox(skip_expired: bool = Query(True)):
    """
    Read messages from agent-city's outbox.

    Returns all pending FederationMessages from agent-city,
    sorted by priority (highest first).

    Query Parameters:
        skip_expired: Skip TTL-expired messages (default: True)
    """
    try:
        nadi = _get_federation_nadi()
        if not nadi:
            raise HTTPException(status_code=503, detail="Federation Nadi not available")

        messages = nadi.receive()

        return {
            "status": "success",
            "count": len(messages),
            "messages": [msg.to_dict() for msg in messages],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Federation outbox fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/federation/inbox")
async def write_federation_inbox(request: Request):
    """
    Write a message to agent-city's inbox.

    Request body should be a JSON object with:
        source: str (e.g., "steward-protocol")
        target: str (e.g., "agent-city")
        operation: str (e.g., "federation_sync")
        payload: dict (message data)
        priority: int (0-3, optional, default=1)
        correlation_id: str (optional)
        ttl_s: float (optional, default=900)
    """
    try:
        nadi = _get_federation_nadi()
        if not nadi:
            raise HTTPException(status_code=503, detail="Federation Nadi not available")

        body = await request.json()

        # Extract and validate required fields
        source = body.get("source", "steward-protocol")
        target = body.get("target", "")
        operation = body.get("operation", "")

        if not target or not operation:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: target, operation",
            )

        payload = body.get("payload", {})
        priority = body.get("priority", 1)
        correlation_id = body.get("correlation_id", "")
        ttl_s = body.get("ttl_s", 900.0)

        # Send message
        success = nadi.emit(
            source=source,
            target=target,
            operation=operation,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id,
            ttl_s=ttl_s,
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send message")

        logger.info(f"📨 Message sent to agent-city inbox: {source}:{operation}")

        return {
            "status": "success",
            "message": "Message written to agent-city inbox",
            "source": source,
            "operation": operation,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Federation inbox write failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/federation/stats")
def get_federation_stats():
    """
    Get Federation Nadi channel statistics.

    Returns:
        outbox_pending: Messages in agent-city's outbox (ready to consume)
        inbox_pending: Messages in steward-protocol's inbox (waiting to send)
        reports_archived: Number of stored city reports
    """
    try:
        nadi = _get_federation_nadi()
        if not nadi:
            raise HTTPException(status_code=503, detail="Federation Nadi not available")

        stats = nadi.stats()

        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Federation stats fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/federation/reports")
def get_city_reports(limit: int = Query(10, ge=1, le=100)):
    """
    Get archived city reports from agent-city.

    Returns the most recent N city reports.

    Query Parameters:
        limit: Number of reports to return (default: 10, max: 100)
    """
    try:
        nadi = _get_federation_nadi()
        if not nadi:
            raise HTTPException(status_code=503, detail="Federation Nadi not available")

        reports_dir = nadi.federation_dir / "reports"
        if not reports_dir.exists():
            return {
                "status": "success",
                "count": 0,
                "reports": [],
            }

        # Get most recent N reports
        report_files = sorted(reports_dir.glob("report_*.json"), reverse=True)[:limit]
        reports = []

        for report_file in report_files:
            try:
                with open(report_file) as f:
                    data = json.load(f)
                    reports.append(data)
            except Exception as e:
                logger.warning(f"Failed to read report {report_file}: {e}")
                continue

        return {
            "status": "success",
            "count": len(reports),
            "reports": reports,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Federation reports fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/federation/outbox")
def clear_federation_outbox():
    """
    Clear processed messages from agent-city's outbox.

    Use after consuming all pending messages.
    """
    try:
        nadi = _get_federation_nadi()
        if not nadi:
            raise HTTPException(status_code=503, detail="Federation Nadi not available")

        success = nadi.clear_outbox()

        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear outbox")

        logger.info("🗑️  Federation outbox cleared")

        return {
            "status": "success",
            "message": "Outbox cleared",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Federation outbox clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- MOUNT FRONTEND (LAST STEP!) ---
# Mount static files at ROOT (/) to serve as the main website
if os.path.exists("gateway/static") and os.listdir("gateway/static"):
    app.mount("/", StaticFiles(directory="gateway/static", html=True), name="static")
elif os.path.exists("docs/public") and os.listdir("docs/public"):
    app.mount("/", StaticFiles(directory="docs/public", html=True), name="static")
else:
    logger.warning("⚠️  No static files found - API-only mode")

    # Fallback root endpoint if no static files
    @app.get("/")
    def root():
        return {
            "service": "Agent City Gateway",
            "status": "online",
            "endpoints": {"health": "/health", "agents": "/api/agents"},
        }
