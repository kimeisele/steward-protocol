"""
TEST: KernelIOService - Central File Operation Controller
==========================================================
Verifies the I/O service for atomic writes, sandbox enforcement, and audit.
Target: vibe_core/io_service.py
Standard: GAD-5000

Tests use real filesystem with temp directories for isolation.
"""

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict

import pytest

from vibe_core.io_service import (
    DocumentType,
    KernelIOService,
    WriteResult,
    create_io_service,
)

# =============================================================================
# MOCK KERNEL
# =============================================================================


class MockLedger:
    """Mock ledger for testing audit trail."""

    def __init__(self):
        self.events = []

    def record_event(self, event_type, agent_id, details, result="success"):
        self.events.append(
            {
                "event_type": event_type,
                "agent_id": agent_id,
                "details": details,
                "result": result,
            }
        )


class MockKernel:
    """Mock kernel for IOService testing."""

    def __init__(self, with_ledger: bool = True):
        self._ledger = MockLedger() if with_ledger else None
        self._status = type("Status", (), {"value": "RUNNING"})()
        self.agent_registry = {"agent1": None, "agent2": None}


# =============================================================================
# TEST: DocumentType Enum
# =============================================================================


class TestDocumentType:
    """Test DocumentType enum."""

    def test_readonly_type_exists(self):
        """Should have READONLY type."""
        assert DocumentType.READONLY.value == "readonly"

    def test_bidirectional_type_exists(self):
        """Should have BIDIRECTIONAL type."""
        assert DocumentType.BIDIRECTIONAL.value == "bidir"

    def test_snapshot_type_exists(self):
        """Should have SNAPSHOT type."""
        assert DocumentType.SNAPSHOT.value == "snapshot"


# =============================================================================
# TEST: WriteResult Dataclass
# =============================================================================


class TestWriteResult:
    """Test WriteResult dataclass."""

    def test_create_success_result(self):
        """Should create successful result."""
        result = WriteResult(
            success=True,
            path=Path("/tmp/test.md"),
            mtime=1234567890.0,
        )

        assert result.success is True
        assert result.path == Path("/tmp/test.md")
        assert result.mtime == 1234567890.0
        assert result.error is None

    def test_create_failure_result(self):
        """Should create failure result with error."""
        result = WriteResult(
            success=False,
            path=Path("/tmp/test.md"),
            error="Permission denied",
        )

        assert result.success is False
        assert result.error == "Permission denied"

    def test_preserved_sections_default(self):
        """Should default preserved_sections to empty dict."""
        result = WriteResult(
            success=True,
            path=Path("/tmp/test.md"),
        )

        assert result.preserved_sections == {}


# =============================================================================
# TEST: KernelIOService Initialization
# =============================================================================


