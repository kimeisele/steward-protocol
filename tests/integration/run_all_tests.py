#!/usr/bin/env python3
"""
Integration Test Runner (No pytest required)
==============================================

Runs all integration tests and reports results.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.process_manager import ProcessManager
from vibe_core.lineage import LineageChain, LineageEventType
import tempfile
import os


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, name, test_func):
        """Run a single test and track results."""
        try:
            test_func()
            print(f"✅ {name}")
            self.passed += 1
        except AssertionError as e:
            error_msg = str(e) if str(e) else repr(e)
            print(f"❌ {name}: {error_msg}")
            self.failed += 1
            self.errors.append((name, error_msg))
            import traceback

            traceback.print_exc()
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e)
            print(f"💥 {name}: {error_msg}")
            self.failed += 1
            self.errors.append((name, error_msg))
            import traceback

            traceback.print_exc()

    def report(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print(f"TESTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nFAILURES:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print("=" * 70)
        return self.failed == 0


# =============================================================================
# TEST: Kernel Boot
# =============================================================================


def test_kernel_boots():
    """Test that kernel can boot without crashing."""
    kernel = RealVibeKernel()
    assert kernel is not None
    # Status is an Enum, check its value
    status_value = (
        kernel._status.value
        if hasattr(kernel._status, "value")
        else str(kernel._status)
    )
    assert status_value in ["INIT", "RUNNING", "BOOTED", "STOPPED"]


def test_kernel_has_parampara():
    """Test that kernel has Parampara lineage chain."""
    kernel = RealVibeKernel()
    assert kernel.lineage is not None

    # Verify Genesis Block exists
    genesis = kernel.lineage.get_genesis_block()
    assert genesis is not None
    # event_type is a string, not an Enum
    assert genesis.event_type == "GENESIS"


def test_kernel_has_economic_substrate():
    """Test that kernel can access CivicBank (lazy-loaded)."""
    kernel = RealVibeKernel()

    # Bank should be lazy-loaded (not initialized yet)
    assert kernel._bank is None

    # Access bank (triggers lazy load)
    bank = kernel.get_bank()
    assert bank is not None
    assert kernel._bank is not None

    # Get system stats (should not crash)
    stats = bank.get_system_stats()
    assert "accounts" in stats
    assert "total_balance" in stats


def test_kernel_status_has_credits():
    """Test that kernel status includes total_credits from CivicBank."""
    kernel = RealVibeKernel()

    status = kernel.get_status()
    assert "total_credits" in status
    assert isinstance(status["total_credits"], int)
    assert status["total_credits"] >= 0


# =============================================================================
# TEST: Process Isolation
# =============================================================================


def test_process_manager_exists():
    """Test that kernel has ProcessManager."""
    kernel = RealVibeKernel()
    assert hasattr(kernel, "process_manager")
    assert kernel.process_manager is not None
    assert isinstance(kernel.process_manager, ProcessManager)


def test_process_health_monitoring():
    """Test that ProcessManager can monitor health."""
    # ProcessManager takes no init args
    pm = ProcessManager()

    # Verify health monitoring methods exist (actual method is check_health)
    assert hasattr(pm, "check_health")
    assert callable(pm.check_health)

    # Verify spawn capability exists
    assert hasattr(pm, "spawn_agent")
    assert callable(pm.spawn_agent)


# =============================================================================
# TEST: Parampara Integrity
# =============================================================================


def test_genesis_block_creation():
    """Test that Genesis Block is created correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Genesis Block should exist
        genesis = chain.get_genesis_block()
        assert genesis is not None
        # event_type is stored as string in DB
        assert genesis.event_type == "GENESIS"
        assert genesis.index == 0
        assert genesis.previous_hash == "0" * 64

        # Genesis should have constitutional anchors
        assert "anchors" in genesis.data
        # Actual keys: philosophy_hash, constitution_hash, kernel_version, migration_phase
        assert "philosophy_hash" in genesis.data["anchors"]
        assert "constitution_hash" in genesis.data["anchors"]

        chain.close()


def test_chain_integrity_verification():
    """Test that chain integrity can be verified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Add some blocks
        chain.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id="test_kernel",
            data={"timestamp": "2025-11-28T12:00:00Z"},
        )

        # Verify chain integrity
        is_valid = chain.verify_chain()
        assert is_valid is True

        # Get all blocks
        blocks = chain.get_all_blocks()
        assert len(blocks) == 2  # Genesis + 1 block

        chain.close()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INTEGRATION TEST SUITE")
    print("=" * 70)
    print()

    runner = TestRunner()

    print("[KERNEL BOOT TESTS]")
    runner.run_test("Kernel boots", test_kernel_boots)
    runner.run_test("Kernel has Parampara", test_kernel_has_parampara)
    runner.run_test("Kernel has economic substrate", test_kernel_has_economic_substrate)
    runner.run_test("Kernel status has credits", test_kernel_status_has_credits)

    print("\n[PROCESS ISOLATION TESTS]")
    runner.run_test("ProcessManager exists", test_process_manager_exists)
    runner.run_test("Process health monitoring", test_process_health_monitoring)

    print("\n[PARAMPARA INTEGRITY TESTS]")
    runner.run_test("Genesis Block creation", test_genesis_block_creation)
    runner.run_test("Chain integrity verification", test_chain_integrity_verification)

    success = runner.report()
    sys.exit(0 if success else 1)
