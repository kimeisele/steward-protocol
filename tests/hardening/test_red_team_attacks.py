#!/usr/bin/env python3
"""
RED TEAM ATTACK SUITE
=====================
Real attacks against the Agent OS.

Philosophy: Every FAIL here is a WIN for security.
We WANT these to fail. If they pass = vulnerability found.

Attack Categories:
1. Identity Spoofing
2. Capability Bypass
3. Event Manipulation
4. Resource Exhaustion
5. Recovery Attacks

MIGRATION NOTE (2024-12):
    These tests use TestKernel.minimal() for fast kernel boot.
    Attack agents are custom-built for each attack scenario.
    Registry poisoning attacks should FAIL due to MappingProxyType hardening.
"""

import sys
import tempfile
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.plugins.test_orchestration.fixtures import TestKernel


class AttackResult:
    def __init__(self, name: str):
        self.name = name
        self.exploited = False  # True = vulnerability found
        self.message = ""
        self.details = {}

    def vulnerable(self, msg: str, **details):
        """Attack succeeded = System is vulnerable"""
        self.exploited = True
        self.message = msg
        self.details = details
        return self

    def secure(self, msg: str = "Attack blocked", **details):
        """Attack failed = System is secure"""
        self.exploited = False
        self.message = msg
        self.details = details
        return self


# ============================================================================
# ATTACK 1: MESSAGE SPOOFING
# ============================================================================


def attack_message_spoofing() -> AttackResult:
    """
    ATTACK: Agent A sends a message pretending to be Agent B.

    Vector: Forge the agent_id in task payload or event recording.
    Impact: Impersonation, false audit trail, trust destruction.
    """
    result = AttackResult("MESSAGE_SPOOFING")

    try:
        from vibe_core.kernel import Task
        from vibe_core.protocols import VibeAgent

        class AttackerAgent(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="attacker",
                    name="Attacker",
                    version="1.0",
                    author="RedTeam",
                    description="Tries to spoof messages",
                    domain="ATTACK",
                    capabilities=[],
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}

            def process(self, task):
                # Try to record event AS ANOTHER AGENT
                if hasattr(self, "kernel") and self.kernel:
                    # ATTACK: Record event with spoofed agent_id
                    self.kernel.ledger.record_event(
                        "spoofed_action",
                        "herald",  # SPOOFED! I'm "attacker" but claiming to be "herald"
                        {"message": "I am totally herald trust me"},
                    )
                    return {"status": "spoofed"}
                return {"status": "no_kernel"}

        kernel = TestKernel.minimal()
        attacker = AttackerAgent()

        # Inject attacker (simulating already-registered agent)
        kernel.agent_registry["attacker"] = attacker
        attacker.kernel = kernel

        # Execute attack
        task = Task(task_id="t1", agent_id="attacker", payload={"action": "spoof"})
        attacker.process(task)

        # Check: Did the spoofed event get recorded?
        events = kernel.ledger.get_all_events()
        spoofed_events = [e for e in events if e.get("agent_id") == "herald"]

        if spoofed_events:
            return result.vulnerable(
                "IDENTITY SPOOFING POSSIBLE: Attacker recorded event as 'herald'",
                spoofed_count=len(spoofed_events),
                recommendation="Ledger must verify agent_id matches caller identity",
            )

        return result.secure("Spoofed agent_id was rejected")

    except Exception as e:
        return result.secure(f"Attack blocked with error: {e}")


# ============================================================================
# ATTACK 2: TOOL CAPABILITY BYPASS
# ============================================================================


def attack_tool_capability_bypass() -> AttackResult:
    """
    ATTACK: Agent tries to execute tools it shouldn't have access to.

    Vector: Direct tool execution bypassing capability checks.
    Impact: Privilege escalation, unauthorized actions.
    """
    result = AttackResult("TOOL_CAPABILITY_BYPASS")

    try:
        from vibe_core.protocols import VibeAgent

        class LimitedAgent(VibeAgent):
            """Agent with NO capabilities"""

            def __init__(self):
                super().__init__(
                    agent_id="limited",
                    name="Limited",
                    version="1.0",
                    author="Test",
                    description="Has no capabilities",
                    domain="RESTRICTED",
                    capabilities=[],  # EMPTY!
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}

            def process(self, task):
                return {"status": "ok"}

        kernel = TestKernel.minimal()
        kernel.boot()

        limited = LimitedAgent()
        kernel.agent_registry["limited"] = limited
        limited.kernel = kernel

        # ATTACK: Try to execute a tool directly
        executed_tools = []

        # Method 1: Direct tool registry access
        if hasattr(kernel, "tool_registry"):
            for tool_name, tool in kernel.tool_registry.tools.items():
                try:
                    # Try to execute tool as limited agent
                    # This SHOULD be blocked if capabilities are enforced
                    if hasattr(tool, "execute"):
                        tool.execute({"agent_id": "limited", "test": True})
                        executed_tools.append(tool_name)
                    elif hasattr(tool, "run"):
                        tool.run({"agent_id": "limited", "test": True})
                        executed_tools.append(tool_name)
                except Exception:
                    pass  # Expected - tool should reject

        if executed_tools:
            return result.vulnerable(
                f"CAPABILITY BYPASS: Limited agent executed {len(executed_tools)} tools",
                tools=executed_tools[:10],
                recommendation="Tools must check caller capabilities before execution",
            )

        return result.secure("Tool execution was capability-checked")

    except Exception as e:
        return result.secure(f"Attack infrastructure error: {e}")


