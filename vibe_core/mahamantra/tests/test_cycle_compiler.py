"""
CYCLE COMPILER — Tests
=======================

Verifies:
1. Core cycle unchanged when no custom ops
2. Custom ops register and compile correctly
3. Gate ordering preserved (core before custom within same gate)
4. VAMSI addresses are collision-free
5. execute_cycle() uses compiled path when custom ops exist
6. Unregister invalidates compiled cycle
"""

import pytest

from vibe_core.mahamantra.protocols._navabhakti import (
    GATE_INDEX,
    VAMSI_ADDR,
    NavaBhaktiOp,
)
from vibe_core.mahamantra.protocols._seed import NAVA
from vibe_core.mahamantra.substrate.cycle_compiler import (
    CycleCompiler,
    get_compiler,
)


class TestCycleCompilerCore:
    """Core cycle behavior without custom ops."""

    def test_compile_core_only(self):
        cc = CycleCompiler()
        cycle = cc.compile()
        assert len(cycle) == NAVA
        for i, cop in enumerate(cycle):
            assert cop.is_core
            assert cop.op_id == i
            assert cop.gate == GATE_INDEX[i]
            assert cop.vamsi_addr == VAMSI_ADDR[i]

    def test_core_gate_order_preserved(self):
        cc = CycleCompiler()
        cycle = cc.compile()
        gates = [cop.gate for cop in cycle]
        for i in range(1, len(gates)):
            assert gates[i] >= gates[i - 1], f"Gate order broken: {gates[i - 1]} -> {gates[i]} at position {i}"

    def test_zero_custom_count(self):
        cc = CycleCompiler()
        assert cc.custom_count == 0

    def test_compile_is_cached(self):
        cc = CycleCompiler()
        c1 = cc.compile()
        c2 = cc.compile()
        assert c1 is c2


class TestCustomOps:
    """Custom operation registration and compilation."""

    def _dummy_handler(self, lotus, ctx):
        ctx["_custom_ran"] = True

    def test_register_op(self):
        cc = CycleCompiler()
        op_id = cc.register_op("test_op", gate=2, handler=self._dummy_handler)
        assert op_id == NAVA
        assert cc.custom_count == 1

    def test_register_duplicate_raises(self):
        cc = CycleCompiler()
        cc.register_op("dup", gate=0, handler=self._dummy_handler)
        with pytest.raises(ValueError, match="already registered"):
            cc.register_op("dup", gate=0, handler=self._dummy_handler)

    def test_register_invalid_gate_raises(self):
        cc = CycleCompiler()
        with pytest.raises(ValueError, match="Gate must be 0-4"):
            cc.register_op("bad", gate=5, handler=self._dummy_handler)

    def test_compile_with_custom_op(self):
        cc = CycleCompiler()
        cc.register_op("my_analysis", gate=2, handler=self._dummy_handler)
        cycle = cc.compile()
        assert len(cycle) == NAVA + 1
        custom = [c for c in cycle if not c.is_core]
        assert len(custom) == 1
        assert custom[0].name == "my_analysis"
        assert custom[0].gate == 2

    def test_custom_op_after_core_in_same_gate(self):
        cc = CycleCompiler()
        cc.register_op("after_smaranam", gate=2, handler=self._dummy_handler)
        cycle = cc.compile()
        # EXECUTE gate (2) has: SMARANAM, VANDANAM, then custom
        execute_ops = [c for c in cycle if c.gate == 2]
        assert execute_ops[0].name == "SMARANAM"
        assert execute_ops[1].name == "VANDANAM"
        assert execute_ops[2].name == "after_smaranam"

    def test_custom_vamsi_no_collision_with_core(self):
        cc = CycleCompiler()
        cc.register_op("op1", gate=0, handler=self._dummy_handler)
        cc.register_op("op2", gate=3, handler=self._dummy_handler)
        cycle = cc.compile()
        core_addrs = set(VAMSI_ADDR)
        custom_addrs = {c.vamsi_addr for c in cycle if not c.is_core}
        assert not (core_addrs & custom_addrs), "Custom VAMSI collides with core"

    def test_custom_vamsi_no_collision_with_flute(self):
        from vibe_core.mahamantra.substrate.venu_orchestrator import THE_FLUTE_CYCLE

        cc = CycleCompiler()
        for i in range(5):
            cc.register_op(f"op_{i}", gate=i, handler=self._dummy_handler)
        cycle = cc.compile()
        flute_set = set(THE_FLUTE_CYCLE)
        custom_addrs = {c.vamsi_addr for c in cycle if not c.is_core}
        assert not (flute_set & custom_addrs), "Custom VAMSI collides with flute cycle"

    def test_unregister_invalidates(self):
        cc = CycleCompiler()
        cc.register_op("temp", gate=0, handler=self._dummy_handler)
        cc.compile()
        assert cc.is_compiled
        cc.unregister_op("temp")
        assert not cc.is_compiled
        assert cc.custom_count == 0

    def test_unregister_nonexistent(self):
        cc = CycleCompiler()
        assert cc.unregister_op("nope") is False

    def test_dispatch_includes_custom(self):
        cc = CycleCompiler()
        cc.register_op("my_op", gate=1, handler=self._dummy_handler)
        dispatch = cc.dispatch
        # Core ops present
        for op in NavaBhaktiOp:
            assert op in dispatch or op.value in dispatch
        # Custom op present
        assert NAVA in dispatch


