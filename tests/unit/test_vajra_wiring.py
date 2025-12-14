"""
⚡ VAJRA Wiring Tests
=====================

Tests for the VAJRA kernel wiring enforcement system.

OPUS-070: These tests ensure wiring protocol compliance.
"""

from pathlib import Path

import pytest


class TestWiringProtocol:
    """Test WiringProtocol detection."""

    def test_is_wirable_detects_protocol(self):
        """Component with _vibe_kernel and inject_kernel is wirable."""
        from vibe_core.vajra.protocol import is_wirable

        class WirableComponent:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

        assert is_wirable(WirableComponent())

    def test_is_wirable_rejects_non_protocol(self):
        """Component without inject_kernel is not wirable."""
        from vibe_core.vajra.protocol import is_wirable

        class NotWirable:
            pass

        assert not is_wirable(NotWirable())

    def test_is_wired_checks_kernel(self):
        """is_wired returns True only when _vibe_kernel is set."""
        from vibe_core.vajra.protocol import is_wired

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

        c = Component()
        assert not is_wired(c)

        c._vibe_kernel = "fake_kernel"
        assert is_wired(c)


class TestAutoWire:
    """Test auto_wire functionality."""

    def test_auto_wire_injects_kernel(self, fresh_kernel):
        """auto_wire calls inject_kernel on wirable components."""
        from vibe_core.vajra import auto_wire

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

        c = Component()
        result = auto_wire(fresh_kernel, c)

        assert result is True
        assert c._vibe_kernel is fresh_kernel

    def test_auto_wire_skips_non_wirable(self, fresh_kernel):
        """auto_wire returns False for non-wirable objects."""
        from vibe_core.vajra import auto_wire

        class NotWirable:
            pass

        result = auto_wire(fresh_kernel, NotWirable())
        assert result is False

    def test_wire_all_wires_multiple(self, fresh_kernel):
        """wire_all wires multiple components."""
        from vibe_core.vajra import wire_all

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

        c1, c2, c3 = Component(), Component(), Component()
        count = wire_all(fresh_kernel, c1, c2, c3)

        assert count == 3
        assert c1._vibe_kernel is fresh_kernel
        assert c2._vibe_kernel is fresh_kernel
        assert c3._vibe_kernel is fresh_kernel


class TestEnforcement:
    """Test wiring enforcement decorators."""

    def test_assert_wired_allows_wired(self, fresh_kernel):
        """@assert_wired allows execution when wired."""
        from vibe_core.vajra import assert_wired, auto_wire

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

            @assert_wired
            def execute(self):
                return "success"

        c = Component()
        auto_wire(fresh_kernel, c)
        assert c.execute() == "success"

    def test_assert_wired_warns_when_unwired(self, caplog):
        """@assert_wired logs warning when unwired (permissive mode)."""
        import logging

        from vibe_core.vajra import assert_wired

        caplog.set_level(logging.WARNING)

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

            @assert_wired
            def execute(self):
                return "shadow_mode"

        c = Component()
        result = c.execute()

        assert result == "shadow_mode"
        assert "SHADOW MODE" in caplog.text

    def test_require_wiring_strict_raises(self):
        """@require_wiring(strict=True) raises WiringError."""
        from vibe_core.vajra import WiringError, require_wiring

        class Component:
            _vibe_kernel = None

            def inject_kernel(self, kernel):
                self._vibe_kernel = kernel

            @require_wiring(strict=True)
            def critical_operation(self):
                return "should not reach"

        c = Component()
        with pytest.raises(WiringError) as exc:
            c.critical_operation()

        assert "VAJRA VIOLATION" in str(exc.value)
        assert "Component" in str(exc.value)


class TestVAJRAScanner:
    """Test the static scanner."""

    def test_scanner_finds_wirable_classes(self):
        """Scanner detects classes with inject_kernel."""
        from vibe_core.vajra.scanner import VAJRAScanner

        scanner = VAJRAScanner(Path(__file__).parent.parent.parent)
        result = scanner.scan(["vibe_core/vajra"])

        # Should find our own test fixtures at minimum
        assert result.total_components > 0

    def test_scan_for_orphans_convenience(self):
        """scan_for_orphans convenience function works."""
        from vibe_core.vajra import scan_for_orphans

        result = scan_for_orphans(
            project_root=Path(__file__).parent.parent.parent,
            scan_dirs=["vibe_core/vajra"],
        )

        assert hasattr(result, "health_score")
        assert hasattr(result, "orphans")


class TestRealComponents:
    """Test that real components are properly wirable."""

    def test_analyst_tools_are_wirable(self):
        """All 6 Analyst tools implement WiringProtocol."""
        # Import all analyst tools
        from vibe_core.cartridges.agent_city.analyst.tools.architecture_tool import (
            ArchitectureAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.code_tool import (
            CodeAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.deps_tool import (
            DependencyAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.docs_tool import (
            DocsAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.git_tool import (
            GitAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.structure_tool import (
            StructureAnalysisTool,
        )
        from vibe_core.vajra.protocol import is_wirable

        tools = [
            ArchitectureAnalysisTool(),
            CodeAnalysisTool(),
            DependencyAnalysisTool(),
            DocsAnalysisTool(),
            GitAnalysisTool(),
            StructureAnalysisTool(),
        ]

        for tool in tools:
            assert is_wirable(tool), f"{tool.name} should be wirable"

    def test_analyst_tools_can_be_wired(self, fresh_kernel):
        """All 6 Analyst tools can be auto-wired."""
        from vibe_core.cartridges.agent_city.analyst.tools.architecture_tool import (
            ArchitectureAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.code_tool import (
            CodeAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.deps_tool import (
            DependencyAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.docs_tool import (
            DocsAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.git_tool import (
            GitAnalysisTool,
        )
        from vibe_core.cartridges.agent_city.analyst.tools.structure_tool import (
            StructureAnalysisTool,
        )
        from vibe_core.vajra import wire_all
        from vibe_core.vajra.protocol import is_wired

        tools = [
            ArchitectureAnalysisTool(),
            CodeAnalysisTool(),
            DependencyAnalysisTool(),
            DocsAnalysisTool(),
            GitAnalysisTool(),
            StructureAnalysisTool(),
        ]

        wired = wire_all(fresh_kernel, *tools)
        assert wired == 6

        for tool in tools:
            assert is_wired(tool), f"{tool.name} should be wired"
            assert tool._get_ledger() is fresh_kernel.ledger

    def test_sruti_validator_is_wirable(self):
        """SrutiValidator implements WiringProtocol."""
        from vibe_core.plugins.opus_assistant.manas.validator import SrutiValidator
        from vibe_core.vajra.protocol import is_wirable

        validator = SrutiValidator()
        assert is_wirable(validator)

    def test_audit_ledger_is_wirable(self):
        """AuditLedger implements WiringProtocol."""
        from vibe_core.cartridges.system.archivist.tools.ledger import AuditLedger
        from vibe_core.vajra.protocol import is_wirable

        ledger = AuditLedger()
        assert is_wirable(ledger)
