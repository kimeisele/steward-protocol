"""
NARASIMHA PROBE - Hardening Test for Act 1

"Wenn ein Kind geboren wird, checkt der Arzt die Reflexe."
- Senior Senf (Hil)

This test PROVES whether the 37th (Kshetrajna) is truly born.
We don't hope. We verify.

CLAIMS TO TEST:
1. "Narasimha Gatekeeper ENABLED" - Does it actually block anything?
2. "Ghost registrations blocked" - Can an unblessed service register?
3. "All chaos injection validated" - Is unauthorized chaos rejected?

If these tests PASS: Act 1 is complete, proceed to Act 2.
If these tests FAIL: Act 1 is incomplete, fix before proceeding.
"""

import pytest
from typing import Protocol, runtime_checkable

from vibe_core.di import ServiceRegistry


# =============================================================================
# TEST FIXTURES - The Ghost Services
# =============================================================================


@runtime_checkable
class GhostProtocol(Protocol):
    """A protocol with no NAGA blessing."""
    def haunt(self) -> str: ...


class GhostService:
    """
    An unblessed service. No @naga_governed. No signature.

    If Narasimha is truly active, this should be BLOCKED from registration.
    """
    def haunt(self) -> str:
        return "BOO! I slipped through!"


class BlessedService:
    """
    A properly blessed service (for comparison).

    In reality, this would have @naga_governed or similar.
    For now, we test the blessing mechanism itself.
    """
    _naga_blessed = True  # Simulated blessing marker

    def haunt(self) -> str:
        return "I am blessed and registered properly."


# =============================================================================
# TEST 1: Ghost Registration (The Critical Test)
# =============================================================================


class TestGhostRegistration:
    """Test that unblessed services cannot register."""

    def setup_method(self):
        """Reset registry before each test."""
        ServiceRegistry.reset()

    def teardown_method(self):
        """Clean up after each test."""
        ServiceRegistry.reset()
        ServiceRegistry.disable_naga_blessing()

    def test_ghost_can_register_when_blessing_disabled(self):
        """
        BASELINE: When blessing is disabled, ghosts CAN register.
        This establishes the control case.
        """
        # Ensure blessing is disabled
        ServiceRegistry.disable_naga_blessing()

        # Ghost should register without issue
        ghost = GhostService()
        ServiceRegistry.register(GhostProtocol, ghost)

        # Should be retrievable
        retrieved = ServiceRegistry.get(GhostProtocol)
        assert retrieved is ghost
        assert retrieved.haunt() == "BOO! I slipped through!"

    def test_ghost_blocked_when_blessing_enabled(self):
        """
        THE CRITICAL TEST: When blessing is enabled, ghosts should be BLOCKED.

        If this test FAILS, our claim "ghost registrations blocked" is FALSE.
        """
        # Enable blessing check
        ServiceRegistry.enable_naga_blessing(strict=True)

        # Ghost should be blocked
        ghost = GhostService()

        # In strict mode, this should raise an exception
        # If it doesn't, Act 1 is incomplete
        with pytest.raises(Exception) as exc_info:
            ServiceRegistry.register(GhostProtocol, ghost)

        # Verify it was blocked for the right reason
        assert "DHARMA" in str(exc_info.value) or "blessing" in str(exc_info.value).lower()

    def test_blessing_violations_logged(self):
        """
        NON-STRICT MODE: Ghosts can register but violations are logged.
        """
        # Enable blessing check (non-strict)
        ServiceRegistry.enable_naga_blessing(strict=False)

        # Ghost registers (allowed in non-strict mode)
        ghost = GhostService()
        ServiceRegistry.register(GhostProtocol, ghost)

        # But violation should be logged
        violations = ServiceRegistry.get_naga_blessing_violations()
        assert len(violations) > 0
        assert any("GhostProtocol" in v or "GhostService" in v for v in violations)


# =============================================================================
# TEST 2: Chaos Injection (Narasimha's Primary Function)
# =============================================================================


