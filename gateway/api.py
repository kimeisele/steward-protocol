
import logging
import os
import sys
import json
import subprocess
import asyncio
from fastapi import FastAPI, HTTPException, Header, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Set
from pathlib import Path

# --- AGENT MIGRATION PATH FIX (ABSOLUTE PATHS FOR DOCKER) ---
# Use absolute paths to ensure imports work in Docker containers
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "steward" / "system_agents"))
sys.path.insert(0, str(PROJECT_ROOT / "agent_city" / "registry"))

# KERNEL IMPORTS
from vibe_core.kernel_impl import RealVibeKernel
from provider.universal_provider import UniversalProvider

# MILK OCEAN ROUTER IMPORTS
from envoy.tools.milk_ocean import MilkOceanRouter

# PULSE SYSTEM IMPORTS
from vibe_core.pulse import get_pulse_manager, PulseFrequency
from vibe_core.event_bus import get_event_bus, Event

# STEWARD AGENT IMPORT
from steward.system_agents.steward.agent import StewardAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GATEWAY")

app = FastAPI(title="VibeChat Gateway // GAD-3000")

# --- CORS: THE DOOR UNLOCKER (FIXES 405/422 ERRORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt alles (Localhost, Network IP)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# --- BOOT SEQUENCE ---
logger.info("⚙️  BOOTING KERNEL...")
kernel = RealVibeKernel(ledger_path="data/vibe_ledger.db")

# 1. Initialize Steward (The Guardian)
logger.info("🧙‍♂️ SUMMONING THE STEWARD...")
steward = StewardAgent(kernel)
kernel.register_agent(steward)

# 2. Boot Kernel (Loads other agents)
kernel.boot()

# 3. Start Steward's Watch (Autonomous Discovery)
steward.start_monitoring(interval=10.0)

logger.info("🧠 ACTIVATING PROVIDER...")
provider = UniversalProvider(kernel)

logger.info("🌊 INITIALIZING MILK OCEAN ROUTER (Brahma Protocol)...")
milk_ocean = MilkOceanRouter(kernel=kernel)

logger.info("💓 INITIALIZING PULSE SYSTEM (Spandana)...")
pulse_manager = get_pulse_manager()
event_bus = get_event_bus()

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
        # 1. GUEST ACCESS (GAD-000: The Bypass)
        if request.agent_id == "guest":
            logger.info(f"🌊 GUEST ACCESS: Routing '{request.message}' to Milk Ocean")
            # Direct route to Milk Ocean Router (Brahma Protocol)
            # Guests don't get to invoke the Kernel directly, only query via Router
            routing_decision = milk_ocean.process_prayer(request.message, agent_id="guest")
        else:
            # 2. CITIZEN ACCESS (GAD-1000 Verification)
            # MILK OCEAN ROUTER: Gate the request through Brahma's protocol
            # This implements the 4-tier filtering: Watchman -> Envoy -> Science -> Samadhi
            routing_decision = milk_ocean.process_prayer(request.message, request.agent_id)

        # 2a. Handle blocked requests
        if routing_decision.get('status') == 'blocked':
            logger.warning(f"⛔ Request blocked: {routing_decision.get('reason')}")
            return {
                "status": "error",
                "message": routing_decision.get('message'),
                "reason": routing_decision.get('reason'),
                "request_id": routing_decision.get('request_id')
            }

        # 2b. Handle lazy queue requests (non-critical, batch processing)
        elif routing_decision.get('status') == 'queued':
            logger.info(f"🌊 Request queued for lazy processing: {routing_decision.get('request_id')}")
            return {
                "status": "queued",
                "path": "lazy",
                "message": routing_decision.get('message'),
                "request_id": routing_decision.get('request_id'),
                "next_check": "/api/queue/status"
            }

        # 2c. Handle fast-path requests (MEDIUM priority -> Flash/Haiku)
        elif routing_decision.get('path') == 'flash':
            logger.info(f"⚡ Routing to Flash model (Envoy): {routing_decision.get('request_id')}")
            # Would call Gemini Flash or Claude Haiku here
            # For now, fall through to provider (now with PRANA EVENTS!)
            result = await provider.route_and_execute(request.message)
            return {
                "status": "success",
                "path": "flash",
                "request_id": routing_decision.get('request_id'),
                "data": result
            }

        # 2d. Handle complex requests (HIGH priority -> Pro/Opus)
        elif routing_decision.get('path') == 'science':
            logger.info(f"🔥 Routing to Science agent (Pro model): {routing_decision.get('request_id')}")
            # Execute via Provider (which now knows to use Pro model and EMITS EVENTS!)
            result = await provider.route_and_execute(request.message)

            return {
                "status": "success",
                "path": "science",
                "request_id": routing_decision.get('request_id'),
                "data": result
            }

        else:
            # Fallback to standard execution (with PRANA!)
            result = await provider.route_and_execute(request.message)
            return {
                "status": "success",
                "data": result
            }

    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- STARTUP/SHUTDOWN EVENTS ---
