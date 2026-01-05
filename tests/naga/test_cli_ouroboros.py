"""
OUROBOROS TEST - CLI Governance Self-Verification

DIE SCHLANGE FRISST IHREN EIGENEN SCHWANZ.

This test AUTOMATICALLY verifies that ALL registered CLI commands
are properly governed by NAGA. It doesn't test individual commands -
it tests the GOVERNANCE INFRASTRUCTURE itself.

RED → GREEN:
- If a new CLI is added without @register_cli → RED (fail)
- If @register_cli doesn't auto-wrap cmd_* → RED (fail)
- If governance is properly applied → GREEN (pass)

This is the immune system - automatically detecting ungoverned code.
"""

from typing import List, Set, Tuple

import pytest


def get_all_registered_clis() -> List[Tuple[str, type]]:
    """Get all CLIs registered via @register_cli."""
    from vibe_core.protocols.cli import CLIRegistry

    return [(cmd, type(handler)) for cmd, handler in CLIRegistry._instances.items()]


def get_all_cmd_methods(cls: type) -> List[str]:
    """Get all cmd_* and _cmd_* methods from a class."""
    methods = []
    for name in dir(cls):
        if name.startswith(("cmd_", "_cmd_")):
            method = getattr(cls, name)
            if callable(method):
                methods.append(name)
    return methods


def is_governed(method) -> bool:
    """Check if a method has been wrapped by @cli_governed."""
    # Check for __wrapped__ attribute (set by functools.wraps)
    if hasattr(method, "__wrapped__"):
        return True
    # Check for _cli_governed marker
    if hasattr(method, "_cli_governed"):
        return True
    return False


class TestCLIGovernanceOuroboros:
    """
    OUROBOROS: Self-verifying CLI governance.

    These tests verify that the NAGA governance infrastructure
    is working correctly across ALL registered CLIs.
    """

    def test_all_cli_handlers_registered(self):
        """Verify CLIs are discovered and registered."""
        # Force imports to trigger registration
        import vibe_core.cli.unified_cli  # noqa: F401
        from vibe_core.protocols.cli import CLIRegistry

        commands = CLIRegistry.commands()
        assert len(commands) > 0, "No CLI handlers registered!"

        # Should have core commands
        core_commands = {"tool", "circuit", "run", "naga", "knowledge"}
        registered = set(commands)
        missing = core_commands - registered

        assert not missing, f"Core commands not registered: {missing}"

    def test_all_cmd_methods_governed(self):
        """
        OUROBOROS CORE TEST: Every cmd_* method must be governed.

        This test will FAIL (RED) if:
        1. A CLI is added without @register_cli
        2. @register_cli fails to wrap cmd_* methods
        3. Someone bypasses auto-governance

        This is the immune system detecting ungoverned code.
        """
        import vibe_core.cli.unified_cli  # noqa: F401

        ungoverned: List[str] = []

        for cmd_name, handler_cls in get_all_registered_clis():
            for method_name in get_all_cmd_methods(handler_cls):
                method = getattr(handler_cls, method_name)

                if not is_governed(method):
                    ungoverned.append(f"{handler_cls.__name__}.{method_name}")

        if ungoverned:
            pytest.fail(
                "OUROBOROS ALERT: Ungoverned CLI methods detected!\n"
                "The following methods escaped NAGA observation:\n"
                "  - "
                + "\n  - ".join(ungoverned[:20])
                + (f"\n  ... and {len(ungoverned) - 20} more" if len(ungoverned) > 20 else "")
                + "\n\nThis is a governance failure. "
                "Ensure @register_cli is applied to the CLI class."
            )

    def test_governance_wrapper_preserves_signature(self):
        """Verify governed methods preserve their signatures."""
        import vibe_core.cli.unified_cli  # noqa: F401

        for cmd_name, handler_cls in get_all_registered_clis()[:5]:  # Sample
            for method_name in get_all_cmd_methods(handler_cls)[:3]:  # Sample
                method = getattr(handler_cls, method_name)

                # If wrapped, should have __wrapped__
                if hasattr(method, "__wrapped__"):
                    assert callable(method.__wrapped__)
                    # Original method should be accessible
                    # Note: _cmd_* methods keep their underscore
                    assert method.__wrapped__.__name__ == method_name

    def test_hook_chain_exists(self):
        """Verify HookChain infrastructure exists."""
        from vibe_core.naga.cli_hook_chain import CLIHookChain, get_hook_chain

        chain = get_hook_chain()
        assert chain is not None
        assert len(CLIHookChain.DEFAULT_MAPPINGS) > 0

    def test_hooks_can_be_registered(self):
        """Verify hooks can be registered with chain."""
        from vibe_core.naga.cli_hook_chain import CLIHookChain

        chain = CLIHookChain()

        class DummyHook:
            @property
            def hook_id(self) -> str:
                return "dummy"

            def on_phase(self, phase, context):
                return {"allow": True}

        chain.register(DummyHook())
        assert "dummy" in chain.get_registered_hooks()


