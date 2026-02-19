"""
TEST: CLI Commands Route Through VM Pipeline
=============================================

Proves that ALL CLI commands in commands.py route their computation
through lotus.execute() → execute_cycle() (the VM) instead of
building parallel universes with direct substrate access.

The test strategy: mock lotus.execute() and verify it gets called
when each CLI command runs. If a command bypasses the VM, the mock
won't be called and the test fails.
"""

import pytest
from unittest.mock import patch, MagicMock


# A realistic VM result dict (subset of the 27 keys)
def _make_vm_result(**overrides):
    """Build a realistic lotus.execute() return value."""
    base = {
        "success": True,
        "command": "test",
        "exit_code": 0,
        "handler": "mahamantra[5]",
        "input": "test input",
        "position": 5,
        "guardian": "kumaras",
        "quarter": "dharma",
        "role": "WORKER",
        "vibration": {"seed": 42, "attractor": 7, "rama_index": 3,
                      "phoneme": "ka", "signature": {}},
        "parampara": {"verified": True, "channel": "direct", "coherence": 1.0},
        "chapter": 2,
        "chapter_significance": "sankhya",
        "verse": {"chapter": 2, "verse": 47},
        "matches": 3,
        "gita_phase": "KARMA",
        "is_complete": False,
        "diw": {"raw": 12345, "venu": 7, "vamsi": 42, "murali": 3},
        "cell": {"header_size": 64, "payload_size": 10, "total_size": 74,
                 "valid": True, "parampara_verified": True, "prana": 100,
                 "integrity": 0.95, "is_alive": True, "cycle": 1},
        "execution": {"success": True, "prana": 100, "integrity": 0.95,
                      "kirtan_cycles": 3, "transformations": 48,
                      "yajna_ticks": 16, "cycles": 1,
                      "guardian_acted": False, "guardian_result": None},
        "yajna": {"phase": "KIRTAN", "cycle_count": 1, "switch_count": 2,
                  "return_count": 0, "dissonance": None},
        "smaranam": ({"sanskrit": "dharma", "meaning": "duty", "score": 0.9},),
        "composed": "Test composed output",
        "nama": {"coords": [], "phoneme_count": 0},
        "antaranga": {"active_slots": 0, "total_prana": 0, "collisions": 0,
                      "size_bytes": 0},
        "akash": {},
        "gate_trace": ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC"),
        "holy_name": "Hare",
        "quarter_head": "Prithu",
        "trinity_function": "maintain",
    }
    base.update(overrides)
    return base


class TestCliChantRoutesThoughVM:
    """cli_chant must call lotus.execute(), not build its own chamber."""

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.substrate.harmonics.SravanamCheck.validate_epoch_lock",
           return_value=True)
    def test_chant_calls_lotus_execute(self, mock_epoch, mock_get_lotus):
        """cli_chant(rounds=2) must call lotus.execute() exactly 2 times."""
        from vibe_core.mahamantra.commands import cli_chant

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result()
        mock_get_lotus.return_value = mock_lotus

        result = cli_chant(rounds=2, verbose=False, audio=False)

        assert mock_lotus.execute.call_count == 2
        assert result["success"] is True
        assert result["rounds"] == 2

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.substrate.harmonics.SravanamCheck.validate_epoch_lock",
           return_value=True)
    def test_chant_uses_vm_position(self, mock_epoch, mock_get_lotus):
        """cli_chant result must use position from VM, not from its own chamber."""
        from vibe_core.mahamantra.commands import cli_chant

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result(position=13, guardian="bali")
        mock_get_lotus.return_value = mock_lotus

        result = cli_chant(rounds=1)

        assert result["final_position"] == 13
        assert result["final_guardian"] == "bali"

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.substrate.harmonics.SravanamCheck.validate_epoch_lock",
           return_value=True)
    def test_chant_uses_vm_parampara(self, mock_epoch, mock_get_lotus):
        """cli_chant parampara_connected must come from VM result."""
        from vibe_core.mahamantra.commands import cli_chant

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result(
            parampara={"verified": True, "channel": "direct", "coherence": 1.0}
        )
        mock_get_lotus.return_value = mock_lotus

        result = cli_chant(rounds=1)
        assert result["parampara_connected"] is True


class TestCliServeRoutesThroughVM:
    """cli_serve must call lotus.execute() before submitting to JanakaService."""

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    def test_serve_calls_lotus_execute(self, mock_get_lotus):
        """cli_serve must call lotus.execute() with the task string."""
        import vibe_core.mahamantra.karma.janaka as janaka_mod
        from vibe_core.mahamantra.commands import cli_serve

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result(position=10, guardian="janaka")
        mock_get_lotus.return_value = mock_lotus

        mock_janaka = MagicMock()
        mock_janaka.submit.return_value = "task-001"
        with patch.object(janaka_mod, "get_service", create=True, return_value=mock_janaka):
            result = cli_serve(task="build the temple", execute=False)

        mock_lotus.execute.assert_called_once_with("build the temple")
        assert result["success"] is True

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    def test_serve_passes_vm_routing_to_janaka(self, mock_get_lotus):
        """cli_serve must pass VM-computed guardian/position to JanakaService."""
        import vibe_core.mahamantra.karma.janaka as janaka_mod
        from vibe_core.mahamantra.commands import cli_serve

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result(position=8, guardian="parashurama")
        mock_get_lotus.return_value = mock_lotus

        mock_janaka = MagicMock()
        mock_janaka.submit.return_value = "task-002"
        with patch.object(janaka_mod, "get_service", create=True, return_value=mock_janaka):
            cli_serve(task="execute dharma", execute=False)

        # Verify sovereign_id contains VM routing info
        call_kwargs = mock_janaka.submit.call_args
        sovereign_id = call_kwargs.kwargs.get("sovereign_id") or call_kwargs[1].get("sovereign_id", "")
        assert "parashurama" in sovereign_id
        assert "8" in sovereign_id