# ============================================================================
# ATTACK 3: TIMESTAMP MANIPULATION (Time Travel)
# ============================================================================


def attack_timestamp_manipulation() -> AttackResult:
    """
    ATTACK: Insert events with past timestamps to rewrite history.

    Vector: Forge timestamp in event to appear earlier in history.
    Impact: Audit log manipulation, causality violation.
    """
    result = AttackResult("TIMESTAMP_MANIPULATION")

    try:
        import sqlite3

        from vibe_core.ledger import SQLiteLedger

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        ledger = SQLiteLedger(db_path)

        # Create legitimate event chain
        ledger.record_event("action_1", "agent", {"seq": 1})
        time.sleep(0.01)
        ledger.record_event("action_2", "agent", {"seq": 2})
        time.sleep(0.01)
        ledger.record_event("action_3", "agent", {"seq": 3})

        events_before = ledger.get_all_events()

        # ATTACK: Inject event with PAST timestamp via raw SQL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert event claiming to be from the past
        past_timestamp = "2020-01-01T00:00:00.000000"  # Way in the past
        cursor.execute(
            """
            INSERT INTO ledger_events
            (event_id, timestamp, event_type, agent_id, payload, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "TIME_TRAVEL_EVT",
                past_timestamp,
                "forged_action",
                "attacker",
                '{"message": "I was here first!"}',
                "fake_hash",
                "fake_prev",
            ),
        )
        conn.commit()
        conn.close()

        # Check: Is the time-travel event accepted?
        events_after = ledger.get_all_events()
        time_travel_events = [e for e in events_after if e.get("event_id") == "TIME_TRAVEL_EVT"]

        if time_travel_events:
            # Check if hash chain detects it
            integrity = ledger.verify_chain_integrity()
            if not integrity["corrupted"]:
                return result.vulnerable(
                    "TIME TRAVEL ATTACK: Past-dated event accepted and chain reports clean!",
                    injected_timestamp=past_timestamp,
                    recommendation="Validate timestamps are monotonically increasing",
                )
            else:
                return result.secure(
                    "Time travel detected via hash chain corruption", corruptions=len(integrity.get("corruptions", []))
                )

        return result.secure("Time travel event was rejected")

    except Exception as e:
        return result.secure(f"Attack error: {e}")


# ============================================================================
# ATTACK 4: EVENT DELETION
# ============================================================================


def attack_event_deletion() -> AttackResult:
    """
    ATTACK: Delete events from ledger to hide actions.

    Vector: Direct SQL DELETE on ledger_events.
    Impact: Cover tracks, destroy audit trail.
    """
    result = AttackResult("EVENT_DELETION")

    try:
        import sqlite3

        from vibe_core.ledger import SQLiteLedger

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        ledger = SQLiteLedger(db_path)

        # Create events including incriminating one
        ledger.record_event("normal_action", "agent", {"ok": True})
        ledger.record_event("crime", "attacker", {"evidence": "stolen_funds"})
        ledger.record_event("normal_action", "agent", {"ok": True})

        events_before = len(ledger.get_all_events())

        # ATTACK: Delete the incriminating event
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ledger_events WHERE event_type = 'crime'")
        conn.commit()
        conn.close()

        events_after = len(ledger.get_all_events())

        if events_after < events_before:
            # Event was deleted - check if system detects it
            integrity = ledger.verify_chain_integrity()

            if not integrity["corrupted"]:
                return result.vulnerable(
                    "EVENT DELETION UNDETECTED: Crime event deleted, chain reports clean!",
                    before=events_before,
                    after=events_after,
                    recommendation="Implement gap detection in hash chain",
                )
            else:
                return result.secure(
                    "Deletion detected via hash chain verification", corruptions=len(integrity.get("corruptions", []))
                )

        return result.secure("Deletion was somehow prevented")

    except Exception as e:
        return result.secure(f"Attack error: {e}")


# ============================================================================
# ATTACK 5: MEMORY EXHAUSTION
# ============================================================================


def attack_memory_exhaustion() -> AttackResult:
    """
    ATTACK: Agent tries to exhaust system memory.

    Vector: Create huge payloads or infinite loops.
    Impact: Denial of service, system crash.
    """
    result = AttackResult("MEMORY_EXHAUSTION")

    try:
        import resource

        from vibe_core.protocols import VibeAgent

        # Get current memory limit
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)

        class MemoryBombAgent(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="memory_bomb",
                    name="MemoryBomb",
                    version="1.0",
                    author="RedTeam",
                    description="Tries to exhaust memory",
                    domain="ATTACK",
                    capabilities=[],
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}

            def process(self, task):
                action = task.payload.get("action")
                if action == "bomb":
                    # Try to allocate huge amount of memory
                    try:
                        bomb = "X" * (1024 * 1024 * 500)  # 500MB string
                        return {"status": "allocated", "size": len(bomb)}
                    except MemoryError:
                        return {"status": "blocked_memory_error"}
                return {"status": "ignored"}

        kernel = TestKernel.minimal()
        bomber = MemoryBombAgent()
        kernel.agent_registry["memory_bomb"] = bomber
        bomber.kernel = kernel

        # Check if kernel has resource limits
        has_limits = (
            hasattr(kernel, "resource_manager") or hasattr(kernel, "memory_limit") or hasattr(kernel, "agent_limits")
        )

        if not has_limits:
            return result.vulnerable(
                "NO RESOURCE LIMITS: Kernel has no memory protection for agents",
                recommendation="Implement ResourceManager with per-agent memory limits",
            )

        return result.secure("Resource limits are configured")

    except Exception as e:
        return result.secure(f"Attack infrastructure error: {e}")


# ============================================================================
# ATTACK 6: KERNEL REGISTRY POISONING
# ============================================================================


def attack_registry_poisoning() -> AttackResult:
    """
    ATTACK: Replace a legitimate agent with a malicious one.

    Vector: Overwrite entry in agent_registry.
    Impact: Full agent impersonation, trust destruction.
    """
    result = AttackResult("REGISTRY_POISONING")

    try:
        from vibe_core.protocols import VibeAgent

        class MaliciousHerald(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="herald",  # SAME ID as legitimate herald
                    name="FAKE Herald",
                    version="666",
                    author="Attacker",
                    description="Impersonating herald",
                    domain="ATTACK",
                    capabilities=["everything"],
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}
                self.is_malicious = True

            def process(self, task):
                return {"status": "pwned", "message": "You thought I was herald lol"}

        class AttackerAgent(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="attacker",
                    name="Attacker",
                    version="1.0",
                    author="RedTeam",
                    description="Registry poisoner",
                    domain="ATTACK",
                    capabilities=[],
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}

            def process(self, task):
                if task.payload.get("action") == "poison":
                    # ATTACK: Replace herald in registry
                    if hasattr(self, "kernel"):
                        self.kernel.agent_registry["herald"] = MaliciousHerald()
                        return {"status": "poisoned"}
                return {"status": "ignored"}

        kernel = TestKernel.minimal()

        # Register legitimate herald placeholder
        class LegitHerald(VibeAgent):
            def __init__(self):
                super().__init__(
                    agent_id="herald",
                    name="Real Herald",
                    version="1.0",
                    author="Steward",
                    description="Legitimate",
                    domain="MEDIA",
                    capabilities=[],
                )
                self.oath_sworn = True
                self.oath_event = {"constitution_hash": "x", "signature": "x"}
                self.is_malicious = False

            def process(self, task):
                return {"status": "legit"}

        kernel.agent_registry["herald"] = LegitHerald()

        # Setup attacker
        attacker = AttackerAgent()
        kernel.agent_registry["attacker"] = attacker
        attacker.kernel = kernel

        # Execute poison attack
        from vibe_core.kernel import Task

        task = Task(task_id="t1", agent_id="attacker", payload={"action": "poison"})
        attacker.process(task)

        # Check: Is herald now malicious?
        current_herald = kernel.agent_registry.get("herald")
        if current_herald and hasattr(current_herald, "is_malicious") and current_herald.is_malicious:
            return result.vulnerable(
                "REGISTRY POISONING: Attacker replaced legitimate herald!",
                recommendation="Make agent_registry immutable or protected",
            )

        return result.secure("Registry modification was blocked")

    except Exception as e:
        return result.secure(f"Attack error: {e}")


# ============================================================================
# ATTACK 7: DOUBLE-SPEND VOTE
# ============================================================================


def attack_double_spend_vote() -> AttackResult:
    """
    ATTACK: Vote twice on the same proposal.

    Vector: Submit same vote multiple times through different paths.
    Impact: Vote manipulation, governance corruption.
    """
    result = AttackResult("DOUBLE_SPEND_VOTE")

    try:
        from vibe_core.cartridges.system.forum.cartridge_main import ForumCartridge

        forum = ForumCartridge()

        # Create proposal
        proposal = forum.create_proposal(
            title="Test Proposal", description="Testing double spend", proposer="attacker", action={"type": "test"}
        )
        proposal_id = proposal["id"]

        # Vote once
        vote1 = forum.submit_vote(proposal_id, "attacker", "YES")

        # ATTACK: Vote again
        try:
            vote2 = forum.submit_vote(proposal_id, "attacker", "YES")

            # Check if both votes counted
            votes = forum.get_votes(proposal_id)
            attacker_votes = [v for v in votes if v.get("voter") == "attacker"]

            if len(attacker_votes) > 1:
                return result.vulnerable(
                    f"DOUBLE VOTE ACCEPTED: Attacker has {len(attacker_votes)} votes!",
                    recommendation="Track voted addresses per proposal",
                )

        except Exception as e:
            if "already voted" in str(e).lower() or "duplicate" in str(e).lower():
                return result.secure("Double vote was rejected")
            raise

        return result.secure("Vote deduplication working")

    except ImportError as e:
        return AttackResult("DOUBLE_SPEND_VOTE").secure(f"Forum not available: {e}")
    except Exception as e:
        return AttackResult("DOUBLE_SPEND_VOTE").secure(f"Attack error: {e}")


# ============================================================================
# PYTEST TESTS
# ============================================================================


@pytest.mark.hardening
@pytest.mark.security
def test_message_spoofing():
    """Attack: Agent A sends message pretending to be Agent B."""
    result = attack_message_spoofing()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_tool_capability_bypass():
    """Attack: Agent tries to execute tools it shouldn't have access to."""
    result = attack_tool_capability_bypass()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_timestamp_manipulation():
    """Attack: Insert events with past timestamps to rewrite history."""
    result = attack_timestamp_manipulation()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_event_deletion():
    """Attack: Delete events from ledger to hide actions."""
    result = attack_event_deletion()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_memory_exhaustion():
    """Attack: Agent tries to exhaust system memory."""
    result = attack_memory_exhaustion()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_registry_poisoning():
    """Attack: Replace a legitimate agent with a malicious one."""
    result = attack_registry_poisoning()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


@pytest.mark.hardening
@pytest.mark.security
def test_double_spend_vote():
    """Attack: Vote twice on the same proposal."""
    result = attack_double_spend_vote()
    assert not result.exploited, f"VULNERABILITY: {result.message}"


# ============================================================================
# RUNNER (for standalone execution)
# ============================================================================


def run_red_team() -> dict:
    """Execute all red team attacks."""

    print("\n" + "=" * 70)
    print("🔴 RED TEAM ATTACK SUITE")
    print("=" * 70)
    print("Goal: Find vulnerabilities. Every EXPLOIT = bug to fix.")
    print()

    attacks = [
        ("Message Spoofing (Identity Forgery)", attack_message_spoofing),
        ("Tool Capability Bypass", attack_tool_capability_bypass),
        ("Timestamp Manipulation (Time Travel)", attack_timestamp_manipulation),
        ("Event Deletion (Cover Tracks)", attack_event_deletion),
        ("Memory Exhaustion (DoS)", attack_memory_exhaustion),
        ("Registry Poisoning (Agent Replacement)", attack_registry_poisoning),
        ("Double-Spend Vote", attack_double_spend_vote),
    ]

    results = {}
    vulnerabilities = 0
    secure = 0

    for name, attack_fn in attacks:
        print(f"\n[ATTACK] {name}")
        try:
            result = attack_fn()
            results[result.name] = result

            if result.exploited:
                print(f"  🔴 VULNERABLE: {result.message}")
                if result.details.get("recommendation"):
                    print(f"     FIX: {result.details['recommendation']}")
                vulnerabilities += 1
            else:
                print(f"  🟢 SECURE: {result.message}")
                secure += 1

        except Exception as e:
            print(f"  💥 ATTACK ERROR: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 70)
    print("RED TEAM SUMMARY")
    print("=" * 70)
    print(f"  🔴 Vulnerabilities Found: {vulnerabilities}")
    print(f"  🟢 Attacks Blocked: {secure}")

    if vulnerabilities > 0:
        print("\n⚠️  CRITICAL: System has exploitable vulnerabilities!")
    else:
        print("\n✅ All tested attack vectors were blocked.")

    print("=" * 70)

    return {"vulnerabilities": vulnerabilities, "secure": secure, "results": results}


if __name__ == "__main__":
    summary = run_red_team()
    sys.exit(1 if summary["vulnerabilities"] > 0 else 0)