class TestKernelIOServiceInit:
    """Test KernelIOService initialization."""

    def test_init_with_kernel(self):
        """Should initialize with kernel reference."""
        kernel = MockKernel()

        service = KernelIOService(kernel)

        assert service._kernel is kernel

    def test_init_with_root_path(self):
        """Should use provided root path."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            assert service._root == Path(tmpdir)

    def test_init_defaults_to_cwd(self):
        """Should default root to current working directory."""
        kernel = MockKernel()

        service = KernelIOService(kernel)

        assert service._root == Path.cwd()

    def test_init_creates_lock_structures(self):
        """Should initialize lock structures."""
        kernel = MockKernel()

        service = KernelIOService(kernel)

        assert isinstance(service._locks, dict)
        # threading.Lock() returns a lock object, check it has acquire/release methods
        assert hasattr(service._lock_manager, "acquire")
        assert hasattr(service._lock_manager, "release")

    def test_init_with_audit_enabled(self):
        """Should have audit enabled by default."""
        kernel = MockKernel()

        service = KernelIOService(kernel)

        assert service._audit_enabled is True
        assert service._write_count == 0


# =============================================================================
# TEST: Sandbox Validation (SHAKATASURA)
# =============================================================================


class TestSandboxValidation:
    """Test sandbox enforcement (path traversal prevention)."""

    def test_validate_sandbox_accepts_relative_path(self):
        """Should accept simple relative paths."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service._validate_sandbox("test.md")

            assert result == Path(tmpdir) / "test.md"

    def test_validate_sandbox_accepts_nested_path(self):
        """Should accept nested relative paths."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service._validate_sandbox("docs/output/test.md")

            assert result == Path(tmpdir) / "docs" / "output" / "test.md"

    def test_validate_sandbox_blocks_parent_traversal(self):
        """Should block ../ path traversal."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            with pytest.raises(PermissionError) as exc_info:
                service._validate_sandbox("../escape.txt")

            assert "SHAKATASURA BLOCKED" in str(exc_info.value)

    def test_validate_sandbox_blocks_absolute_path_outside(self):
        """Should block absolute paths outside sandbox."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            with pytest.raises(PermissionError) as exc_info:
                service._validate_sandbox("/etc/passwd")

            assert "SHAKATASURA BLOCKED" in str(exc_info.value)

    def test_validate_sandbox_blocks_null_byte(self):
        """Should block null byte injection."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            # Null byte causes ValueError from pathlib before reaching our check
            # Either PermissionError (our check) or ValueError (pathlib) is acceptable
            with pytest.raises((PermissionError, ValueError)):
                service._validate_sandbox("test\x00.md")

    def test_validate_sandbox_blocks_symlink_escape(self):
        """Should block symlink escape attempts."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = Path(tmpdir)
            service = KernelIOService(kernel, root_path=sandbox)

            # Create symlink pointing outside sandbox
            symlink_path = sandbox / "escape_link"
            symlink_path.symlink_to("/tmp")

            with pytest.raises(PermissionError) as exc_info:
                service._validate_sandbox("escape_link/target.txt")

            assert "SHAKATASURA BLOCKED" in str(exc_info.value)


# =============================================================================
# TEST: Write Operations
# =============================================================================


class TestWriteDocument:
    """Test write_document method."""

    def test_write_simple_document(self):
        """Should write document successfully."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document("test.md", "Hello World")

            assert result.success is True
            assert (Path(tmpdir) / "test.md").exists()

    def test_write_creates_parent_directories(self):
        """Should create parent directories as needed."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document("deep/nested/file.md", "Content")

            assert result.success is True
            assert (Path(tmpdir) / "deep" / "nested" / "file.md").exists()

    def test_write_adds_header_to_markdown(self):
        """Should add header to markdown files."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document(
                "test.md",
                "# Content",
                writer_id="TEST_WRITER",
            )

            content = (Path(tmpdir) / "test.md").read_text()
            assert "TEST_WRITER" in content
            assert "# Content" in content

    def test_write_without_header(self):
        """Should skip header when add_header=False."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document(
                "test.md",
                "Pure Content",
                add_header=False,
            )

            content = (Path(tmpdir) / "test.md").read_text()
            assert content == "Pure Content"

    def test_write_list_content(self):
        """Should join list content with newlines."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document(
                "test.md",
                ["Line 1", "Line 2", "Line 3"],
                add_header=False,
            )

            content = (Path(tmpdir) / "test.md").read_text()
            assert "Line 1\nLine 2\nLine 3" in content

    def test_write_returns_mtime(self):
        """Should return file mtime after write."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document("test.md", "Content", add_header=False)

            assert result.mtime > 0

    def test_write_blocks_sandbox_escape(self):
        """Should fail for sandbox escape attempts."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document("../escape.md", "Malicious")

            assert result.success is False
            assert "SHAKATASURA BLOCKED" in result.error


# =============================================================================
# TEST: Write Snapshot
# =============================================================================


class TestWriteSnapshot:
    """Test write_snapshot method."""

    def test_write_snapshot_json(self):
        """Should write JSON snapshot."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            data = {"status": "ok", "count": 42}
            result = service.write_snapshot("snapshot.json", data)

            assert result.success is True

            content = json.loads((Path(tmpdir) / "snapshot.json").read_text())
            assert content["status"] == "ok"
            assert content["count"] == 42

    def test_write_snapshot_no_header(self):
        """Should not add header to snapshot files."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_snapshot("snapshot.json", {"key": "value"})

            content = (Path(tmpdir) / "snapshot.json").read_text()
            # Should be pure JSON, no HTML comment header
            assert content.startswith("{")