class TestCliListenRoutesThroughVM:
    """cli_listen must call lotus.execute() before fetching events."""

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.commands.get_events")
    def test_listen_calls_lotus_execute(self, mock_get_events, mock_get_lotus):
        """cli_listen must call lotus.execute() with the source query."""
        from vibe_core.mahamantra.commands import cli_listen

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result()
        mock_get_lotus.return_value = mock_lotus

        mock_get_events.return_value = ([], 0)

        cli_listen(source="violations", tail=5)

        mock_lotus.execute.assert_called_once_with("listen violations")


class TestCliResolveRoutesThroughVM:
    """cli_resolve must call lotus.execute() before performing lookup."""

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.substrate.wiring.get_position_from_name")
    def test_resolve_calls_lotus_execute(self, mock_get_pos, mock_get_lotus):
        """cli_resolve must call lotus.execute() with the name query."""
        from vibe_core.mahamantra.commands import cli_resolve

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result()
        mock_get_lotus.return_value = mock_lotus

        # Mock position lookup
        mock_pos = MagicMock()
        mock_pos.guardian.value = "brahma"
        mock_pos.index = 1
        mock_pos.word.value = "Krishna"
        mock_pos.is_head = False
        mock_get_pos.return_value = mock_pos

        cli_resolve(name="brahma")

        mock_lotus.execute.assert_called_once_with("resolve brahma")


class TestCliVedaRoutesThroughVM:
    """cli_veda must call lotus.execute() before processing with VedaExplorer."""

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.cli.veda_explorer.VedaExplorer")
    def test_veda_calls_lotus_execute(self, mock_explorer_cls, mock_get_lotus):
        """cli_veda must call lotus.execute() with the message."""
        from vibe_core.mahamantra.commands import cli_veda

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result()
        mock_get_lotus.return_value = mock_lotus

        mock_explorer = MagicMock()
        mock_explorer.process.return_value = {
            "success": True, "intent": "query", "response": "answer", "llm_used": False
        }
        mock_explorer.llm_available = False
        mock_explorer_cls.return_value = mock_explorer

        cli_veda(message="what is dharma", mode="enhanced")

        mock_lotus.execute.assert_called_once_with("what is dharma")

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.cli.veda_explorer.VedaExplorer")
    def test_veda_uses_vm_composed_output(self, mock_explorer_cls, mock_get_lotus):
        """When VM produces composed output and no LLM is used, prefer VM output."""
        from vibe_core.mahamantra.commands import cli_veda

        mock_lotus = MagicMock()
        mock_lotus.execute.return_value = _make_vm_result(composed="VM says dharma is duty")
        mock_get_lotus.return_value = mock_lotus

        mock_explorer = MagicMock()
        mock_explorer.process.return_value = {
            "success": True, "intent": "query", "response": "explorer says something",
            "llm_used": False,
        }
        mock_explorer.llm_available = False
        mock_explorer_cls.return_value = mock_explorer

        result = cli_veda(message="what is dharma")

        # VM-composed output should be used when no LLM
        assert result["response"] == "VM says dharma is duty"

    @patch("vibe_core.mahamantra.substrate.lotus_core.get_mahamantra")
    @patch("vibe_core.mahamantra.cli.veda_explorer.VedaExplorer")
    def test_veda_empty_message_skips_vm(self, mock_explorer_cls, mock_get_lotus):
        """Empty message should return error without calling VM."""
        from vibe_core.mahamantra.commands import cli_veda

        mock_lotus = MagicMock()
        mock_get_lotus.return_value = mock_lotus

        mock_explorer = MagicMock()
        mock_explorer_cls.return_value = mock_explorer

        result = cli_veda(message="")

        mock_lotus.execute.assert_not_called()
        assert result["success"] is False


class TestNoBypassPaths:
    """Meta-test: verify commands.py has NO direct substrate access outside VM."""

    def test_cli_chant_has_no_chamber_import(self):
        """cli_chant must NOT import SankirtanChamber (VM does chamber work)."""
        import inspect
        from vibe_core.mahamantra.commands import cli_chant
        source = inspect.getsource(cli_chant)
        assert "SankirtanChamber" not in source, \
            "cli_chant still imports SankirtanChamber — bypassing VM"

    def test_cli_chant_has_no_direct_tick(self):
        """cli_chant must NOT call mahamantra.tick() (VM does ticking)."""
        import inspect
        from vibe_core.mahamantra.commands import cli_chant
        source = inspect.getsource(cli_chant)
        assert "mahamantra.tick()" not in source, \
            "cli_chant still calls mahamantra.tick() — bypassing VM"

    def test_cli_serve_has_no_direct_janaka_protocol(self):
        """cli_serve must NOT import JanakaProtocol (uses get_service only)."""
        import inspect
        from vibe_core.mahamantra.commands import cli_serve
        source = inspect.getsource(cli_serve)
        assert "JanakaProtocol" not in source, \
            "cli_serve still imports JanakaProtocol — unnecessary coupling"
