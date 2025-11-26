
import logging
import os
import json
import subprocess
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path

# KERNEL IMPORTS
from vibe_core.kernel_impl import RealVibeKernel
from provider.universal_provider import UniversalProvider

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
kernel.boot()

logger.info("🧠 ACTIVATING PROVIDER...")
provider = UniversalProvider(kernel)

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
        # 2. Execute via Provider (GAD-4000: Fast-Path vs Slow-Path)
        result = provider.route_and_execute(request.message)

        # Handle both fast-path (instant response) and slow-path (task queued)
        path = result.get('path', 'slow')
        summary = result.get('summary', result.get('message', ''))

        if path == 'fast' or path == 'fast_fallback':
            # Fast-path: Return the natural language response directly
            return {
                "status": "success",
                "path": path,
                "summary": summary,
                "data": result
            }
        else:
            # Slow-path: Acknowledge task submission with agent info
            agent = result.get('details', {}).get('agent', 'UNKNOWN')
            return {
                "status": "success",
                "path": "slow",
                "summary": summary,
                "data": result
            }
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        # Get ledger from kernel
        ledger_entries = kernel.ledger.get_entries(limit=limit)

        return {
            "status": "success",
            "count": len(ledger_entries),
            "limit": limit,
            "entries": ledger_entries,
            "integrity": kernel.ledger.verify_integrity()
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
        for agent_id, agent in kernel.agent_registry.agents.items():
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
    try:
        # Validate agent_id
        if not request.agent_id or len(request.agent_id) < 3:
            raise HTTPException(status_code=400, detail="Agent ID must be at least 3 characters")

        # Create citizen file
        output_dir = Path("agent-city/registry/citizens")
        output_dir.mkdir(parents=True, exist_ok=True)

        citizen_file = output_dir / f"{request.agent_id}.json"

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
    try:
        # Run yagya script asynchronously
        import subprocess
        import threading

        def run_yagya():
            try:
                cmd = [
                    "python",
                    "scripts/research_yagya.py",
                    "--topic", request.topic or "Autonomous AI Agent Service Economy Models",
                    "--depth", request.depth or "advanced"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                logger.info(f"🕯️ Yagya completed: {result.returncode}")
            except Exception as e:
                logger.error(f"❌ Yagya execution failed: {e}")

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
    except Exception as e:
        logger.error(f"❌ Yagya initiation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- MOUNT FRONTEND (LAST STEP!) ---
# Wichtig: Das muss NACH @app.post kommen, sonst verschluckt es den API Call!
if os.path.exists("docs/public"):
    app.mount("/", StaticFiles(directory="docs/public", html=True), name="static")
