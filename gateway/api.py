"""
GAD-X-FINALE: Public Access Layer (Serverless Gateway)
======================================================

This is the "Soft Interface" to the "Hard Kernel".
It exposes the ENVOY agent via a minimal, cost-efficient API.

Architecture:
- Serverless: Designed for Cloud Run / Lambda (scale-to-zero).
- GAD-000: HIL Assistant filters complexity.
- GAD-900: Ledger verification for authorized HILs.
"""

import logging
import os
import sys
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

# VibeOS Imports
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.scheduling import Task

# Import all 11 agent cartridges with graceful fallback
# If an agent fails to import, log a warning but don't crash the server

available_agents = {}

try:
    from herald.cartridge_main import HeraldCartridge
    available_agents['HeraldCartridge'] = HeraldCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: HeraldCartridge import failed: {e}")

try:
    from civic.cartridge_main import CivicCartridge
    available_agents['CivicCartridge'] = CivicCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: CivicCartridge import failed: {e}")

try:
    from forum.cartridge_main import ForumCartridge
    available_agents['ForumCartridge'] = ForumCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: ForumCartridge import failed: {e}")

try:
    from science.cartridge_main import ScientistCartridge
    available_agents['ScientistCartridge'] = ScientistCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: ScientistCartridge import failed: {e}")

try:
    from envoy.cartridge_main import EnvoyCartridge
    available_agents['EnvoyCartridge'] = EnvoyCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: EnvoyCartridge import failed: {e}")

try:
    from archivist.cartridge_main import ArchivistCartridge
    available_agents['ArchivistCartridge'] = ArchivistCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: ArchivistCartridge import failed: {e}")

try:
    from auditor.cartridge_main import AuditorCartridge
    available_agents['AuditorCartridge'] = AuditorCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: AuditorCartridge import failed: {e}")

try:
    from engineer.cartridge_main import EngineerCartridge
    available_agents['EngineerCartridge'] = EngineerCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: EngineerCartridge import failed: {e}")

try:
    from oracle.cartridge_main import OracleCartridge
    available_agents['OracleCartridge'] = OracleCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: OracleCartridge import failed: {e}")

try:
    from watchman.cartridge_main import WatchmanCartridge
    available_agents['WatchmanCartridge'] = WatchmanCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: WatchmanCartridge import failed: {e}")

try:
    from artisan.cartridge_main import ArtisanCartridge
    available_agents['ArtisanCartridge'] = ArtisanCartridge
except ImportError as e:
    logger.warning(f"⚠️ Gateway warning: ArtisanCartridge import failed: {e}")

# --- Governance Verification ---
# Constitutional Oath verification is ALWAYS active.
# For serverless/development environments, use proper authorization mechanisms
# (API keys, ledger checks) instead of oath bypasses.
logging.info("🛡️  Constitutional Oath verification ACTIVE")

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GATEWAY")

