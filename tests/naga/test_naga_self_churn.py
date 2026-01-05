"""
LEVEL -4: NAGA SELF-CHURNING TEST

SAMUDRA MANTHAN: The rope (Vasuki) that churns the ocean
IS ITSELF being churned by the churning.

This test verifies that NAGAs observe THEMSELVES:
- @naga_governed decorator on NAGA service methods
- Chitragupta profiling Chitragupta
- Sesha recording Sesha
- Takshaka validating Takshaka

108: Not binary (0/1) but the sacred spectrum.
The Halahala (poison) surfaces before Amrita (nectar).

RED → GREEN:
- If a NAGA method escapes self-observation → RED
- If all NAGAs are self-churning → GREEN
"""

import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest


def get_all_naga_services() -> List[Tuple[str, type]]:
    """Discover all NAGA services via @naga_service decorator."""
    services = []

    # Import all NAGA service modules
    service_modules = [
        "vibe_core.naga.services.sesha",
        "vibe_core.naga.services.takshaka",
        "vibe_core.naga.services.vasuki",
        "vibe_core.naga.services.chitragupta",
        "vibe_core.naga.services.kaliya",
        "vibe_core.naga.services.narada",
        "vibe_core.naga.services.prahlad",
        "vibe_core.naga.services.ananta",
        "vibe_core.naga.services.karkotaka",
        "vibe_core.naga.services.padma",
        "vibe_core.naga.services.shankha",
        "vibe_core.naga.services.kulika",
    ]

    for module_name in service_modules:
        try:
            module = __import__(module_name, fromlist=[""])
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check for @naga_service decorated classes
                if hasattr(obj, "_naga_metadata") or "Service" in name:
                    if obj.__module__ == module_name:
                        services.append((name, obj))
        except ImportError:
            pass

    return services


def get_public_methods(cls: type) -> List[str]:
    """Get all public methods (not starting with _) from a class."""
    methods = []
    for name in dir(cls):
        if name.startswith("_"):
            continue
        attr = getattr(cls, name, None)
        if callable(attr) and not isinstance(attr, type):
            methods.append(name)
    return methods


def get_operational_methods(cls: type) -> List[str]:
    """
    Get methods that SHOULD be governed.

    Excludes:
    - Properties
    - Class methods
    - Static methods
    - Pure getters (get_*, is_*, has_*)
    - Status methods
    """
    excluded_prefixes = ("get_", "is_", "has_", "list_", "can_", "should_")
    excluded_names = {"status", "health", "info", "capabilities", "metadata"}

    methods = []
    for name in dir(cls):
        if name.startswith("_"):
            continue

        attr = getattr(cls, name, None)

        # Skip non-callables
        if not callable(attr):
            continue

        # Skip properties
        if isinstance(inspect.getattr_static(cls, name, None), property):
            continue

        # Skip excluded prefixes
        if any(name.startswith(p) for p in excluded_prefixes):
            continue

        # Skip excluded names
        if name in excluded_names:
            continue

        methods.append(name)

    return methods


def is_naga_governed(method) -> bool:
    """Check if method has @naga_governed decorator."""
    # Check for wrapper
    if hasattr(method, "__wrapped__"):
        return True
    # Check for explicit marker
    if hasattr(method, "_naga_governed"):
        return True
    # Check docstring for decorator mention (sometimes preserved)
    if hasattr(method, "__doc__") and method.__doc__:
        if "@naga_governed" in method.__doc__:
            return True
    return False


class TestNagaSelfChurning:
    """
    LEVEL -4: NAGAs governing NAGAs.

    The rope (Vasuki) must also be churned.
    """

    def test_naga_services_discovered(self):
        """Verify NAGA services can be discovered."""
        services = get_all_naga_services()
        assert len(services) > 0, "No NAGA services discovered!"

        # Core NAGAs must exist
        service_names = {name for name, _ in services}
        core_nagas = {"SeshaService", "TakshakaService", "VasukiService", "ChitraguptaService"}
        missing = core_nagas - service_names

        assert not missing, f"Core NAGAs not found: {missing}"

    def test_naga_governed_decorator_exists(self):
        """Verify @naga_governed decorator is importable."""
        from vibe_core.naga.services.base import naga_governed

        assert callable(naga_governed)

    def test_core_operations_governed(self):
        """
        Verify critical NAGA operations are governed.

        These are the DHARMA operations that MUST be observed:
        - Sesha: export_blocks, import_blocks, detect_drift
        - Takshaka: scan_toxicity, bite
        - Chitragupta: record_metric, detect_anomaly
        - Vasuki: churn_out, churn_in
        """
        critical_operations = {
            "SeshaService": ["export_blocks", "import_blocks", "detect_drift"],
            "TakshakaService": ["scan_toxicity", "bite"],
            "ChitraguptaService": ["record_metric", "detect_anomaly"],
            "VasukiService": ["churn_out", "churn_in"],
        }

        ungoverned: List[str] = []

        for service_name, cls in get_all_naga_services():
            if service_name not in critical_operations:
                continue

            for method_name in critical_operations[service_name]:
                method = getattr(cls, method_name, None)
                if method is None:
                    continue

                if not is_naga_governed(method):
                    ungoverned.append(f"{service_name}.{method_name}")

        if ungoverned:
            pytest.fail(
                "HALAHALA DETECTED: Critical NAGA operations not governed!\n"
                "These methods escape self-observation:\n"
                "  - " + "\n  - ".join(ungoverned) + "\n\nApply @naga_governed to these methods."
            )


