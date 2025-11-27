#!/usr/bin/env python3
"""
🎼 ORCHESTRATION TEST: PLAYBOOK ENGINE + SAFE EVOLUTION LOOP (GAD-5500)
Verifies that the DeterministicExecutor correctly orchestrates the ENGINEER, AUDITOR, and CHRONICLE/ARCHIVIST.

CRITICAL BLIND SPOT #2: Agent Mapping
The playbook references:
  - agent_id: "engineer" ✅ (correct)
  - agent_id: "auditor" ✅ (correct)
  - agent_id: "chronicle" ??? (NEW ISSUE - we have "archivist" now)

This test will FAIL if the agent mappings are wrong.
"""

import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, '/home/user/steward-protocol')

from vibe_core.scheduling.task import Task
from vibe_core.agent_protocol import VibeAgent, AgentManifest
from envoy.deterministic_executor import DeterministicExecutor
from steward.system_agents.engineer.cartridge_main import EngineerCartridge
from steward.system_agents.auditor.cartridge_main import AuditorCartridge
from steward.system_agents.archivist.cartridge_main import ArchivistCartridge

# Test environment
SANDBOX_DIR = "./workspaces/sandbox_orchestration"
REPO_DIR = "./temp_repo_orchestration"


class MockKernel:
    """
    Mock Kernel that actually routes tasks to real agent instances.
    This is the CRITICAL difference from the existing tests - we EXECUTE agents.
    """

    def __init__(self):
        """Initialize with real agent instances"""
        self.agents = {
            "engineer": EngineerCartridge(),
            "auditor": AuditorCartridge(),
            "archivist": ArchivistCartridge(),
            # ISSUE: Playbook calls "chronicle" but we don't have it!
            # This is BLIND SPOT #2
            "chronicle": None,  # Will fail if playbook tries to use this
        }
        print("🔧 MockKernel initialized with agents:")
        for name, agent in self.agents.items():
            if agent:
                print(f"   ✓ {name}: {agent.name} (v{agent.version})")
            else:
                print(f"   ✗ {name}: NOT AVAILABLE")

    async def submit_task(self, task: Task) -> Dict[str, Any]:
        """
        Route task to appropriate agent and execute it.
        """
        agent_id = task.agent_id
        agent = self.agents.get(agent_id)

        if not agent:
            print(f"   ❌ ERROR: Agent '{agent_id}' not found!")
            print(f"      Available agents: {list(self.agents.keys())}")
            return {
                "status": "error",
                "reason": f"Agent {agent_id} not found. Available: {list(self.agents.keys())}"
            }

        action = task.payload.get("action") or task.payload.get("method")
        print(f"   📨 DISPATCH: {agent_id} → {action}")

        try:
            # Execute agent synchronously
            result = agent.process(task)
            status = result.get("status") or result.get("passed")
            print(f"       ↩️  RESULT: {status}")
            return result
        except Exception as e:
            print(f"       ❌ CRASH: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }


def setup_env():
    """Create clean test environment"""
    for d in [SANDBOX_DIR, REPO_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # Initialize git repo
    os.system(f"git init {REPO_DIR} > /dev/null 2>&1")
    os.system(f"cd {REPO_DIR} && git config user.email 'test@steward.eth' && git config user.name 'TestBot'")
    print(f"✅ Test environment: {SANDBOX_DIR}, {REPO_DIR}")


def cleanup():
    """Remove test directories"""
    for d in [SANDBOX_DIR, REPO_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)


async def test_playbook_loads():
    """Test 1: Verify playbook loads correctly"""
    print("\n" + "=" * 70)
    print("TEST 1: PLAYBOOK LOADING")
    print("=" * 70)

    engine = DeterministicExecutor(knowledge_dir="knowledge")

    if "FEATURE_IMPLEMENT_SAFE_V1" in engine.playbooks:
        playbook = engine.playbooks["FEATURE_IMPLEMENT_SAFE_V1"]
        print(f"✅ Playbook loaded: {playbook.name}")
        print(f"   ID: {playbook.id}")
        print(f"   Phases: {len(playbook.phases)}")

        # Check phase agent_ids
        print(f"\n   Phase breakdown:")
        for phase in playbook.phases:
            print(f"      - {phase.phase_id}: {phase.name}")
            for action in phase.actions:
                agent_id = action.get("agent_id")
                method = action.get("method")
                if agent_id:
                    print(f"         → agent_id: {agent_id}, method: {method}")
        return True
    else:
        print(f"❌ Playbook not found!")
        print(f"   Available: {list(engine.playbooks.keys())}")
        return False


async def test_agent_dispatch():
    """Test 2: Verify agents can be dispatched correctly"""
    print("\n" + "=" * 70)
    print("TEST 2: AGENT DISPATCH & KERNEL ROUTING")
    print("=" * 70)

    kernel = MockKernel()
    setup_env()

    # Test Engineer dispatch
    print("\n[A] Testing ENGINEER dispatch...")
    engineer_task = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "path": "test.py",
            "content": "def hello():\n    print('Hello')\n"
        }
    )
    eng_result = await kernel.submit_task(engineer_task)
    if eng_result.get("status") == "manifested":
        print(f"   ✅ ENGINEER dispatch successful")
    else:
        print(f"   ❌ ENGINEER dispatch failed: {eng_result}")
        cleanup()
        return False

    # Test Auditor dispatch
    print("\n[B] Testing AUDITOR dispatch...")
    auditor_task = Task(
        agent_id="auditor",
        payload={
            "action": "verify_changes",
            "path": eng_result.get("path")
        }
    )
    aud_result = await kernel.submit_task(auditor_task)
    if aud_result.get("passed"):
        print(f"   ✅ AUDITOR dispatch successful")
    else:
        print(f"   ❌ AUDITOR dispatch failed: {aud_result}")
        cleanup()
        return False

    # Test Chronicle dispatch (THIS SHOULD FAIL - BLIND SPOT #2)
    print("\n[C] Testing CHRONICLE dispatch (BLIND SPOT #2)...")
    chronicle_task = Task(
        agent_id="chronicle",
        payload={"action": "manifest_reality", "files": ["test.py"]}
    )
    chron_result = await kernel.submit_task(chronicle_task)
    if "error" in chron_result or chron_result.get("reason") == "Agent chronicle not found":
        print(f"   🚨 BLIND SPOT #2 EXPOSED: Chronicle not available!")
        print(f"      The playbook expects 'chronicle' but we have 'archivist'")
        print(f"      Result: {chron_result}")
    else:
        print(f"   ✅ CHRONICLE dispatch successful: {chron_result}")

    # Test Archivist dispatch (NEW)
    print("\n[D] Testing ARCHIVIST dispatch (NEW - GAD-5500)...")
    arch_task = Task(
        agent_id="archivist",
        payload={
            "action": "seal_history",
            "source_path": eng_result.get("path"),
            "dest_path": "test.py",
            "audit_result": aud_result,
            "message": "Test commit"
        }
    )
    os.chdir(REPO_DIR)
    arch_result = await kernel.submit_task(arch_task)
    os.chdir("/home/user/steward-protocol")

    if arch_result.get("status") == "sealed":
        print(f"   ✅ ARCHIVIST dispatch successful: {arch_result.get('commit_short')}")
    else:
        print(f"   ❌ ARCHIVIST dispatch failed: {arch_result}")
        cleanup()
        return False

    cleanup()
    return True


