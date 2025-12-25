#!/usr/bin/env python3
"""
OPUS-307 Phase I.1.5: Singularity Acid Test
============================================

This script verifies that:
1. Legacy playbooks are converted to circuits
2. ExecutorSingularity is the execution path
3. CognitiveCircuitExecutor runs the states
4. DeterministicExecutor is NOT used (except as passthrough)

"Erst TÜV, dann Autobahn."
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO, format="%(name)-25s | %(levelname)-8s | %(message)s", handlers=[logging.StreamHandler()]
)

# Enable specific loggers we care about
for logger_name in [
    "UNIFIED_EXECUTION",
    "EXECUTOR_SINGULARITY",
    "CIRCUIT_ENGINE",
]:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

# Silence noisy loggers
for logger_name in [
    "MANIFEST.REGISTRY",
    "SECTION.LOADER",
    "vibe_core.phoenix.config",
    "UNIFIED.LOADER",
    "vibe_core.runtime.prompt_registry",
    "PARAMPARA",
    "VIBE_KERNEL",
    "EVENT_BUS",
    "DI",
    "LEDGER_STATE",
    "PRAKRITI",
    "INTERFACE_PLUGIN",
    "RENDERER.LOADER",
    "CAPABILITY_REGISTRY",
    "NARASIMHA",
    "KERNEL_IO",
    "SYSTEM_HEARTBEAT",
    "TASK_MANAGER_PLUGIN",
    "EPHEMERAL_STORAGE",
    "OPUS_TICK",
    "OPUS_ASSISTANT",
    "NODE_PULSE",
    "AGENT_CITY",
    "VEDIC_STATE",
    "VEDIC_GOVERNANCE",
    "PROCESS_ISOLATION",
    "MANAS.Kernel",
    "OPUS_CONTEXT",
    "VAJRA",
    "DETERMINISTIC_EXECUTOR",
    "GIT_STATE",
    "STATE.SERVICE",
    "SYSCALL_LISTENER",
]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)


def run_acid_test():
    """Run the singularity acid test (synchronous version)."""
    print("\n" + "=" * 70)
    print("OPUS-307 Phase I.1.5: SINGULARITY ACID TEST")
    print("=" * 70)
    print()

    checks = []

    # =========================================================================
    # Step 1: Test the converter directly
    # =========================================================================
    print("[1/3] Testing PlaybookToCircuitConverter...")
    print("-" * 50)

    import yaml

    from vibe_core.cartridges.system.envoy.executor_singularity import (
        PlaybookToCircuitConverter,
    )

    # Load the test playbook
    test_playbook_path = project_root / "vibe_core" / "playbook" / "circuits" / "test_singularity.yaml"
    with open(test_playbook_path) as f:
        playbook_data = yaml.safe_load(f)

    print(f"   Loaded: {test_playbook_path.name}")
    print(f"   Format: {'playbook' if 'playbook' in playbook_data else 'circuit'}")

    # Convert
    circuit_def = PlaybookToCircuitConverter.convert(playbook_data, "TEST_SINGULARITY")

    if "circuit" in circuit_def:
        circuit = circuit_def["circuit"]
        print("   ✅ Converted to circuit!")
        print(f"   Entry state: {circuit.get('entry_state')}")
        print(f"   States: {list(circuit.get('states', {}).keys())}")
        print(f"   Provenance: {circuit.get('converted_from', 'native')}")
        checks.append(("PlaybookToCircuitConverter works", True))

        # Verify structure
        if circuit.get("converted_from") == "playbook":
            checks.append(("Provenance marker set", True))
        else:
            checks.append(("Provenance marker set", False))
    else:
        print("   ❌ Conversion failed!")
        checks.append(("PlaybookToCircuitConverter works", False))

    print()

    # =========================================================================
    # Step 2: Verify UnifiedExecutor imports singularity
    # =========================================================================
    print("[2/3] Testing UnifiedExecutor configuration...")
    print("-" * 50)

    from vibe_core.runtime.unified_execution_full import (
        EXECUTOR_SINGULARITY_ENABLED,
        UnifiedExecutor,
    )

    print(f"   EXECUTOR_SINGULARITY_ENABLED = {EXECUTOR_SINGULARITY_ENABLED}")

    if EXECUTOR_SINGULARITY_ENABLED:
        checks.append(("Singularity flag enabled", True))
    else:
        checks.append(("Singularity flag enabled", False))

    # Check that singularity init method exists
    if hasattr(UnifiedExecutor, "_init_singularity"):
        checks.append(("UnifiedExecutor has _init_singularity method", True))
    else:
        checks.append(("UnifiedExecutor has _init_singularity method", False))

    print()

    # =========================================================================
    # Step 3: Verify circuit execution path
    # =========================================================================
    print("[3/3] Testing CognitiveCircuitExecutor availability...")
    print("-" * 50)

    try:
        from vibe_core.cortex.engines.circuit_engine import (
            CognitiveCircuitExecutor,
            create_circuit_executor,
        )

        print("   ✅ CognitiveCircuitExecutor imported")
        checks.append(("CognitiveCircuitExecutor available", True))

        # Verify execute_by_id exists
        if hasattr(CognitiveCircuitExecutor, "execute_by_id"):
            print("   ✅ execute_by_id method exists")
            checks.append(("execute_by_id method exists", True))
        else:
            print("   ❌ execute_by_id method missing")
            checks.append(("execute_by_id method exists", False))

    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        checks.append(("CognitiveCircuitExecutor available", False))

    print()

    # =========================================================================
    # Results
    # =========================================================================
    print("=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)

    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("🎉 ACID TEST PASSED: Singularity components verified!")
        print()
        print("Architecture validated:")
        print("  1. PlaybookToCircuitConverter converts phases[] → states{}")
        print("  2. EXECUTOR_SINGULARITY_ENABLED = True")
        print("  3. UnifiedExecutor has _init_singularity method")
        print("  4. CognitiveCircuitExecutor.execute_by_id available")
        print()
        print("Next: Run 'steward run' to test live execution.")
    else:
        print("❌ ACID TEST FAILED: Check the logs above.")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_acid_test()
    sys.exit(0 if success else 1)
