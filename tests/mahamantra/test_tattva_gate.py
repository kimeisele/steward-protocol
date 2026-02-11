"""
TATTVA GATE PIPELINE — Tests
============================

Verifies that the 5 TattvaGate stages are explicit in MahamantraLotus.__call__()
and that MahamantraLotus implements PanchaTattvaProtocol via __tattva__.
"""

import pytest
from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate


class TestTattvaGateInLotus:
    """TattvaGate pipeline is explicit in MahamantraLotus."""

    def test_lotus_has_tattva(self):
        """MahamantraLotus implements __tattva__ (PanchaTattvaProtocol)."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        tattva = lotus.__tattva__
        assert isinstance(tattva, dict)
        assert "chaitanya" in tattva
        assert "nityananda" in tattva
        assert "advaita" in tattva
        assert "gadadhara" in tattva
        assert "srivasa" in tattva

    def test_lotus_tattva_protocol_compliant(self):
        """MahamantraLotus passes isinstance check for PanchaTattvaProtocol."""
        from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        assert isinstance(lotus, PanchaTattvaProtocol)

    def test_active_gate_idle_before_call(self):
        """active_gate is None when no __call__ is in progress."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        assert lotus.active_gate is None

    def test_call_returns_gate_trace(self):
        """__call__ response includes gate_trace with all 5 TattvaGates."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        result = lotus("dharma")
        assert "gate_trace" in result
        trace = result["gate_trace"]
        assert len(trace) == 5
        assert trace == ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC")

    def test_call_returns_tattva_gate_field(self):
        """__call__ response includes tattva_gate field."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        result = lotus("satya")
        assert "tattva_gate" in result
        assert result["tattva_gate"] == "SRIVASA"

    def test_active_gate_resets_after_call(self):
        """active_gate is None after __call__ completes."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        lotus("test")
        assert lotus.active_gate is None

    def test_tattva_gadadhara_shows_live_state(self):
        """__tattva__['gadadhara'] reflects current runtime state."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        tattva_before = lotus.__tattva__
        assert "IDLE" in tattva_before["gadadhara"]

        lotus("karma")
        tattva_after = lotus.__tattva__
        assert "rounds=1" in tattva_after["gadadhara"] or "beats=" in tattva_after["gadadhara"]


class TestTattvaGateEnum:
    """TattvaGate enum is correct."""

    def test_five_gates(self):
        assert len(TattvaGate) == 5

    def test_gate_order(self):
        assert TattvaGate.PARSE < TattvaGate.VALIDATE
        assert TattvaGate.VALIDATE < TattvaGate.EXECUTE
        assert TattvaGate.EXECUTE < TattvaGate.RESULT
        assert TattvaGate.RESULT < TattvaGate.SYNC

    def test_gate_names(self):
        names = [g.name for g in TattvaGate]
        assert names == ["PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC"]