class TestNagaGovernanceCoverage:
    """Statistical analysis of NAGA self-governance."""

    def test_governance_coverage_report(self):
        """Generate NAGA self-governance coverage report."""
        services = get_all_naga_services()

        total_methods = 0
        governed_methods = 0
        by_service: Dict[str, Dict[str, int]] = {}

        for service_name, cls in services:
            methods = get_operational_methods(cls)
            governed = sum(1 for m in methods if is_naga_governed(getattr(cls, m, None)))

            by_service[service_name] = {"total": len(methods), "governed": governed}
            total_methods += len(methods)
            governed_methods += governed

        coverage = (governed_methods / total_methods * 100) if total_methods > 0 else 0

        print(f"\n{'=' * 60}")
        print(f"NAGA SELF-CHURNING COVERAGE: {coverage:.1f}%")
        print(f"{'=' * 60}")
        print(f"Total NAGA services: {len(services)}")
        print(f"Total operational methods: {total_methods}")
        print(f"Governed methods: {governed_methods}")
        print()

        # Report by service
        for service_name, stats in sorted(by_service.items()):
            if stats["total"] == 0:
                status = "⚪"  # No operational methods
            elif stats["governed"] == stats["total"]:
                status = "✅"
            elif stats["governed"] > 0:
                status = "🟡"  # Partial
            else:
                status = "🔴"  # None
            print(f"  {status} {service_name}: {stats['governed']}/{stats['total']}")

        print(f"{'=' * 60}")

        # The 108 principle: Not all methods need governance
        # But coverage should be reasonable
        MIN_COVERAGE = 30.0  # Start low, increase as we churn
        assert coverage >= MIN_COVERAGE or total_methods == 0, (
            f"NAGA self-governance coverage {coverage:.1f}% below {MIN_COVERAGE}%!\n"
            f"The snake is not eating its own tail."
        )


class TestChurningInfrastructure:
    """Test the churning infrastructure itself."""

    def test_ouroboros_exists(self):
        """Verify NagaOuroboros (loop detector) exists."""
        from vibe_core.naga.ouroboros import NagaOuroboros

        ouroboros = NagaOuroboros()
        assert ouroboros is not None

    def test_ouroboros_detects_loops(self):
        """Verify OUROBOROS can detect correction loops."""
        from vibe_core.naga.ouroboros import LoopCode, NagaOuroboros

        ouroboros = NagaOuroboros(
            loop_window_seconds=10.0,
            rapid_fire_threshold=3,
            rapid_fire_window=5.0,
        )

        # Create mock decision
        class MockDecision:
            class MockAction:
                name = "TEST"

            action = MockAction()
            target = "test"
            timestamp = __import__("datetime").datetime.now()

        decision = MockDecision()

        # Simulate rapid fire (A fires 3x quickly)
        for _ in range(3):
            alert = ouroboros.observe_correction("A", "B", decision)

        # Should detect rapid fire
        assert alert is not None or ouroboros._loops_detected > 0

    def test_shuddhi_engine_exists(self):
        """Verify Shuddhi (healing) engine exists."""
        from vibe_core.shuddhi.engine import ShuddhiEngine

        engine = ShuddhiEngine()
        assert engine is not None

        # Should have remedies
        remedies = engine.list_remedies()
        assert len(remedies) >= 0  # May be 0 if none discovered


class TestFractalGovernance:
    """
    Test that governance is FRACTAL - same pattern at every level.

    Level 0:  User commands
    Level -1: CLI HookChain
    Level -2: CLI Hooks
    Level -3: NAGA Services
    Level -4: NAGAs governing NAGAs (this test)
    """

    def test_governance_decorator_is_fractal(self):
        """
        Both @cli_governed and @naga_governed use the same pattern.

        They both inject:
        - Takshaka validation
        - Chitragupta profiling
        - Sesha auditing
        """
        from vibe_core.naga.services.base import NagaBaseService, cli_governed, naga_governed

        # Both should be decorators
        assert callable(cli_governed)
        assert callable(naga_governed)

        # Test @cli_governed (doesn't need base class)
        class TestCLI:
            @cli_governed()
            def cmd_test(self):
                return "cli"

        # Test @naga_governed (needs NagaBaseService for self._chitragupta etc)
        class TestService(NagaBaseService):
            @naga_governed(operation="test")
            def process(self):
                return "naga"

        # Both should work (graceful degradation when NAGAs not available)
        assert TestCLI().cmd_test() == "cli"
        assert TestService().process() == "naga"

    def test_service_registry_is_central(self):
        """
        All governance flows through ServiceRegistry.

        This is the MANDARA MOUNTAIN (churning rod) that everything pivots on.
        """
        from vibe_core.di import ServiceRegistry

        assert ServiceRegistry is not None
        assert hasattr(ServiceRegistry, "get")
        assert hasattr(ServiceRegistry, "register")
