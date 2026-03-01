"""
Tests for EnforceGateProvider.write_source() — Governed Source File Writes
==========================================================================

Verifies:
1. RAJAS Guna allows source file writes
2. SATTVA Guna blocks source file writes (sattva_read_only)
3. No Guna (DENIED) blocks source file writes
4. Audit trail is recorded for all write attempts
5. Backup .bak file is created before overwrite
"""

import pytest

from vibe_core.mahamantra.substrate.gate_providers import (
    EnforceGateProvider,
    IOPolicy,
)
from vibe_core.mahamantra.substrate.guna import Guna

# =============================================================================
# write_source() TESTS
# =============================================================================


class TestWriteSourceGate:
    """Test governed source file writes through Srivasa gate."""

    @pytest.fixture
    def gate(self):
        """Fresh EnforceGateProvider for each test."""
        return EnforceGateProvider()

    @pytest.fixture
    def source_file(self, tmp_path):
        """Create a temporary Python file to write to."""
        f = tmp_path / "test_file.py"
        f.write_text("# original content\n")
        return f

    def test_rajas_write_source_succeeds(self, gate, source_file):
        """RAJAS Guna allows writing source files."""
        result = gate.write_source(
            file_path=source_file,
            content="# healed content\n",
            actor="shuddhi_healer",
            guna=Guna.RAJAS,
        )
        assert result["success"] is True
        assert result["flushed"] is True
        assert result["guna_policy"] == IOPolicy.WRITE_BEHIND.value
        assert source_file.read_text() == "# healed content\n"

    def test_sattva_write_source_blocked(self, gate, source_file):
        """SATTVA Guna blocks source writes (read-only)."""
        original = source_file.read_text()

        result = gate.write_source(
            file_path=source_file,
            content="# should not be written\n",
            actor="shuddhi_healer",
            guna=Guna.SATTVA,
        )
        assert result["success"] is False
        assert result["reason"] == "sattva_read_only"
        # File must not be modified
        assert source_file.read_text() == original

    def test_no_guna_write_source_blocked(self, gate, source_file):
        """No Guna (None) blocks source writes (DENIED)."""
        original = source_file.read_text()

        result = gate.write_source(
            file_path=source_file,
            content="# should not be written\n",
            actor="shuddhi_healer",
            guna=None,
        )
        assert result["success"] is False
        assert result["reason"] == "void_no_guna"
        assert source_file.read_text() == original

    def test_tamas_write_source_succeeds(self, gate, source_file):
        """TAMAS Guna allows source writes (sync flush)."""
        result = gate.write_source(
            file_path=source_file,
            content="# tamas content\n",
            actor="shuddhi_healer",
            guna=Guna.TAMAS,
        )
        assert result["success"] is True
        assert source_file.read_text() == "# tamas content\n"

    def test_backup_file_created(self, gate, source_file):
        """Backup .bak file is created before overwrite."""
        bak = source_file.with_suffix(".py.bak")
        assert not bak.exists()

        gate.write_source(
            file_path=source_file,
            content="# new content\n",
            actor="shuddhi_healer",
            guna=Guna.RAJAS,
        )
        assert bak.exists()
        assert bak.read_text() == "# original content\n"

    def test_no_backup_when_disabled(self, gate, source_file):
        """No backup when backup=False."""
        gate.write_source(
            file_path=source_file,
            content="# new content\n",
            actor="shuddhi_healer",
            guna=Guna.RAJAS,
            backup=False,
        )
        bak = source_file.with_suffix(".py.bak")
        assert not bak.exists()

    def test_write_source_audit_trail(self, gate, source_file):
        """Audit entries are recorded for all write attempts."""
        # Successful write
        gate.write_source(
            file_path=source_file,
            content="# new\n",
            actor="healer_1",
            guna=Guna.RAJAS,
        )
        # Blocked write
        gate.write_source(
            file_path=source_file,
            content="# blocked\n",
            actor="healer_2",
            guna=Guna.SATTVA,
        )

        stats = gate.stats
        assert stats["writes_total"] >= 2
        assert stats["writes_denied"] >= 1
        assert stats["audit_log_size"] >= 2

    def test_sattva_blocks_counter(self, gate, source_file):
        """SATTVA blocks are specifically counted."""
        gate.write_source(
            file_path=source_file,
            content="# blocked\n",
            actor="test",
            guna=Guna.SATTVA,
        )
        assert gate.stats["sattva_blocks"] == 1

    def test_write_to_new_file(self, gate, tmp_path):
        """Can write source to a new file (no backup needed)."""
        new_file = tmp_path / "brand_new.py"
        assert not new_file.exists()

        result = gate.write_source(
            file_path=new_file,
            content="# brand new file\n",
            actor="shuddhi_healer",
            guna=Guna.RAJAS,
        )
        assert result["success"] is True
        assert new_file.exists()
        assert new_file.read_text() == "# brand new file\n"