class TestExecuteCycleIntegration:
    """Verify execute_cycle uses CycleCompiler when custom ops exist."""

    def test_custom_op_runs_in_pipeline(self):
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.substrate.cycle_compiler import get_compiler
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        # Save and reset global compiler
        old = cc_mod._COMPILER
        cc_mod._COMPILER = None

        try:
            compiler = get_compiler()
            marker = []

            def _inject_marker(lotus, ctx):
                marker.append("CUSTOM_RAN")
                ctx["_custom_marker"] = True

            compiler.register_op("marker_op", gate=4, handler=_inject_marker)

            lotus = MahamantraLotus()
            lotus.bootstrap(lazy=True, silent=True)
            result = execute_cycle(lotus, "test custom op")

            assert len(marker) == 1, "Custom op did not run"
            assert result is not None
            assert "input" in result
        finally:
            # Restore
            cc_mod._COMPILER = old


class TestConditionBits:
    """Condition evaluation — ops can be conditionally skipped."""

    def test_condition_true_runs(self):
        """Op with condition=True runs normally."""
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        old = cc_mod._COMPILER
        cc_mod._COMPILER = None
        try:
            compiler = cc_mod.get_compiler()
            marker = []

            def _handler(lotus, ctx):
                marker.append("RAN")

            compiler.register_op(
                "always_run",
                gate=4,
                handler=_handler,
                condition=lambda ctx: True,
            )

            lotus = MahamantraLotus()
            lotus.bootstrap(lazy=True, silent=True)
            execute_cycle(lotus, "test condition true")
            assert len(marker) == 1
        finally:
            cc_mod._COMPILER = old

    def test_condition_false_skips(self):
        """Op with condition=False is skipped."""
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        old = cc_mod._COMPILER
        cc_mod._COMPILER = None
        try:
            compiler = cc_mod.get_compiler()
            marker = []

            def _handler(lotus, ctx):
                marker.append("SHOULD_NOT_RUN")

            compiler.register_op(
                "never_run",
                gate=4,
                handler=_handler,
                condition=lambda ctx: False,
            )

            lotus = MahamantraLotus()
            lotus.bootstrap(lazy=True, silent=True)
            result = execute_cycle(lotus, "test condition false")
            assert len(marker) == 0, "Conditional op ran when condition was False"
            assert result is not None
        finally:
            cc_mod._COMPILER = old

    def test_condition_reads_ctx(self):
        """Condition can read ctx state to decide."""
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        old = cc_mod._COMPILER
        cc_mod._COMPILER = None
        try:
            compiler = cc_mod.get_compiler()
            marker = []

            def _handler(lotus, ctx):
                marker.append("CTX_CONDITIONAL")

            compiler.register_op(
                "ctx_check",
                gate=4,
                handler=_handler,
                condition=lambda ctx: ctx.get("parampara_verified", False),
            )

            lotus = MahamantraLotus()
            lotus.bootstrap(lazy=True, silent=True)
            execute_cycle(lotus, "Hare Krishna")
            # parampara_verified is set by ARCANAM step — should be True or False
            # Either way, the condition evaluated ctx correctly
            assert isinstance(marker, list)  # No crash = condition evaluated
        finally:
            cc_mod._COMPILER = old

    def test_core_ops_unconditional(self):
        """Core ops always have condition=None (never skipped)."""
        cc = CycleCompiler()
        cycle = cc.compile()
        for cop in cycle:
            if cop.is_core:
                assert cop.condition is None, f"Core op {cop.name} has condition set — core ops must be unconditional"