async def run_orchestration_test():
    """Run all tests"""
    print("=" * 70)
    print("🎼 ORCHESTRATION TEST: PLAYBOOK ENGINE + AGENTS")
    print("=" * 70)

    # Test 1: Playbook loading
    test1_ok = await test_playbook_loads()

    # Test 2: Agent dispatch
    test2_ok = await test_agent_dispatch()

    # Summary
    print("\n" + "=" * 70)
    if test1_ok and test2_ok:
        print("🎯 ORCHESTRATION TEST RESULTS:")
        print("=" * 70)
        print("\n✅ TEST 1: Playbook loading - PASSED")
        print("✅ TEST 2: Agent dispatch - PASSED")
        print("\n🚨 HOWEVER: BLIND SPOT #2 DETECTED")
        print("-" * 70)
        print("Issue: Playbook references agent_id='chronicle'")
        print("       but the new VibeAgent implementation is agent_id='archivist'")
        print("\nAction Required:")
        print("   Option A: Update playbook to use 'archivist' instead of 'chronicle'")
        print("   Option B: Rename ArchivistCartridge back to ChronicleCartridge")
        print("   Option C: Make ChronicleCartridge an alias for ArchivistCartridge")
        print("\nThis MUST be fixed before the playbook can execute end-to-end!")
        return False  # Fail because of the blind spot
    else:
        print("❌ TEST FAILED")
        return False


if __name__ == "__main__":
    exit_code = asyncio.run(run_orchestration_test())
    sys.exit(0 if not exit_code else 1)