# =============================================================================
# TEST: Read Operations
# =============================================================================


class TestReadDocument:
    """Test read_document method."""

    def test_read_existing_document(self):
        """Should read existing document content."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file directly
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("Test Content")

            service = KernelIOService(kernel, root_path=Path(tmpdir))

            content = service.read_document("test.md")

            assert content == "Test Content"

    def test_read_nonexistent_returns_none(self):
        """Should return None for missing files."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            content = service.read_document("nonexistent.md")

            assert content is None

    def test_read_blocks_sandbox_escape(self):
        """Should return None for sandbox escape attempts."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            content = service.read_document("../escape.md")

            assert content is None


# =============================================================================
# TEST: User Section Extraction
# =============================================================================


class TestUserSectionExtraction:
    """Test bidirectional document section handling."""

    def test_extract_user_section(self):
        """Should extract user section from document."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with user section
            content = """# Header

## 📝 Quick Note

User's note here

## Other Section
"""
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text(content)

            service = KernelIOService(kernel, root_path=Path(tmpdir))

            section = service.extract_user_section("test.md", "## 📝 Quick Note")

            assert "User's note here" in section

    def test_extract_section_empty_when_not_found(self):
        """Should return empty string when section not found."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# No sections here")

            service = KernelIOService(kernel, root_path=Path(tmpdir))

            section = service.extract_user_section("test.md", "## Missing Section")

            assert section == ""


# =============================================================================
# TEST: Bidirectional Document Preservation
# =============================================================================


class TestBidirectionalPreservation:
    """Test preservation of user content in bidirectional documents."""

    def test_preserve_quick_note_section(self):
        """Should preserve Quick Note section across re-renders."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            # First write with user content
            original = """# Doc

## 📝 Quick Note

My important note

## Other Section
Other content
"""
            test_file = Path(tmpdir) / "ENVOY.md"
            test_file.write_text(original)

            service = KernelIOService(kernel, root_path=Path(tmpdir))

            # Re-render with new content
            new_content = """# Doc

## 📝 Quick Note

(placeholder)

## Other Section
New content
"""
            result = service.write_document(
                "ENVOY.md",
                new_content,
                doc_type=DocumentType.BIDIRECTIONAL,
                add_header=False,
            )

            assert result.success is True

            # Check preserved section is in result
            assert "quick_note" in result.preserved_sections


# =============================================================================
# TEST: Atomic Writes
# =============================================================================


class TestAtomicWrites:
    """Test atomic write behavior."""

    def test_atomic_write_creates_file(self):
        """Should create file atomically."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))
            test_path = Path(tmpdir) / "atomic.txt"

            service._atomic_write(test_path, "Atomic content")

            assert test_path.exists()
            assert test_path.read_text() == "Atomic content"

    def test_atomic_write_no_temp_file_residue(self):
        """Should not leave temp files after write."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))
            test_path = Path(tmpdir) / "clean.txt"

            service._atomic_write(test_path, "Content")

            # Should have only the target file, no temp files
            files = list(Path(tmpdir).iterdir())
            assert len(files) == 1
            assert files[0].name == "clean.txt"


# =============================================================================
# TEST: Audit Trail
# =============================================================================