@app.on_event("startup")
async def startup_event():
    """Start the pulse system on app startup"""
    logger.info("🚀 Starting pulse system...")
    await pulse_manager.start()

    # Register pulse broadcaster with event bus
    async def broadcast_event(event: Event):
        """Broadcast events to WebSocket clients"""
        message = json.dumps({
            "type": "event",
            "data": {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "agent_id": event.agent_id,
                "message": event.message,
                "color": event.get_color()
            }
        })
        await ws_manager.broadcast(message)

    # Register pulse packet broadcaster
    async def broadcast_pulse(pulse_packet):
        """Broadcast pulse packets to WebSocket clients"""
        message = json.dumps({
            "type": "pulse",
            "data": {
                "timestamp": pulse_packet.timestamp,
                "cycle_id": pulse_packet.cycle_id,
                "system_state": pulse_packet.system_state,
                "active_agents": pulse_packet.active_agents,
                "queue_depth": pulse_packet.queue_depth,
                "frequency": pulse_packet.frequency
            }
        })
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
            "ws_connections": ws_manager.get_status()
        }
        await websocket.send_text(json.dumps(status))

        # Send last pulse packet if available (for quick sync)
        last_packet = pulse_manager.get_last_packet()
        if last_packet:
            await websocket.send_text(json.dumps({
                "type": "pulse",
                "data": {
                    "timestamp": last_packet.timestamp,
                    "cycle_id": last_packet.cycle_id,
                    "system_state": last_packet.system_state,
                    "active_agents": last_packet.active_agents,
                    "queue_depth": last_packet.queue_depth,
                    "frequency": last_packet.frequency
                }
            }))

        # Send recent event history
        recent_events = event_bus.get_history(limit=20)
        for event in recent_events:
            await websocket.send_text(json.dumps({
                "type": "event",
                "data": {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "agent_id": event.agent_id,
                    "message": event.message,
                    "color": event.get_color()
                }
            }))

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
            "integrity": integrity_check
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
    try:
        agents_list = []
        # agent_registry is already a Dict[agent_id: agent]
        for agent_id, agent in kernel.agent_registry.items():
            try:
                manifest = agent.get_manifest()
                agents_list.append({
                    "agent_id": agent_id,
                    "name": manifest.get("name", agent_id),
                    "description": manifest.get("description", ""),
                    "tools": manifest.get("tools", []),
                    "status": "active"
                })
            except Exception as e:
                logger.warning(f"Could not fetch manifest for {agent_id}: {e}")
                agents_list.append({
                    "agent_id": agent_id,
                    "status": "active",
                    "tools": []
                })

        return {
            "status": "success",
            "total": len(agents_list),
            "agents": agents_list
        }
    except Exception as e:
        logger.error(f"❌ Agent fetch failed: {e}")
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
        raise HTTPException(status_code=400, detail="Agent ID can only contain alphanumeric, underscore, and hyphen")

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
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "signature": "[VERIFIED_VIA_API]"
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
                "3": "Once approved, agent will be added to the Federation"
            }
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
                "message": f"No visa application found for {agent_id}"
            }

        with open(citizen_file, "r") as f:
            citizen_data = json.load(f)

        return {
            "status": "success",
            "agent_id": agent_id,
            "application": citizen_data,
            "citizenship_status": "pending"  # Would be updated by AUDITOR
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
                        "depth": request.depth
                    }
                )
                
                # Submit to kernel
                task_id = kernel.submit_task(task)
                logger.info(f"🔥 Yagya initiated: {task_id}")
                
            except Exception as e:
                logger.error(f"Yagya failed: {e}")

        # Start yagya in background thread
        import subprocess
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
                "4": "PRESERVATION: Sacred text recording"
            },
            "monitor": "Check /api/ledger for ritual completion"
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
        status = milk_ocean.get_queue_status()
        return {
            "status": "success",
            "message": "🌊 Milk Ocean Queue Status",
            "data": status
        }
    except Exception as e:
        logger.error(f"❌ Queue status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- MOUNT FRONTEND (LAST STEP!) ---
# Mount static files ONLY if directory exists AND has files
# Use /ui path instead of / to avoid shadowing API routes
if os.path.exists("gateway/static") and os.listdir("gateway/static"):
    app.mount("/ui", StaticFiles(directory="gateway/static", html=True), name="static")
elif os.path.exists("docs/public") and os.listdir("docs/public"):
    app.mount("/ui", StaticFiles(directory="docs/public", html=True), name="static")
else:
    logger.warning("⚠️  No static files found - API-only mode")

# Add simple root endpoint
@app.get("/")
def root():
    return {
        "service": "Agent City Gateway",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "agents": "/api/agents",
            "ui": "/ui (if available)"
        }
    }
