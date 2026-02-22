"""
TEST: CLI Commands — Real Integration Through VM Pipeline
==========================================================

Every test calls the REAL CLI command with the REAL Lotus/VM.
No mocks. No MagicMock. No patch. Real objects, real assertions.

Tests verify:
  1. Return types match TypedDict contracts
  2. Field values are sane (positions 0-15, guardians are strings, etc.)
  3. Determinism: same input → same output
  4. Architecture guards: CLI does NOT bypass the VM
"""

import pytest

from vibe_core.mahamantra.protocols._seed import WORDS

# =============================================================================
# CLI_CHANT — Real Integration
# =============================================================================


class TestCliChant:
    """cli_chant calls the real VM pipeline end-to-end."""

    def test_chant_returns_success(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        assert result["success"] is True

    def test_chant_result_has_all_fields(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        for key in (
            "success",
            "bhakti",
            "rounds",
            "ticks",
            "final_position",
            "final_guardian",
            "cycle_count",
            "switch_count",
            "parampara_connected",
        ):
            assert key in result, f"Missing key: {key}"

    def test_chant_position_in_range(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        assert 0 <= result["final_position"] < WORDS

    def test_chant_guardian_is_string(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        assert isinstance(result["final_guardian"], str)
        assert len(result["final_guardian"]) > 0

    def test_chant_ticks_equals_rounds_times_words(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=2, verbose=False, audio=False)
        assert result["rounds"] == 2
        assert result["ticks"] == 2 * WORDS

    def test_chant_parampara_is_bool(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        assert isinstance(result["parampara_connected"], bool)

    def test_chant_switch_count_non_negative(self):
        from vibe_core.mahamantra.commands import cli_chant

        result = cli_chant(rounds=1, verbose=False, audio=False)
        assert result["switch_count"] >= 0

    def test_chant_deterministic(self):
        """Same input → same position and guardian (VM is deterministic)."""
        from vibe_core.mahamantra.commands import cli_chant

        r1 = cli_chant(rounds=1, verbose=False, audio=False)
        r2 = cli_chant(rounds=1, verbose=False, audio=False)
        assert r1["final_position"] == r2["final_position"]
        assert r1["final_guardian"] == r2["final_guardian"]


# =============================================================================
# CLI_LISTEN — Real Integration
# =============================================================================


class TestCliListen:
    """cli_listen calls the real VM + event bridge."""

    def test_listen_returns_success(self):
        from vibe_core.mahamantra.commands import cli_listen

        result = cli_listen(source="all", tail=5, json=True)
        assert result["success"] is True

    def test_listen_result_has_all_fields(self):
        from vibe_core.mahamantra.commands import cli_listen

        result = cli_listen(source="all", tail=5, json=True)
        for key in ("success", "bhakti", "source", "total_entries", "filtered_entries", "entries"):
            assert key in result, f"Missing key: {key}"

    def test_listen_entries_is_list(self):
        from vibe_core.mahamantra.commands import cli_listen

        result = cli_listen(source="all", tail=3, json=True)
        assert isinstance(result["entries"], list)

    def test_listen_filtered_le_total(self):
        from vibe_core.mahamantra.commands import cli_listen

        result = cli_listen(source="all", tail=100, json=True)
        assert result["filtered_entries"] <= result["total_entries"]


# =============================================================================
# CLI_RESOLVE — Real Integration
# =============================================================================


class TestCliResolve:
    """cli_resolve calls the real VM + SSOT wiring."""

    def test_resolve_brahma(self):
        from vibe_core.mahamantra.commands import cli_resolve

        result = cli_resolve(name="brahma", json=True)
        assert result["success"] is True
        assert result["name"] == "brahma"
        assert result["position"] == 1

    def test_resolve_by_position(self):
        from vibe_core.mahamantra.commands import cli_resolve

        result = cli_resolve(name="0", json=True)
        assert result["success"] is True
        assert result["position"] == 0

    def test_resolve_unknown_fails(self):
        from vibe_core.mahamantra.commands import cli_resolve

        result = cli_resolve(name="nonexistent_xyz", json=True)
        assert result["success"] is False

    def test_resolve_result_has_all_fields(self):
        from vibe_core.mahamantra.commands import cli_resolve

        result = cli_resolve(name="narada", json=True)
        for key in ("success", "bhakti", "name", "position", "aliases", "description", "quarter"):
            assert key in result, f"Missing key: {key}"

    def test_resolve_all_16_positions(self):
        """Every position 0-15 must resolve successfully."""
        from vibe_core.mahamantra.commands import cli_resolve

        for pos in range(WORDS):
            result = cli_resolve(name=str(pos), json=True)
            assert result["success"] is True, f"Position {pos} failed to resolve"
            assert result["position"] == pos


# =============================================================================
# CLI_SERVE — Real Integration
# =============================================================================


class TestCliServe:
    """cli_serve calls the real VM + JanakaService."""

    def test_serve_returns_success(self):
        from vibe_core.mahamantra.commands import cli_serve

        result = cli_serve(task="test task", execute=False, json=True)
        assert result["success"] is True

    def test_serve_result_has_all_fields(self):
        from vibe_core.mahamantra.commands import cli_serve

        result = cli_serve(task="test task", execute=False, json=True)
        for key in ("success", "bhakti", "task_id", "task_name", "status", "execution_time_ms", "message"):
            assert key in result, f"Missing key: {key}"

    def test_serve_status_is_queued(self):
        from vibe_core.mahamantra.commands import cli_serve

        result = cli_serve(task="test task", execute=False, json=True)
        assert result["status"] == "queued"

    def test_serve_task_name_truncated(self):
        from vibe_core.mahamantra.commands import cli_serve

        long_task = "x" * 100
        result = cli_serve(task=long_task, execute=False, json=True)
        assert len(result["task_name"]) <= 50

    def test_serve_sovereign_id_contains_vm_routing(self):
        """JanakaService receives VM-computed guardian in sovereign_id."""
        from vibe_core.mahamantra.commands import cli_serve

        result = cli_serve(task="build the temple", execute=False, json=True)
        # The message contains the VM routing info
        assert "cli_serve[" in result["message"] or "@" in result["message"]


# =============================================================================
# CLI_VEDA — Real Integration
# =============================================================================


class TestCliVeda:
    """cli_veda calls the real VM + VedaExplorer."""

    def test_veda_empty_message_fails(self):
        from vibe_core.mahamantra.commands import cli_veda

        result = cli_veda(message="", json=True)
        assert result["success"] is False

    @pytest.mark.xfail(reason="Requires LLM API key; mock mode returns success=False")
    def test_veda_with_message_succeeds(self):
        from vibe_core.mahamantra.commands import cli_veda

        result = cli_veda(message="what is dharma", json=True)
        assert result["success"] is True

    def test_veda_result_has_all_fields(self):
        from vibe_core.mahamantra.commands import cli_veda

        result = cli_veda(message="what is dharma", json=True)
        for key in ("success", "bhakti", "mode", "intent", "response", "llm_used"):
            assert key in result, f"Missing key: {key}"

    def test_veda_response_is_string(self):
        from vibe_core.mahamantra.commands import cli_veda

        result = cli_veda(message="what is dharma", json=True)
        assert isinstance(result["response"], str)

    def test_veda_deterministic(self):
        """Same input → same response (deterministic path, no LLM)."""
        from vibe_core.mahamantra.commands import cli_veda

        r1 = cli_veda(message="what is dharma", mode="enhanced", json=True)
        r2 = cli_veda(message="what is dharma", mode="enhanced", json=True)
        assert r1["response"] == r2["response"]


# =============================================================================
# ARCHITECTURE GUARDS — Source-level regression prevention
# =============================================================================


class TestNoBypassPaths:
    """Verify commands.py has NO direct substrate access outside VM."""

    def test_cli_chant_has_no_chamber_import(self):
        """cli_chant must NOT import SankirtanChamber (VM does chamber work)."""
        import inspect

        from vibe_core.mahamantra.commands import cli_chant

        source = inspect.getsource(cli_chant)
        assert "SankirtanChamber" not in source, "cli_chant still imports SankirtanChamber — bypassing VM"

    def test_cli_chant_has_no_direct_tick(self):
        """cli_chant must NOT call mahamantra.tick() (VM does ticking)."""
        import inspect

        from vibe_core.mahamantra.commands import cli_chant

        source = inspect.getsource(cli_chant)
        assert "mahamantra.tick()" not in source, "cli_chant still calls mahamantra.tick() — bypassing VM"

    def test_cli_serve_has_no_direct_janaka_protocol(self):
        """cli_serve must NOT import JanakaProtocol (uses get_service only)."""
        import inspect

        from vibe_core.mahamantra.commands import cli_serve

        source = inspect.getsource(cli_serve)
        assert "JanakaProtocol" not in source, "cli_serve still imports JanakaProtocol — unnecessary coupling"
