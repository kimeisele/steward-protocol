"""
CLI Execution Protocol - Level -1 Fractal Infrastructure

PROMPT.md: "Protocol statt konkrete Klassen"
GAD-000 v2.0: Cryptographically bound capability tokens

This protocol enables NAGAs to wrap CLI execution at Level -2.
The HookChain (Vasuki) churns the CLI ocean, transforming Gift to Nektar.

Architecture Layers:
- Level 0:  User Commands (steward naga status)
- Level -1: CLIExecutionContext + HookChain (THIS FILE)
- Level -2: NAGA Hooks (Takshaka, Chitragupta, Sesha)
- Level -3: Command Handlers (NagaCLI, ToolCLI, etc.)
"""

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, TypedDict

if TYPE_CHECKING:
    pass


# =============================================================================
# ENUMS - CLI Execution Phases and Permission Levels
# =============================================================================


class CLIExecutionPhase(str, Enum):
    """
    Phases of CLI command execution - hooks intercept at each phase.

    Order: PRE_VALIDATE -> POST_VALIDATE -> PRE_EXECUTE -> [execute] -> POST_EXECUTE
    On exception: ON_ERROR
    """

    PRE_VALIDATE = "pre_validate"  # Before argument validation
    POST_VALIDATE = "post_validate"  # After validation, before execution
    PRE_EXECUTE = "pre_execute"  # Just before handler runs
    POST_EXECUTE = "post_execute"  # After handler completes
    ON_ERROR = "on_error"  # On exception


class CLIPermissionLevel(str, Enum):
    """
    Permission levels for CLI commands.

    Used by CLIMeta to declare required permission level.
    """

    PUBLIC = "public"  # Anyone can execute (steward --version)
    AUTHENTICATED = "auth"  # Requires valid identity
    PRIVILEGED = "privileged"  # Requires elevated capabilities
    KERNEL = "kernel"  # Kernel-only operations


# =============================================================================
# TYPED DICTS - VIMANA RANGE ROVER (No Dict[str, Any])
# =============================================================================


class CLIExecutionContextData(TypedDict, total=False):
    """Execution context for CLI command - replaces Dict[str, Any]."""

    command_name: str
    namespace: str
    args: List[str]
    caller_id: str
    timestamp: str
    permission_level: str
    capabilities_required: List[str]
    token_subject: str
    token_issuer: str
    token_valid: bool


class CLIExecutionResult(TypedDict, total=False):
    """Result of CLI execution - replaces Dict[str, Any]."""

    success: bool
    exit_code: int
    output: str
    error: str
    duration_ms: float
    phase_completed: str
    blocked_by: str
    blocked_reason: str


class CLIHookResult(TypedDict, total=False):
    """Result from a CLI hook - replaces Dict[str, Any]."""

    allow: bool
    reason: str
    modified_args: List[str]
    injected_context: Dict[str, str]


class CLITokenClaims(TypedDict, total=False):
    """Claims inside a capability token - replaces Dict[str, Any]."""

    sub: str  # Subject (caller identity)
    caps: List[str]  # Capabilities granted
    iat: int  # Issued at (unix timestamp)
    exp: int  # Expires at (unix timestamp)
    iss: str  # Issuer (KERNEL | CIVIC)


# =============================================================================
# CLI CAPABILITY TOKEN - Signed, Not Zettel!
# =============================================================================


