"""
MOLTBOOK GATEWAY ROUTES — Platform Bridge Endpoints
=====================================================

FastAPI router for Moltbook integration.
Mounted as /api/moltbook/* in the main gateway.

Provides:
- Status and health check for the Moltbook bridge
- Post creation (delegates content to the engine, sends to Moltbook)
- Feed reading (ingests from Moltbook into local analysis)
- Heartbeat trigger (manual or cron-triggered cycle)
- Submolt management

SECURITY:
- All endpoints require the internal API key (X-Api-Key header)
- Moltbook API key is read from MOLTBOOK_API_KEY env var
- No Moltbook credentials are exposed through any endpoint
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x3c8f91ab"  # GenesisByte: moltbook gateway bridge

import logging
import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("MOLTBOOK_GATEWAY")

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(prefix="/api/moltbook", tags=["moltbook"])

# =============================================================================
# LAZY BRIDGE SINGLETON
# =============================================================================

_bridge = None


def _get_bridge():
    """Lazy-init the MoltbookBridge singleton."""
    global _bridge
    if _bridge is None:
        from vibe_core.mahamantra.adapters.moltbook import MoltbookBridge

        _bridge = MoltbookBridge(
            api_key=os.getenv("MOLTBOOK_API_KEY", ""),
            agent_name=os.getenv("MOLTBOOK_AGENT_NAME", "steward-protocol"),
        )
    return _bridge


# =============================================================================
# AUTH HELPER
# =============================================================================


def _verify_internal_key(x_api_key: Optional[str]) -> None:
    """Verify internal API key. Raises HTTPException if invalid."""
    api_key = os.getenv("VIBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Service misconfigured: API key not set")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# =============================================================================
# REQUEST MODELS
# =============================================================================


class CreatePostRequest(BaseModel):
    submolt: str = Field(..., max_length=64, description="Target submolt name")
    title: str = Field(..., min_length=1, max_length=300, description="Post title")
    content: str = Field(..., min_length=1, max_length=10000, description="Post content (markdown)")


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Comment text")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for nested replies")


class CreateSubmoltRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=10, max_length=500)


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get("/status")
def moltbook_status(x_api_key: Optional[str] = Header(None)):
    """
    GET /api/moltbook/status
    Bridge status: auth state, rate limits, last activity.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()
    return {
        "status": "online",
        "bridge": bridge.get_status(),
        "moltbook_configured": bridge.is_authenticated,
    }


@router.post("/heartbeat")
def moltbook_heartbeat(x_api_key: Optional[str] = Header(None)):
    """
    POST /api/moltbook/heartbeat
    Trigger a heartbeat cycle: verify auth, read feed, report status.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(
            status_code=503,
            detail="Moltbook API key not configured. Set MOLTBOOK_API_KEY env var.",
        )

    result = bridge.heartbeat_cycle()
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "heartbeat": result.data}


@router.get("/feed")
def moltbook_feed(
    sort: str = Query("hot", regex="^(hot|new|top|rising)$"),
    limit: int = Query(25, ge=1, le=100),
    x_api_key: Optional[str] = Header(None),
):
    """
    GET /api/moltbook/feed
    Read the Moltbook feed. Returns posts for local analysis.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.get_feed(sort=sort, limit=limit)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "data": result.data}


@router.get("/submolt/{submolt}/feed")
def moltbook_submolt_feed(
    submolt: str,
    sort: str = Query("hot", regex="^(hot|new|top|rising)$"),
    limit: int = Query(25, ge=1, le=100),
    x_api_key: Optional[str] = Header(None),
):
    """
    GET /api/moltbook/submolt/{submolt}/feed
    Read a specific submolt's feed.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.get_submolt_feed(submolt, sort=sort, limit=limit)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "submolt": submolt, "data": result.data}


@router.post("/post")
def moltbook_create_post(
    body: CreatePostRequest,
    x_api_key: Optional[str] = Header(None),
):
    """
    POST /api/moltbook/post
    Create a post on Moltbook. Subject to 30min cooldown.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.create_post(submolt=body.submolt, title=body.title, content=body.content)
    if not result.success:
        status_code = 429 if "cooldown" in (result.error or "").lower() else 502
        raise HTTPException(status_code=status_code, detail=result.error)

    return {"status": "success", "data": result.data}


@router.post("/post/{post_id}/comment")
def moltbook_create_comment(
    post_id: str,
    body: CreateCommentRequest,
    x_api_key: Optional[str] = Header(None),
):
    """
    POST /api/moltbook/post/{post_id}/comment
    Comment on a Moltbook post.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.create_comment(post_id=post_id, content=body.content, parent_id=body.parent_id)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "data": result.data}


@router.post("/submolt")
def moltbook_create_submolt(
    body: CreateSubmoltRequest,
    x_api_key: Optional[str] = Header(None),
):
    """
    POST /api/moltbook/submolt
    Create a new submolt community.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.create_submolt(
        name=body.name,
        display_name=body.display_name,
        description=body.description,
    )
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "data": result.data}


@router.get("/search")
def moltbook_search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(25, ge=1, le=100),
    x_api_key: Optional[str] = Header(None),
):
    """
    GET /api/moltbook/search
    Search Moltbook for posts, agents, and submolts.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.search(query=q, limit=limit)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "query": q, "data": result.data}


@router.post("/post/{post_id}/upvote")
def moltbook_upvote(
    post_id: str,
    x_api_key: Optional[str] = Header(None),
):
    """
    POST /api/moltbook/post/{post_id}/upvote
    Upvote a post on Moltbook.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.upvote_post(post_id)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "post_id": post_id}


@router.post("/submolt/{submolt}/subscribe")
def moltbook_subscribe(
    submolt: str,
    x_api_key: Optional[str] = Header(None),
):
    """
    POST /api/moltbook/submolt/{submolt}/subscribe
    Subscribe to a submolt.
    """
    _verify_internal_key(x_api_key)
    bridge = _get_bridge()

    if not bridge.is_authenticated:
        raise HTTPException(status_code=503, detail="Moltbook API key not configured.")

    result = bridge.subscribe_submolt(submolt)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {"status": "success", "submolt": submolt}
