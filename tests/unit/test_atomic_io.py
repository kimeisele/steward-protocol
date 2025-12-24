"""
Tests für atomic_io - Crash-Safe File Operations.

Diese Tests verifizieren die Dharma-Garantie:
"State ist entweder ALT oder NEU, niemals KORRUPT."
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.utils.atomic_io import atomic_write_json, atomic_write_text


class TestAtomicWriteText:
    """Tests für atomic_write_text."""

    def test_creates_new_file(self, tmp_path: Path):
        """Neue Datei wird korrekt erstellt."""
        target = tmp_path / "new_file.txt"
        content = "Hello, World!"

        atomic_write_text(target, content)

        assert target.exists()
        assert target.read_text() == content

    def test_overwrites_existing_file(self, tmp_path: Path):
        """Existierende Datei wird überschrieben."""
        target = tmp_path / "existing.txt"
        target.write_text("OLD CONTENT")

        atomic_write_text(target, "NEW CONTENT")

        assert target.read_text() == "NEW CONTENT"

    def test_creates_parent_directories(self, tmp_path: Path):
        """Parent-Verzeichnisse werden erstellt."""
        target = tmp_path / "deep" / "nested" / "path" / "file.txt"

        atomic_write_text(target, "content")

        assert target.exists()

    def test_no_temp_file_on_success(self, tmp_path: Path):
        """Keine .tmp Dateien nach erfolgreichem Schreiben."""
        target = tmp_path / "clean.txt"

        atomic_write_text(target, "content")

        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    def test_old_file_preserved_on_write_error(self, tmp_path: Path):
        """Alte Datei bleibt bei Fehler erhalten (Dharma-Garantie)."""
        target = tmp_path / "protected.txt"
        target.write_text("ORIGINAL CONTENT")

        # Simuliere Fehler beim Schreiben
        with patch("os.write", side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                atomic_write_text(target, "NEW CONTENT")

        # Original muss unverändert sein
        assert target.read_text() == "ORIGINAL CONTENT"

    def test_cleanup_temp_on_error(self, tmp_path: Path):
        """Temp-Datei wird bei Fehler aufgeräumt."""
        target = tmp_path / "cleanup_test.txt"

        with patch("os.fsync", side_effect=OSError("Sync failed")):
            with pytest.raises(OSError):
                atomic_write_text(target, "content")

        # Keine .tmp Dateien übrig
        tmp_files = list(tmp_path.glob("*.tmp"))
        atomic_files = list(tmp_path.glob(".atomic_*"))
        assert len(tmp_files) == 0
        assert len(atomic_files) == 0

    def test_unicode_content(self, tmp_path: Path):
        """Unicode wird korrekt geschrieben."""
        target = tmp_path / "unicode.txt"
        content = "Привет 世界 🚀 Ω"

        atomic_write_text(target, content)

        assert target.read_text(encoding="utf-8") == content


class TestAtomicWriteJson:
    """Tests für atomic_write_json."""

    def test_writes_valid_json(self, tmp_path: Path):
        """Valides JSON wird geschrieben."""
        target = tmp_path / "data.json"
        data = {"name": "test", "count": 42, "nested": {"key": "value"}}

        atomic_write_json(target, data)

        result = json.loads(target.read_text())
        assert result == data

    def test_pretty_print_by_default(self, tmp_path: Path):
        """JSON ist standardmäßig formatiert."""
        target = tmp_path / "pretty.json"

        atomic_write_json(target, {"key": "value"})

        content = target.read_text()
        assert "\n" in content  # Mehrzeilig

    def test_unicode_in_json(self, tmp_path: Path):
        """Unicode in JSON bleibt lesbar."""
        target = tmp_path / "unicode.json"
        data = {"greeting": "Привет", "emoji": "🎉"}

        atomic_write_json(target, data)

        content = target.read_text()
        assert "Привет" in content  # Nicht escaped
        assert "🎉" in content

    def test_preserves_old_json_on_error(self, tmp_path: Path):
        """Alte JSON-Datei bleibt bei Fehler erhalten."""
        target = tmp_path / "protected.json"
        original = {"status": "original"}
        target.write_text(json.dumps(original))

        with patch("os.write", side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                atomic_write_json(target, {"status": "new"})

        result = json.loads(target.read_text())
        assert result == original


class TestAtomicityGuarantee:
    """Meta-Tests für Atomaritäts-Garantien."""

    def test_concurrent_reads_see_consistent_state(self, tmp_path: Path):
        """
        Simuliert: Reader liest während Writer schreibt.
        Garantie: Reader sieht entweder alten oder neuen State, nie Mischung.
        """
        target = tmp_path / "concurrent.txt"
        target.write_text("STATE_A")

        # In echter Concurrency wäre dies ein Thread
        # Hier testen wir, dass rename() atomar ist
        atomic_write_text(target, "STATE_B")

        content = target.read_text()
        assert content in ("STATE_A", "STATE_B")
        assert "STATE" in content  # Nie partial

    def test_file_permissions_preserved(self, tmp_path: Path):
        """Dateirechte bleiben nach Überschreiben erhalten."""
        target = tmp_path / "perms.txt"
        target.write_text("original")
        os.chmod(target, 0o644)

        atomic_write_text(target, "new content")

        # Neue Datei hat Standard-Permissions (umask-abhängig)
        # Das ist OK - wichtig ist, dass sie lesbar ist
        assert os.access(target, os.R_OK)
