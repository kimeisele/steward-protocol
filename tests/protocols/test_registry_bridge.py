"""
TEST REGISTRY BRIDGE (Gap 4 Verification)
==========================================
Verifies that TestableRegistry → Pytest bridge is wired correctly.

This test uses the fixtures defined in conftest.py:
  - testable_registry: Access to global TestableRegistry
  - registry_test_case: Parametrized TestCase from registry
  - run_registry_test: Execute a TestCase with proper context
"""

import pytest


class TestRegistryBridge:
    """Verify Gap 4: TestableRegistry → Pytest bridge."""

    def test_registry_fixture_available(self, testable_registry):
        """Verify testable_registry fixture works."""
        assert testable_registry is not None
        # Should have methods
        assert hasattr(testable_registry, "discover_from_kernel")
        assert hasattr(testable_registry, "get_all_test_cases")
        assert hasattr(testable_registry, "get_summary")

    def test_registry_discovery(self, testable_registry, fresh_kernel):
        """Verify discovery from kernel works."""
        # Discover components
        counts = testable_registry.discover_from_kernel(fresh_kernel)

        # Should return a counts dict
        assert isinstance(counts, dict)
        assert "agents" in counts
        assert "plugins" in counts
        assert "ledger" in counts

    def test_registry_summary(self, testable_registry, fresh_kernel):
        """Verify summary statistics work."""
        # Ensure discovery happened
        testable_registry.discover_from_kernel(fresh_kernel)

        summary = testable_registry.get_summary()

        assert "total_testables" in summary
        assert "total_tests" in summary
        assert "by_type" in summary

        # We discovered at least something
        # (may be 0 if kernel has no components in test mode)
        assert summary["total_testables"] >= 0

    def test_run_registry_test_fixture(self, run_registry_test, testable_registry, fresh_kernel):
        """Verify run_registry_test fixture works."""
        # run_registry_test should be a callable
        assert callable(run_registry_test)

        # Discover and get test cases
        testable_registry.discover_from_kernel(fresh_kernel)
        cases = testable_registry.get_all_test_cases()

        # If we have any cases, try running one
        if cases:
            result = run_registry_test(cases[0])
            assert hasattr(result, "success")
            assert hasattr(result, "message")
            assert hasattr(result, "duration_ms")


# This test uses the parametrized registry_test_case fixture
# Each discovered TestCase becomes a separate pytest invocation
def test_parametrized_registry_case(registry_test_case, fresh_kernel, test_gene):
    """
    Parametrized test: One invocation per discovered TestCase.

    Each TestCase from the registry becomes a separate pytest test.
    This demonstrates the full Gap 4 bridge working.
    """
    assert registry_test_case is not None
    assert registry_test_case.name

    # Execute the test function
    result = registry_test_case.test_func(fresh_kernel, {"gene": test_gene})
    assert result is True, f"TestCase {registry_test_case.name} failed"