@dataclass
class CLICapabilityToken:
    """
    Signed capability token - notariell beglaubigt, not handgeschrieben.

    Narada Correction: A UUID session_id is worthless - attacker generates new one.
    The token MUST be cryptographically signed by a trusted issuer (Kernel/Civic).

    Takshaka validates:
    1. Signature is valid (ed25519)
    2. Token not expired
    3. Capability is in token claims

    If signature invalid -> BITE (forgery attempt!)
    """

    subject: str  # Caller identity (e.g., "agent_007")
    capabilities: List[str]  # Granted capabilities
    issued_at: datetime
    expires_at: datetime
    issuer: str  # "KERNEL" | "CIVIC"
    signature: bytes = field(default=b"", repr=False)

    # Token ID for tracking
    token_id: str = field(default="")

    def __post_init__(self) -> None:
        """Generate token_id if not provided."""
        if not self.token_id:
            # Deterministic ID from claims
            claims = f"{self.subject}:{self.issuer}:{self.issued_at.timestamp()}"
            self.token_id = hashlib.sha256(claims.encode()).hexdigest()[:16]

    def to_claims(self) -> CLITokenClaims:
        """Convert to claims dict for signing."""
        return CLITokenClaims(
            sub=self.subject,
            caps=self.capabilities,
            iat=int(self.issued_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            iss=self.issuer,
        )

    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now() > self.expires_at

    def has_capability(self, cap: str) -> bool:
        """
        Check if token grants capability.

        IMPORTANT: Call verify() first! This only checks claims.
        """
        return cap in self.capabilities

    @classmethod
    def issue(
        cls,
        subject: str,
        capabilities: List[str],
        issuer: str,
        issuer_private_key: bytes,
        ttl_seconds: int = 3600,
    ) -> "CLICapabilityToken":
        """
        Issue a signed capability token.

        Only Kernel/Civic should call this - they hold the private key.

        Args:
            subject: Caller identity
            capabilities: List of granted capabilities
            issuer: "KERNEL" or "CIVIC"
            issuer_private_key: ed25519 private key bytes
            ttl_seconds: Token lifetime (default 1 hour)

        Returns:
            Signed CLICapabilityToken
        """
        now = datetime.now()
        token = cls(
            subject=subject,
            capabilities=capabilities,
            issued_at=now,
            expires_at=datetime.fromtimestamp(now.timestamp() + ttl_seconds),
            issuer=issuer,
        )

        # Sign the claims
        token.signature = token._sign(issuer_private_key)
        return token

    def _sign(self, secret_key: bytes) -> bytes:
        """
        Sign token claims with HMAC-SHA256.

        Uses HMAC with shared secret for simplicity.
        Ed25519 can be added later for asymmetric signing if needed.

        Args:
            secret_key: Shared secret key (at least 32 bytes recommended)
        """
        import hmac

        claims_bytes = self._claims_to_bytes()
        return hmac.new(secret_key, claims_bytes, hashlib.sha256).digest()

    def verify(self, secret_key: bytes) -> bool:
        """
        Verify signature is valid.

        MUST call this before trusting any claims!

        Args:
            secret_key: Same shared secret used for signing

        Returns:
            True if signature valid, False otherwise
        """
        if not self.signature:
            return False

        import hmac

        try:
            claims_bytes = self._claims_to_bytes()
            expected = hmac.new(secret_key, claims_bytes, hashlib.sha256).digest()
            return hmac.compare_digest(self.signature, expected)
        except Exception:
            return False

    def _claims_to_bytes(self) -> bytes:
        """Serialize claims to bytes for signing."""
        import json

        claims = self.to_claims()
        # Sort keys for deterministic serialization
        return json.dumps(claims, sort_keys=True).encode()

    @classmethod
    def create_anonymous(cls) -> "CLICapabilityToken":
        """
        Create an anonymous token with PUBLIC capabilities only.

        Used for unauthenticated CLI access (steward --version).
        """
        now = datetime.now()
        return cls(
            subject="anonymous",
            capabilities=["cli.public"],
            issued_at=now,
            expires_at=datetime.fromtimestamp(now.timestamp() + 300),  # 5 min
            issuer="SYSTEM",
            signature=b"anonymous",  # Not cryptographically valid
            token_id="anonymous",
        )


# =============================================================================
# EXECUTION CONTEXT (Capability Injection Point)
# =============================================================================


@dataclass
class CLIExecutionContext:
    """
    Execution context passed through CLI pipeline.

    This is the CAPABILITY INJECTION POINT - NAGAs can:
    1. Read context to understand what's being executed
    2. Verify capability token
    3. Block execution by setting blocked=True
    """

    command_name: str
    namespace: str
    args: List[str]
    capability_token: CLICapabilityToken

    # Derived from token (set by hooks)
    caller_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    # Command requirements (set by command lookup)
    permission_level: CLIPermissionLevel = CLIPermissionLevel.PUBLIC
    capabilities_required: List[str] = field(default_factory=list)

    # NAGA observation state
    blocked: bool = False
    blocked_by: str = ""
    blocked_reason: str = ""

    # Execution timing
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize caller_id from token."""
        if not self.caller_id and self.capability_token:
            self.caller_id = self.capability_token.subject

    @property
    def duration_ms(self) -> float:
        """Get execution duration in milliseconds."""
        if self.end_time > 0:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000

    def to_dict(self) -> CLIExecutionContextData:
        """Serialize to typed dict."""
        return CLIExecutionContextData(
            command_name=self.command_name,
            namespace=self.namespace,
            args=self.args,
            caller_id=self.caller_id,
            timestamp=self.timestamp.isoformat(),
            permission_level=self.permission_level.value,
            capabilities_required=self.capabilities_required,
            token_subject=self.capability_token.subject,
            token_issuer=self.capability_token.issuer,
            token_valid=not self.capability_token.is_expired(),
        )


# =============================================================================
# CLI HOOK PROTOCOL (NAGA Integration Point)
# =============================================================================


class CLIHookProtocol(Protocol):
    """
    Protocol for CLI execution hooks.

    NAGAs implement this to wrap CLI commands at Level -2.
    The HookChain orchestrates execution order (Takshaka -> Capability -> Chitragupta -> Sesha).

    All hooks must allow for execution to proceed.
    """

    @property
    def hook_id(self) -> str:
        """Unique identifier for this hook."""
        ...

    def on_phase(self, phase: CLIExecutionPhase, context: CLIExecutionContext) -> CLIHookResult:
        """
        Called at each execution phase.

        Return allow=False to block execution.
        Return modified_args to transform input.
        Return injected_context to add data.
        """
        ...


# =============================================================================
# CLI EXECUTOR PROTOCOL (Unified Execution)
# =============================================================================


class CLIExecutorProtocol(Protocol):
    """
    Protocol for CLI command executor.

    This is the Level -1 orchestrator that:
    1. Receives commands from Level 0 (user)
    2. Runs hooks at Level -2 (NAGAs)
    3. Delegates to handlers at Level -3 (implementation)
    """

    def register_hook(self, hook_id: str, hook: CLIHookProtocol) -> None:
        """Register a CLI execution hook (NAGA integration)."""
        ...

    def unregister_hook(self, hook_id: str) -> bool:
        """Unregister a hook by ID."""
        ...

    def execute(
        self,
        command: str,
        args: List[str],
        capability_token: Optional[CLICapabilityToken] = None,
    ) -> CLIExecutionResult:
        """
        Execute a CLI command through the hook pipeline.

        Flow:
        1. Create CLIExecutionContext with token
        2. Run PRE_VALIDATE hooks (Takshaka validates args)
        3. Validate command exists
        4. Run POST_VALIDATE hooks (Capability check)
        5. Run PRE_EXECUTE hooks (Chitragupta starts profiling)
        6. Execute handler
        7. Run POST_EXECUTE hooks (Chitragupta/Sesha record)
        8. Return result
        """
        ...

    def get_required_capabilities(self, command: str) -> List[str]:
        """Get capabilities required for a command."""
        ...
