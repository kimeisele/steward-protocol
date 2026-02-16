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


class TestGateHooksViaGovardhan:
    """
    Gate hooks fire at the BOUNDARY (GovardhanGateway), not inside __call__().

    Architecture: Functional Core / Imperative Shell
    - __call__() is pure computation (Vrindavan) — no gates
    - GovardhanGateway is the boundary (Govardhan) — gates fire here
    """

    def test_hook_fires_on_parse_via_gateway(self):
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.gateway.mahamantra_gateway import GovardhanGateway
        from vibe_core.protocols.gateway import create_request, EntryType

        lotus = get_mahamantra()
        captured = []
        lotus.on_gate(TattvaGate.PARSE, lambda gate, ctx: captured.append((gate, ctx)))
        gw = GovardhanGateway()
        gw.receive(create_request("test", [], EntryType.CLI))
        assert len(captured) >= 1
        assert captured[0][0] == TattvaGate.PARSE
        assert "input_data" in captured[0][1]

    def test_all_five_gates_fire_via_gateway(self):
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.gateway.mahamantra_gateway import GovardhanGateway
        from vibe_core.protocols.gateway import create_request, EntryType

        lotus = get_mahamantra()
        gates_seen = []
        for gate in TattvaGate:
            lotus.on_gate(gate, lambda g, ctx, _g=gate: gates_seen.append(_g))
        gw = GovardhanGateway()
        gw.receive(create_request("dharma", [], EntryType.CLI))
        assert gates_seen == [
            TattvaGate.PARSE,
            TattvaGate.VALIDATE,
            TattvaGate.EXECUTE,
            TattvaGate.RESULT,
            TattvaGate.SYNC,
        ]

    def test_sync_hook_receives_position_via_gateway(self):
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.gateway.mahamantra_gateway import GovardhanGateway
        from vibe_core.protocols.gateway import create_request, EntryType

        lotus = get_mahamantra()
        captured = []
        lotus.on_gate(TattvaGate.SYNC, lambda g, ctx: captured.append(ctx))
        gw = GovardhanGateway()
        gw.receive(create_request("bhakti", [], EntryType.CLI))
        assert len(captured) >= 1
        assert "position" in captured[0]
        assert "guardian" in captured[0]

    def test_sync_hook_receives_guna_via_gateway(self):
        """SYNC gate context includes guna at the boundary."""
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.gateway.mahamantra_gateway import GovardhanGateway
        from vibe_core.protocols.gateway import create_request, EntryType

        lotus = get_mahamantra()
        captured = []
        lotus.on_gate(TattvaGate.SYNC, lambda g, ctx: captured.append(ctx))
        gw = GovardhanGateway()
        gw.receive(create_request("dharma", [], EntryType.CLI))
        ctx = captured[0]
        assert "guna" in ctx, "SYNC gate must receive guna"

    def test_call_is_pure_no_gates_fire(self):
        """__call__() is pure computation — no gates fire inside it."""
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        gates_seen = []
        for gate in TattvaGate:
            lotus.on_gate(gate, lambda g, ctx, _g=gate: gates_seen.append(_g))
        lotus("dharma")
        assert gates_seen == [], "__call__() must NOT fire any gates (pure computation)"

    def test_hook_error_does_not_crash_gateway(self):
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.gateway.mahamantra_gateway import GovardhanGateway
        from vibe_core.protocols.gateway import create_request, EntryType

        lotus = get_mahamantra()

        def bad_hook(gate, ctx):
            raise ValueError("intentional test error")

        lotus.on_gate(TattvaGate.PARSE, bad_hook)
        gw = GovardhanGateway()
        result = gw.receive(create_request("resilience", [], EntryType.CLI))
        assert result is not None

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