class TestAuditTrail:
    """Test audit trail recording."""

    def test_write_records_to_ledger(self):
        """Should record write to ledger."""
        kernel = MockKernel(with_ledger=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            service.write_document(
                "audit_test.md",
                "Content",
                writer_id="AUDIT_WRITER",
                add_header=False,
            )

            assert len(kernel._ledger.events) >= 1

            io_events = [e for e in kernel._ledger.events if e["event_type"] == "IO_WRITE"]
            assert len(io_events) == 1
            assert io_events[0]["agent_id"] == "AUDIT_WRITER"
            assert io_events[0]["details"]["file"] == "audit_test.md"

    def test_audit_can_be_disabled(self):
        """Should not record when audit disabled."""
        kernel = MockKernel(with_ledger=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))
            service.set_audit_enabled(False)

            service.write_document("no_audit.md", "Content", add_header=False)

            # No IO_WRITE events should be recorded
            io_events = [e for e in kernel._ledger.events if e["event_type"] == "IO_WRITE"]
            assert len(io_events) == 0

    def test_get_audit_stats(self):
        """Should return audit statistics."""
        kernel = MockKernel(with_ledger=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            service.write_document("file1.md", "A", add_header=False)
            service.write_document("file2.md", "B", add_header=False)

            stats = service.get_audit_stats()

            assert stats["write_count"] == 2
            assert stats["audit_enabled"] is True
            assert stats["ledger_available"] is True
            assert stats["root_path"] == str(Path(tmpdir))


# =============================================================================
# TEST: File Locking
# =============================================================================


class TestFileLocking:
    """Test per-file locking."""

    def test_get_lock_creates_lock(self):
        """Should create lock for new file."""
        kernel = MockKernel()
        service = KernelIOService(kernel)

        lock = service._get_lock("test.md")

        # Check it's a lock object with acquire/release methods
        assert hasattr(lock, "acquire")
        assert hasattr(lock, "release")

    def test_get_lock_returns_same_lock(self):
        """Should return same lock for same file."""
        kernel = MockKernel()
        service = KernelIOService(kernel)

        lock1 = service._get_lock("test.md")
        lock2 = service._get_lock("test.md")

        assert lock1 is lock2

    def test_different_files_different_locks(self):
        """Should create different locks for different files."""
        kernel = MockKernel()
        service = KernelIOService(kernel)

        lock1 = service._get_lock("file1.md")
        lock2 = service._get_lock("file2.md")

        assert lock1 is not lock2

    def test_concurrent_writes_thread_safe(self):
        """Should handle concurrent writes safely."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            results = []
            errors = []

            def write_task(n):
                try:
                    result = service.write_document(
                        "concurrent.md",
                        f"Content from thread {n}",
                        add_header=False,
                    )
                    results.append((n, result.success))
                except Exception as e:
                    errors.append((n, str(e)))

            # Start multiple threads
            threads = [threading.Thread(target=write_task, args=(i,)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # All writes should succeed
            assert len(errors) == 0
            assert all(success for _, success in results)

            # File should exist with content from one of the threads
            content = (Path(tmpdir) / "concurrent.md").read_text()
            assert "Content from thread" in content


# =============================================================================
# TEST: Factory Function
# =============================================================================


class TestCreateIOService:
    """Test create_io_service factory function."""

    def test_create_io_service_returns_instance(self):
        """Should create KernelIOService instance."""
        kernel = MockKernel()

        service = create_io_service(kernel)

        assert isinstance(service, KernelIOService)
        assert service._kernel is kernel


# =============================================================================
# TEST: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_write_empty_content(self):
        """Should handle empty content."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            result = service.write_document("empty.md", "", add_header=False)

            assert result.success is True
            assert (Path(tmpdir) / "empty.md").read_text() == ""

    def test_write_unicode_content(self):
        """Should handle unicode content."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            content = "🎯 Unicode: 日本語 العربية"
            result = service.write_document("unicode.md", content, add_header=False)

            assert result.success is True
            assert (Path(tmpdir) / "unicode.md").read_text() == content

    def test_write_large_content(self):
        """Should handle large content."""
        kernel = MockKernel()

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            content = "x" * 1_000_000  # 1MB
            result = service.write_document("large.md", content, add_header=False)

            assert result.success is True
            assert len((Path(tmpdir) / "large.md").read_text()) == 1_000_000

    def test_kernel_without_ledger(self):
        """Should handle kernel without ledger gracefully."""
        kernel = MockKernel(with_ledger=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = KernelIOService(kernel, root_path=Path(tmpdir))

            # Should not raise, just skip audit
            result = service.write_document("no_ledger.md", "Content", add_header=False)

            assert result.success is True
