
import logging
import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

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

# --- DATA MODEL ---
class SignedChatRequest(BaseModel):
    message: str
    agent_id: str
    signature: str
    public_key: str
    timestamp: int

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

# --- MOUNT FRONTEND (LAST STEP!) ---
# Wichtig: Das muss NACH @app.post kommen, sonst verschluckt es den API Call!
if os.path.exists("docs/public"):
    app.mount("/", StaticFiles(directory="docs/public", html=True), name="static")
