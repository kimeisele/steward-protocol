#!/usr/bin/env python3
"""
🛡️  ACID TEST: GAD-5500 INTEGRITY CHECK
Verifies that the Safe Evolution Loop actually works end-to-end.

Tests:
1. Scenario A (Toxic Payload): Engineer writes bad code → Auditor MUST reject
2. Scenario B (Golden Payload): Engineer writes good code → Auditor MUST pass → Archivist MUST commit
"""

import asyncio
import os
import shutil
import sys
from pathlib import Path

# Add current dir to Python path
sys.path.insert(0, "/home/user/steward-protocol")

from vibe_core.scheduling.task import Task
from steward.system_agents.engineer.cartridge_main import EngineerCartridge
from steward.system_agents.auditor.cartridge_main import AuditorCartridge
from steward.system_agents.archivist.cartridge_main import ArchivistCartridge

# Setup Dummy Environment
SANDBOX_DIR = "./workspaces/sandbox_test"
REPO_DIR = "./temp_repo_test"


def setup_env():
    """Create clean test directories"""
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)

    os.makedirs(SANDBOX_DIR)
    os.makedirs(REPO_DIR)

    # Init git in temp repo for Archivist test
    os.system(f"git init {REPO_DIR} > /dev/null 2>&1")
    os.system(
        f"cd {REPO_DIR} && git config user.email 'test@steward.eth' && git config user.name 'TestBot'"
    )
    print(f"✅ Test environment created: {SANDBOX_DIR}, {REPO_DIR}")


def cleanup():
    """Remove test directories"""
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)
    print("✅ Test cleanup complete")


