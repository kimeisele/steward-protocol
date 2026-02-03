#!/usr/bin/env python3
"""
GAD-000 COMPLIANCE TEST - MahaCLI Adapter
==========================================

"dharmaṁ tu sākṣād bhagavat-praṇītaṁ"
"Dharma is directly enacted by the Supreme Lord."
— Srimad Bhagavatam 6.3.19

This test validates that the MahaCLI Adapter is GAD-000 compliant:
    6 Criteria (Sharanagati) + 4 Dharma + 37 Signature

CHAOS TESTING:
    - Random inputs to test seed stability
    - Edge cases (empty, unicode, very long)
    - Collision detection at same position
    - Fingerprint disambiguation accuracy

RUN:
    python -m vibe_core.mahamantra.research.CLI.05_GAD_COMPLIANCE_TEST

RESEARCH FILE - Validate here before production integration.
"""

from __future__ import annotations

import random
import string
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# =============================================================================
# IMPORTS FROM OUR BOUNDARY
# =============================================================================

try:
    from vibe_core.mahamantra import mahamantra
    from vibe_core.mahamantra.adapters.cli import (
        AdapterResult,
        CellFingerprint,
        MahaCLIAdapter,
        get_adapter,
    )
    from vibe_core.mahamantra.protocols._gad import (
        CRITERIA_COUNT,
        DHARMA_COUNT,
        DharmaPrinciple,
        GADAudit,
        GADCriterion,
    )

    IMPORTS_OK = True
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    IMPORTS_OK = False


# =============================================================================
# TEST RESULT TRACKING
# =============================================================================


@dataclass
class TestResult:
    """Result of a single test."""

    name: str
    passed: bool
    details: str = ""
    duration_ms: float = 0.0


@dataclass
class TestSuite:
    """Collection of test results."""

    name: str
    results: List[TestResult]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    def summary(self) -> str:
        return f"{self.name}: {self.passed_count}/{len(self.results)} passed"


# =============================================================================
# GAD-000 CRITERIA TESTS (6 Sharanagati)
# =============================================================================