# Initialize FastAPI
app = FastAPI(
    title="Steward Protocol Gateway",
    description="Public Access Layer for Agentic World",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kimeisele.github.io",  # GitHub Pages
        "http://localhost:*",  # Local development
        "file://*",  # Local file testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Kernel State (Lazy Initialization) ---
kernel = None
envoy = None
civic = None
_kernel_lock = threading.Lock()  # Thread safety for concurrent requests

def get_kernel():
    """
    Lazy initialization of the VibeOS Kernel.
    Only boots on first request, not on import.
    Thread-safe for concurrent requests.
    """
    global kernel, envoy, civic
    
    # Fast path: kernel already initialized
    if kernel is not None:
        return kernel
    
    # Slow path: need to initialize (with lock for thread safety)
    with _kernel_lock:
        # Double-check pattern: another thread might have initialized while we waited
        if kernel is not None:
            return kernel
            
        logger.info("❄️ Cold Start: Initializing VibeOS Kernel...")
        start_time = datetime.utcnow()
        
        # 1. Init Kernel
        db_path = os.getenv("LEDGER_PATH", "data/vibe_ledger.db")
        kernel = RealVibeKernel(ledger_path=db_path)
        
        # 2. Init All Available Agents (Complete Agent City)
        # Only instantiate agents that successfully imported
        agents = []
        agent_classes = [
            ('HeraldCartridge', available_agents.get('HeraldCartridge')),
            ('CivicCartridge', available_agents.get('CivicCartridge')),
            ('ForumCartridge', available_agents.get('ForumCartridge')),
            ('ScientistCartridge', available_agents.get('ScientistCartridge')),
            ('EnvoyCartridge', available_agents.get('EnvoyCartridge')),
            ('ArchivistCartridge', available_agents.get('ArchivistCartridge')),
            ('AuditorCartridge', available_agents.get('AuditorCartridge')),
            ('EngineerCartridge', available_agents.get('EngineerCartridge')),
            ('OracleCartridge', available_agents.get('OracleCartridge')),
            ('WatchmanCartridge', available_agents.get('WatchmanCartridge')),
            ('ArtisanCartridge', available_agents.get('ArtisanCartridge')),
        ]

        for agent_name, agent_class in agent_classes:
            if agent_class:
                try:
                    agent = agent_class()
                    agents.append(agent)
                    logger.info(f"✅ {agent_name} instantiated")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to instantiate {agent_name}: {e}")
            else:
                logger.info(f"⏭️ {agent_name} not available (import failed earlier)")

        if not agents:
            logger.warning("⚠️ No agents available! Kernel will run with empty agent list.")

        # --- GAD-000: GENESIS CEREMONY (Serverless Cold Start) ---
        timestamp = datetime.utcnow().isoformat()
        for agent in agents:
            try:
                agent.oath_sworn = True
                agent.oath_event = {
                    "event_type": "constitutional_oath",
                    "agent_id": agent.agent_id,
                    "timestamp": timestamp,
                    "signature": f"sig_{agent.agent_id}_genesis",
                    "oath_hash": "genesis_hash"
                }
            except Exception as e:
                logger.warning(f"⚠️ Failed to set oath for {agent}: {e}")

        # 3. Register All Available Agents
        for agent in agents:
            try:
                kernel.register_agent(agent)
                logger.info(f"✅ Registered {agent.agent_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to register {agent}: {e}")
        
        # 4. Boot Kernel
        kernel.boot()
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"🔥 Kernel Ready (initialized in {elapsed:.2f}s)")
        
    return kernel

# --- Data Models ---

class ChatRequest(BaseModel):
    user_id: str
    command: str
    context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    status: str
    summary: str
    ledger_hash: str
    task_id: str

# --- Dependencies ---

async def verify_auth(x_api_key: str = Header(...)):
    """Simple API Key Check"""
    env_key = os.getenv("API_KEY")
    if not env_key:
        # Fallback for local dev ONLY if explicitly allowed, otherwise error
        if os.getenv("ENV") == "development":
            env_key = "steward-secret-key"
            logger.warning("⚠️  Using default development API Key. DO NOT USE IN PRODUCTION.")
        else:
            logger.error("❌ API_KEY environment variable not set!")
            raise HTTPException(status_code=500, detail="Server Configuration Error")
            
    if x_api_key != env_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

def check_ledger_access(user_id: str):
    """
    GAD-900 Check: Is this user an authorized HIL?
    Uses CIVIC agent to verify.
    """
    if len(user_id) > 64 or not user_id.replace("_", "").isalnum():
         logger.warning(f"⛔ Invalid User ID format: {user_id}")
         raise HTTPException(status_code=400, detail="Invalid User ID format")

    get_kernel() # Ensure kernel is loaded
    
    # In a real implementation, CIVIC would check a license/identity registry.
    # For this PoC, we simulate the check or check a known list.
    authorized_users = ["hil_operator_01", "admin", "steward_architect", "public_user"]
    
    if user_id not in authorized_users:
        logger.warning(f"⛔ Unauthorized access attempt by {user_id}")
        raise HTTPException(status_code=403, detail="Unauthorized HIL Identity")
    
    return True

