"""
METAL TEST: OUROBOROS Violation Ingestion (P0 Loop Fix)

Tests that the ingestion script:
1. Reads watchman_report.json
2. Persists violations to .vibe/state/ouroboros/violations.jsonl
3. Uses append-only JSONL format

OPUS-312: Ingestion was broken - called non-existent prakriti.save_knowledge().
Fix: Rewrote to use direct JSONL persistence.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest


class TestOuroborosIngestion:
    """Verify OUROBOROS violation ingestion works."""

    @pytest.fixture
    def clean_state(self, tmp_path, monkeypatch):
        """Set up clean test environment."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Create .vibe/state/ouroboros/ structure
        state_dir = tmp_path / ".vibe" / "state" / "ouroboros"
        state_dir.mkdir(parents=True, exist_ok=True)

        return tmp_path

    def test_script_handles_missing_report(self, clean_state, monkeypatch):
        """Script should exit cleanly if no watchman_report.json."""
        script_path = Path(__file__).parent.parent.parent.parent / "scripts/ci/ingest_violations.py"

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=clean_state,
        )

        assert result.returncode == 0
        assert "No watchman_report.json" in result.stdout

    def test_script_handles_empty_violations(self, clean_state):
        """Script should handle report with no violations."""
        script_path = Path(__file__).parent.parent.parent.parent / "scripts/ci/ingest_violations.py"

        # Create empty report
        report = {"violations": []}
        (clean_state / "watchman_report.json").write_text(json.dumps(report))

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=clean_state,
        )

        assert result.returncode == 0
        assert "No violations to ingest" in result.stdout

    def test_script_persists_violations_to_jsonl(self, clean_state):
        """Script MUST persist violations to .vibe/state/ouroboros/violations.jsonl."""
        script_path = Path(__file__).parent.parent.parent.parent / "scripts/ci/ingest_violations.py"

        # Create report with violations
        report = {
            "violations": [
                {
                    "file_path": "src/foo.py",
                    "line_number": 42,
                    "rule_id": "E501",
                    "message": "line too long",
                    "severity": "LOW",
                    "has_remedy": True,
                    "agent": "watchman",
                },
                {
                    "file_path": "src/bar.py",
                    "line_number": 17,
                    "rule_id": "F401",
                    "message": "unused import",
                    "severity": "MEDIUM",
                    "has_remedy": True,
                    "agent": "watchman",
                },
            ]
        }
        (clean_state / "watchman_report.json").write_text(json.dumps(report))

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=clean_state,
        )

        assert result.returncode == 0
        assert "Ingested 2 violations" in result.stdout

        # Verify JSONL file was created
        violations_file = clean_state / ".vibe" / "state" / "ouroboros" / "violations.jsonl"
        assert violations_file.exists()

        # Verify content
        lines = violations_file.read_text().strip().split("\n")
        assert len(lines) == 2

        # Parse first violation
        v1 = json.loads(lines[0])
        assert v1["file_path"] == "src/foo.py"
        assert v1["line"] == 42
        assert v1["rule_id"] == "E501"
        assert "ingested_at" in v1

    def test_script_appends_to_existing_jsonl(self, clean_state):
        """Script MUST append to existing log, not overwrite."""
        script_path = Path(__file__).parent.parent.parent.parent / "scripts/ci/ingest_violations.py"

        # Create state dir and pre-existing violations
        state_dir = clean_state / ".vibe" / "state" / "ouroboros"
        state_dir.mkdir(parents=True, exist_ok=True)
        violations_file = state_dir / "violations.jsonl"

        # Write initial violation
        existing = {"ingested_at": "2026-01-01T00:00:00", "file_path": "old.py", "rule_id": "OLD"}
        violations_file.write_text(json.dumps(existing) + "\n")

        # Create new report
        report = {"violations": [{"file_path": "new.py", "rule_id": "NEW", "message": "new violation"}]}
        (clean_state / "watchman_report.json").write_text(json.dumps(report))

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=clean_state,
        )

        assert result.returncode == 0

        # Verify both violations exist
        lines = violations_file.read_text().strip().split("\n")
        assert len(lines) == 2

        v1 = json.loads(lines[0])
        v2 = json.loads(lines[1])

        assert v1["file_path"] == "old.py"
        assert v2["file_path"] == "new.py"

    def test_ingested_record_has_required_fields(self, clean_state):
        """Each ingested record MUST have all required fields."""
        script_path = Path(__file__).parent.parent.parent.parent / "scripts/ci/ingest_violations.py"

        report = {
            "violations": [
                {
                    "file_path": "test.py",
                    "line_number": 1,
                    "rule_id": "TEST",
                    "message": "test",
                    "severity": "HIGH",
                    "has_remedy": False,
                    "agent": "test_agent",
                }
            ]
        }
        (clean_state / "watchman_report.json").write_text(json.dumps(report))

        subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            cwd=clean_state,
        )

        violations_file = clean_state / ".vibe" / "state" / "ouroboros" / "violations.jsonl"
        record = json.loads(violations_file.read_text().strip())

        # All required fields
        required_fields = [
            "ingested_at",
            "file_path",
            "line",
            "rule_id",
            "message",
            "severity",
            "has_remedy",
            "agent",
        ]

        for field in required_fields:
            assert field in record, f"Missing required field: {field}"
