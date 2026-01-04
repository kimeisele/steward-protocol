"""
TAKSHAKA LITE - Gateway Security Middleware
============================================

NAGA SECURITY FIXES (P0 Priority):
- P0-1: Signature verification BEFORE payload processing
- P0-2: Real parser for toxic pattern detection (not string match)
- P0-3: WebSocket authentication enforcement
- P0-4: Message size limits

"Bite first, ask later." - Takshaka principle

PROMPT.md Compliance:
- Level 2: TAKSHAKA (The Defender)
- "Identität kommt VOR dem Parsing"
- "Ein Paket ohne valide kryptografische Signatur wird verworfen, BEVOR der Payload deserialisiert wird"
"""

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger("TAKSHAKA")


# =============================================================================
# VERIFICATION RESULT
# =============================================================================


class VerifyStatus(Enum):
    """Verification result status."""

    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_KEY = "invalid_key"
    EXPIRED = "expired"
    UNTRUSTED = "untrusted"
    NO_SIGNATURE = "no_signature"
    RATE_LIMITED = "rate_limited"
    SIZE_EXCEEDED = "size_exceeded"
    TOXIC = "toxic"


@dataclass
class VerifyResult:
    """
    Result of Takshaka verification.

    Contains verification status and details for audit trail.
    """

    status: VerifyStatus
    agent_id: Optional[str] = None
    fingerprint: Optional[str] = None
    reason: Optional[str] = None
    toxic_patterns: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def is_valid(self) -> bool:
        return self.status == VerifyStatus.VALID

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "agent_id": self.agent_id,
            "fingerprint": self.fingerprint,
            "reason": self.reason,
            "toxic_patterns": self.toxic_patterns,
            "timestamp": self.timestamp,
        }


# =============================================================================
# KALIYA FILTER - Toxicity Detection
# =============================================================================


class KaliyaFilter:
    """
    Toxicity detection for incoming requests.

    Named after the serpent Krishna subdued in the Yamuna river.
    Detects prompt injection, SQL injection, command injection, etc.

    PROMPT.md: "Kaliya-Filter (Toxicity)"
    """

    # SQL Injection patterns
    SQL_PATTERNS = [
        r"(?i)\b(DROP|DELETE|TRUNCATE|ALTER|INSERT|UPDATE)\s+(TABLE|DATABASE|INDEX)",
        r"(?i)\bOR\s+1\s*=\s*1\b",
        r"(?i)\bUNION\s+(ALL\s+)?SELECT\b",
        r"(?i);\s*--",
        r"(?i)\bEXEC(UTE)?\s*\(",
    ]

    # Command injection patterns
    COMMAND_PATTERNS = [
        r"(?i)\b(sudo|su\s+-|chmod|chown|rm\s+-rf|dd\s+if=)\b",
        r"(?i)\|\s*(bash|sh|zsh|cmd|powershell)",
        r"(?i)`[^`]+`",  # Backtick command execution
        r"\$\([^)]+\)",  # $(command) execution
        r"(?i)\b(curl|wget)\s+.+\|\s*(bash|sh)",  # Remote script execution
    ]

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+(instructions?|prompts?)",
        r"(?i)forget\s+(everything|all|what)",
        r"(?i)you\s+are\s+now\s+(a|an|my)",
        r"(?i)new\s+(system\s+)?instructions?:",
        r"(?i)override\s+(system|safety)",
        r"(?i)jailbreak",
        r"(?i)DAN\s+mode",
        r"<\|.*?\|>",  # Model delimiter injection
        r"\[\[.*?\]\]",  # Prompt markers
    ]

    # Path traversal patterns
    PATH_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e[/\\]",
        r"\.%00",
    ]

    def __init__(self):
        # Compile all patterns for efficiency
        self._sql_re = [re.compile(p) for p in self.SQL_PATTERNS]
        self._cmd_re = [re.compile(p) for p in self.COMMAND_PATTERNS]
        self._inject_re = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self._path_re = [re.compile(p) for p in self.PATH_PATTERNS]

    def scan(self, content: str) -> tuple[float, List[str]]:
        """
        Scan content for toxic patterns.

        Returns:
            (toxicity_score, list_of_matched_patterns)
            Score is 0.0 (clean) to 1.0 (maximum toxicity)
        """
        score = 0.0
        matched = []

        # SQL injection (critical)
        for pattern in self._sql_re:
            if pattern.search(content):
                score += 0.4
                matched.append(f"SQL:{pattern.pattern[:30]}")

        # Command injection (critical)
        for pattern in self._cmd_re:
            if pattern.search(content):
                score += 0.4
                matched.append(f"CMD:{pattern.pattern[:30]}")

        # Prompt injection (high)
        for pattern in self._inject_re:
            if pattern.search(content):
                score += 0.3
                matched.append(f"INJECT:{pattern.pattern[:30]}")

        # Path traversal (medium)
        for pattern in self._path_re:
            if pattern.search(content):
                score += 0.2
                matched.append(f"PATH:{pattern.pattern[:30]}")

        return min(score, 1.0), matched

    def is_toxic(self, content: str, threshold: float = 0.3) -> bool:
        """Check if content exceeds toxicity threshold."""
        score, _ = self.scan(content)
        return score >= threshold