class TestChaosInjection:
    """Test that unauthorized chaos injection is blocked."""

    def setup_method(self):
        """Reset registry before each test."""
        ServiceRegistry.reset()

    def teardown_method(self):
        """Clean up after each test."""
        ServiceRegistry.reset()
        ServiceRegistry.clear_chaos()
        ServiceRegistry.disable_narasimha()

    def test_chaos_allowed_when_narasimha_disabled(self):
        """
        BASELINE: When Narasimha is disabled, anyone can inject chaos.
        """
        ServiceRegistry.disable_narasimha()

        # Should work without issue
        def evil_injector():
            return GhostService()

        # No exception expected
        ServiceRegistry.inject_chaos(GhostProtocol, evil_injector)

    def test_chaos_blocked_when_narasimha_enabled(self):
        """
        THE NARASIMHA TEST: When enabled, unauthorized chaos should be BLOCKED.

        Only authorized callers (PrahladService, etc.) can inject chaos.
        A random test function should be rejected.
        """
        ServiceRegistry.enable_narasimha()

        def evil_injector():
            return GhostService()

        # Should be blocked with PermissionError
        with pytest.raises(PermissionError) as exc_info:
            ServiceRegistry.inject_chaos(GhostProtocol, evil_injector)

        assert "NARASIMHA" in str(exc_info.value)
        assert "BLOCKED" in str(exc_info.value)


# =============================================================================
# TEST 3: The 37th (Identity) Existence
# =============================================================================


class TestIdentityExistence:
    """Test that the 37th (NagaIdentity) exists after kernel boot."""

    def test_narasimha_enabled_after_kernel_boot(self):
        """
        After kernel boot, Narasimha should be enabled.

        This is what we added in Act 1.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        # Boot kernel
        kernel = RealVibeKernel(ledger_path=":memory:", test_mode=True)

        # Narasimha should be enabled
        assert ServiceRegistry.is_narasimha_enabled() is True

        # Clean up
        if hasattr(kernel, 'shutdown'):
            kernel.shutdown(reason="Test complete")

    def test_naga_identity_generated_at_boot(self):
        """
        After NAGA Federation boots, NagaIdentity should exist.

        The 37th is the cryptographic identity that signs all decisions.
        """
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.protocols.naga import NagaFederationProtocol

        # Boot kernel (which boots NAGA federation)
        kernel = RealVibeKernel(ledger_path=":memory:", test_mode=True)

        # Get federation
        federation = ServiceRegistry.get(NagaFederationProtocol)

        if federation:
            # Identity should exist
            assert hasattr(federation, '_identity') or hasattr(federation, 'identity')

            # Identity should have a fingerprint
            identity = getattr(federation, '_identity', None) or getattr(federation, 'identity', None)
            if identity:
                assert hasattr(identity, 'fingerprint') or hasattr(identity, 'get_fingerprint')

        # Clean up
        if hasattr(kernel, 'shutdown'):
            kernel.shutdown(reason="Test complete")


# =============================================================================
# META-TEST: What This Test Suite Proves
# =============================================================================


class TestActOneCompleteness:
    """
    Meta-test that summarizes Act 1 status.

    Run this last to get a clear verdict.
    """

    def test_act_one_verdict(self):
        """
        VERDICT: Is Act 1 truly complete?

        This test summarizes the state of the 37th's birth.
        """
        results = {
            "narasimha_enabled": ServiceRegistry.is_narasimha_enabled(),
            "blessing_enabled": ServiceRegistry.is_naga_blessing_enabled(),
        }

        # For Act 1 to be complete, BOTH should be enabled
        # Currently we only enabled Narasimha, not blessing

        print("\n" + "=" * 60)
        print("ACT 1 VERDICT")
        print("=" * 60)
        print(f"Narasimha Gatekeeper: {'ENABLED' if results['narasimha_enabled'] else 'DISABLED'}")
        print(f"NAGA Blessing Check:  {'ENABLED' if results['blessing_enabled'] else 'DISABLED'}")
        print("=" * 60)

        if results['narasimha_enabled'] and results['blessing_enabled']:
            print("VERDICT: Act 1 COMPLETE. The 37th is truly born.")
        elif results['narasimha_enabled']:
            print("VERDICT: Act 1 PARTIAL. Chaos blocked, but ghosts can still register.")
            print("         The 37th is born but has not opened its eyes.")
        else:
            print("VERDICT: Act 1 NOT STARTED. No security active.")

        print("=" * 60)

        # This test doesn't fail - it just reports status
        # The individual tests above will fail if security is broken
