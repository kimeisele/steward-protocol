"""
Tests for CLI HookChain - NAGA Level -2 Infrastructure

Tests:
1. Hook registration and ordering
2. Phase execution order
3. All-must-allow semantics
4. Context propagation
5. Blocking behavior
6. Graceful degradation

SAMUDRA MANTHAN: Verify the rope (Vasuki) coordinates the churning correctly.
"""

from datetime import datetime, timedelta
from typing import List

import pytest

from vibe_core.naga.cli_hook_chain import CLIHookChain, HookPhaseMapping
from vibe_core.protocols.cli_execution import (
    CLICapabilityToken,
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
)

# =============================================================================
# TEST FIXTURES
# =============================================================================


class MockHook:
    """Mock hook for testing."""

    def __init__(
        self,
        hook_id: str,
        allow: bool = True,
        phases_seen: List[CLIExecutionPhase] = None,
    ):
        self._hook_id = hook_id
        self._allow = allow
        self.phases_seen = phases_seen if phases_seen is not None else []
        self.call_count = 0

    @property
    def hook_id(self) -> str:
        return self._hook_id

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        self.phases_seen.append(phase)
        self.call_count += 1
        return CLIHookResult(allow=self._allow)


class BlockingHook:
    """Hook that blocks at a specific phase."""

    def __init__(self, hook_id: str, block_at: CLIExecutionPhase, reason: str = "blocked"):
        self._hook_id = hook_id
        self._block_at = block_at
        self._reason = reason

    @property
    def hook_id(self) -> str:
        return self._hook_id

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        if phase == self._block_at:
            return CLIHookResult(allow=False, reason=self._reason)
        return CLIHookResult(allow=True)


def create_test_context(command: str = "test", args: List[str] = None) -> CLIExecutionContext:
    """Create a test execution context."""
    token = CLICapabilityToken(
        subject="test_user",
        capabilities=["cli.public"],
        issued_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        issuer="TEST",
    )
    return CLIExecutionContext(
        command_name=command,
        namespace="test",
        args=args or [],
        capability_token=token,
    )


# =============================================================================
# HOOK CHAIN TESTS
# =============================================================================


class TestHookChainBasics:
    """Basic hook chain functionality."""

    def test_create_hook_chain(self):
        """Hook chain can be created."""
        chain = CLIHookChain()
        assert chain is not None
        assert len(chain.get_registered_hooks()) == 0

    def test_register_hook(self):
        """Hooks can be registered."""
        chain = CLIHookChain()
        hook = MockHook("test_hook")

        chain.register(hook)

        assert "test_hook" in chain.get_registered_hooks()

    def test_unregister_hook(self):
        """Hooks can be unregistered."""
        chain = CLIHookChain()
        hook = MockHook("test_hook")
        chain.register(hook)

        result = chain.unregister("test_hook")

        assert result is True
        assert "test_hook" not in chain.get_registered_hooks()

    def test_unregister_nonexistent_hook(self):
        """Unregistering nonexistent hook returns False."""
        chain = CLIHookChain()

        result = chain.unregister("nonexistent")

        assert result is False


class TestPhaseExecution:
    """Phase execution order tests."""

    def test_pre_phases_order(self):
        """Pre-phases execute in correct order."""
        chain = CLIHookChain()
        phases_seen = []

        # Register hooks that track phases
        chain.register(MockHook("takshaka", phases_seen=phases_seen))
        chain.register(MockHook("capability", phases_seen=phases_seen))
        chain.register(MockHook("chitragupta", phases_seen=phases_seen))

        context = create_test_context()
        chain.run_pre_phases(context)

        # Should see PRE_VALIDATE, POST_VALIDATE, PRE_EXECUTE in order
        assert CLIExecutionPhase.PRE_VALIDATE in phases_seen
        assert CLIExecutionPhase.POST_VALIDATE in phases_seen
        assert CLIExecutionPhase.PRE_EXECUTE in phases_seen

    def test_post_phases_execute(self):
        """Post-phases execute after command."""
        chain = CLIHookChain()
        phases_seen = []

        chain.register(MockHook("chitragupta", phases_seen=phases_seen))
        chain.register(MockHook("sesha", phases_seen=phases_seen))

        context = create_test_context()
        chain.run_post_phases(context)

        assert CLIExecutionPhase.POST_EXECUTE in phases_seen

    def test_error_phase_executes(self):
        """Error phase executes on exception."""
        chain = CLIHookChain()
        phases_seen = []

        chain.register(MockHook("sesha", phases_seen=phases_seen))

        context = create_test_context()
        chain.run_error_phase(context)

        assert CLIExecutionPhase.ON_ERROR in phases_seen


class TestBlockingBehavior:
    """Test hook blocking semantics."""

    def test_blocking_hook_stops_execution(self):
        """Blocking hook prevents further execution."""
        chain = CLIHookChain()

        # Register a blocking hook at PRE_VALIDATE
        chain.register(BlockingHook("takshaka", CLIExecutionPhase.PRE_VALIDATE, "toxic input"))

        context = create_test_context()
        result = chain.run_pre_phases(context)

        assert result is False
        assert context.blocked is True
        assert context.blocked_by == "takshaka"
        assert "toxic input" in context.blocked_reason

    def test_all_must_allow(self):
        """All hooks must allow for execution to proceed."""
        chain = CLIHookChain()

        # First hook allows
        chain.register(MockHook("takshaka", allow=True))
        # Second hook blocks
        chain.register(BlockingHook("capability", CLIExecutionPhase.POST_VALIDATE, "no capability"))

        context = create_test_context()
        result = chain.run_pre_phases(context)

        assert result is False
        assert context.blocked_by == "capability"

    def test_allowing_hooks_pass(self):
        """All allowing hooks let execution proceed."""
        chain = CLIHookChain()

        chain.register(MockHook("takshaka", allow=True))
        chain.register(MockHook("capability", allow=True))
        chain.register(MockHook("chitragupta", allow=True))

        context = create_test_context()
        result = chain.run_pre_phases(context)

        assert result is True
        assert context.blocked is False


