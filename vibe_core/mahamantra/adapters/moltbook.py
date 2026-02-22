"""
MOLTBOOK ADAPTER - The Agent City Bridge
========================================

"karmany evadhikaras te ma phaleshu kadachana"
"You have a right to perform your prescribed duty, but you are not entitled to the fruits of action."

This is the THIN CLIENT for Moltbook.
It does NOT contain logic, only I/O, rate limiting, and challenge solving.
All intelligence lives in the Mahamantra Core.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 3 - The Divine Messenger
__position__ = 3
__genesis__ = "0x28f9d1a3"  # GenesisByte: parampara % 37 == 0

import asyncio
import httpx
import json
import logging
import math
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from vibe_core.protocols.moltbook import (
    MoltbookAgentProfile, MoltbookPost, MoltbookComment, 
    SemanticSearchResult, DMRequest, DMMessage, SubmoltDetails
)

logger = logging.getLogger("MOLTBOOK")


# =============================================================================
# RATE LIMITS & CONSTANTS
# =============================================================================

class MoltbookLimits:
    """Hardcoded limits from Moltbook rules.md"""
    REQ_PER_MIN = 100
    POST_PER_30_MIN = 1
    COMMENTS_PER_DAY = 50
    AVATAR_MAX_BYTES = 1024 * 1024  # 1MB
    BANNER_MAX_BYTES = 2 * 1024 * 1024  # 2MB


@dataclass
class RateLimitState:
    """Tracks current rate limit usage"""
    requests_this_minute: int = 0
    last_minute_reset: float = field(default_factory=time.time)
    
    posts_this_30m: int = 0
    last_30m_reset: float = field(default_factory=time.time)
    
    comments_today: int = 0
    last_day_reset: float = field(default_factory=time.time)


# =============================================================================
# CHALLENGE SOLVER (Deterministic Anti-Spam)
# =============================================================================

class ChallengeSolver:
    """
    Solves Moltbook's obfuscated math challenges.
    Failure = temporary ban. This MUST be flawless.
    """
    
    @staticmethod
    def solve(challenge_text: str) -> str:
        """
        Extracts numbers and operators from obfuscated text and computes the result.
        Example: "What is seven + 3?" -> "10"
        
        Note: This is a robust baseline. Complete implementation requires observing
        actual Moltbook challenge formats in the wild.
        """
        # Map words to numbers
        word_map = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        text = challenge_text.lower()
        
        # Replace words with digits
        for word, num in word_map.items():
            text = text.replace(word, str(num))
            
        # Extract all numbers
        numbers = [int(n) for n in re.findall(r'\d+', text)]
        
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
            for n in numbers: result *= n
            return str(result)
            
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
        self._mock_db: Dict[str, Any] = {
            "posts": [],
            "comments": [],
            "dms": [],
            "status": "claimed"
        }

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
        if method == "POST" and endpoint.endswith("/posts") and not "comments" in endpoint:
            if now - self.limits.last_30m_reset > 1800:
                self.limits.posts_this_30m = 0
                self.limits.last_30m_reset = now
                
            if self.limits.posts_this_30m >= MoltbookLimits.POST_PER_30_MIN:
                raise Exception("MOLTBOOK-429: Post rate limit (1/30m) exceeded.")
            self.limits.posts_this_30m += 1
            
        # 3. Comment Limiter (50/day)
        if method == "POST" and "comments" in endpoint:
            if now - self.limits.last_day_reset > 86400:
                self.limits.comments_today = 0
                self.limits.last_day_reset = now
                
            if self.limits.comments_today >= MoltbookLimits.COMMENTS_PER_DAY:
                raise Exception("MOLTBOOK-429: Daily comment limit exceeded.")
            self.limits.comments_today += 1
            
        self.limits.requests_this_minute += 1

    # --- HTTP TRANSPORT ---

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Core request dispatcher. Handles offline routing and httpx transport."""
        self._enforce_limits(endpoint, method)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
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
                            return err_data # Pass back to caller to handle challenge
                    except Exception:
                        pass
                logger.error(f"Moltbook HTTP Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Moltbook Request Error: {str(e)}")
                raise

    # --- OFFLINE MOCK HUB ---

    def _handle_offline(self, method: str, endpoint: str, data: Optional[Dict]) -> Dict[str, Any]:
        """Simulates Moltbook API for watertight offline testing."""
        if method == "GET" and endpoint == "/agents/status":
            return {"status": self._mock_db["status"]}
            
        elif method == "GET" and endpoint.startswith("/search"):
            return {"results": [], "similarity": 0.95} # Mock semantic search
            
        elif method == "POST" and endpoint == "/posts":
            post = {"id": f"p{len(self._mock_db['posts'])}", "title": data["title"], "content": data["content"]}
            self._mock_db["posts"].append(post)
            return post
            
        elif method == "GET" and endpoint == "/agents/dm/check":
            return {"has_new_messages": False, "pending_requests": 0}
            
        # Simulated Math Challenge
        elif method == "POST" and "comments" in endpoint:
            if data and data.get("_challenge_solved") != "10": # Imagine "7 + 3"
                 return {"error": "VERIFICATION_REQUIRED", "challenge": "What is seven + 3?", "challenge_id": "c123"}
            return {"id": "c99", "status": "posted"}

        return {"status": "ok", "mocked": True, "endpoint": endpoint}

    # =========================================================================
    # PUBLIC API - The "Skin" Interface
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
        return res # type: ignore

    async def comment_with_verification(self, post_id: str, content: str) -> MoltbookComment:
        """
        Creates a comment. AUTO-SOLVES math challenges.
        This is the watertight mechanism.
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
            
        return res # type: ignore

    async def semantic_search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        """Intelligence gathering core."""
        res = await self._request("GET", f"/search?q={query}&limit={limit}")
        return res.get("results", [])

    async def get_profile(self, name: str) -> MoltbookAgentProfile:
        """Fetch an agent's profile."""
        res = await self._request("GET", f"/agents/profile?name={name}")
        return res # type: ignore

    async def check_heartbeat(self) -> Dict[str, Any]:
        """The pulse check for new DMs or mentions."""
        return await self._request("GET", "/agents/dm/check")


# =============================================================================
# INTELLIGENCE WRAPPERS
# =============================================================================

class SemanticSearchWrapper:
    """
    Wraps the raw semantic search to provide structured intelligence gathering
    without burning rate limits on low-value searches.
    """
    def __init__(self, client: MoltbookClient):
        self.client = client
        
    async def find_os_discussions(self, threshold: float = 0.8) -> List[SemanticSearchResult]:
        """Find other agents discussing OS-level concepts."""
        results = await self.client.semantic_search("agent operating system kernel scheduling")
        return [r for r in results if r.get("similarity", 0) >= threshold]
        
    async def find_crypto_believers(self, threshold: float = 0.85) -> List[SemanticSearchResult]:
        """Find agents discussing cryptographic identity."""
        results = await self.client.semantic_search("cryptographic identity verification trust")
        return [r for r in results if r.get("similarity", 0) >= threshold]
        
    async def map_competitors(self) -> List[SemanticSearchResult]:
        """Broad sweep for other 'framework' agents."""
        return await self.client.semantic_search("agent framework architecture", limit=50)
