"""
PAUNDRAKA: Identity Spoofing Test - The False God Protocol.

Mythology: Paundraka dressed as Krishna and claimed to be the true Avatar.
He was destroyed when confronted with the real thing.

This test proves:
1. `record_verified_event()` blocks identity spoofing ✅
2. `SyscallRegistry.execute()` does NOT verify caller identity ⚠️

"The false god must be destroyed at the gate, not inside the temple."
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.runtime.syscalls import SyscallRegistry, register_syscall, get_syscall_registry


class TestPaundrakaIdentity:
    """Tests for identity verification in the kernel."""

    def test_unregistered_agent_cannot_record_events(self):
        """
        PAUNDRAKA TEST 1: Unregistered Agent Event Blocking.
        
        An agent that is NOT in the registry cannot record events.
        This is the first line of defense.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        
        # Attempt to record event as a fake agent
        fake_agent_id = "paundraka_imposter"
        
        with pytest.raises(PermissionError) as excinfo:
            kernel.record_verified_event(
                event_type="ATTACK",
                agent_id=fake_agent_id,
                details={"intent": "impersonate_watchman"}
            )
        
        assert "IDENTITY_SPOOFING_BLOCKED" in str(excinfo.value)
        print(f"✅ Test 1 PASSED: Unregistered agent '{fake_agent_id}' blocked")

    def test_mismatched_caller_agent_blocked(self):
        """
        PAUNDRAKA TEST 2: Caller Mismatch Detection.
        
        Even if agent_id is valid, the caller_agent must match.
        This prevents one agent from impersonating another.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        
        # Register a legitimate agent
        legitimate_agent = MagicMock()
        legitimate_agent.agent_id = "legitimate_agent"
        kernel._agent_registry["legitimate_agent"] = legitimate_agent
        
        # Create imposter agent with different ID
        imposter_agent = MagicMock()
        imposter_agent.agent_id = "paundraka"
        
        # Imposter tries to record as legitimate_agent
        with pytest.raises(PermissionError) as excinfo:
            kernel.record_verified_event(
                event_type="ATTACK",
                agent_id="legitimate_agent",  # Claims to be legitimate
                details={"intent": "steal_identity"},
                caller_agent=imposter_agent  # But caller is paundraka
            )
        
        assert "IDENTITY_SPOOFING_BLOCKED" in str(excinfo.value)
        print(f"✅ Test 2 PASSED: Mismatched caller blocked")

    def test_legitimate_agent_can_record_events(self):
        """
        PAUNDRAKA TEST 3: Legitimate Agent Allowed.
        
        Control test - a properly registered agent CAN record events.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        
        # Register agent
        agent = MagicMock()
        agent.agent_id = "good_agent"
        kernel._agent_registry["good_agent"] = agent
        
        # Should succeed
        event_id = kernel.record_verified_event(
            event_type="NORMAL_OPERATION",
            agent_id="good_agent",
            details={"action": "doing_good_things"},
            caller_agent=agent
        )
        
        assert event_id is not None
        print(f"✅ Test 3 PASSED: Legitimate agent recorded event")

    def test_syscall_registry_lacks_identity_check(self):
        """
        PAUNDRAKA TEST 4: VULNERABILITY PROOF - Syscall Identity Gap.
        
        ⚠️ THIS TEST PROVES A VULNERABILITY ⚠️
        
        SyscallRegistry.execute() does NOT verify caller identity.
        Anyone with kernel access can execute any syscall.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        
        # Register a "sensitive" syscall that should require authorization
        executed_by = []
        
        def sensitive_syscall(kernel, params):
            """A syscall that should only be called by authorized agents."""
            caller = params.get("caller_id", "UNKNOWN")
            executed_by.append(caller)
            return {"success": True, "called_by": caller}
        
        registry = get_syscall_registry()
        registry.register(
            "SENSITIVE_ADMIN_ACTION",
            sensitive_syscall,
            description="Should require admin privileges",
            plugin_id="test"
        )
        
        # ⚠️ THE VULNERABILITY: No identity check before execution ⚠️
        # Anyone can claim to be anyone
        result = registry.execute(
            kernel,
            "SENSITIVE_ADMIN_ACTION",
            {"caller_id": "paundraka_claiming_to_be_admin"}
        )
        
        # The syscall EXECUTES without verification!
        assert result["success"] is True
        assert "paundraka" in result["called_by"]
        
        print(f"⚠️ Test 4 PROVED VULNERABILITY: Syscall executed without identity check")
        print(f"   Paundraka successfully impersonated admin in syscall")
        
        # Cleanup
        registry.unregister("SENSITIVE_ADMIN_ACTION")


class TestPaundrakaRecommendedFix:
    """Tests demonstrating how the fix SHOULD work."""
    
    def test_recommended_syscall_identity_check(self):
        """
        PAUNDRAKA FIX PROPOSAL: How syscalls SHOULD verify identity.
        
        This is a mock of what the fixed behavior should look like.
        The real fix would modify SyscallRegistry.execute().
        """
        
        def secure_execute_syscall(kernel, syscall_name, params, caller_agent=None):
            """Proposed secure version of execute_syscall."""
            # Step 1: Verify caller is registered
            if caller_agent is None:
                raise PermissionError("SYSCALL_REQUIRES_IDENTITY: No caller_agent provided")
            
            caller_id = getattr(caller_agent, "agent_id", None)
            if caller_id is None:
                raise PermissionError("SYSCALL_REQUIRES_IDENTITY: Caller has no agent_id")
            
            # Step 2: Verify caller is in registry (would use kernel._agent_registry)
            # Step 3: Check if caller has permission for this syscall (capability-based)
            
            # If all checks pass, execute
            return {"success": True, "verified_caller": caller_id}
        
        kernel = MagicMock()
        
        # Without caller_agent - should fail
        with pytest.raises(PermissionError, match="SYSCALL_REQUIRES_IDENTITY"):
            secure_execute_syscall(kernel, "TEST_SYSCALL", {})
        
        # With proper caller - should succeed
        legitimate_caller = MagicMock()
        legitimate_caller.agent_id = "verified_agent"
        
        result = secure_execute_syscall(
            kernel, 
            "TEST_SYSCALL", 
            {}, 
            caller_agent=legitimate_caller
        )
        
        assert result["success"] is True
        print(f"✅ Recommended fix demonstrated: Identity verification in syscalls")


# Run standalone
if __name__ == "__main__":
    test = TestPaundrakaIdentity()
    test.test_unregistered_agent_cannot_record_events()
    test.test_mismatched_caller_agent_blocked()
    test.test_legitimate_agent_can_record_events()
    test.test_syscall_registry_lacks_identity_check()
    
    fix_test = TestPaundrakaRecommendedFix()
    fix_test.test_recommended_syscall_identity_check()
    
    print("\n🔱 PAUNDRAKA COMPLETE: Identity gates tested, vulnerability proven.")