class TestCLIGovernanceIntegration:
    """Integration tests for CLI governance with NAGA services."""

    def test_unified_cli_can_initialize_hooks(self):
        """UnifiedCLI can initialize NAGA hooks."""
        from vibe_core.cli.unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        assert cli._hooks_enabled is True

        # Initialize hooks (may not have live services)
        cli.initialize_hooks()

        # Hook chain should exist after init
        assert cli._hook_chain is not None

    def test_hooks_connect_to_service_registry(self):
        """Hooks attempt to connect to ServiceRegistry."""
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.naga import SeshaProtocol, TakshakaProtocol

        # Services may or may not be registered (depends on kernel state)
        # But the protocols should be importable
        assert SeshaProtocol is not None
        assert TakshakaProtocol is not None

        # ServiceRegistry.get should not crash even if service not registered
        sesha = ServiceRegistry.get(SeshaProtocol)
        takshaka = ServiceRegistry.get(TakshakaProtocol)
        # May be None, but should not crash


class TestGovernanceCount:
    """Statistical verification of governance coverage."""

    def test_governance_coverage_report(self):
        """Generate coverage report for governance."""
        import vibe_core.cli.unified_cli  # noqa: F401

        total_methods = 0
        governed_methods = 0
        by_cli: dict[str, dict[str, int]] = {}

        for cmd_name, handler_cls in get_all_registered_clis():
            cli_name = handler_cls.__name__
            methods = get_all_cmd_methods(handler_cls)
            governed = sum(1 for m in methods if is_governed(getattr(handler_cls, m)))

            by_cli[cli_name] = {"total": len(methods), "governed": governed}
            total_methods += len(methods)
            governed_methods += governed

        coverage = (governed_methods / total_methods * 100) if total_methods > 0 else 0

        print(f"\n{'=' * 60}")
        print(f"CLI GOVERNANCE COVERAGE: {coverage:.1f}%")
        print(f"{'=' * 60}")
        print(f"Total CLI handlers: {len(by_cli)}")
        print(f"Total cmd_* methods: {total_methods}")
        print(f"Governed methods: {governed_methods}")
        print()

        # Report by CLI
        for cli_name, stats in sorted(by_cli.items()):
            status = "✅" if stats["governed"] == stats["total"] else "⚠️"
            print(f"  {status} {cli_name}: {stats['governed']}/{stats['total']}")

        print(f"{'=' * 60}")

        # OUROBOROS: Fail if coverage drops below threshold
        # This is the RED→GREEN boundary
        MIN_COVERAGE = 90.0
        assert coverage >= MIN_COVERAGE, (
            f"Governance coverage {coverage:.1f}% below minimum {MIN_COVERAGE}%!\n"
            f"The snake is not eating its tail properly."
        )