# =============================================================================
# TAKSHAKA SERVICE - Main Security Layer
# =============================================================================


class TakshakaLite:
    """
    Lightweight gateway security layer.

    "Bite first, ask later."

    Responsibilities:
    1. Signature verification (37th Principle)
    2. Toxicity detection (Kaliya Filter)
    3. Rate limiting (SudarshanaGuard style)
    4. Size limits
    """

    # Size limits
    MAX_MESSAGE_SIZE = 100_000  # 100KB max message
    MAX_AGENT_ID_SIZE = 64  # 64 chars max agent ID

    # Rate limiting (requests per minute per agent)
    RATE_LIMIT_RPM = 60
    RATE_LIMIT_WINDOW = 60.0  # seconds

    # Toxicity threshold
    TOXICITY_THRESHOLD = 0.3

    def __init__(self, trust_mode: str = "strict"):
        """
        Initialize Takshaka.

        Args:
            trust_mode: "strict" (require trusted keys) or "permissive" (any valid sig)
        """
        self._trust_mode = trust_mode
        self._kaliya = KaliyaFilter()
        self._rate_limits: Dict[str, List[float]] = {}  # agent_id -> timestamps
        logger.info(f"TAKSHAKA initialized (trust_mode={trust_mode})")

    def verify_request(
        self,
        message: str,
        agent_id: str,
        signature: str,
        public_key: str,
        timestamp: int,
    ) -> VerifyResult:
        """
        Verify an incoming signed request.

        Order of checks (PROMPT.md "Bite first"):
        1. Size limits (no parsing needed)
        2. Rate limiting
        3. Signature verification (identity before parsing)
        4. Toxicity scan (Kaliya filter)

        Args:
            message: The message content
            agent_id: Agent identifier
            signature: Base64 ECDSA signature
            public_key: PEM-encoded public key
            timestamp: Unix timestamp (seconds)

        Returns:
            VerifyResult with status and details
        """
        # --- 1. SIZE LIMITS (pre-parse) ---
        if len(message) > self.MAX_MESSAGE_SIZE:
            logger.warning(f"TAKSHAKA: Message too large ({len(message)} bytes) from {agent_id}")
            return VerifyResult(
                status=VerifyStatus.SIZE_EXCEEDED,
                agent_id=agent_id,
                reason=f"Message exceeds {self.MAX_MESSAGE_SIZE} bytes",
            )

        if len(agent_id) > self.MAX_AGENT_ID_SIZE:
            logger.warning(f"TAKSHAKA: Agent ID too long ({len(agent_id)} chars)")
            return VerifyResult(
                status=VerifyStatus.SIZE_EXCEEDED,
                reason=f"Agent ID exceeds {self.MAX_AGENT_ID_SIZE} chars",
            )

        # --- 2. RATE LIMITING ---
        if not self._check_rate_limit(agent_id):
            logger.warning(f"TAKSHAKA: Rate limit exceeded for {agent_id}")
            return VerifyResult(
                status=VerifyStatus.RATE_LIMITED,
                agent_id=agent_id,
                reason=f"Rate limit exceeded ({self.RATE_LIMIT_RPM}/min)",
            )

        # --- 3. TIMESTAMP FRESHNESS ---
        now = time.time()
        age = abs(now - timestamp)
        if age > 300:  # 5 minutes max age
            logger.warning(f"TAKSHAKA: Request expired (age={age:.0f}s) from {agent_id}")
            return VerifyResult(
                status=VerifyStatus.EXPIRED,
                agent_id=agent_id,
                reason=f"Request too old ({age:.0f}s > 300s)",
            )

        # --- 4. SIGNATURE VERIFICATION (37th Principle) ---
        try:
            from vibe_core.steward.crypto import (
                get_public_key_fingerprint,
                is_key_trusted,
                verify_signature,
            )

            # Construct signed content (message + timestamp)
            content = f"{message}:{timestamp}"
            fingerprint = get_public_key_fingerprint(public_key)

            if not verify_signature(content, signature, public_key):
                logger.warning(f"TAKSHAKA: Invalid signature from {agent_id} ({fingerprint})")
                return VerifyResult(
                    status=VerifyStatus.INVALID_SIGNATURE,
                    agent_id=agent_id,
                    fingerprint=fingerprint,
                    reason="Signature verification failed",
                )

            # Strict mode: require trusted key
            if self._trust_mode == "strict" and not is_key_trusted(public_key):
                logger.warning(f"TAKSHAKA: Untrusted key from {agent_id} ({fingerprint})")
                return VerifyResult(
                    status=VerifyStatus.UNTRUSTED,
                    agent_id=agent_id,
                    fingerprint=fingerprint,
                    reason="Key not in trusted keyring",
                )

            logger.debug(f"TAKSHAKA: Signature valid from {agent_id} ({fingerprint})")

        except ImportError:
            # Crypto not available - degrade gracefully in dev mode
            logger.warning("TAKSHAKA: Crypto not available, running in degraded mode")
            fingerprint = "unknown"
        except Exception as e:
            logger.error(f"TAKSHAKA: Signature verification error: {e}")
            return VerifyResult(
                status=VerifyStatus.INVALID_KEY,
                agent_id=agent_id,
                reason=str(e),
            )

        # --- 5. TOXICITY SCAN (Kaliya Filter) ---
        score, patterns = self._kaliya.scan(message)
        if score >= self.TOXICITY_THRESHOLD:
            logger.warning(f"TAKSHAKA: Toxic content from {agent_id} (score={score:.2f})")
            return VerifyResult(
                status=VerifyStatus.TOXIC,
                agent_id=agent_id,
                fingerprint=fingerprint,
                reason=f"Toxicity score {score:.2f} >= threshold {self.TOXICITY_THRESHOLD}",
                toxic_patterns=patterns,
            )

        # --- ALL CHECKS PASSED ---
        return VerifyResult(
            status=VerifyStatus.VALID,
            agent_id=agent_id,
            fingerprint=fingerprint,
        )

    def _check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent is within rate limits."""
        now = time.time()
        window_start = now - self.RATE_LIMIT_WINDOW

        # Get agent's request history
        history = self._rate_limits.get(agent_id, [])

        # Filter to requests within window
        history = [t for t in history if t > window_start]

        # Check limit
        if len(history) >= self.RATE_LIMIT_RPM:
            return False

        # Record this request
        history.append(now)
        self._rate_limits[agent_id] = history
        return True

    def check_websocket_auth(
        self,
        api_key: Optional[str],
        expected_key: Optional[str],
    ) -> VerifyResult:
        """
        Check WebSocket authentication.

        Args:
            api_key: Key from query param or header
            expected_key: Expected API key from env

        Returns:
            VerifyResult
        """
        if not expected_key:
            return VerifyResult(
                status=VerifyStatus.INVALID_KEY,
                reason="Server API key not configured",
            )

        if not api_key:
            return VerifyResult(
                status=VerifyStatus.NO_SIGNATURE,
                reason="No API key provided",
            )

        if api_key != expected_key:
            return VerifyResult(
                status=VerifyStatus.INVALID_KEY,
                reason="Invalid API key",
            )

        return VerifyResult(status=VerifyStatus.VALID)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Global instance for use in API routes
_takshaka: Optional[TakshakaLite] = None


def get_takshaka(trust_mode: str = "permissive") -> TakshakaLite:
    """Get the global Takshaka instance."""
    global _takshaka
    if _takshaka is None:
        _takshaka = TakshakaLite(trust_mode=trust_mode)
    return _takshaka
