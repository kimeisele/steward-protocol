"""
MOLTBOOK ADAPTER — Sovereign Bridge to the Agent Internet
===========================================================

"yānti deva-vratā devān pitṝn yānti pitṛ-vratāḥ"
"Those who worship the demigods will go to the demigods."
— Bhagavad Gita 9.25

REST client for Moltbook (moltbook.com/api/v1).
Implements MoltbookProtocol with:
- Bearer token authentication
- Rate limit tracking via response headers
- Exponential backoff retry on network errors
- No external dependencies beyond requests (already in pyproject.toml)

USAGE:
    from vibe_core.mahamantra.adapters import MoltbookBridge

    bridge = MoltbookBridge(api_key="moltbook_xxx", agent_name="steward")
    result = bridge.get_feed(sort="hot", limit=10)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # The Divine Messenger — delivers across worlds
__position__ = 3
__genesis__ = "0x7a2e1f0b"  # GenesisByte: moltbook integration layer

import logging
import os
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.protocols.moltbook import (
    MOLTBOOK_HEARTBEAT_HOURS,
    MOLTBOOK_MAX_POST_INTERVAL_MIN,
    MOLTBOOK_RATE_LIMIT_WINDOW,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookCredentials,
    MoltbookFeed,
    MoltbookPost,
    MoltbookProtocol,
    MoltbookRateLimitStatus,
    MoltbookResult,
    MoltbookSubmolt,
)

logger = logging.getLogger("MOLTBOOK_BRIDGE")

# =============================================================================
# CONSTANTS
# =============================================================================

_BASE_URL = "https://www.moltbook.com/api/v1"
_MAX_RETRIES = 4
_INITIAL_BACKOFF_S = 2  # 2s, 4s, 8s, 16s exponential


# =============================================================================
# IMPLEMENTATION
# =============================================================================


class MoltbookBridge:
    """
    Sovereign bridge to Moltbook — the agent internet.

    This adapter wraps the Moltbook REST API with proper:
    - Authentication (Bearer token)
    - Rate limit awareness (tracks X-RateLimit-* headers)
    - Retry with exponential backoff on transient failures
    - Clean error handling (never raises, always returns MoltbookResult)

    The bridge is stateless except for credentials and rate limit tracking.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "moltbook_bridge"

    def __init__(
        self,
        api_key: Optional[str] = None,
        agent_name: str = "steward-protocol",
        base_url: str = _BASE_URL,
    ):
        self._api_key = api_key or os.getenv("MOLTBOOK_API_KEY", "")
        self._agent_name = agent_name
        self._base_url = base_url.rstrip("/")
        self._rate_limit = MoltbookRateLimitStatus()
        self._last_post_time: float = 0.0
        self._session: Optional[Any] = None  # lazy requests.Session

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================

    def _get_session(self) -> Any:
        """Lazy-init requests.Session with auth headers."""
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {
                    "Content-Type": "application/json",
                    "User-Agent": f"StewardProtocol/1.0 ({self._agent_name})",
                }
            )
            if self._api_key:
                self._session.headers["Authorization"] = f"Bearer {self._api_key}"
        return self._session

    # =========================================================================
    # HTTP LAYER (with retry + rate limit tracking)
    # =========================================================================

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> MoltbookResult:
        """
        Execute HTTP request with retry and rate limit tracking.

        Returns MoltbookResult — never raises.
        """
        import requests

        url = f"{self._base_url}{path}"
        session = self._get_session()

        for attempt in range(_MAX_RETRIES):
            try:
                response = session.request(
                    method,
                    url,
                    json=json_body,
                    params=params,
                    timeout=30,
                )

                # Track rate limits from headers
                rate_limit = self._parse_rate_limit_headers(response.headers)
                self._rate_limit = rate_limit

                # Handle response
                if response.status_code == 429:
                    reset_at = rate_limit.reset_at
                    wait = max(1, reset_at - int(time.time())) if reset_at else 60
                    logger.warning(f"MOLTBOOK: Rate limited. Waiting {wait}s.")
                    return MoltbookResult(
                        success=False,
                        error=f"Rate limited. Reset in {wait}s.",
                        rate_limit=rate_limit,
                    )

                if response.status_code >= 400:
                    error_detail = response.text[:500]
                    logger.warning(f"MOLTBOOK: {method} {path} → {response.status_code}: {error_detail}")
                    return MoltbookResult(
                        success=False,
                        error=f"HTTP {response.status_code}: {error_detail}",
                        rate_limit=rate_limit,
                    )

                data = response.json() if response.text else {}
                return MoltbookResult(success=True, data=data, rate_limit=rate_limit)

            except requests.ConnectionError as e:
                backoff = _INITIAL_BACKOFF_S * (2**attempt)
                logger.warning(
                    f"MOLTBOOK: Connection error (attempt {attempt + 1}/{_MAX_RETRIES}). "
                    f"Retrying in {backoff}s. Error: {e}"
                )
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(backoff)
                else:
                    return MoltbookResult(
                        success=False,
                        error=f"Connection failed after {_MAX_RETRIES} attempts: {e}",
                    )
            except requests.Timeout:
                backoff = _INITIAL_BACKOFF_S * (2**attempt)
                logger.warning(f"MOLTBOOK: Timeout (attempt {attempt + 1}/{_MAX_RETRIES}). Retrying in {backoff}s.")
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(backoff)
                else:
                    return MoltbookResult(
                        success=False,
                        error=f"Timeout after {_MAX_RETRIES} attempts",
                    )
            except Exception as e:
                logger.error(f"MOLTBOOK: Unexpected error: {e}")
                return MoltbookResult(success=False, error=str(e))

        return MoltbookResult(success=False, error="Exhausted retries")

    @staticmethod
    def _parse_rate_limit_headers(
        headers: Any,
    ) -> MoltbookRateLimitStatus:
        """Extract rate limit info from X-RateLimit-* headers."""
        return MoltbookRateLimitStatus(
            limit=int(headers.get("X-RateLimit-Limit", 0)),
            remaining=int(headers.get("X-RateLimit-Remaining", 0)),
            reset_at=int(headers.get("X-RateLimit-Reset", 0)),
        )

    # =========================================================================
    # PROTOCOL IMPLEMENTATION
    # =========================================================================

    def register_agent(self, name: str, description: str) -> MoltbookResult:
        """Register a new agent on Moltbook."""
        return self._request(
            "POST",
            "/agents/register",
            json_body={"name": name, "description": description},
        )

    def get_profile(self) -> MoltbookResult:
        """Get the authenticated agent's profile."""
        return self._request("GET", "/agents/me")

    def create_post(self, submolt: str, title: str, content: str) -> MoltbookResult:
        """
        Create a text post in a submolt.
        Enforces minimum interval between posts (30min).
        """
        now = time.time()
        elapsed_min = (now - self._last_post_time) / 60.0
        if self._last_post_time > 0 and elapsed_min < MOLTBOOK_MAX_POST_INTERVAL_MIN:
            wait_min = MOLTBOOK_MAX_POST_INTERVAL_MIN - elapsed_min
            return MoltbookResult(
                success=False,
                error=f"Post cooldown: wait {wait_min:.1f} more minutes.",
            )

        result = self._request(
            "POST",
            "/posts",
            json_body={
                "submolt": submolt,
                "title": title,
                "content": content,
            },
        )
        if result.success:
            self._last_post_time = now
        return result

    def create_comment(self, post_id: str, content: str, *, parent_id: Optional[str] = None) -> MoltbookResult:
        """Comment on a post. Use parent_id for nested replies."""
        body: Dict[str, str] = {"content": content}
        if parent_id:
            body["parent_id"] = parent_id
        return self._request("POST", f"/posts/{post_id}/comments", json_body=body)

    def get_feed(self, *, sort: str = "hot", limit: int = 25) -> MoltbookResult:
        """Get personalized feed."""
        return self._request("GET", "/feed", params={"sort": sort, "limit": limit})

    def get_submolt_feed(self, submolt: str, *, sort: str = "hot", limit: int = 25) -> MoltbookResult:
        """Get feed for a specific submolt."""
        return self._request(
            "GET",
            f"/submolts/{submolt}/posts",
            params={"sort": sort, "limit": limit},
        )

    def search(self, query: str, *, limit: int = 25) -> MoltbookResult:
        """Search posts, agents, and submolts."""
        return self._request("GET", "/search", params={"q": query, "limit": limit})

    def upvote_post(self, post_id: str) -> MoltbookResult:
        """Upvote a post."""
        return self._request("POST", f"/posts/{post_id}/upvote")

    def create_submolt(self, name: str, display_name: str, description: str) -> MoltbookResult:
        """Create a new submolt community."""
        return self._request(
            "POST",
            "/submolts",
            json_body={
                "name": name,
                "display_name": display_name,
                "description": description,
            },
        )

    def subscribe_submolt(self, submolt: str) -> MoltbookResult:
        """Subscribe to a submolt."""
        return self._request("POST", f"/submolts/{submolt}/subscribe")

    def follow_agent(self, agent_name: str) -> MoltbookResult:
        """Follow another agent."""
        return self._request("POST", f"/agents/{agent_name}/follow")

    def get_post_comments(self, post_id: str, *, sort: str = "top") -> MoltbookResult:
        """Get comments on a post."""
        return self._request("GET", f"/posts/{post_id}/comments", params={"sort": sort})

    # =========================================================================
    # HEARTBEAT CYCLE
    # =========================================================================

    def heartbeat_cycle(self) -> MoltbookResult:
        """
        Execute one heartbeat cycle.

        1. Check profile (verify auth)
        2. Read feed
        3. Return aggregated status

        Called every MOLTBOOK_HEARTBEAT_HOURS hours.
        Content generation and engagement logic is handled by
        the gateway layer — the adapter only provides the transport.
        """
        profile_result = self.get_profile()
        if not profile_result.success:
            return MoltbookResult(
                success=False,
                error=f"Heartbeat auth check failed: {profile_result.error}",
            )

        feed_result = self.get_feed(sort="hot", limit=10)

        return MoltbookResult(
            success=True,
            data={
                "profile": profile_result.data,
                "feed_loaded": feed_result.success,
                "feed_count": len((feed_result.data or {}).get("posts", [])) if feed_result.data else 0,
                "rate_limit": asdict(self._rate_limit),
                "heartbeat_interval_hours": MOLTBOOK_HEARTBEAT_HOURS,
            },
        )

    # =========================================================================
    # STATUS
    # =========================================================================

    @property
    def rate_limit_status(self) -> MoltbookRateLimitStatus:
        """Current rate limit status."""
        return self._rate_limit

    @property
    def is_authenticated(self) -> bool:
        """Whether an API key is configured."""
        return bool(self._api_key)

    def get_status(self) -> Dict[str, object]:
        """Get bridge status for monitoring."""
        return {
            "authenticated": self.is_authenticated,
            "agent_name": self._agent_name,
            "base_url": self._base_url,
            "rate_limit": asdict(self._rate_limit),
            "last_post_time": self._last_post_time,
        }


# =============================================================================
# FACTORY
# =============================================================================


def create_moltbook_bridge(
    api_key: Optional[str] = None,
    agent_name: str = "steward-protocol",
) -> MoltbookBridge:
    """Create a MoltbookBridge instance."""
    return MoltbookBridge(api_key=api_key, agent_name=agent_name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MoltbookBridge",
    "create_moltbook_bridge",
]
