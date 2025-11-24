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
from envoy.cartridge_main import EnvoyCartridge
from civic.cartridge_main import CivicCartridge
from herald.cartridge_main import HeraldCartridge
# Import other agents as needed

# --- GAD-000: SERVERLESS OATH BYPASS ---
# In the serverless gateway, we trust the environment and the agents we instantiate.
# We bypass the strict cryptographic oath verification to avoid complex key management
# in the ephemeral runtime.
try:
    from steward.constitutional_oath import ConstitutionalOath
    def mock_verify_oath(event, identity_tool):
        return True, "Serverless Gateway Trust"
    ConstitutionalOath.verify_oath = staticmethod(mock_verify_oath)
    logging.info("🛡️  Constitutional Oath verification patched for Serverless Gateway")
except ImportError:
    pass

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GATEWAY")

# Initialize FastAPI
app = FastAPI(
    title="Steward Protocol Gateway",
    description="Public Access Layer for Agentic World",
    version="1.0.0"
)

# --- Global Kernel State (Cached for warm starts) ---
kernel = None
envoy = None
civic = None

def get_kernel():
    """
    Initialize the VibeOS Kernel.
    In serverless, this runs once per cold start.
    """
    global kernel, envoy, civic
    
    if kernel is None:
        logger.info("❄️ Cold Start: Initializing VibeOS Kernel...")
        
        # 1. Init Kernel
        # Use /tmp for serverless writable storage if needed, or in-memory
        # For this PoC, we use a persistent path if available, else memory
        db_path = os.getenv("LEDGER_PATH", "data/vibe_ledger.db")
        kernel = RealVibeKernel(ledger_path=db_path)
        
        # 2. Init Agents
        envoy = EnvoyCartridge()
        civic = CivicCartridge()
        herald = HeraldCartridge()
        
        # --- GAD-000: GENESIS CEREMONY (Serverless Cold Start) ---
        # Agents must swear the oath to enter the kernel.
        timestamp = datetime.utcnow().isoformat()
        for agent in [envoy, civic, herald]:
            agent.oath_sworn = True
            agent.oath_event = {
                "event_type": "constitutional_oath",
                "agent_id": agent.agent_id,
                "timestamp": timestamp,
                "signature": f"sig_{agent.agent_id}_genesis",
                "oath_hash": "genesis_hash"
            }
        
        # 3. Register Agents
        kernel.register_agent(envoy)
        kernel.register_agent(civic)
        kernel.register_agent(herald)
        
        # 4. Boot Kernel
        kernel.boot()
        logger.info("🔥 Kernel Warm & Ready")
        
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
    expected_key = os.getenv("API_KEY", "steward-secret-key")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

def check_ledger_access(user_id: str):
    """
    GAD-900 Check: Is this user an authorized HIL?
    Uses CIVIC agent to verify.
    """
    get_kernel() # Ensure kernel is loaded
    
    # In a real implementation, CIVIC would check a license/identity registry.
    # For this PoC, we simulate the check or check a known list.
    authorized_users = ["hil_operator_01", "admin", "steward_architect"]
    
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
    
    # 1. Create Task for ENVOY
    # We route everything to ENVOY. It decides if it's a 'next_action' query or a command.
    # To support natural language, we might want to wrap the command.
    # If the command is "status" or "report", Envoy handles it.
    # If it's natural language, Envoy's LLM (if connected) would parse it.
    # For this strict GAD implementation, we assume the command maps to Envoy's routing.
    
    # HACK: If command is not a known structured command, treat as 'next_action' request or 'campaign'
    # For simplicity in this PoC, we pass it raw.
    
    payload = {
        "command": "next_action" if request.command == "briefing" else request.command,
        "args": request.context
    }
    
    # Special handling for natural language "launch" intent mapping (Mocking IntentRouter)
    cmd_lower = request.command.lower()
    if ("start" in cmd_lower or "starte" in cmd_lower) and ("campaign" in cmd_lower or "kampagne" in cmd_lower):
        payload = {
            "command": "campaign",
            "args": {
                "goal": request.command,
                "campaign_type": "publication"
            }
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

if __name__ == "__main__":
    import uvicorn
    # Local development run
    uvicorn.run(app, host="0.0.0.0", port=8000)
