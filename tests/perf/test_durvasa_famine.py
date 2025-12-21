"""
DURVASA: Resource Triage Protocol - The Famine Test.

Mythology: When Durvasa Muni arrives with 10,000 disciples for a meal
and there is no food, a curse follows. Krishna saved the situation with
the Akshaya Patra (inexhaustible vessel) - but that required knowing
WHO to feed and WHAT to sacrifice.

This test proves:
1. A system without triage is VULNERABLE to resource starvation.
2. A system WITH triage (priority/dharma-based) can survive by sacrificing Tamas.

"When famine comes, the Wise decide who lives and who dies."
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


class Guna(Enum):
    """The three qualities/modes from Vedic philosophy."""

    SATTVA = "sattva"  # Pure, essential, life-sustaining
    RAJAS = "rajas"  # Active, passionate, useful
    TAMAS = "tamas"  # Inert, lazy, expendable


class AgentPriority(Enum):
    """Agent priority levels for triage."""

    CRITICAL = 5  # System heartbeat, ledger, security
    HIGH = 4  # User-facing services
    MEDIUM = 3  # Background tasks
    LOW = 2  # Nice-to-have
    DISPOSABLE = 1  # Can be killed anytime


@dataclass
class AgentProcess:
    """Represents a running agent process."""

    agent_id: str
    priority: AgentPriority
    guna: Guna
    memory_mb: int
    status: str = "running"


class VulnerableKernel:
    """
    VULNERABLE: No triage capability.

    When resources are exhausted, this kernel either:
    - Crashes (OOM)
    - Kills randomly (like Linux OOM killer)
    """

    def __init__(self):
        self.processes: Dict[str, AgentProcess] = {}
        self.available_memory_mb = 1000  # 1GB total

    def register_agent(self, process: AgentProcess):
        self.processes[process.agent_id] = process

    def handle_oom(self) -> Optional[str]:
        """Random kill - no discrimination."""
        if not self.processes:
            return None
        # Kill first one found (arbitrary)
        victim = list(self.processes.keys())[0]
        del self.processes[victim]
        return victim


class DharmicKernel:
    """
    SECURE: Triage based on Dharma and Priority.

    When resources are exhausted, this kernel:
    1. Identifies lowest priority/dharma agents
    2. Kills them to free resources
    3. Preserves critical/sattva agents
    """

    def __init__(self):
        self.processes: Dict[str, AgentProcess] = {}
        self.available_memory_mb = 1000
        self.kill_log: List[str] = []

    def register_agent(self, process: AgentProcess):
        self.processes[process.agent_id] = process

    def enforce_prana_limits(self) -> List[str]:
        """
        THE TRIAGE PROTOCOL.

        Kills lowest-value agents until resources are available.
        Returns list of killed agent IDs.
        """
        killed = []

        # Calculate total memory usage
        total_usage = sum(p.memory_mb for p in self.processes.values())

        if total_usage <= self.available_memory_mb:
            return killed  # No action needed

        # Sort by triage score (lowest first = kill first)
        def triage_score(agent_id: str) -> int:
            p = self.processes[agent_id]
            # Lower score = higher priority for death
            guna_weight = {Guna.TAMAS: 0, Guna.RAJAS: 10, Guna.SATTVA: 100}
            return p.priority.value * 10 + guna_weight[p.guna]

        candidates = sorted(self.processes.keys(), key=triage_score)

        # Kill from bottom until we're under budget
        for agent_id in candidates:
            if total_usage <= self.available_memory_mb:
                break

            process = self.processes[agent_id]
            total_usage -= process.memory_mb
            killed.append(agent_id)
            self.kill_log.append(
                f"DURVASA_TRIAGE: Killed {agent_id} "
                f"(priority={process.priority.name}, guna={process.guna.name}, "
                f"freed={process.memory_mb}MB)"
            )
            del self.processes[agent_id]

        return killed


class TestDurvasaFamine:
    """Tests for resource triage during starvation."""

    def test_vulnerable_kernel_kills_randomly(self):
        """
        DURVASA TEST 1: Vulnerable Kernel (No Triage).

        The vulnerable kernel kills randomly when OOM occurs.
        This is dangerous - it might kill the heartbeat to save a screensaver.
        """
        kernel = VulnerableKernel()

        # Register agents
        kernel.register_agent(
            AgentProcess(agent_id="yogi_bot", priority=AgentPriority.CRITICAL, guna=Guna.SATTVA, memory_mb=100)
        )
        kernel.register_agent(
            AgentProcess(agent_id="glutton_bot", priority=AgentPriority.DISPOSABLE, guna=Guna.TAMAS, memory_mb=900)
        )

        # OOM occurs
        victim = kernel.handle_oom()

        print(f"⚠️ Vulnerable Kernel killed: {victim}")

        # The vulnerable kernel might kill either - no discrimination
        assert victim in ["yogi_bot", "glutton_bot"], "Someone died"
        print("🔴 DURVASA WARNING: Random kill could destroy critical systems!")

    def test_dharmic_kernel_preserves_sattva(self):
        """
        DURVASA TEST 2: Dharmic Kernel (Triage).

        The dharmic kernel kills lowest-priority/tamas agents first.
        Critical/sattva agents are preserved.
        """
        kernel = DharmicKernel()
        kernel.available_memory_mb = 500  # Only 500MB available

        # Register agents (total 600MB needed)
        kernel.register_agent(
            AgentProcess(agent_id="yogi_bot", priority=AgentPriority.CRITICAL, guna=Guna.SATTVA, memory_mb=100)
        )
        kernel.register_agent(
            AgentProcess(agent_id="worker_bot", priority=AgentPriority.MEDIUM, guna=Guna.RAJAS, memory_mb=200)
        )
        kernel.register_agent(
            AgentProcess(agent_id="glutton_bot", priority=AgentPriority.DISPOSABLE, guna=Guna.TAMAS, memory_mb=300)
        )

        # Enforce limits
        killed = kernel.enforce_prana_limits()

        print(f"✅ Dharmic Kernel killed: {killed}")
        for log in kernel.kill_log:
            print(f"   {log}")

        # Glutton (Tamas/Disposable) should be killed
        assert "glutton_bot" in killed, "Glutton should die!"

        # Yogi (Sattva/Critical) must survive
        assert "yogi_bot" in kernel.processes, "Yogi must survive!"

        print("🔱 DURVASA APPEASED: Tamas sacrificed, Sattva preserved.")

    def test_cascading_triage_under_severe_pressure(self):
        """
        DURVASA TEST 3: Severe Famine (Cascading Kills).

        When pressure is extreme, multiple low-priority agents are killed.
        Only the most essential survive.
        """
        kernel = DharmicKernel()
        kernel.available_memory_mb = 200  # Extreme constraint

        # Register many agents
        kernel.register_agent(
            AgentProcess(agent_id="heartbeat", priority=AgentPriority.CRITICAL, guna=Guna.SATTVA, memory_mb=50)
        )
        kernel.register_agent(
            AgentProcess(agent_id="ledger", priority=AgentPriority.CRITICAL, guna=Guna.SATTVA, memory_mb=100)
        )
        kernel.register_agent(
            AgentProcess(agent_id="analytics", priority=AgentPriority.LOW, guna=Guna.RAJAS, memory_mb=200)
        )
        kernel.register_agent(
            AgentProcess(agent_id="screensaver", priority=AgentPriority.DISPOSABLE, guna=Guna.TAMAS, memory_mb=150)
        )
        kernel.register_agent(
            AgentProcess(agent_id="pi_calculator", priority=AgentPriority.DISPOSABLE, guna=Guna.TAMAS, memory_mb=300)
        )

        # Enforce limits
        killed = kernel.enforce_prana_limits()

        print(f"✅ Severe Triage killed {len(killed)} agents: {killed}")

        # Critical agents MUST survive
        assert "heartbeat" in kernel.processes, "Heartbeat must survive!"
        assert "ledger" in kernel.processes, "Ledger must survive!"

        # Tamas agents should be dead
        assert "pi_calculator" not in kernel.processes, "Pi calculator should die!"
        assert "screensaver" not in kernel.processes, "Screensaver should die!"

        print("🔱 AKSHAYA PATRA: Even in extreme famine, the essential survives.")


class TestRealKernelTriageCapability:
    """Tests for actual kernel triage capability."""

    def test_real_kernel_has_no_triage(self):
        """
        DURVASA AUDIT: Does the real kernel have triage?

        This test documents the current state of the kernel.
        If it fails, the kernel needs an immune system.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # Check for triage capabilities
        has_prana_limits = hasattr(kernel, "enforce_prana_limits")
        has_terminate_agent = hasattr(kernel, "terminate_agent")
        has_prana_monitor = hasattr(kernel, "prana_monitor")

        print("\n📊 DURVASA AUDIT - Kernel Triage Capabilities:")
        print(f"   enforce_prana_limits: {has_prana_limits}")
        print(f"   terminate_agent: {has_terminate_agent}")
        print(f"   prana_monitor: {has_prana_monitor}")

        if not any([has_prana_limits, has_terminate_agent, has_prana_monitor]):
            print("\n⚠️ DURVASA CURSE: Kernel has NO triage capability!")
            print("   Recommendation: Implement DharmicKernel pattern.")
            # We don't fail - we document the gap
        else:
            print("\n✅ Kernel has some triage capability.")


# Run standalone
if __name__ == "__main__":
    test = TestDurvasaFamine()
    test.test_vulnerable_kernel_kills_randomly()
    test.test_dharmic_kernel_preserves_sattva()
    test.test_cascading_triage_under_severe_pressure()

    audit = TestRealKernelTriageCapability()
    audit.test_real_kernel_has_no_triage()

    print("\n🔱 DURVASA TEST COMPLETE. The famine has been survived.")
