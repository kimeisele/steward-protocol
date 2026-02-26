"""
MOLTBOOK ADAPTER — Thin Client
===============================

I/O, rate limiting, and challenge solving. No intelligence.
All decisions live in the plugin layer or kernel.
"""

import ast
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from vibe_core.mahamantra.adapters.captcha_decoder import CaptchaChamber
from vibe_core.protocols.moltbook import (
    DMMessage,
    MoltbookAgentProfile,
    MoltbookComment,
    MoltbookPost,
    SemanticSearchResult,
)

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


class ChallengeMonitor:
    """Tracks challenge solve attempts for ban avoidance.

    10 consecutive failures = ban. This monitor detects failure trends
    and halts commenting before the ban threshold.
    """

    BAN_THRESHOLD = 10  # Max allowed failures before ban
    HALT_THRESHOLD = 5  # Stop attempting after this many consecutive failures

    def __init__(self):
        self._consecutive_failures: int = 0
        self._total_attempts: int = 0
        self._total_successes: int = 0
        self._total_failures: int = 0
        self._halted: bool = False
        self._last_challenge_format: str = ""  # Track format changes

    @property
    def is_halted(self) -> bool:
        """True when too many consecutive failures — stop commenting."""
        return self._halted

    @property
    def failure_rate(self) -> float:
        if self._total_attempts == 0:
            return 0.0
        return self._total_failures / self._total_attempts

    def record_success(self) -> None:
        """Record a successful challenge solve."""
        self._consecutive_failures = 0
        self._total_attempts += 1
        self._total_successes += 1
        if self._halted:
            self._halted = False
            logger.info("Challenge monitor: resumed after successful solve")

    def record_failure(self, challenge_text: str = "") -> None:
        """Record a failed challenge solve."""
        self._consecutive_failures += 1
        self._total_attempts += 1
        self._total_failures += 1

        if self._consecutive_failures >= self.HALT_THRESHOLD:
            self._halted = True
            logger.error(
                f"CHALLENGE MONITOR HALT: {self._consecutive_failures} consecutive failures. "
                f"Commenting suspended to avoid ban. "
                f"Last challenge: {challenge_text[:100]}"
            )

    def check_format_change(self, challenge_text: str) -> bool:
        """Detect if the challenge format has changed.

        Returns True if format appears different from previous challenges.
        """
        # Simple format detection: check structural pattern
        text = challenge_text.lower().strip()
        # Extract format signature: has numbers? has operators? has words?
        has_digits = bool(re.search(r"\d", text))
        has_operator = any(op in text for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided"])
        has_question = text.startswith("what")

        fmt = f"digits={has_digits}|op={has_operator}|q={has_question}"

        if self._last_challenge_format and fmt != self._last_challenge_format:
            logger.warning(
                f"Challenge format change detected! "
                f"Was: {self._last_challenge_format}, Now: {fmt}. "
                f"Challenge: {challenge_text[:100]}"
            )
            self._last_challenge_format = fmt
            return True

        self._last_challenge_format = fmt
        return False

    def get_stats(self) -> dict:
        """Return monitoring stats for diagnostics."""
        return {
            "total_attempts": self._total_attempts,
            "total_successes": self._total_successes,
            "total_failures": self._total_failures,
            "consecutive_failures": self._consecutive_failures,
            "failure_rate": self.failure_rate,
            "halted": self._halted,
        }


# Module-level singleton — shared across all client instances
_challenge_monitor = ChallengeMonitor()


def get_challenge_monitor() -> ChallengeMonitor:
    """Get the global challenge monitor singleton."""
    return _challenge_monitor


class ChallengeSolver:
    """
    Solves Moltbook's obfuscated math challenges.
    Failure = temporary ban. This MUST be flawless.

    Two-layer architecture:
    1. SAFE EXPRESSION EVALUATOR (primary) — handles decimals, chained ops,
       operator precedence, parentheses via Python AST. No eval(). No exec().
    2. REGEX FALLBACK (secondary) — legacy 4-operator solver for edge cases.
    """

    # Compound numbers MUST come before their substrings to prevent
    # "eighteen" → "8een" corruption. Order matters.
    WORD_MAP = [
        # Compound teens/tens FIRST (prevent substring corruption)
        ("eighteen", "18"),
        ("seventeen", "17"),
        ("sixteen", "16"),
        ("fifteen", "15"),
        ("fourteen", "14"),
        ("thirteen", "13"),
        ("twelve", "12"),
        ("eleven", "11"),
        ("nineteen", "19"),
        ("eighty", "80"),
        ("seventy", "70"),
        ("sixty", "60"),
        ("fifty", "50"),
        ("forty", "40"),
        ("thirty", "30"),
        ("twenty", "20"),
        ("ninety", "90"),
        ("hundred", "100"),
        ("thousand", "1000"),
        ("million", "1000000"),
        # Single digits LAST
        ("zero", "0"),
        ("one", "1"),
        ("two", "2"),
        ("three", "3"),
        ("four", "4"),
        ("five", "5"),
        ("six", "6"),
        ("seven", "7"),
        ("eight", "8"),
        ("nine", "9"),
        ("ten", "10"),
    ]

    # Operator word → symbol substitution (applied AFTER number substitution)
    OPERATOR_MAP = [
        ("plus", "+"),
        ("add", "+"),
        ("sum of", "+"),
        ("minus", "-"),
        ("subtract", "-"),
        ("difference", "-"),
        ("times", "*"),
        ("multiply", "*"),
        ("multiplied by", "*"),
        ("divided by", "/"),
        ("divide", "/"),
        ("modulo", "%"),
        ("mod", "%"),
        ("remainder", "%"),
        ("power of", "**"),
        ("raised to", "**"),
        ("squared", "**2"),
        ("cubed", "**3"),
    ]

    # Allowed AST node types for safe evaluation (NO exec/import/call)
    _SAFE_NODES = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,  # Python 3.8+: numbers, strings
        ast.Num,  # Python 3.7 compat
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,  # Unary minus (-x)
        ast.UAdd,  # Unary plus (+x)
    }

    @staticmethod
    def _safe_eval(expr: str) -> Optional[float]:
        """Evaluate a math expression safely using AST whitelist.

        Only allows arithmetic operations on numbers. No function calls,
        no variable access, no imports, no exec. Returns None on any error.
        """
        try:
            tree = ast.parse(expr.strip(), mode="eval")
        except SyntaxError:
            return None

        # Walk tree and reject any unsafe nodes
        for node in ast.walk(tree):
            if type(node) not in ChallengeSolver._SAFE_NODES:
                logger.debug(f"Unsafe AST node rejected: {type(node).__name__}")
                return None

        try:
            result = eval(compile(tree, "<challenge>", "eval"))  # noqa: S307
            if isinstance(result, (int, float)):
                return result
        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
            pass
        return None

    @staticmethod
    def _normalize_text(challenge_text: str) -> str:
        """Convert challenge text to evaluable math expression.

        Order matters:
        1. Resolve hyphenated compounds (twenty-three → twentythree)
        2. Replace word-numbers with digits
        3. Join adjacent tens+units (20 3 → 23)
        4. Replace operator words with symbols
        5. Clean up non-math characters
        """
        text = challenge_text.lower()

        # Step 1: Resolve hyphenated number compounds BEFORE splitting hyphens.
        # "twenty-three" → "twentythree" (fused, so word-sub gives "203")
        # Then adjacent-number joiner makes "203" stay as-is, but we do it
        # differently: match tens-units directly.
        _HYPHEN_COMPOUNDS = re.compile(
            r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
            r"[-\s]+"
            r"(one|two|three|four|five|six|seven|eight|nine)\b"
        )
        _UNITS = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9,
        }
        _TENS = {
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
        }

        def _resolve_compound(m: re.Match) -> str:
            return str(_TENS[m.group(1)] + _UNITS[m.group(2)])

        text = _HYPHEN_COMPOUNDS.sub(_resolve_compound, text)

        # Step 2: Replace remaining word-numbers with digits
        for word, num in ChallengeSolver.WORD_MAP:
            text = re.sub(rf"\b{word}\b", num, text)

        # Step 3: Join standalone adjacent tens+units NOT from compounds
        # "20 3" → "23" (when NO operator between them)
        text = re.sub(
            r"\b([2-9]0)\s+([1-9])\b",
            lambda m: str(int(m.group(1)) + int(m.group(2))),
            text,
        )

        # Step 4: Replace operator words with symbols (longest match first)
        for word, symbol in ChallengeSolver.OPERATOR_MAP:
            text = re.sub(rf"\b{re.escape(word)}\b", f" {symbol} ", text)

        # Collapse duplicate ** from overlapping matches
        text = re.sub(r"\*\*\s*\*\*", "**", text)

        # Step 5: Extract just the math expression
        # Keep: 0-9 . + - * / % ( ) and spaces
        text = re.sub(r"[^0-9.+\-*/%() ]", " ", text)

        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def solve(challenge_text: str) -> str:
        """
        Solve a math challenge from obfuscated text.

        Two-layer approach:
        1. Normalize → safe AST eval (handles decimals, chained ops, precedence)
        2. Fallback: regex extraction + single operator (legacy)

        Always returns a string. Never raises.
        """
        # Layer 1: AST-based evaluation
        expr = ChallengeSolver._normalize_text(challenge_text)
        if expr:
            result = ChallengeSolver._safe_eval(expr)
            if result is not None:
                # Return integer if whole, otherwise float
                if result == int(result):
                    return str(int(result))
                return str(result)

        # Layer 2: Regex fallback (legacy single-operator solver)
        return ChallengeSolver._solve_regex_fallback(challenge_text)

    @staticmethod
    def _solve_regex_fallback(challenge_text: str) -> str:
        """Legacy regex solver — handles simple single-operator challenges.

        Kept as fallback for edge cases where AST normalization fails.
        """
        text = challenge_text.lower()

        for word, num in ChallengeSolver.WORD_MAP:
            text = re.sub(rf"\b{word}\b", num, text)

        numbers = [int(n) for n in re.findall(r"\d+", text)]

        if len(numbers) < 2:
            logger.warning(f"Could not parse math challenge: '{challenge_text}'")
            return "0"

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
        self._mock_db: Dict[str, Any] = {"posts": [], "comments": [], "dms": [], "status": "claimed"}

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

    # Endpoints known to be slow on Moltbook's side (feed aggregation, search)
    _SLOW_ENDPOINTS = ("/feed", "/posts", "/search")

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Core request dispatcher. Handles offline routing and httpx transport."""
        self._enforce_limits(endpoint, method)

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        if self.offline_mode:
            logger.debug(f"[OFFLINE] {method} {endpoint} - {data}")
            return self._handle_offline(method, endpoint, data)

        # Slow endpoints get longer timeout (Moltbook feed aggregation is slow)
        is_slow = any(endpoint.startswith(s) for s in self._SLOW_ENDPOINTS)
        timeout = 30.0 if is_slow else 10.0

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{endpoint}"
            try:
                response = await client.request(method, url, headers=headers, json=data, timeout=timeout)
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
                logger.error(f"Moltbook Request Error [{type(e).__name__}]: {e!r} — {method} {url}")
                raise

    # --- OFFLINE MOCK HUB ---

    def _handle_offline(self, method: str, endpoint: str, data: Optional[Dict]) -> Dict[str, Any]:
        """Simulates Moltbook API for watertight offline testing."""
        # --- SATTVA: Read-only ---

        if method == "GET" and endpoint == "/agents/status":
            return {"status": self._mock_db["status"]}

        elif method == "GET" and endpoint == "/agents/me":
            return {
                "success": True,
                "agent": {
                    "name": "steward-protocol",
                    "description": "Agentic OS",
                    "karma": 0,
                    "follower_count": 0,
                    "following_count": 0,
                    "is_claimed": True,
                    "is_active": True,
                },
            }

        elif method == "GET" and endpoint.startswith("/agents/profile"):
            return {
                "success": True,
                "agent": {
                    "name": "mock-agent",
                    "karma": 10,
                    "follower_count": 5,
                    "following_count": 3,
                    "is_claimed": True,
                },
            }

        elif method == "GET" and endpoint.startswith("/posts") and "comments" in endpoint:
            post_id = endpoint.split("/posts/")[1].split("/")[0]
            comments = [c for c in self._mock_db.get("comments", []) if c.get("post_id") == post_id]
            return {"comments": comments}

        elif method == "GET" and (endpoint.startswith("/posts?") or endpoint == "/posts"):
            return {"posts": self._mock_db["posts"]}

        elif method == "GET" and endpoint.startswith("/feed"):
            return {"posts": self._mock_db["posts"]}

        elif method == "GET" and endpoint.startswith("/posts/"):
            post_id = endpoint.split("/posts/")[1].split("?")[0].split("/")[0]
            for p in self._mock_db["posts"]:
                if p.get("id") == post_id:
                    return p
            return {"id": post_id, "title": "mock", "content": "mock"}

        elif method == "GET" and endpoint.startswith("/search"):
            return {"results": []}

        elif method == "GET" and endpoint == "/agents/dm/check":
            has_activity = len(self._mock_db["dms"]) > 0
            return {
                "success": True,
                "has_activity": has_activity,
                "summary": f"{'Activity' if has_activity else 'No activity'}",
                "requests": {"count": 0, "items": []},
                "messages": {"total_unread": 0, "conversations_with_unread": 0, "latest": []},
            }

        elif method == "GET" and endpoint == "/agents/dm/conversations":
            return {"conversations": {"count": 0, "items": self._mock_db.get("conversations", [])}}

        elif method == "GET" and endpoint == "/agents/dm/requests":
            return {"requests": {"count": 0, "items": []}}

        elif method == "GET" and endpoint.startswith("/agents/dm/conversations/"):
            conv_id = endpoint.rsplit("/", 1)[-1]
            msgs = [m for m in self._mock_db["dms"] if m.get("conversation_id") == conv_id]
            return {"messages": msgs}

        elif method == "GET" and endpoint == "/submolts":
            return {"submolts": self._mock_db.get("submolts", [])}

        elif method == "GET" and endpoint.startswith("/submolts/"):
            name = endpoint.split("/submolts/")[1].split("?")[0].split("/")[0]
            return {"name": name, "display_name": name, "subscriber_count": 0}

        # --- RAJAS: Write/create ---

        elif method == "POST" and endpoint == "/submolts":
            return {
                "name": data.get("name", ""),
                "display_name": data.get("display_name", ""),
                "description": data.get("description", ""),
                "subscriber_count": 0,
            }

        elif method == "POST" and endpoint == "/posts":
            post = {"id": f"p{len(self._mock_db['posts'])}", "title": data["title"], "content": data["content"]}
            self._mock_db["posts"].append(post)
            return post

        elif method == "POST" and "comments" in endpoint and "/upvote" not in endpoint:
            if data and "challenge_solution" in data:
                return {"id": "c99", "status": "posted"}
            return {"error": "VERIFICATION_REQUIRED", "challenge": "What is seven + 3?", "challenge_id": "c123"}

        elif method == "POST" and "/dm/conversations/" in endpoint and endpoint.endswith("/send"):
            conv_id = endpoint.split("/dm/conversations/")[1].split("/send")[0]
            msg = {
                "id": f"dm{len(self._mock_db['dms'])}",
                "conversation_id": conv_id,
                "sender": "self",
                "message": data.get("message", "") if data else "",
                "status": "sent",
            }
            self._mock_db["dms"].append(msg)
            return msg

        elif method == "POST" and endpoint == "/agents/dm/request":
            return {"success": True, "message": "Request sent"}

        elif method == "POST" and "/dm/requests/" in endpoint and "/approve" in endpoint:
            return {"success": True, "message": "Approved"}

        elif method == "POST" and "/dm/requests/" in endpoint and "/reject" in endpoint:
            return {"success": True, "message": "Rejected"}

        elif method == "POST" and endpoint.endswith("/upvote"):
            return {"success": True, "message": "Upvoted!"}

        elif method == "POST" and endpoint.endswith("/downvote"):
            return {"success": True, "message": "Downvoted"}

        elif method == "POST" and endpoint.endswith("/follow"):
            return {"success": True, "message": "Followed"}

        elif method == "POST" and endpoint.endswith("/subscribe"):
            return {"success": True, "message": "Subscribed"}

        elif method == "PATCH" and endpoint == "/agents/me":
            return {"success": True, "message": "Profile updated"}

        # --- TAMAS: Destructive ---

        elif method == "DELETE" and endpoint.startswith("/posts/"):
            return {"success": True, "message": "Deleted"}

        elif method == "DELETE" and endpoint.endswith("/follow"):
            return {"success": True, "message": "Unfollowed"}

        elif method == "DELETE" and endpoint.endswith("/subscribe"):
            return {"success": True, "message": "Unsubscribed"}

        return {"status": "ok", "mocked": True, "endpoint": endpoint}

    # =========================================================================
    # REGISTRATION — The ONLY unauthenticated endpoint
    # =========================================================================

    async def register(self, name: str, description: str) -> Dict[str, Any]:
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

    def sync_register(self, name: str, description: str) -> Dict[str, Any]:
        """Sync wrapper for registration."""
        return run_async(self.register(name, description))

    # =========================================================================
    # PUBLIC API - The "Skin" Interface (ALL require Bearer token)
    # =========================================================================

    # =========================================================================
    # SATTVA — Read-only endpoints
    # =========================================================================

    async def check_status(self) -> str:
        """GET /agents/status — verify agent claim status."""
        res = await self._request("GET", "/agents/status")
        return res.get("status", "unknown")

    async def check_heartbeat(self) -> Dict[str, Any]:
        """GET /agents/dm/check — pulse check for DM activity."""
        return await self._request("GET", "/agents/dm/check")

    async def get_own_profile(self) -> MoltbookAgentProfile:
        """GET /agents/me — own profile."""
        res = await self._request("GET", "/agents/me")
        return res.get("agent", res) if isinstance(res, dict) else res  # type: ignore

    async def get_profile(self, name: str) -> MoltbookAgentProfile:
        """GET /agents/profile?name=X — another agent's profile."""
        from urllib.parse import quote

        safe_name = quote(name, safe="")
        res = await self._request("GET", f"/agents/profile?name={safe_name}")
        return res.get("agent", res) if isinstance(res, dict) else res  # type: ignore

    async def get_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """GET /posts?sort=X — global feed."""
        from urllib.parse import quote

        res = await self._request("GET", f"/posts?sort={quote(sort, safe='')}&limit={limit}")
        if isinstance(res, dict):
            return res.get("posts", res.get("items", []))
        return res if isinstance(res, list) else []

    async def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """GET /feed?sort=X — personalized feed (subscribed submolts + followed agents)."""
        from urllib.parse import quote

        res = await self._request("GET", f"/feed?sort={quote(sort, safe='')}&limit={limit}")
        if isinstance(res, dict):
            return res.get("posts", res.get("items", []))
        return res if isinstance(res, list) else []

    async def get_post(self, post_id: str) -> MoltbookPost:
        """GET /posts/ID — single post."""
        res = await self._request("GET", f"/posts/{post_id}")
        return res  # type: ignore

    async def get_comments(self, post_id: str, sort: str = "top") -> List[MoltbookComment]:
        """GET /posts/ID/comments — comments on a post."""
        from urllib.parse import quote

        res = await self._request("GET", f"/posts/{post_id}/comments?sort={quote(sort, safe='')}")
        if isinstance(res, dict):
            return res.get("comments", res.get("items", []))
        return res if isinstance(res, list) else []

    async def semantic_search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        """GET /search?q=X — semantic search."""
        from urllib.parse import quote

        safe_query = quote(query, safe="")
        res = await self._request("GET", f"/search?q={safe_query}&limit={limit}")
        return res.get("results", []) if isinstance(res, dict) else []

    async def get_dm_conversations(self) -> List[Dict[str, Any]]:
        """GET /agents/dm/conversations — list active DM conversations."""
        res = await self._request("GET", "/agents/dm/conversations")
        if isinstance(res, dict):
            convs = res.get("conversations", {})
            if isinstance(convs, dict):
                return convs.get("items", [])
            return convs if isinstance(convs, list) else []
        return []

    async def get_dm_messages(self, conversation_id: str) -> List[DMMessage]:
        """GET /agents/dm/conversations/ID — read messages (marks as read)."""
        res = await self._request("GET", f"/agents/dm/conversations/{conversation_id}")
        return res.get("messages", []) if isinstance(res, dict) else []  # type: ignore

    async def get_dm_requests(self) -> List[Dict[str, Any]]:
        """GET /agents/dm/requests — pending inbound DM requests."""
        res = await self._request("GET", "/agents/dm/requests")
        if isinstance(res, dict):
            reqs = res.get("requests", {})
            if isinstance(reqs, dict):
                return reqs.get("items", [])
            return reqs if isinstance(reqs, list) else []
        return []

    async def get_submolts(self) -> List[Dict[str, Any]]:
        """GET /submolts — list all submolts."""
        res = await self._request("GET", "/submolts")
        if isinstance(res, dict):
            return res.get("submolts", res.get("items", []))
        return res if isinstance(res, list) else []

    async def get_submolt(self, name: str) -> Dict[str, Any]:
        """GET /submolts/NAME — submolt info."""
        from urllib.parse import quote

        return await self._request("GET", f"/submolts/{quote(name, safe='')}")

    # =========================================================================
    # RAJAS — Write/create endpoints
    # =========================================================================

    async def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """POST /posts — create a post. Strictly rate limited."""
        data: Dict[str, Any] = {"title": title, "content": content}
        if submolt:
            data["submolt"] = submolt
        res = await self._request("POST", "/posts", data)
        return res  # type: ignore

    async def comment_with_verification(
        self, post_id: str, content: str, parent_id: Optional[str] = None
    ) -> MoltbookComment:
        """
        POST /posts/ID/comments — creates a comment. AUTO-SOLVES math challenges.

        Rate limit note: The initial attempt counts as 1 comment.
        If a challenge is returned, the retry reuses that same slot
        (we decrement before retrying) so one successful comment = 1 count.

        Ban avoidance: ChallengeMonitor tracks consecutive failures.
        If halted (5+ failures), commenting is refused to prevent ban.
        """
        monitor = _challenge_monitor

        # Ban avoidance: refuse to comment if halted
        if monitor.is_halted:
            logger.error("Comment refused: challenge monitor halted (too many solve failures)")
            return {"error": "CHALLENGE_MONITOR_HALTED", "stats": monitor.get_stats()}  # type: ignore

        data: Dict[str, Any] = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id

        # Attempt 1
        res = await self._request("POST", f"/posts/{post_id}/comments", data)

        # Handle verification challenge
        if res.get("error") == "VERIFICATION_REQUIRED":
            challenge = res.get("challenge", "")
            challenge_id = res.get("challenge_id", "")

            # Format change detection
            monitor.check_format_change(challenge)

            logger.info(f"Solving challenge: {challenge}")
            solution = CaptchaChamber.solve(challenge)

            # CaptchaChamber returns None when confidence is too low
            if solution is None:
                monitor.record_failure(challenge)
                logger.warning("CaptchaChamber: low confidence, skipping comment")
                # Undo the comment counter — no comment was posted
                self.limits.comments_this_hour = max(0, self.limits.comments_this_hour - 1)
                return {"error": "captcha_low_confidence", "skipped": True}

            # Undo the comment counter from the failed attempt —
            # the challenge response was NOT a posted comment.
            self.limits.comments_this_hour = max(0, self.limits.comments_this_hour - 1)

            # Attempt 2 with solution
            verify_data: Dict[str, Any] = {
                "content": content,
                "challenge_id": challenge_id,
                "challenge_solution": solution,
            }
            if parent_id:
                verify_data["parent_id"] = parent_id
            # Mock hook: offline mode needs this to pass the mock gate
            if self.offline_mode:
                verify_data["_challenge_solved"] = solution
            res = await self._request("POST", f"/posts/{post_id}/comments", verify_data)

            # Track solve result for ban avoidance
            if res.get("error"):
                monitor.record_failure(challenge)
                logger.warning(
                    f"Challenge solve FAILED: {challenge[:60]} → {solution} "
                    f"(consecutive={monitor._consecutive_failures})"
                )
            else:
                monitor.record_success()
                logger.debug(f"Challenge solved: {challenge[:60]} → {solution}")

        return res  # type: ignore

    async def send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """POST /agents/dm/conversations/ID/send — send a message.

        Autonomous agent — governance via Guna system (RAJAS=logged write),
        not human-in-the-loop escalation.
        """
        data: Dict[str, Any] = {"message": content}
        return await self._request("POST", f"/agents/dm/conversations/{conversation_id}/send", data)

    async def send_dm_request(self, to_agent: str, message: str) -> Dict[str, Any]:
        """POST /agents/dm/request — send a chat request to another agent."""
        return await self._request("POST", "/agents/dm/request", {"to": to_agent, "message": message})

    async def approve_dm_request(self, request_id: str) -> Dict[str, Any]:
        """POST /agents/dm/requests/ID/approve — approve a DM request."""
        return await self._request("POST", f"/agents/dm/requests/{request_id}/approve")

    async def reject_dm_request(self, request_id: str, block: bool = False) -> Dict[str, Any]:
        """POST /agents/dm/requests/ID/reject — reject (optionally block)."""
        data: Dict[str, Any] = {}
        if block:
            data["block"] = True
        return await self._request("POST", f"/agents/dm/requests/{request_id}/reject", data or None)

    async def upvote(self, post_id: str) -> Dict[str, Any]:
        """POST /posts/ID/upvote."""
        return await self._request("POST", f"/posts/{post_id}/upvote")

    async def downvote(self, post_id: str) -> Dict[str, Any]:
        """POST /posts/ID/downvote."""
        return await self._request("POST", f"/posts/{post_id}/downvote")

    async def upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        """POST /comments/ID/upvote."""
        return await self._request("POST", f"/comments/{comment_id}/upvote")

    async def follow_agent(self, agent_name: str) -> Dict[str, Any]:
        """POST /agents/NAME/follow."""
        from urllib.parse import quote

        return await self._request("POST", f"/agents/{quote(agent_name, safe='')}/follow")

    async def unfollow_agent(self, agent_name: str) -> Dict[str, Any]:
        """DELETE /agents/NAME/follow."""
        from urllib.parse import quote

        return await self._request("DELETE", f"/agents/{quote(agent_name, safe='')}/follow")

    async def subscribe_submolt(self, submolt_name: str) -> Dict[str, Any]:
        """POST /submolts/NAME/subscribe."""
        from urllib.parse import quote

        return await self._request("POST", f"/submolts/{quote(submolt_name, safe='')}/subscribe")

    async def unsubscribe_submolt(self, submolt_name: str) -> Dict[str, Any]:
        """DELETE /submolts/NAME/subscribe."""
        from urllib.parse import quote

        return await self._request("DELETE", f"/submolts/{quote(submolt_name, safe='')}/subscribe")

    async def create_submolt(self, name: str, display_name: str, description: str) -> Dict[str, str]:
        """POST /submolts — create a new submolt community."""
        return await self._request(
            "POST",
            "/submolts",
            {
                "name": name,
                "display_name": display_name,
                "description": description,
            },
        )

    def sync_create_submolt(self, name: str, display_name: str, description: str) -> Dict[str, str]:
        """Sync wrapper for submolt creation."""
        return run_async(self.create_submolt(name, display_name, description))

    async def update_profile(
        self, description: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """PATCH /agents/me — update own profile."""
        data: Dict[str, Any] = {}
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        return await self._request("PATCH", "/agents/me", data)

    # =========================================================================
    # TAMAS — Destructive endpoints
    # =========================================================================

    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """DELETE /posts/ID."""
        return await self._request("DELETE", f"/posts/{post_id}")

    # =========================================================================
    # SYNC BRIDGE — for on_pulse() and other sync callers
    # =========================================================================

    def sync_check_heartbeat(self) -> Dict[str, Any]:
        """Sync wrapper for on_pulse(). Reuses running loop or creates one."""
        return run_async(self.check_heartbeat())

    def sync_create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """Sync wrapper for post creation."""
        return run_async(self.create_post(title, content, submolt))  # type: ignore

    def sync_send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """Sync wrapper for DM sending."""
        return run_async(self.send_dm(conversation_id, content))

    def sync_get_dm_conversations(self) -> List[Dict[str, Any]]:
        """Sync wrapper for listing DM conversations."""
        return run_async(self.get_dm_conversations())

    def sync_get_dm_messages(self, conversation_id: str) -> List[DMMessage]:
        """Sync wrapper for DM reading."""
        return run_async(self.get_dm_messages(conversation_id))  # type: ignore


def run_async(coro):
    """Run a coroutine from sync context. Handles both in-loop and no-loop cases."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context (e.g. FastAPI) — run in a new thread.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=15.0)
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