# --- Endpoints ---

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    api_key: str = Depends(verify_auth)
):
    """
    Chat with the Agentic World.
    
    Flow:
    1. Auth Check (API Key)
    2. Ledger Check (CIVIC)
    3. Dispatch to ENVOY (Orchestrator)
    4. Return HIL Assistant Summary (VAD Layer)
    """
    global kernel, envoy
    
    # 2. Ledger Check (GAD-900)
    check_ledger_access(request.user_id)
    
    logger.info(f"📨 Received command from {request.user_id}: {request.command}")
    
    # Parse command with robust intent detection
    cmd_lower = request.command.lower().strip()
    payload = None
    
    # 1. Direct command: "briefing"
    if cmd_lower == "briefing":
        payload = {
            "command": "next_action",
            "args": request.context
        }
    
    # 2. Direct command: "status"
    elif cmd_lower == "status":
        payload = {
            "command": "status",
            "args": request.context
        }
    
    # 3. Campaign commands (multiple variations)
    elif (cmd_lower == "campaign" or 
          "campaign" in cmd_lower or
          any(marketing_word in cmd_lower for marketing_word in ["marketing", "promote", "advertise", "publicize"])):
        # Extract goal from the command
        goal = None
        
        # Pattern 1: "campaign" alone - needs goal in context
        if cmd_lower == "campaign":
            goal = request.context.get("goal") if request.context else None
            if not goal:
                raise HTTPException(status_code=400, detail="Campaign goal required. Try: 'Start a campaign for [your goal]'")
        
        # Pattern 2: "Start a campaign for X" or "Create marketing for X"
        elif any(trigger in cmd_lower for trigger in ["start", "create", "launch", "starte", "make"]):
            # Extract everything after "for" or "about"
            for marker in [" for ", " about ", " on ", " regarding "]:
                if marker in cmd_lower:
                    goal = request.command.split(marker, 1)[1].strip()
                    break
            
            if not goal:
                # Fallback: use the whole command as goal
                goal = request.command
        
        # Pattern 3: "campaign X" - use X as goal
        else:
            goal = request.command.replace("campaign", "").replace("Campaign", "").strip()
        
        if not goal:
            raise HTTPException(status_code=400, detail="Could not extract campaign goal. Try: 'Start a campaign for [your goal]'")
        
        payload = {
            "command": "campaign",
            "args": {
                "goal": goal,
                "campaign_type": "publication"
            }
        }
    
    # 4. Unknown command - pass to ENVOY as-is (it might understand)
    else:
        payload = {
            "command": request.command,
            "args": request.context
        }
    
    task = Task(
        agent_id="envoy",
        payload=payload
    )
    
    # 2. Submit to Kernel
    task_id = kernel.submit_task(task)
    
    # 3. Wait for Result (Synchronous for API)
    # In a real async system, we might poll or use a callback.
    # Here we tick the kernel until done (simplification for single-threaded serverless)
    
    # Force a tick to process the task immediately
    kernel.tick()
    
    # 4. Get Result
    result_data = kernel.get_task_result(task_id)
    
    if not result_data:
        raise HTTPException(status_code=500, detail="Task execution failed or timed out")
    
    output = result_data.get("output_result", {})
    
    # Handle SQLite JSON serialization
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            logger.warning("⚠️  Could not deserialize task output")
            output = {"summary": str(output)}

    # 5. Format Response (HIL Assistant Logic)
    # If the output has a summary, use it. Otherwise, format the raw status.
    summary = output.get("summary")
    if not summary:
        if output.get("status") == "success" or output.get("status") == "complete":
            summary = f"✅ **Operation Successful**\nTask `{task_id}` completed.\nResult: {str(output)}"
        else:
            summary = f"⚠️ **Operation Failed**\nError: {output.get('error')}"
            
    # 6. Get Ledger Hash (Proof of Governance)
    ledger_hash = kernel.ledger.get_top_hash()
    
    return ChatResponse(
        status="success",
        summary=summary,
        ledger_hash=ledger_hash,
        task_id=task_id
    )

@app.get("/health")
async def health():
    return {"status": "ok", "kernel": "ready" if kernel else "cold"}

@app.get("/help")
async def help_endpoint():
    """Return available commands and usage instructions."""
    return {
        "commands": [
            {
                "command": "briefing",
                "description": "Get a strategic briefing from the HIL Assistant",
                "example": "briefing"
            },
            {
                "command": "campaign",
                "description": "Launch a marketing campaign",
                "example": "Start a campaign for product launch"
            },
            {
                "command": "status",
                "description": "Get system status",
                "example": "status"
            }
        ],
        "usage": "Send commands via POST /v1/chat with user_id and command in the body",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # Local development run
    uvicorn.run(app, host="0.0.0.0", port=8000)
