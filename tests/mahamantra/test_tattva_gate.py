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


class TestGateHooks:
    """Gate hooks fire at gate boundaries with pipeline context."""

    def test_hook_fires_on_parse(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        captured = []
        lotus.on_gate(TattvaGate.PARSE, lambda gate, ctx: captured.append((gate, ctx)))
        lotus("test")
        assert len(captured) == 1
        assert captured[0][0] == TattvaGate.PARSE
        assert "input_data" in captured[0][1]

    def test_all_five_gates_fire(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        gates_seen = []
        for gate in TattvaGate:
            lotus.on_gate(gate, lambda g, ctx, _g=gate: gates_seen.append(_g))
        lotus("dharma")
        assert gates_seen == [
            TattvaGate.PARSE,
            TattvaGate.VALIDATE,
            TattvaGate.EXECUTE,
            TattvaGate.RESULT,
            TattvaGate.SYNC,
        ]

    def test_validate_hook_receives_seed(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        captured = []
        lotus.on_gate(TattvaGate.VALIDATE, lambda g, ctx: captured.append(ctx))
        lotus("karma")
        assert len(captured) == 1
        assert "seed" in captured[0]
        assert isinstance(captured[0]["seed"], int)

    def test_execute_hook_receives_attractor(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        captured = []
        lotus.on_gate(TattvaGate.EXECUTE, lambda g, ctx: captured.append(ctx))
        lotus("jnana")
        assert "attractor" in captured[0]
        assert "parampara_verified" in captured[0]

    def test_sync_hook_receives_position(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        captured = []
        lotus.on_gate(TattvaGate.SYNC, lambda g, ctx: captured.append(ctx))
        lotus("bhakti")
        assert "position" in captured[0]
        assert "guardian" in captured[0]
        assert 0 <= captured[0]["position"] <= 15

    def test_sync_hook_receives_opcode_and_guna(self):
        """SYNC gate context includes opcode and guna (TattvaGate→OpCode→Guna wiring)."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        captured = []
        lotus.on_gate(TattvaGate.SYNC, lambda g, ctx: captured.append(ctx))
        lotus("dharma")
        ctx = captured[0]
        assert "opcode" in ctx, "SYNC gate must receive opcode"
        assert "guna" in ctx, "SYNC gate must receive guna"
        assert hasattr(ctx["opcode"], "name"), "opcode must be a MantraOpCode enum"
        assert hasattr(ctx["guna"], "name"), "guna must be a Guna enum"
        assert ctx["guna"].name in ("SATTVA", "RAJAS", "TAMAS")

    def test_hook_error_does_not_crash_pipeline(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()

        def bad_hook(gate, ctx):
            raise ValueError("intentional test error")

        lotus.on_gate(TattvaGate.PARSE, bad_hook)
        result = lotus("resilience")
        assert result is not None
        assert "gate_trace" in result

    def test_response_contains_guna(self):
        """__call__ response includes guna dict with mode, opcode, source."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        result = lotus("karma")
        assert "guna" in result
        guna = result["guna"]
        assert guna["mode"] in ("SATTVA", "RAJAS", "TAMAS")
        assert "opcode" in guna
        assert "opcode_value" in guna
        assert guna["source"] == "position"  # no caller opcode → derived from position

    def test_caller_supplied_opcode_overrides_position(self):
        """Caller can supply opcode explicitly — Guna derived from it, not position."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        lotus = MahamantraLotus()
        # Force TAMAS opcode (IO_FLUSH = 13)
        result = lotus("hello world", opcode=MantraOpCode.IO_FLUSH.value)
        guna = result["guna"]
        assert guna["mode"] == "TAMAS"
        assert guna["opcode"] == "IO_FLUSH"
        assert guna["source"] == "caller"

    def test_guna_consistent_with_guna_module(self):
        """Guna in response matches guna.get_guna(MantraOpCode(position))."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode
        from vibe_core.mahamantra.substrate.guna import get_guna

        lotus = MahamantraLotus()
        result = lotus("test consistency")
        position = result["position"]
        expected_guna = get_guna(MantraOpCode(position))
        assert result["guna"]["mode"] == expected_guna.name

    def test_auto_registers_in_tattva_registry(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
        from vibe_core.mahamantra.substrate.tattva_registry import get_registry

        lotus = MahamantraLotus()
        reg = get_registry()
        assert "mahamantra_lotus" in reg
        tattva = reg.get("mahamantra_lotus")
        assert "MahamantraLotus" in tattva["chaitanya"]
