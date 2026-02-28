"""Tests for Federation Dispatcher — cross-repo communication."""

import json
from unittest.mock import MagicMock, patch

from vibe_core.plugins.moltbook.managers.federation import (
    FederationDispatcher,
    extract_city_context,
    read_city_report,
)


class TestFederationDispatcher:
    def test_unavailable_without_pat(self):
        with patch.dict("os.environ", {}, clear=True):
            d = FederationDispatcher()
            assert not d.available

    def test_available_with_pat(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            assert d.available

    def test_dispatch_returns_false_without_pat(self):
        with patch.dict("os.environ", {}, clear=True):
            d = FederationDispatcher()
            assert not d.dispatch_create_mission("topic", "context")

    def test_dispatch_calls_gh_api(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                result = d.dispatch_create_mission(
                    topic="Fix error handling",
                    context="Community discussion",
                    source_post_id="post_123",
                    priority="high",
                )
                assert result is True
                assert mock_run.called
                call_args = mock_run.call_args
                assert "repos/kimeisele/agent-city/dispatches" in call_args[0][0]
                # Verify payload
                payload = json.loads(call_args[1]["input"])
                assert payload["event_type"] == "mothership-directive"
                assert payload["client_payload"]["directive_type"] == "create_mission"
                assert payload["client_payload"]["params"]["topic"] == "Fix error handling"

    def test_dispatch_handles_failure(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Not Found"
            with patch("subprocess.run", return_value=mock_result):
                result = d.dispatch_create_mission("topic", "context")
                assert result is False

    def test_dispatch_handles_timeout(self):
        import subprocess

        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("gh", 15)):
                result = d.dispatch_create_mission("topic", "context")
                assert result is False

    def test_dispatch_handles_gh_not_found(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            with patch("subprocess.run", side_effect=FileNotFoundError):
                result = d.dispatch_create_mission("topic", "context")
                assert result is False

    def test_dispatch_register_agent(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                result = d.dispatch_register_agent("alice", karma=42)
                assert result is True
                payload = json.loads(mock_run.call_args[1]["input"])
                assert payload["client_payload"]["directive_type"] == "register_agent"
                assert payload["client_payload"]["params"]["agent_name"] == "alice"

    def test_dispatched_count_increments(self):
        with patch.dict("os.environ", {"FEDERATION_PAT": "ghp_test123"}):
            d = FederationDispatcher()
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result):
                d.dispatch_create_mission("a", "b")
                d.dispatch_create_mission("c", "d")
                assert d._dispatched_count == 2


class TestReadCityReport:
    def test_returns_none_when_no_file(self, tmp_path):
        assert read_city_report(tmp_path) is None

    def test_reads_valid_report(self, tmp_path):
        report = {"heartbeat": 42, "population": 20, "alive": 15}
        (tmp_path / "city_report.json").write_text(json.dumps(report))
        result = read_city_report(tmp_path)
        assert result is not None
        assert result["heartbeat"] == 42
        assert result["population"] == 20

    def test_handles_invalid_json(self, tmp_path):
        (tmp_path / "city_report.json").write_text("not json")
        assert read_city_report(tmp_path) is None

    def test_handles_non_dict(self, tmp_path):
        (tmp_path / "city_report.json").write_text('"just a string"')
        assert read_city_report(tmp_path) is None


class TestExtractCityContext:
    def test_full_report(self):
        report = {
            "population": 20,
            "alive": 15,
            "elected_mayor": "alice",
            "contract_status": {"ruff_clean": "passing", "tests_pass": "failing"},
            "recent_actions": ["frozen:bob", "election:mayor=alice"],
            "mission_results": [
                {"mission_id": "m1", "status": "completed", "pr_url": "#42"},
            ],
        }
        ctx = extract_city_context(report)
        assert "15/20 agents alive" in ctx
        assert "Mayor: alice" in ctx
        assert "Failing contracts: tests_pass" in ctx
        assert "frozen:bob" in ctx
        assert "Completed missions: 1" in ctx

    def test_empty_report(self):
        assert extract_city_context({}) == ""

    def test_partial_report(self):
        report = {"population": 5, "alive": 5}
        ctx = extract_city_context(report)
        assert "5/5 agents alive" in ctx
        assert "Mayor" not in ctx