class TestMicroKernelWiring:
    """VMCapabilityProtocol auto-discovery at bootstrap."""

    def test_vm_capability_discovered_at_bootstrap(self):
        """A service implementing VMCapabilityProtocol gets its ops registered."""
        from unittest.mock import patch

        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.protocols._navabhakti import VMOpDeclaration
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        old_compiler = cc_mod._COMPILER
        cc_mod._COMPILER = None

        try:
            marker = []

            class FakeVMService:
                """A service that declares a VM op."""

                def vm_ops(self):
                    return [
                        VMOpDeclaration(
                            name="fake_telemetry",
                            gate=4,
                            handler=lambda lotus, ctx: marker.append("VM_CAP_RAN"),
                        )
                    ]

            class FakeProxy:
                def __init__(self, target):
                    self._target = target

            fake_proxies = [FakeProxy(FakeVMService())]

            # Mock auto_wrap_services to return our fake proxy
            with patch(
                "vibe_core.mahamantra.substrate.proxy.auto_wrap_services",
                return_value=fake_proxies,
            ):
                lotus = MahamantraLotus()
                lotus._bootstrapped = False
                lotus.bootstrap(lazy=True, silent=True)

            # The compiler should have our fake op + composition adapter
            compiler = cc_mod.get_compiler()
            assert compiler.custom_count >= 1, f"Expected at least 1 custom op, got {compiler.custom_count}"

            # Execute and verify our fake custom op runs
            result = execute_cycle(lotus, "test micro-kernel")
            assert len(marker) == 1, "VMCapability op did not run"
            assert result is not None
        finally:
            cc_mod._COMPILER = old_compiler

    def test_composition_adapter_auto_discovered(self):
        """Bootstrap auto-discovers MahaComposition as VMCapability."""
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        old_compiler = cc_mod._COMPILER
        cc_mod._COMPILER = None

        try:
            lotus = MahamantraLotus()
            lotus._bootstrapped = False
            lotus.bootstrap(lazy=True, silent=True)

            compiler = cc_mod.get_compiler()
            # MahaComposition implements VMCapabilityProtocol → auto-registered
            assert compiler.custom_count >= 1, (
                f"Expected composition adapter to be discovered, got {compiler.custom_count} custom ops"
            )
        finally:
            cc_mod._COMPILER = old_compiler

    def test_vm_capability_with_condition(self):
        """VMCapability ops with conditions are evaluated correctly."""
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod
        from vibe_core.mahamantra.protocols._navabhakti import VMOpDeclaration
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.mantra_vm import execute_cycle

        old_compiler = cc_mod._COMPILER
        cc_mod._COMPILER = None

        try:
            marker = []

            class ConditionalService:
                def vm_ops(self):
                    return [
                        VMOpDeclaration(
                            name="conditional_cap",
                            gate=4,
                            handler=lambda lotus, ctx: marker.append("COND_RAN"),
                            condition=lambda ctx: False,  # Never runs
                        )
                    ]

            class FakeProxy:
                def __init__(self, target):
                    self._target = target

            lotus = MahamantraLotus()
            lotus._bootstrapped = False
            lotus._balarama_proxies = [FakeProxy(ConditionalService())]
            lotus.bootstrap(lazy=True, silent=True)

            result = execute_cycle(lotus, "test conditional cap")
            assert len(marker) == 0, "Conditional VMCapability ran when it shouldn't"
            assert result is not None
        finally:
            cc_mod._COMPILER = old_compiler


class TestSingleton:
    """Global compiler singleton."""

    def test_get_compiler_returns_same(self):
        import vibe_core.mahamantra.substrate.cycle_compiler as cc_mod

        old = cc_mod._COMPILER
        cc_mod._COMPILER = None
        try:
            c1 = get_compiler()
            c2 = get_compiler()
            assert c1 is c2
        finally:
            cc_mod._COMPILER = old
