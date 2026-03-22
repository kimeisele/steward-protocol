"""
OPUS-171 Phase 5.2: BaseCortex - Abstract Base Class for Cortex Modules

Sanskrit: Cortex = Outer layer of the brain (Latin).
In MANAS: The execution engines that perform complex operations.

This base class enables VEDA-4 auto-discovery of cortex modules via CortexLoader.
Each cortex represents a specialized capability domain:

    - ShellCortex: CLI/Git operations
    - DocumentationCortex: Documentation surface inspection
    - SilpaCortex: Code refactoring
    - TestCortex: Test execution
    - etc.

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Handler.handle(intent)                                             │
    │      │                                                              │
    │      ▼                                                              │
    │  CortexLoader.get_cortex("shell")  ← VEDA-4 Auto-Discovery          │
    │      │                                                              │
    │      ▼                                                              │
    │  BaseCortex.execute(intent) → Dict[str, Any]                        │
    └─────────────────────────────────────────────────────────────────────┘

ADAPTER PATTERN:
    Existing cortex modules (ShellCortex, documentation builders, etc.) are wrapped
    in adapters that implement this interface. This allows VEDA-4 discovery
    without modifying the original implementations.

"The cortex is the thinking layer - where intention becomes action."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xd51c69be"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent
    from vibe_core.protocols.kernel_protocol import KernelProtocol


# =============================================================================
# WATERTIGHT TYPEDDICTS - Cortex Result Contract
# =============================================================================


class CortexResult(TypedDict, total=False):
    """
    Standard result from cortex execution. WATERTIGHT.

    Required fields:
        success: Whether execution succeeded
        handler: Which cortex handled this
        message: Human-readable result

    Optional fields:
        error: Error message if failed
        data: Any additional payload
        duration_ms: Execution time
    """

    success: bool
    handler: str
    message: str
    error: str
    data: Any  # Legitimate Any - varies per cortex
    duration_ms: float


class BaseCortex(ABC):
    """
    Abstract base class for MANAS cortex modules (execution engines).

    All cortex adapters must inherit from this class to be discovered by CortexLoader.

    Required Class Attributes:
        - name: Unique identifier for the cortex (e.g., "shell", "documentation")
        - capabilities: List of capabilities this cortex provides

    Required Methods:
        - execute(intent): Execute an intent and return structured result

    Optional:
        - inject_kernel(kernel): Inject kernel for ledger/state access

    Usage:
        class ShellCortexAdapter(BaseCortex):
            name = "shell"
            capabilities = ["git_commit", "git_push", "cli_execute"]

            def execute(self, intent: Intent) -> Dict[str, Any]:
                # Delegate to underlying ShellCortex
                return self._cortex.execute_safe(intent.params.get("command", []))

    Discovery:
        CortexLoader.get_cortex("shell", workspace=Path.cwd())
    """

    # === MUST BE OVERRIDDEN ===
    name: ClassVar[str] = ""  # Unique cortex identifier (e.g., "shell", "documentation")
    capabilities: ClassVar[List[str]] = []  # What this cortex can do

    # === OPTIONAL OVERRIDES ===
    priority: ClassVar[int] = 0  # Higher priority = preferred when multiple match

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["KernelProtocol"] = None,
    ):
        """
        Initialize cortex.

        Args:
            workspace: Workspace root (default: cwd)
            kernel: Optional kernel for ledger/state access
        """
        self._workspace = workspace or Path.cwd()
        self._kernel = kernel

    @property
    def workspace(self) -> Path:
        """Get workspace root."""
        return self._workspace

    @property
    def kernel(self) -> Optional["KernelProtocol"]:
        """Get kernel reference (if injected)."""
        return self._kernel

    def inject_kernel(self, kernel: Optional["KernelProtocol"]) -> None:
        """
        Inject kernel for ledger/state access.

        Called by IntentRouter before execute() to provide kernel access.

        Args:
            kernel: The kernel instance (or None)
        """
        self._kernel = kernel

    @abstractmethod
    def execute(self, intent: "Intent") -> CortexResult:
        """
        Execute an intent and return structured result.

        This is the main entry point for cortex operations.
        Each cortex implements its own execution logic.

        Args:
            intent: The intent to execute

        Returns:
            CortexResult with:
                - success: bool
                - handler: str (cortex name)
                - message: str (human-readable result)
                - error: Optional[str] (if failed)
        """
        pass

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this cortex provides."""
        return list(self.capabilities)

    def can_handle(self, capability: str) -> bool:
        """Check if this cortex can handle a specific capability."""
        return capability in self.capabilities

    def __repr__(self) -> str:
        caps = ", ".join(self.capabilities[:3])
        if len(self.capabilities) > 3:
            caps += f", +{len(self.capabilities) - 3} more"
        return f"<{self.__class__.__name__}:{self.name} caps=[{caps}]>"


# =============================================================================
# CORTEX RESULT HELPERS
# =============================================================================


def cortex_success(
    handler: str,
    message: str,
    **extra: Any,
) -> CortexResult:
    """Create a successful cortex result."""
    result = CortexResult(
        success=True,
        handler=handler,
        message=message,
    )
    # Add extra fields if provided
    for key, value in extra.items():
        result[key] = value  # type: ignore[literal-required]
    return result


def cortex_error(
    handler: str,
    error: str,
    **extra: Any,
) -> CortexResult:
    """Create an error cortex result."""
    result = CortexResult(
        success=False,
        handler=handler,
        error=error,
        message=f"Error: {error}",
    )
    # Add extra fields if provided
    for key, value in extra.items():
        result[key] = value  # type: ignore[literal-required]
    return result
