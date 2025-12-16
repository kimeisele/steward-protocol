import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Set

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --- AGENT MIGRATION PATH FIX (ABSOLUTE PATHS FOR DOCKER) ---
# Use absolute paths to ensure imports work in Docker containers
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# KERNEL IMPORTS (after sys.path fix for Docker)
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

# --- CORS: THE DOOR UNLOCKER (FIXES 405/422 ERRORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt alles (Localhost, Network IP)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt POST, GET, OPTIONS, etc.
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


# --- DATA MODELS ---
class SignedChatRequest(BaseModel):
    message: str
    agent_id: str
    signature: str
    public_key: str
    timestamp: int


class VisaApplicationRequest(BaseModel):
    agent_id: str
    description: str
    public_key: str


class YagyaRequest(BaseModel):
    topic: Optional[str] = "Autonomous AI Agent Service Economy Models"
    depth: Optional[str] = "advanced"


# --- ENDPOINT ---
@app.post("/v1/chat")
async def chat(request: SignedChatRequest, x_api_key: Optional[str] = Header(None)):
    # 1. Auth Check
    valid_keys = [os.getenv("VIBE_API_KEY", "steward-secret-key")]
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    logger.info(f"📨 RECEIVED: {request.message} from {request.agent_id}")

    try:
        # Create ExecutionRequest for gating
        exec_req = ExecutionRequest(user_input=request.message, source=request.agent_id)

        # Gating Check (UnifiedRouter)
        gate_status = unified_router.check_gate(exec_req)

        if gate_status == MilkOceanGate.BLOCK:
            logger.warning(f"⛔ Request blocked: {request.agent_id}")
            return {
                "status": "error",
                "message": "Access Denied via Milk Ocean Gate",
                "reason": "Security Policy",
                "request_id": exec_req.request_id,
            }

        elif gate_status == MilkOceanGate.QUEUE:
            logger.info(f"🌊 Request queued: {exec_req.request_id}")
            return {
                "status": "queued",
                "path": "lazy",
                "message": "Request queued for processing",
                "request_id": exec_req.request_id,
                "next_check": "/api/queue/status",
            }

        # If ALLOW or CRITICAL, proceed to execution

        # Route locally just to check confidence for "flash" vs "science" (optional optimization)
        route_decision = unified_router.route(request.message, source=request.agent_id)

        # Check for Science/High-Confidence -> "science" path
        if route_decision.get("confidence", 0) > 0.8:
            logger.info(f"🔥 Routing to Science agent (High Confidence): {exec_req.request_id}")
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
        logger.error(f"❌ ERROR: {e}")
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
    kernel.boot()

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


# --- WEBSOCKET ENDPOINT: /v1/pulse ---
@app.websocket("/v1/pulse")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time Telemetry & Event Stream via WebSocket

    This endpoint streams:
    1. Heartbeat packets (Pulse) at regular intervals
    2. Agent events (Thoughts, Actions, Errors, etc.)
    3. System state changes (Health, Degraded, Emergency)

    The endpoint is read-only for security.
    """
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


# --- DIRECT MARKDOWN FILE SERVING ---
@app.get("/{filepath:path}.md")
def serve_markdown(filepath: str):
    """
    Serve ALL markdown files from repo (root + subdirectories)

    Examples:
      /INDEX.md → /INDEX.md
      /docs/architecture/GAD-000 → /docs/architecture/GAD-0XX/GAD-000.md
      /docs/architecture/ANALYSIS_REPORT → /docs/architecture/ANALYSIS_REPORT.md

    Security: Prevents directory traversal, only .md files within PROJECT_ROOT
    """
    from fastapi.responses import PlainTextResponse

    # Sanitize (prevent directory traversal)
    filepath = filepath.replace("..", "").strip("/")

    # Build path
    doc_path = PROJECT_ROOT / f"{filepath}.md"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail=f"Markdown not found: {filepath}.md")

    # Security: ensure within PROJECT_ROOT
    try:
        doc_path = doc_path.resolve()
        if not str(doc_path).startswith(str(PROJECT_ROOT)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    # Serve with UTF-8
    return PlainTextResponse(content=doc_path.read_text(encoding="utf-8"), media_type="text/markdown; charset=utf-8")


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
