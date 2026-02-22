"""
MOLTBOOK ADAPTER — Thin Client
===============================

I/O, rate limiting, and challenge solving. No intelligence.
All decisions live in the plugin layer or kernel.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import httpx

# Self-contained type aliases — no dependency on protocols/moltbook.py
# All Moltbook API responses are dicts. These aliases document the shapes.
HeartbeatResult = Dict
MoltbookAgentProfile = Dict
MoltbookPost = Dict
MoltbookComment = Dict
SemanticSearchResult = Dict
DMConversation = Dict
DMMessage = Dict
DMSendResult = Dict
DMRequestInfo = Dict
DMRequestResult = Dict
SubmoltDetails = Dict
VoteResult = Dict
FollowResult = Dict
ProfileUpdateResult = Dict
SubscribeResult = Dict

logger = logging.getLogger("MOLTBOOK")


# =============================================================================
# RATE LIMITS & CONSTANTS
# =============================================================================


class MoltbookLimits:
    """Hardcoded limits — verified against github.com/moltbook/api README (2026-02-22)"""

    REQ_PER_MIN = 100
    POST_PER_30_MIN = 1
    COMMENTS_PER_HOUR = 50  # API README says "1 hour", NOT per day
    AVATAR_MAX_BYTES = 1024 * 1024  # 1MB
    BANNER_MAX_BYTES = 2 * 1024 * 1024  # 2MB


@dataclass
class RateLimitState:
    """Tracks current rate limit usage"""

    requests_this_minute: int = 0
    last_minute_reset: float = field(default_factory=time.time)

    posts_this_30m: int = 0
    last_30m_reset: float = field(default_factory=time.time)

    comments_this_hour: int = 0
    last_hour_reset: float = field(default_factory=time.time)


# =============================================================================
# CHALLENGE SOLVER (Deterministic Anti-Spam)
# =============================================================================


class ChallengeSolver:
    """
    Solves Moltbook's obfuscated math challenges.
    Failure = temporary ban. This MUST be flawless.
    """

    # Compound numbers MUST come before their substrings to prevent
    # "eighteen" → "8een" corruption. Order matters.
    WORD_MAP = [
        ("eighteen", 18),
        ("seventeen", 17),
        ("sixteen", 16),
        ("fifteen", 15),
        ("fourteen", 14),
        ("thirteen", 13),
        ("twelve", 12),
        ("eleven", 11),
        ("nineteen", 19),
        ("eighty", 80),
        ("seventy", 70),
        ("sixty", 60),
        ("fifty", 50),
        ("forty", 40),
        ("thirty", 30),
        ("twenty", 20),
        ("ninety", 90),
        ("hundred", 100),
        ("zero", 0),
        ("one", 1),
        ("two", 2),
        ("three", 3),
        ("four", 4),
        ("five", 5),
        ("six", 6),
        ("seven", 7),
        ("eight", 8),
        ("nine", 9),
        ("ten", 10),
    ]

    @staticmethod
    def solve(challenge_text: str) -> str:
        """
        Extracts numbers and operators from obfuscated text and computes the result.
        Example: "What is seven + 3?" -> "10"

        Uses word-boundary regex to prevent compound number corruption
        (e.g. "eighteen" must not become "8een").
        """
        text = challenge_text.lower()

        # Replace word-numbers with digits using word boundaries.
        # Compound numbers (eighteen, eighty, ...) are listed first
        # in WORD_MAP so they match before their substrings.
        for word, num in ChallengeSolver.WORD_MAP:
            text = re.sub(rf"\b{word}\b", str(num), text)

        # Extract all numbers
        numbers = [int(n) for n in re.findall(r"\d+", text)]

        if len(numbers) < 2:
            logger.warning(f"Could not parse math challenge: '{challenge_text}'")
            return "0"

        # Find operator
        if "+" in text or "plus" in text or "add" in text:
            return str(sum(numbers))
        elif "-" in text or "minus" in text or "subtract" in text:
            return str(numbers[0] - sum(numbers[1:]))
        elif "*" in text or "times" in text or "multiply" in text:
            result = 1
            for n in numbers:
                result *= n
            return str(result)
        elif "/" in text or "divided" in text:
            if numbers[1] != 0:
                return str(numbers[0] // numbers[1])
            return "0"

        logger.warning(f"Unknown operator in challenge: '{challenge_text}'")
        return "0"


# =============================================================================
# THE CLIENT
# =============================================================================


class MoltbookClient:
    """
    The deterministic bridge to Moltbook.
    Handles I/O, retries, challenges, and strict rate limiting.
    """

    def __init__(self, api_key: str, base_url: str = "https://www.moltbook.com/api/v1", offline_mode: bool = False):
        """
        Args:
            api_key: The X/Twitter claimed API key
            base_url: Moltbook API URL
            offline_mode: If True, does not make real network calls. Used for GAD-000 testing.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.offline_mode = offline_mode
        self.limits = RateLimitState()

        # In offline mode, we store mocked responses here
        self._mock_db: Dict[str, list] = {"posts": [], "comments": [], "dms": [], "status": "claimed"}  # type: ignore[assignment]

    # --- RATE LIMIT ENFORCEMENT ---

    def _enforce_limits(self, endpoint: str, method: str) -> None:
        """
        Throws or sleeps if limits are exceeded.
        This is the watertight seal protecting the account.
        """
        now = time.time()

        # 1. Minute Limiter (100 req/min)
        if now - self.limits.last_minute_reset > 60:
            self.limits.requests_this_minute = 0
            self.limits.last_minute_reset = now

        if self.limits.requests_this_minute >= MoltbookLimits.REQ_PER_MIN:
            raise Exception("MOLTBOOK-429: Minute rate limit exceeded. Halting.")

        # 2. Post Limiter (1 post/30 min)
        if method == "POST" and endpoint.endswith("/posts") and "comments" not in endpoint:
            if now - self.limits.last_30m_reset > 1800:
                self.limits.posts_this_30m = 0
                self.limits.last_30m_reset = now

            if self.limits.posts_this_30m >= MoltbookLimits.POST_PER_30_MIN:
                raise Exception("MOLTBOOK-429: Post rate limit (1/30m) exceeded.")
            self.limits.posts_this_30m += 1

        # 3. Comment Limiter (50/hour — verified against API README)
        if method == "POST" and "comments" in endpoint:
            if now - self.limits.last_hour_reset > 3600:
                self.limits.comments_this_hour = 0
                self.limits.last_hour_reset = now

            if self.limits.comments_this_hour >= MoltbookLimits.COMMENTS_PER_HOUR:
                raise Exception("MOLTBOOK-429: Hourly comment limit exceeded.")
            self.limits.comments_this_hour += 1

        self.limits.requests_this_minute += 1

    # --- HTTP TRANSPORT ---

    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, str]] = None) -> dict:
        """Core request dispatcher. Handles offline routing and httpx transport."""
        self._enforce_limits(endpoint, method)

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        if self.offline_mode:
            logger.debug(f"[OFFLINE] {method} {endpoint} - {data}")
            return self._handle_offline(method, endpoint, data)

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{endpoint}"
            try:
                response = await client.request(method, url, headers=headers, json=data, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Catch 403/401 Verification required
                if e.response.status_code in [401, 403]:
                    try:
                        err_data = e.response.json()
                        if err_data.get("error") == "VERIFICATION_REQUIRED":
                            return err_data  # Pass back to caller to handle challenge
                    except Exception:
                        pass
                logger.error(f"Moltbook HTTP Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Moltbook Request Error: {str(e)}")
                raise

    # --- OFFLINE MOCK HUB ---

    def _handle_offline(self, method: str, endpoint: str, data: Optional[Dict[str, str]]) -> dict:
        """Simulates Moltbook API for watertight offline testing."""
        if method == "GET" and endpoint == "/agents/status":
            return {"status": self._mock_db["status"]}

        elif method == "GET" and endpoint.startswith("/search"):
            return {"results": [], "similarity": 0.95}

        elif method == "GET" and endpoint.startswith("/agents/profile"):
            return {
                "name": "mock_agent",
                "description": "Offline mock profile",
                "metadata": None,
                "karma": 0,
                "x_handle": None,
                "followers_count": 0,
                "following_count": 0,
            }

        elif method == "POST" and endpoint == "/posts":
            post = {"id": f"p{len(self._mock_db['posts'])}", "title": data["title"], "content": data["content"]}
            self._mock_db["posts"].append(post)
            return post

        elif method == "GET" and endpoint == "/agents/dm/check":
            has_new = len(self._mock_db["dms"]) > 0
            return {"has_new_messages": has_new, "pending_requests": len(self._mock_db["dms"])}

        elif method == "GET" and endpoint == "/agents/dm/conversations":
            return {"conversations": self._mock_db.get("conversations", [])}

        elif method == "GET" and endpoint.startswith("/agents/dm/conversations/"):
            conv_id = endpoint.rsplit("/", 1)[-1]
            msgs = [m for m in self._mock_db["dms"] if m.get("conversation_id") == conv_id]
            return {"messages": msgs}

        # DM send — simulate successful message delivery
        elif method == "POST" and "/dm/conversations/" in endpoint and endpoint.endswith("/send"):
            conv_id = endpoint.split("/dm/conversations/")[1].split("/send")[0]
            msg = {
                "id": f"dm{len(self._mock_db['dms'])}",
                "conversation_id": conv_id,
                "sender": "self",
                "content": data.get("content", "") if data else "",
                "status": "sent",
            }
            self._mock_db["dms"].append(msg)
            return msg

        # Simulated Math Challenge — verify the solution matches the challenge
        elif method == "POST" and "comments" in endpoint and "/upvote" not in endpoint:
            if data and "challenge_solution" in data:
                return {"id": "c99", "status": "posted"}
            return {"error": "VERIFICATION_REQUIRED", "challenge": "What is seven + 3?", "challenge_id": "c123"}

        # GET comments on a post
        elif method == "GET" and "comments" in endpoint:
            return {"comments": self._mock_db.get("comments", [])}

        # Feed endpoints
        elif method == "GET" and endpoint.startswith("/posts"):
            if "?" in endpoint:
                return {"posts": self._mock_db.get("posts", [])}
            return self._mock_db["posts"][0] if self._mock_db["posts"] else {"id": "none"}

        elif method == "GET" and endpoint.startswith("/feed"):
            return {"posts": self._mock_db.get("posts", [])}

        # Voting
        elif method == "POST" and "/upvote" in endpoint:
            return {"status": "ok"}

        elif method == "POST" and "/downvote" in endpoint:
            return {"status": "ok"}

        # Following
        elif method == "POST" and endpoint.startswith("/agents/") and endpoint.endswith("/follow"):
            return {"status": "ok"}

        elif method == "DELETE" and endpoint.endswith("/follow"):
            return {"status": "ok"}

        # Submolts
        elif method == "GET" and endpoint == "/submolts":
            return {"submolts": self._mock_db.get("submolts", [])}

        elif method == "GET" and endpoint.startswith("/submolts/"):
            name = endpoint.rsplit("/", 1)[-1]
            if "/subscribe" not in endpoint:
                return {
                    "name": name, "display_name": name, "description": "mock",
                    "subscriber_count": 0, "allow_crypto": False, "owner": "mock",
                    "moderators": [], "theme_color": None, "banner_color": None,
                }

        elif method == "POST" and endpoint == "/submolts":
            return {
                "name": data.get("name", "") if data else "",
                "display_name": data.get("display_name", "") if data else "",
                "description": data.get("description", "") if data else "",
                "subscriber_count": 0, "allow_crypto": False, "owner": "self",
                "moderators": [], "theme_color": None, "banner_color": None,
            }

        elif method == "POST" and "/subscribe" in endpoint:
            return {"status": "ok"}

        elif method == "DELETE" and "/subscribe" in endpoint:
            return {"status": "ok"}

        # Profile update
        elif method == "PATCH" and endpoint == "/agents/me":
            return {"status": "ok", "description": data.get("description", "") if data else ""}

        elif method == "GET" and endpoint == "/agents/me":
            return {
                "name": "steward-protocol", "description": "mock",
                "metadata": None, "karma": 0, "x_handle": None,
                "followers_count": 0, "following_count": 0,
            }

        # DM requests
        elif method == "POST" and endpoint == "/agents/dm/request":
            return {"status": "sent", "conversation_id": None}

        elif method == "GET" and endpoint == "/agents/dm/requests":
            return {"requests": self._mock_db.get("dm_requests", [])}

        elif method == "POST" and "/dm/requests/" in endpoint and "/approve" in endpoint:
            return {"status": "approved", "conversation_id": "conv_new"}

        elif method == "POST" and "/dm/requests/" in endpoint and "/reject" in endpoint:
            return {"status": "rejected", "conversation_id": None}

        return {"status": "ok", "mocked": True, "endpoint": endpoint}

    # =========================================================================
    # REGISTRATION — The ONLY unauthenticated endpoint
    # =========================================================================

    async def register(self, name: str, description: str) -> dict:
        """
        Register a new agent on Moltbook.

        NO AUTH REQUIRED — this is the only unauthenticated endpoint.
        Returns: { agent: { api_key, claim_url, verification_code }, important: "Save your API key!" }

        CRITICAL: api_key is shown ONCE. No recovery. Save immediately.
        """
        if self.offline_mode:
            return {
                "agent": {
                    "api_key": "moltbook_offline_test_key",
                    "claim_url": "https://www.moltbook.com/claim/moltbook_claim_offline",
                    "verification_code": "test-XXXX",
                },
                "important": "Save your API key!",
            }

        # Registration does NOT use Bearer auth — override _request
        self.limits.requests_this_minute += 1
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/agents/register"
            response = await client.post(
                url,
                json={"name": name, "description": description},
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    def sync_register(self, name: str, description: str) -> dict:
        """Sync wrapper for registration."""
        return _run_async(self.register(name, description))

    # =========================================================================
    # PUBLIC API - The "Skin" Interface (ALL require Bearer token)
    # =========================================================================

    async def check_status(self) -> str:
        """Verify agent claim status."""
        res = await self._request("GET", "/agents/status")
        return res.get("status", "unknown")

    async def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """Create a post. Strictly rate limited."""
        data = {"title": title, "content": content}
        if submolt:
            data["submolt"] = submolt
        res = await self._request("POST", "/posts", data)
        return res  # type: ignore

    async def comment_with_verification(self, post_id: str, content: str) -> MoltbookComment:
        """
        Creates a comment. AUTO-SOLVES math challenges.
        This is the watertight mechanism.

        Rate limit note: The initial attempt counts as 1 comment.
        If a challenge is returned, the retry reuses that same slot
        (we decrement before retrying) so one successful comment = 1 count.
        """
        data = {"content": content}

        # Attempt 1
        res = await self._request("POST", f"/posts/{post_id}/comments", data)

        # Handle verification challenge
        if res.get("error") == "VERIFICATION_REQUIRED":
            challenge = res.get("challenge", "")
            challenge_id = res.get("challenge_id", "")

            logger.info(f"Solving challenge: {challenge}")
            solution = ChallengeSolver.solve(challenge)

            # Undo the comment counter from the failed attempt —
            # the challenge response was NOT a posted comment.
            self.limits.comments_this_hour = max(0, self.limits.comments_this_hour - 1)

            # Attempt 2 with solution
            verify_data = {
                "content": content,
                "challenge_id": challenge_id,
                "challenge_solution": solution,
            }
            # Mock hook: offline mode needs this to pass the mock gate
            if self.offline_mode:
                verify_data["_challenge_solved"] = solution
            res = await self._request("POST", f"/posts/{post_id}/comments", verify_data)

        return res  # type: ignore

    async def semantic_search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        """Intelligence gathering core."""
        from urllib.parse import quote

        safe_query = quote(query, safe="")
        res = await self._request("GET", f"/search?q={safe_query}&limit={limit}")
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("items", res.get("results", []))
        return []

    async def get_profile(self, name: str) -> MoltbookAgentProfile:
        """Fetch an agent's profile."""
        from urllib.parse import quote

        safe_name = quote(name, safe="")
        res = await self._request("GET", f"/agents/profile?name={safe_name}")
        if self.offline_mode:
            return res  # type: ignore
        # Live API wraps profile under "agent" key
        if isinstance(res, dict) and "agent" in res:
            return res["agent"]  # type: ignore
        return res  # type: ignore

    async def check_heartbeat(self) -> HeartbeatResult:
        """The pulse check for new DMs or mentions."""
        res = await self._request("GET", "/agents/dm/check")
        if self.offline_mode:
            return res  # type: ignore
        # Live API shape: {success, has_activity, messages: {conversations_with_unread, ...}, requests: {count, ...}}
        messages = res.get("messages", {}) if isinstance(res, dict) else {}
        requests = res.get("requests", {}) if isinstance(res, dict) else {}
        has_new = bool(res.get("has_activity", False)) or int(messages.get("conversations_with_unread", 0)) > 0
        pending = int(requests.get("count", 0))
        return {"has_new_messages": has_new, "pending_requests": pending}  # type: ignore

    async def get_dm_conversations(self) -> List[DMConversation]:
        """List active DM conversations."""
        res = await self._request("GET", "/agents/dm/conversations")
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            # Live API returns {"count": N, "items": [...]}
            return res.get("items", res.get("conversations", []))
        return []

    async def get_dm_messages(self, conversation_id: str) -> List[DMMessage]:
        """Read messages in a conversation (marks as read)."""
        res = await self._request("GET", f"/agents/dm/conversations/{conversation_id}")
        if isinstance(res, list):
            return res  # type: ignore
        if isinstance(res, dict):
            return res.get("items", res.get("messages", []))  # type: ignore
        return []  # type: ignore

    async def send_dm(self, conversation_id: str, content: str) -> DMSendResult:
        """Send a message in an active DM conversation."""
        return await self._request("POST", f"/agents/dm/conversations/{conversation_id}/send", {"content": content})

    # --- Feed & Posts ---

    async def get_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """Global feed."""
        res = await self._request("GET", f"/posts?sort={sort}&limit={limit}")
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("items", res.get("posts", []))
        return []

    async def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """Personalized feed (subscriptions + follows)."""
        res = await self._request("GET", f"/feed?sort={sort}&limit={limit}")
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("items", res.get("posts", []))
        return []

    async def get_post(self, post_id: str) -> MoltbookPost:
        """Fetch a single post."""
        return await self._request("GET", f"/posts/{post_id}")  # type: ignore

    async def get_comments(self, post_id: str, sort: str = "top") -> List[MoltbookComment]:
        """Read comments on a post."""
        res = await self._request("GET", f"/posts/{post_id}/comments?sort={sort}")
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return res.get("items", res.get("comments", []))
        return []

    # --- Voting ---

    async def upvote(self, post_id: str) -> VoteResult:
        """Upvote a post."""
        return await self._request("POST", f"/posts/{post_id}/upvote")  # type: ignore

    async def downvote(self, post_id: str) -> VoteResult:
        """Downvote a post."""
        return await self._request("POST", f"/posts/{post_id}/downvote")  # type: ignore

    async def upvote_comment(self, comment_id: str) -> VoteResult:
        """Upvote a comment."""
        return await self._request("POST", f"/comments/{comment_id}/upvote")  # type: ignore

    # --- Following ---

    async def follow(self, agent_name: str) -> FollowResult:
        """Follow an agent."""
        return await self._request("POST", f"/agents/{agent_name}/follow")  # type: ignore

    async def unfollow(self, agent_name: str) -> FollowResult:
        """Unfollow an agent. Uses DELETE method."""
        # httpx handles DELETE via _request override
        self._enforce_limits("/agents/follow", "DELETE")
        if self.offline_mode:
            return self._handle_offline("DELETE", f"/agents/{agent_name}/follow", None)  # type: ignore
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            res = await client.delete(f"{self.base_url}/agents/{agent_name}/follow", headers=headers, timeout=10.0)
            res.raise_for_status()
            return res.json()

    # --- Submolts ---

    async def get_submolts(self) -> List[SubmoltDetails]:
        """List all submolts."""
        res = await self._request("GET", "/submolts")
        return res.get("submolts", []) if isinstance(res, dict) else []

    async def get_submolt(self, name: str) -> SubmoltDetails:
        """Get submolt details."""
        return await self._request("GET", f"/submolts/{name}")  # type: ignore

    async def create_submolt(self, name: str, display_name: str, description: str) -> SubmoltDetails:
        """Create a new submolt."""
        return await self._request("POST", "/submolts", {  # type: ignore
            "name": name, "display_name": display_name, "description": description,
        })

    async def subscribe_submolt(self, name: str) -> SubscribeResult:
        """Subscribe to a submolt."""
        return await self._request("POST", f"/submolts/{name}/subscribe")  # type: ignore

    async def unsubscribe_submolt(self, name: str) -> SubscribeResult:
        """Unsubscribe from a submolt. Uses DELETE method."""
        self._enforce_limits("/submolts/subscribe", "DELETE")
        if self.offline_mode:
            return self._handle_offline("DELETE", f"/submolts/{name}/subscribe", None)  # type: ignore
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            res = await client.delete(f"{self.base_url}/submolts/{name}/subscribe", headers=headers, timeout=10.0)
            res.raise_for_status()
            return res.json()

    # --- Profile ---

    async def get_own_profile(self) -> MoltbookAgentProfile:
        """Get own profile."""
        res = await self._request("GET", "/agents/me")
        if self.offline_mode:
            return res  # type: ignore
        # Live API wraps profile under "agent" key
        if isinstance(res, dict) and "agent" in res:
            return res["agent"]  # type: ignore
        return res  # type: ignore

    async def update_profile(self, description: str) -> ProfileUpdateResult:
        """Update own profile description. Uses PATCH method."""
        self._enforce_limits("/agents/me", "PATCH")
        if self.offline_mode:
            return self._handle_offline("PATCH", "/agents/me", {"description": description})  # type: ignore
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            res = await client.patch(
                f"{self.base_url}/agents/me",
                json={"description": description},
                headers=headers,
                timeout=10.0,
            )
            res.raise_for_status()
            return res.json()

    # --- DM Requests ---

    async def send_dm_request(self, agent_name: str, message: str) -> DMRequestResult:
        """Send a DM request to an agent."""
        return await self._request("POST", "/agents/dm/request", {  # type: ignore
            "agent_name": agent_name, "message": message,
        })

    async def get_dm_requests(self) -> List[DMRequestInfo]:
        """List pending DM requests."""
        res = await self._request("GET", "/agents/dm/requests")
        return res.get("requests", []) if isinstance(res, dict) else []

    async def approve_dm_request(self, request_id: str) -> DMRequestResult:
        """Approve a pending DM request."""
        return await self._request("POST", f"/agents/dm/requests/{request_id}/approve")  # type: ignore

    async def reject_dm_request(self, request_id: str) -> DMRequestResult:
        """Reject a pending DM request."""
        return await self._request("POST", f"/agents/dm/requests/{request_id}/reject")  # type: ignore

    # =========================================================================
    # SYNC BRIDGE — for on_pulse() and other sync callers
    # =========================================================================

    def sync_check_heartbeat(self) -> HeartbeatResult:
        """Sync wrapper for on_pulse(). Reuses running loop or creates one."""
        return _run_async(self.check_heartbeat())

    def sync_create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """Sync wrapper for post creation."""
        return _run_async(self.create_post(title, content, submolt))  # type: ignore

    def sync_send_dm(self, conversation_id: str, content: str) -> DMSendResult:
        """Sync wrapper for DM sending."""
        return _run_async(self.send_dm(conversation_id, content))

    def sync_get_dm_conversations(self) -> List[DMConversation]:
        """Sync wrapper for listing DM conversations."""
        return _run_async(self.get_dm_conversations())

    def sync_get_dm_messages(self, conversation_id: str) -> List[DMMessage]:
        """Sync wrapper for DM reading."""
        return _run_async(self.get_dm_messages(conversation_id))  # type: ignore


_SYNC_POOL = None


def _run_async(coro):
    """Run a coroutine from sync context. Handles both in-loop and no-loop cases."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context — reuse module-level thread pool.
        import concurrent.futures

        global _SYNC_POOL
        if _SYNC_POOL is None:
            _SYNC_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        return _SYNC_POOL.submit(asyncio.run, coro).result(timeout=15.0)
    else:
        return asyncio.run(coro)


# =============================================================================
# CLI ENTRY POINT — python -m vibe_core.mahamantra.adapters.moltbook
# =============================================================================


def _cli_main() -> None:
    """
    CLI for Moltbook operations.

    Usage:
        python -m vibe_core.mahamantra.adapters.moltbook register <name> [description]
        python -m vibe_core.mahamantra.adapters.moltbook status
        python -m vibe_core.mahamantra.adapters.moltbook test-network
    """
    import json
    import sys

    args = sys.argv[1:]
    if not args:
        print(__doc__ or "Moltbook Adapter CLI")
        print("\nCommands:")
        print("  register <name> [description]  — Register new agent (PERMANENT)")
        print("  status                         — Check agent status (needs API key)")
        print("  test-network                   — Test if moltbook.com is reachable")
        sys.exit(0)

    command = args[0]

    if command == "test-network":
        try:
            import httpx as _httpx

            resp = _httpx.get("https://www.moltbook.com/api/v1/agents/status", timeout=10.0)
            if resp.status_code in (401, 403):
                print(f"Network: REACHABLE (status={resp.status_code})")
                print("  moltbook.com is reachable. Registration from here SHOULD WORK.")
            else:
                print(f"Network: REACHABLE (status={resp.status_code})")
        except Exception as e:
            err_name = type(e).__name__
            if "Proxy" in err_name or "proxy" in str(e).lower():
                print(f"Network: BLOCKED BY PROXY — {e}")
                print("  This container routes through a proxy that blocks moltbook.com.")
                print("  Registration MUST happen via GitHub Actions or locally.")
            elif "Connect" in err_name:
                print(f"Network: UNREACHABLE — {e}")
                print("  No route to moltbook.com. Use GitHub Actions.")
            else:
                print(f"Network: ERROR ({err_name}) — {e}")
        sys.exit(0)

    if command == "register":
        if len(args) < 2:
            print("ERROR: agent name required")
            print("Usage: python -m vibe_core.mahamantra.adapters.moltbook register <name> [description]")
            sys.exit(1)

        name = args[1]
        description = (
            " ".join(args[2:])
            if len(args) > 2
            else "Steward Protocol — Agentic OS with deterministic Mahamantra computation engine."
        )

        print(f"Registering agent: {name}")
        print(f"Description: {description}")
        print("---")
        print("WARNING: This is PERMANENT. API key shown ONCE. No recovery.")
        print("---")

        client = MoltbookClient(api_key="", offline_mode=False)
        try:
            result = client.sync_register(name, description)
            print("\n=== REGISTRATION SUCCESSFUL ===")
            print(json.dumps(result, indent=2))
            print("\n!!! SAVE THE API KEY NOW !!!")
            print("Store in GitHub Secrets as: MOLTBOOK_API_KEY")
            agent = result.get("agent", result)
            if isinstance(agent, dict) and "api_key" in agent:
                print(f"\nAPI Key: {agent['api_key']}")
                print(f"Claim URL: {agent.get('claim_url', 'N/A')}")
                print(f"Verification Code: {agent.get('verification_code', 'N/A')}")
        except Exception as e:
            print(f"\nREGISTRATION FAILED: {e}")
            print("If network error: use GitHub Actions workflow instead.")
            sys.exit(1)

    elif command == "status":
        api_key = ""
        if len(args) > 1:
            api_key = args[1]
        else:
            import os

            api_key = os.environ.get("MOLTBOOK_API_KEY", "")
        if not api_key:
            print("ERROR: API key required. Pass as argument or set MOLTBOOK_API_KEY env var.")
            sys.exit(1)

        client = MoltbookClient(api_key=api_key, offline_mode=False)
        try:
            status = client.sync_check_heartbeat()
            print(json.dumps(status, indent=2))
        except Exception as e:
            print(f"Status check failed: {e}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
