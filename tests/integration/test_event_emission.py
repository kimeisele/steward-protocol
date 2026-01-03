#!/usr/bin/env python3
"""
OPUS-073: Event Emission Integration Tests
==========================================

These tests document the event system architecture investigation.

STATUS: INVESTIGATION ONLY
These tests were created during OPUS-073 investigation.
The kernel change was REVERTED - it was not the right approach.

MANAS does NOT need KERNEL_TICK - it needs:
- KERNEL_BOOT (once at boot)
- HOURLY_PULSE (from heartbeat, not kernel)
- IDLE_DETECTED (from activity monitor)
- MANAS_FORCE_THINK (manual trigger)

Discovery: 2025-12-14
Reverted: 2025-12-15
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestManasRequirements:
    """
    Tests that document what MANAS actually needs.
    Based on manas_awakening.yaml triggers.
    """

    def test_manas_does_not_need_kernel_tick(self):
        """MANAS awakening circuit explicitly does NOT trigger on KERNEL_TICK."""
        circuit_path = (
            Path(__file__).parent.parent.parent
            / "vibe_core"
            / "plugins"
            / "opus_assistant"
            / "circuits"
            / "manas_awakening.yaml"
        )
        content = circuit_path.read_text()

        # Verify MANAS does NOT listen for KERNEL_TICK
        assert "NOT triggered on every KERNEL_TICK" in content, "MANAS rate limiting comment missing"

        # Verify what MANAS actually needs
        assert "HOURLY_PULSE" in content, "MANAS needs HOURLY_PULSE"
        assert "IDLE_DETECTED" in content, "MANAS needs IDLE_DETECTED"
        assert "KERNEL_BOOT" in content, "MANAS needs KERNEL_BOOT"

    def test_kernel_boot_emitted(self):
        """Verify KERNEL_BOOT is emitted during kernel.boot(). STATUS: PASSING"""
        kernel_impl = Path(__file__).parent.parent.parent / "vibe_core" / "kernel_impl.py"
        content = kernel_impl.read_text()

        has_boot_emission = "KERNEL_BOOT" in content and "emit" in content

        assert has_boot_emission, "KERNEL_BOOT should be emitted during boot"

    @pytest.mark.skip(
        reason="OPUS-212: heartbeat.py refactored to use DI-based SystemHeartbeatProtocol - HOURLY_PULSE moved to plugin"
    )
    def test_hourly_pulse_source(self):
        """
        Verify HOURLY_PULSE comes from heartbeat.py.

        OPUS-091: FIXED! Heartbeat now emits HOURLY_PULSE instead of direct manas.think() call.
        OPUS-212: heartbeat.py was refactored to use DI-based SystemHeartbeatProtocol.
        """
        heartbeat_path = Path(__file__).parent.parent.parent / "scripts" / "heartbeat.py"
        content = heartbeat_path.read_text()

        # OPUS-091: heartbeat.py now emits HOURLY_PULSE event
        has_hourly_pulse = "HOURLY_PULSE" in content and "EventType.HOURLY_PULSE" in content

        assert has_hourly_pulse, "HOURLY_PULSE should be emitted by heartbeat.py (OPUS-091)"


class TestHeartbeatManasConnection:
    """
    Tests that heartbeat.py is connected to MANAS.
    This is the RIGHT place for MANAS triggering - not the kernel.
    """

    @pytest.mark.skip(
        reason="OPUS-212: heartbeat.py refactored to use DI-based SystemHeartbeatProtocol - no direct MANAS import"
    )
    def test_heartbeat_imports_manas(self):
        """Verify heartbeat.py uses MANAS. STATUS: PASSING (OPUS-073)

        OPUS-212: heartbeat.py was refactored to use DI-based SystemHeartbeatProtocol
        instead of direct MANAS imports. MANAS is now triggered through the plugin system.
        """
        heartbeat_path = Path(__file__).parent.parent.parent / "scripts" / "heartbeat.py"
        content = heartbeat_path.read_text()

        has_manas = "manas" in content.lower() or "cognitive_kernel" in content.lower() or "think(" in content

        assert has_manas, (
            "heartbeat.py should import and use MANAS.\nThis is the right place for MANAS triggering - not the kernel."
        )

    @pytest.mark.xfail(reason="OPUS-073: Heartbeat DRY RUN only")
    def test_heartbeat_has_live_execution(self):
        """Verify heartbeat has live execution mode."""
        heartbeat_path = Path(__file__).parent.parent.parent / "scripts" / "heartbeat.py"
        content = heartbeat_path.read_text()

        has_live_mode = "--live" in content or "DRY_RUN = False" in content or "execute_live" in content

        assert has_live_mode, "heartbeat.py needs live execution mode"


class TestArchitectureDocumentation:
    """
    Tests that the architecture investigation is documented.
    """

    def test_treibsand_documented(self):
        """Verify OPUS-073 investigation is documented."""
        wiring_map = Path(__file__).parent.parent.parent / "docs" / "architecture" / "OPUS" / "070-VAJRA-WIRING-MAP.md"
        content = wiring_map.read_text()

        assert "OPUS-073" in content or "TREIBSAND" in content, "OPUS-073 investigation should be documented"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