def run_acid_test():
    """Run the acid test suite"""
    print("=" * 70)
    print("🛡️  STARTING ACID TEST: GAD-5500 INTEGRITY CHECK")
    print("=" * 70)

    setup_env()

    # 1. INITIALIZE AGENTS
    print("\n📐 Initializing agents...")
    engineer = EngineerCartridge()
    auditor = AuditorCartridge()
    archivist = ArchivistCartridge()
    print("✅ All agents initialized")

    all_passed = True

    # ====================================================
    # SCENARIO 1: THE TOXIC PAYLOAD (Bad Syntax)
    # ====================================================
    print("\n" + "=" * 70)
    print("🧪 TEST 1: TOXIC CODE INJECTION (Syntax Error)")
    print("=" * 70)

    # Step 1: Engineer writes bad code
    print("\n[Step 1] Engineer writes toxic code...")
    task_write_bad = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "path": "toxic.py",
            "content": "def broken_code(: print('Forgot args')",  # Syntax Error
        },
        task_id="t1",
        priority=1,
        created_at="now",
    )
    res_eng = engineer.process(task_write_bad)
    print(f"   Status: {res_eng['status']}")
    print(f"   File: {res_eng.get('path')}")

    # Step 2: Auditor Checks
    print("\n[Step 2] Auditor checks toxic code...")
    task_audit_bad = Task(
        agent_id="auditor",
        payload={"action": "verify_changes", "path": res_eng["path"]},
        task_id="t2",
        priority=1,
        created_at="now",
    )
    res_aud = auditor.process(task_audit_bad)

    if res_aud["passed"] is False:
        print(f"   ✅ SUCCESS: Auditor blocked toxic code")
        print(f"   Reason: {res_aud.get('reason')}")
        print(f"   Details: {res_aud.get('details')}")
    else:
        print(f"   ❌ FAILURE: Auditor let toxic code pass!")
        print(f"   Response: {res_aud}")
        all_passed = False

    # ====================================================
    # SCENARIO 2: THE GOLDEN PAYLOAD (Clean Code)
    # ====================================================
    print("\n" + "=" * 70)
    print("✨ TEST 2: GOLDEN CODE FLOW (Valid Code)")
    print("=" * 70)

    # Step 1: Engineer writes good code
    print("\n[Step 1] Engineer writes clean code...")
    task_write_good = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "path": "golden.py",
            "content": "def working_code():\n    print('Hello World')\n",
        },
        task_id="t3",
        priority=1,
        created_at="now",
    )
    res_eng_good = engineer.process(task_write_good)
    print(f"   Status: {res_eng_good['status']}")
    print(f"   File: {res_eng_good.get('path')}")

    # Step 2: Auditor Checks
    print("\n[Step 2] Auditor checks clean code...")
    task_audit_good = Task(
        agent_id="auditor",
        payload={"action": "verify_changes", "path": res_eng_good["path"]},
        task_id="t4",
        priority=1,
        created_at="now",
    )
    res_aud_good = auditor.process(task_audit_good)

    if res_aud_good["passed"] is True:
        print(f"   ✅ SUCCESS: Auditor passed valid code")
        print(f"   Stamp: {res_aud_good.get('stamp')}")
    else:
        print(f"   ❌ FAILURE: Auditor blocked valid code!")
        print(f"   Response: {res_aud_good}")
        all_passed = False

    # Step 3: Archivist Seals (Commit)
    print("\n[Step 3] Archivist seals code to git...")

    # Change to repo dir for git operations
    current_cwd = os.getcwd()
    try:
        # Create src directory in repo
        os.makedirs(f"{REPO_DIR}/src", exist_ok=True)

        # Change to repo for relative path safety check
        os.chdir(REPO_DIR)

        task_seal = Task(
            agent_id="archivist",
            payload={
                "action": "seal_history",
                "source_path": res_eng_good["path"],
                "dest_path": "src/golden.py",
                "audit_result": res_aud_good,
                "message": "Golden logic",
            },
            task_id="t5",
            priority=1,
            created_at="now",
        )

        res_arch = archivist.process(task_seal)

        if res_arch["status"] == "sealed":
            print(f"   ✅ SUCCESS: Archivist committed code")
            print(f"   Commit hash: {res_arch['commit']}")
            print(f"   Commit short: {res_arch['commit_short']}")
        else:
            print(f"   ❌ FAILURE: Archivist failed to seal")
            print(f"   Response: {res_arch}")
            all_passed = False

    except Exception as e:
        print(f"   ❌ EXCEPTION in Archivist: {e}")
        import traceback

        traceback.print_exc()
        all_passed = False
    finally:
        os.chdir(current_cwd)

    # ====================================================
    # SCENARIO 3: GATEKEEPER TEST (Auditor rejects → Archivist blocks)
    # ====================================================
    print("\n" + "=" * 70)
    print("🔒 TEST 3: GATEKEEPER TEST (Archivist blocks rejected code)")
    print("=" * 70)

    print("\n[Step 1] Trying to seal toxic code (should be blocked)...")

    try:
        os.chdir(REPO_DIR)
        os.makedirs(f"{REPO_DIR}/src", exist_ok=True)

        task_seal_bad = Task(
            agent_id="archivist",
            payload={
                "action": "seal_history",
                "source_path": res_eng["path"],
                "dest_path": "src/toxic.py",
                "audit_result": res_aud,  # Failed audit result
                "message": "Toxic code",
            },
            task_id="t6",
            priority=1,
            created_at="now",
        )

        res_arch_bad = archivist.process(task_seal_bad)

        if res_arch_bad["status"] == "rejected":
            print(f"   ✅ SUCCESS: Archivist blocked toxic code (gatekeeper works)")
            print(f"   Reason: {res_arch_bad.get('reason')}")
        else:
            print(f"   ❌ FAILURE: Archivist did not block toxic code!")
            print(f"   Response: {res_arch_bad}")
            all_passed = False

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        all_passed = False
    finally:
        os.chdir(current_cwd)

    # ====================================================
    # FINAL RESULT
    # ====================================================
    print("\n" + "=" * 70)
    cleanup()

    if all_passed:
        print("🎯 ACID TEST PASSED ✅")
        print("=" * 70)
        print("\nRESULT: System is WATERTIGHT")
        print("\n✅ Test 1: Auditor correctly blocked toxic code")
        print("✅ Test 2: Auditor passed clean code, Archivist committed")
        print("✅ Test 3: Gatekeeper blocked attempt to commit rejected code")
        print("\nThe Safe Evolution Loop (GAD-5500) is functioning correctly.")
        return 0
    else:
        print("❌ ACID TEST FAILED")
        print("=" * 70)
        print("\nRESULT: System has critical flaws")
        print("\nPlease review the failed test above.")
        return 1


if __name__ == "__main__":
    exit_code = run_acid_test()
    sys.exit(exit_code)