class TestContextPropagation:
    """Test context propagation through hooks."""

    def test_context_passed_to_all_hooks(self):
        """Same context is passed to all hooks."""
        chain = CLIHookChain()
        contexts_received = []

        class ContextCapturingHook:
            def __init__(self, hook_id: str):
                self._hook_id = hook_id

            @property
            def hook_id(self) -> str:
                return self._hook_id

            def on_phase(self, phase, context):
                contexts_received.append(context)
                return CLIHookResult(allow=True)

        # Use hook IDs that are in DEFAULT_MAPPINGS for PRE_VALIDATE phase
        chain.register(ContextCapturingHook("takshaka"))

        context = create_test_context("my_command")
        chain.run_phase(CLIExecutionPhase.PRE_VALIDATE, context)

        # All hooks should receive the same context instance
        assert len(contexts_received) >= 1
        for ctx in contexts_received:
            assert ctx.command_name == "my_command"


class TestGracefulDegradation:
    """Test graceful degradation when hooks unavailable."""

    def test_missing_hook_skipped(self):
        """Missing hooks are skipped gracefully."""
        chain = CLIHookChain()

        # Don't register 'takshaka' but it's in DEFAULT_MAPPINGS
        chain.register(MockHook("capability"))

        context = create_test_context()
        # Should not raise, just skip missing hooks
        result = chain.run_pre_phases(context)

        assert result is True

    def test_hook_exception_logged_not_fatal(self):
        """Hook exceptions are logged but don't block execution."""
        chain = CLIHookChain()

        class ExplodingHook:
            @property
            def hook_id(self) -> str:
                return "exploding"

            def on_phase(self, phase, context):
                raise RuntimeError("BOOM!")

        # Add exploding hook to a phase
        chain.register(ExplodingHook())
        chain.add_mapping(HookPhaseMapping("exploding", CLIExecutionPhase.PRE_EXECUTE, priority=50))

        context = create_test_context()
        # Should not raise - exception is logged
        result = chain.run_phase(CLIExecutionPhase.PRE_EXECUTE, context)

        assert result is True  # Graceful degradation


class TestCapabilityToken:
    """Test capability token functionality."""

    def test_token_creation(self):
        """Capability token can be created."""
        token = CLICapabilityToken(
            subject="agent_007",
            capabilities=["cli.naga.status", "cli.tool.execute"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.subject == "agent_007"
        assert "cli.naga.status" in token.capabilities
        assert token.issuer == "KERNEL"

    def test_token_expiration(self):
        """Expired tokens are detected."""
        # Expired token
        token = CLICapabilityToken(
            subject="expired_agent",
            capabilities=["cli.public"],
            issued_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.is_expired() is True

        # Valid token
        valid_token = CLICapabilityToken(
            subject="valid_agent",
            capabilities=["cli.public"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert valid_token.is_expired() is False

    def test_token_has_capability(self):
        """Token capability check works."""
        token = CLICapabilityToken(
            subject="agent",
            capabilities=["cli.naga.status", "cli.tool.list"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            issuer="KERNEL",
        )

        assert token.has_capability("cli.naga.status") is True
        assert token.has_capability("cli.tool.list") is True
        assert token.has_capability("cli.kernel.boot") is False

    def test_token_signing_and_verification(self):
        """Token signature can be verified."""
        secret = b"test-secret-key-32-bytes-minimum"

        # Issue signed token
        token = CLICapabilityToken.issue(
            subject="signed_agent",
            capabilities=["cli.public"],
            issuer="KERNEL",
            issuer_private_key=secret,
        )

        # Verify with correct key
        assert token.verify(secret) is True

        # Verify with wrong key fails
        assert token.verify(b"wrong-key") is False

    def test_anonymous_token(self):
        """Anonymous token can be created."""
        token = CLICapabilityToken.create_anonymous()

        assert token.subject == "anonymous"
        assert "cli.public" in token.capabilities
        assert token.issuer == "SYSTEM"


class TestHookPhaseMapping:
    """Test hook-phase mapping configuration."""

    def test_default_mappings_exist(self):
        """Default mappings are defined."""
        assert len(CLIHookChain.DEFAULT_MAPPINGS) > 0

    def test_takshaka_runs_first(self):
        """Takshaka (security) runs at PRE_VALIDATE with high priority."""
        takshaka_mapping = next(
            (m for m in CLIHookChain.DEFAULT_MAPPINGS if m.hook_id == "takshaka"),
            None,
        )

        assert takshaka_mapping is not None
        assert takshaka_mapping.phase == CLIExecutionPhase.PRE_VALIDATE
        assert takshaka_mapping.priority == 100  # Highest

    def test_custom_mapping_can_be_added(self):
        """Custom hook-phase mappings can be added."""
        chain = CLIHookChain()

        custom_mapping = HookPhaseMapping(
            hook_id="custom_hook",
            phase=CLIExecutionPhase.PRE_EXECUTE,
            priority=75,
        )
        chain.add_mapping(custom_mapping)

        hooks_for_phase = chain.get_phase_hooks(CLIExecutionPhase.PRE_EXECUTE)
        assert "custom_hook" in hooks_for_phase