def test_discoverability(adapter: MahaCLIAdapter) -> TestResult:
    """
    GOPTRITVE VARANAM → DISCOVERABILITY

    Can we discover all CLIs and their capabilities?
    """
    start = time.time()
    try:
        discovered = adapter.discover()

        # Must return a dict with CLI info
        if not isinstance(discovered, dict):
            return TestResult(
                name="DISCOVERABILITY",
                passed=False,
                details=f"discover() returned {type(discovered)}, expected dict",
                duration_ms=(time.time() - start) * 1000,
            )

        # Must have at least some CLIs
        if len(discovered) == 0:
            return TestResult(
                name="DISCOVERABILITY",
                passed=False,
                details="No CLIs discovered",
                duration_ms=(time.time() - start) * 1000,
            )

        return TestResult(
            name="DISCOVERABILITY",
            passed=True,
            details=f"Discovered {len(discovered)} CLIs",
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return TestResult(
            name="DISCOVERABILITY", passed=False, details=f"Exception: {e}", duration_ms=(time.time() - start) * 1000
        )


def test_observability(adapter: MahaCLIAdapter) -> TestResult:
    """
    ATMA-NIKSHEPA → OBSERVABILITY

    Can we observe the adapter's state at any time?
    """
    start = time.time()
    try:
        # Execute something first
        result = adapter.execute("test", mode="observe")

        # Check that we get complete state back
        required_fields = ["resonance", "executed", "cli_command", "fingerprint"]
        missing = [f for f in required_fields if not hasattr(result, f)]

        if missing:
            return TestResult(
                name="OBSERVABILITY",
                passed=False,
                details=f"Missing fields: {missing}",
                duration_ms=(time.time() - start) * 1000,
            )

        # Fingerprint should have all dimensions
        fp = result.fingerprint
        if fp:
            fp_fields = ["position", "payload_size", "prana", "cycle", "seed"]
            fp_missing = [f for f in fp_fields if not hasattr(fp, f)]
            if fp_missing:
                return TestResult(
                    name="OBSERVABILITY",
                    passed=False,
                    details=f"Fingerprint missing: {fp_missing}",
                    duration_ms=(time.time() - start) * 1000,
                )

        return TestResult(
            name="OBSERVABILITY",
            passed=True,
            details="All state fields present, fingerprint complete",
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return TestResult(
            name="OBSERVABILITY", passed=False, details=f"Exception: {e}", duration_ms=(time.time() - start) * 1000
        )


def test_parseability(adapter: MahaCLIAdapter) -> TestResult:
    """
    PRATIKULYASYA VARJANAM → PARSEABILITY

    Can the adapter parse any input without crashing?
    """
    start = time.time()
    test_inputs = [
        "",  # Empty
        "a",  # Single char
        "audit",  # Normal command
        "   spaces   ",  # Whitespace
        "日本語",  # Unicode
        "a" * 1000,  # Very long
        "!@#$%^&*()",  # Special chars
        "\n\t\r",  # Control chars
        "0" * 100,  # Numeric
    ]

    failures = []
    for inp in test_inputs:
        try:
            result = adapter.execute(inp, mode="observe")
            if result.resonance is None:
                failures.append(f"'{inp[:20]}...' returned None resonance")
        except Exception as e:
            failures.append(f"'{inp[:20]}...' raised {type(e).__name__}")

    if failures:
        return TestResult(
            name="PARSEABILITY",
            passed=False,
            details=f"Failed on: {failures[:3]}",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="PARSEABILITY",
        passed=True,
        details=f"Parsed {len(test_inputs)} edge cases successfully",
        duration_ms=(time.time() - start) * 1000,
    )


def test_composability(adapter: MahaCLIAdapter) -> TestResult:
    """
    ANUKULYASYA SANKALPA → COMPOSABILITY

    Can the adapter's outputs be used as inputs to other systems?
    """
    start = time.time()
    try:
        # Execute and get result
        result = adapter.execute("audit", mode="observe")

        # Result should be serializable (all fields are basic types)
        resonance = result.resonance

        # Resonance must be a dict (JSON-serializable)
        if not isinstance(resonance, dict):
            return TestResult(
                name="COMPOSABILITY",
                passed=False,
                details=f"Resonance is {type(resonance)}, not dict",
                duration_ms=(time.time() - start) * 1000,
            )

        # Check that fingerprint is also composable
        fp = result.fingerprint
        if fp:
            # All fingerprint fields should be basic types
            for field in ["position", "payload_size", "prana", "cycle", "seed"]:
                val = getattr(fp, field, None)
                if not isinstance(val, (int, float)):
                    return TestResult(
                        name="COMPOSABILITY",
                        passed=False,
                        details=f"Fingerprint.{field} is {type(val)}, not numeric",
                        duration_ms=(time.time() - start) * 1000,
                    )

        return TestResult(
            name="COMPOSABILITY",
            passed=True,
            details="All outputs are composable/serializable",
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return TestResult(
            name="COMPOSABILITY", passed=False, details=f"Exception: {e}", duration_ms=(time.time() - start) * 1000
        )


def test_idempotency(adapter: MahaCLIAdapter) -> TestResult:
    """
    KARPANYA → IDEMPOTENCY

    Same input should always produce same output.
    """
    start = time.time()
    test_inputs = ["audit", "create", "run", "genesis", "deploy"]
    failures = []

    for inp in test_inputs:
        # Execute 3 times
        results = []
        for _ in range(3):
            result = adapter.execute(inp, mode="observe")
            results.append(
                (
                    result.matched_position,
                    result.fingerprint.position if result.fingerprint else None,
                    result.fingerprint.payload_size if result.fingerprint else None,
                )
            )

        # All should be identical
        if len(set(results)) > 1:
            failures.append(f"'{inp}' gave different results: {results}")

    if failures:
        return TestResult(
            name="IDEMPOTENCY",
            passed=False,
            details=f"Non-idempotent: {failures[0]}",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="IDEMPOTENCY",
        passed=True,
        details=f"All {len(test_inputs)} inputs are idempotent",
        duration_ms=(time.time() - start) * 1000,
    )


def test_recoverability(adapter: MahaCLIAdapter) -> TestResult:
    """
    RAKSISYATI ITI VISHVASA → RECOVERABILITY

    Can the adapter recover from errors gracefully?
    """
    start = time.time()
    # Test various error conditions
    error_inputs = [
        None,  # Will be handled
        "",  # Empty
        "\x00\x01\x02",  # Binary
    ]

    recovered = 0
    for inp in error_inputs:
        try:
            if inp is None:
                # Test with None - should handle gracefully
                try:
                    adapter.execute(inp, mode="observe")
                except (TypeError, AttributeError):
                    # Expected - but should not crash
                    recovered += 1
                    continue
            result = adapter.execute(inp, mode="observe")
            if result is not None:
                recovered += 1
        except SystemExit:
            # Should never exit
            return TestResult(
                name="RECOVERABILITY",
                passed=False,
                details="System exit on error input",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception:
            # Other exceptions are OK if graceful
            recovered += 1

    return TestResult(
        name="RECOVERABILITY",
        passed=True,
        details=f"Recovered from {recovered}/{len(error_inputs)} error cases",
        duration_ms=(time.time() - start) * 1000,
    )


# =============================================================================
# DHARMA TESTS (4 Pillars)
# =============================================================================


def test_daya(adapter: MahaCLIAdapter) -> TestResult:
    """
    DAYA → MERCY

    Does the adapter handle edge cases with mercy (graceful degradation)?
    """
    start = time.time()
    # Test with unknown/unusual inputs
    mercy_cases = ["unknown_command_xyz", "äöü", "🔥🔥🔥"]

    for inp in mercy_cases:
        result = adapter.execute(inp, mode="observe")
        # Should still return a valid result, not crash
        if result is None or result.resonance is None:
            return TestResult(
                name="DAYA (Mercy)",
                passed=False,
                details=f"No mercy for input '{inp}'",
                duration_ms=(time.time() - start) * 1000,
            )

    return TestResult(
        name="DAYA (Mercy)",
        passed=True,
        details="Graceful handling of unknown inputs",
        duration_ms=(time.time() - start) * 1000,
    )


def test_satyam(adapter: MahaCLIAdapter) -> TestResult:
    """
    SATYAM → TRUTHFULNESS

    Does the adapter report truthful information about matches?
    """
    start = time.time()
    # Test that candidates list is truthful
    result = adapter.execute("audit", mode="observe")

    if result.cli_command:
        # If a CLI was matched, it should be in candidates
        if result.candidates and result.cli_command not in result.candidates:
            return TestResult(
                name="SATYAM (Truthfulness)",
                passed=False,
                details=f"Matched '{result.cli_command}' not in candidates {result.candidates}",
                duration_ms=(time.time() - start) * 1000,
            )

    # Position should match fingerprint position
    if result.fingerprint:
        if result.matched_position != result.fingerprint.position:
            return TestResult(
                name="SATYAM (Truthfulness)",
                passed=False,
                details=f"Position mismatch: {result.matched_position} vs {result.fingerprint.position}",
                duration_ms=(time.time() - start) * 1000,
            )

    return TestResult(
        name="SATYAM (Truthfulness)",
        passed=True,
        details="All reported information is consistent",
        duration_ms=(time.time() - start) * 1000,
    )


def test_tapas(adapter: MahaCLIAdapter) -> TestResult:
    """
    TAPAS → AUSTERITY

    Does the adapter work within resource constraints?
    """
    start = time.time()
    # Test that discovery caching works (austerity = not wasting resources)
    adapter._discovered = False  # Reset

    # First discovery
    t1_start = time.time()
    adapter.discover()
    t1 = time.time() - t1_start

    # Second discovery (should be cached)
    t2_start = time.time()
    adapter.discover()
    t2 = time.time() - t2_start

    # Cached should be much faster
    if t2 > t1 * 0.5 and t1 > 0.001:  # Allow some margin
        return TestResult(
            name="TAPAS (Austerity)",
            passed=False,
            details=f"No caching: first={t1:.4f}s, second={t2:.4f}s",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="TAPAS (Austerity)",
        passed=True,
        details=f"Caching works: first={t1:.4f}s, cached={t2:.4f}s",
        duration_ms=(time.time() - start) * 1000,
    )


def test_saucam(adapter: MahaCLIAdapter) -> TestResult:
    """
    SAUCAM → CLEANLINESS

    Is the adapter's state clean and well-organized?
    """
    start = time.time()
    # Check internal state is clean

    # After discovery, fingerprints should all be valid
    adapter._discover_all_clis()

    for cmd, fp in adapter._cli_fingerprints.items():
        # Position should be 0-15
        if not (0 <= fp.position <= 15):
            return TestResult(
                name="SAUCAM (Cleanliness)",
                passed=False,
                details=f"CLI '{cmd}' has invalid position {fp.position}",
                duration_ms=(time.time() - start) * 1000,
            )

        # Payload size should be positive
        if fp.payload_size < 0:
            return TestResult(
                name="SAUCAM (Cleanliness)",
                passed=False,
                details=f"CLI '{cmd}' has negative payload_size",
                duration_ms=(time.time() - start) * 1000,
            )

    return TestResult(
        name="SAUCAM (Cleanliness)",
        passed=True,
        details=f"All {len(adapter._cli_fingerprints)} CLI fingerprints are clean",
        duration_ms=(time.time() - start) * 1000,
    )


# =============================================================================
# CHAOS TESTING
# =============================================================================


def chaos_test_random_inputs(adapter: MahaCLIAdapter, iterations: int = 100) -> TestResult:
    """
    CHAOS: Random Input Stability

    Test with random inputs to ensure no crashes.
    """
    start = time.time()
    failures = []

    for i in range(iterations):
        # Generate random input
        length = random.randint(1, 100)
        chars = string.ascii_letters + string.digits + " "
        random_input = "".join(random.choice(chars) for _ in range(length))

        try:
            result = adapter.execute(random_input, mode="observe")
            if result is None:
                failures.append(f"Iteration {i}: None result")
        except Exception as e:
            failures.append(f"Iteration {i}: {type(e).__name__}")

    if failures:
        return TestResult(
            name="CHAOS: Random Inputs",
            passed=False,
            details=f"{len(failures)} failures in {iterations} iterations",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="CHAOS: Random Inputs",
        passed=True,
        details=f"Survived {iterations} random inputs",
        duration_ms=(time.time() - start) * 1000,
    )


def chaos_test_seed_stability(adapter: MahaCLIAdapter) -> TestResult:
    """
    CHAOS: Seed Stability

    Test that same input always produces same seed/position.
    """
    start = time.time()
    test_inputs = ["audit", "create", "run", "genesis", "deploy", "verify", "build", "test", "lint", "format"]

    # Run each input multiple times
    inconsistencies = []
    for inp in test_inputs:
        positions = []
        seeds = []
        for _ in range(5):
            result = adapter.execute(inp, mode="observe")
            positions.append(result.matched_position)
            seeds.append(result.resonance.get("vibration", {}).get("seed"))

        if len(set(positions)) > 1:
            inconsistencies.append(f"'{inp}' positions: {positions}")
        if len(set(seeds)) > 1:
            inconsistencies.append(f"'{inp}' seeds: {seeds}")

    if inconsistencies:
        return TestResult(
            name="CHAOS: Seed Stability",
            passed=False,
            details=f"Inconsistent: {inconsistencies[0]}",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="CHAOS: Seed Stability",
        passed=True,
        details=f"All {len(test_inputs)} inputs are stable",
        duration_ms=(time.time() - start) * 1000,
    )


def chaos_test_collision_handling(adapter: MahaCLIAdapter) -> TestResult:
    """
    CHAOS: Collision Handling

    Test that collisions at same position are handled via fingerprint.
    """
    start = time.time()
    adapter._discover_all_clis()

    # Group CLIs by position
    by_position: Dict[int, List[str]] = {}
    for cmd, fp in adapter._cli_fingerprints.items():
        pos = fp.position
        if pos not in by_position:
            by_position[pos] = []
        by_position[pos].append(cmd)

    # Find positions with collisions
    collisions = {pos: cmds for pos, cmds in by_position.items() if len(cmds) > 1}

    if not collisions:
        return TestResult(
            name="CHAOS: Collision Handling",
            passed=True,
            details="No collisions to test (lucky distribution)",
            duration_ms=(time.time() - start) * 1000,
        )

    # Test that colliding CLIs are still distinguishable
    for pos, cmds in collisions.items():
        # Each CLI name should match itself
        for cmd in cmds:
            result = adapter.execute(cmd, mode="observe")
            if result.cli_command and result.cli_command != cmd:
                # Allow if input is substring (e.g., "run" might match "run_cli")
                if cmd not in result.cli_command and result.cli_command not in cmd:
                    return TestResult(
                        name="CHAOS: Collision Handling",
                        passed=False,
                        details=f"'{cmd}' matched '{result.cli_command}' (collision at pos {pos})",
                        duration_ms=(time.time() - start) * 1000,
                    )

    collision_count = sum(len(cmds) for cmds in collisions.values())
    return TestResult(
        name="CHAOS: Collision Handling",
        passed=True,
        details=f"Handled {collision_count} CLIs at {len(collisions)} collision positions",
        duration_ms=(time.time() - start) * 1000,
    )


def chaos_test_fingerprint_distance(adapter: MahaCLIAdapter) -> TestResult:
    """
    CHAOS: Fingerprint Distance

    Test that fingerprint.distance() is mathematically sound.
    """
    start = time.time()

    # Create test fingerprints
    fp1 = CellFingerprint(position=5, payload_size=10, prana=100, cycle=1, seed=12345)
    fp2 = CellFingerprint(position=5, payload_size=10, prana=100, cycle=1, seed=12345)
    fp3 = CellFingerprint(position=5, payload_size=15, prana=100, cycle=1, seed=12345)
    fp4 = CellFingerprint(position=6, payload_size=10, prana=100, cycle=1, seed=12345)

    # Same fingerprint = distance 0
    if fp1.distance(fp2) != 0:
        return TestResult(
            name="CHAOS: Fingerprint Distance",
            passed=False,
            details=f"Same fingerprint distance != 0: {fp1.distance(fp2)}",
            duration_ms=(time.time() - start) * 1000,
        )

    # Different payload = small distance
    d3 = fp1.distance(fp3)
    if d3 <= 0:
        return TestResult(
            name="CHAOS: Fingerprint Distance",
            passed=False,
            details=f"Different payload distance <= 0: {d3}",
            duration_ms=(time.time() - start) * 1000,
        )

    # Different position = very large distance
    d4 = fp1.distance(fp4)
    if d4 < 1000000:
        return TestResult(
            name="CHAOS: Fingerprint Distance",
            passed=False,
            details=f"Different position distance < 1000000: {d4}",
            duration_ms=(time.time() - start) * 1000,
        )

    return TestResult(
        name="CHAOS: Fingerprint Distance",
        passed=True,
        details="Distance function is mathematically sound",
        duration_ms=(time.time() - start) * 1000,
    )


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================


def run_all_tests() -> Tuple[List[TestSuite], bool]:
    """Run all GAD-000 compliance tests."""
    if not IMPORTS_OK:
        print("Cannot run tests - imports failed")
        return [], False

    adapter = get_adapter()
    suites = []

    # 6 GAD Criteria
    criteria_suite = TestSuite(
        name="GAD-000 Criteria (6 Sharanagati)",
        results=[
            test_discoverability(adapter),
            test_observability(adapter),
            test_parseability(adapter),
            test_composability(adapter),
            test_idempotency(adapter),
            test_recoverability(adapter),
        ],
    )
    suites.append(criteria_suite)

    # 4 Dharma Principles
    dharma_suite = TestSuite(
        name="Dharma Principles (4 Pillars)",
        results=[
            test_daya(adapter),
            test_satyam(adapter),
            test_tapas(adapter),
            test_saucam(adapter),
        ],
    )
    suites.append(dharma_suite)

    # Chaos Testing
    chaos_suite = TestSuite(
        name="Chaos Testing (Seed-Based Systems)",
        results=[
            chaos_test_random_inputs(adapter, iterations=50),
            chaos_test_seed_stability(adapter),
            chaos_test_collision_handling(adapter),
            chaos_test_fingerprint_distance(adapter),
        ],
    )
    suites.append(chaos_suite)

    all_passed = all(suite.all_passed for suite in suites)
    return suites, all_passed


def print_results(suites: List[TestSuite]) -> None:
    """Print formatted test results."""
    print("\n" + "=" * 72)
    print("GAD-000 COMPLIANCE TEST - MahaCLI Adapter")
    print("=" * 72)

    total_passed = 0
    total_tests = 0

    for suite in suites:
        print(f"\n{suite.name}")
        print("-" * 72)

        for result in suite.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"  {status}  {result.name}")
            if result.details:
                print(f"         {result.details}")
            print(f"         [{result.duration_ms:.1f}ms]")

        print(f"\n  {suite.summary()}")
        total_passed += suite.passed_count
        total_tests += len(suite.results)

    print("\n" + "=" * 72)
    all_passed = total_passed == total_tests
    status = "GAD-000 COMPLIANT" if all_passed else "NOT COMPLIANT"
    print(f"FINAL: {total_passed}/{total_tests} tests passed - {status}")
    print("=" * 72)

    # Calculate legitimacy
    criteria_passed = suites[0].passed_count if len(suites) > 0 else 0
    dharma_passed = suites[1].passed_count if len(suites) > 1 else 0

    legitimacy = min(criteria_passed / 6, dharma_passed / 4) if all_passed else 0.0
    print(f"\nLegitimacy = (6 ∩ 4) × Signature₃₇ = {legitimacy:.2%}")

    if legitimacy >= 1.0:
        print("Status: BONA FIDE - Full Parampara Connection")
    elif legitimacy >= 0.75:
        print("Status: NEEDS IMPROVEMENT - Partial Connection")
    else:
        print("Status: VIOLATES GAD-000 - Disconnected")


if __name__ == "__main__":
    suites, all_passed = run_all_tests()
    print_results(suites)
    sys.exit(0 if all_passed else 1)
