"""
KERNEL I/O SERVICE - Central File Operation Controller

PHILOSOPHY: Plugins produce content. Kernel writes.

This service is the ONLY authorized way to write files in VibeOS.
All plugins, agents, and kernel components MUST use this service.

Features:
- Atomic writes (temp file + rename)
- File locking (prevent race conditions)
- Unified headers for markdown files
- User section preservation for bidirectional docs
- Audit trail (ledger integration)

Usage:
    # In plugin:
    def on_tick_post(self, kernel):
        content = self._generate_content()
        kernel.io.write_document("MY_OUTPUT.md", content, DocumentType.READONLY)
"""

from __future__ import annotations

import logging
import os
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("KERNEL_IO")


class DocumentType(Enum):
    """Types of documents managed by the I/O Service."""

    READONLY = "readonly"  # Kernel writes, user reads (OPERATIONS.md, GIT.md)
    BIDIRECTIONAL = "bidir"  # Both write, kernel preserves user input (SETTINGS.md, ENVOY.md)
    SNAPSHOT = "snapshot"  # Internal state files (JSON)


@dataclass
class WriteResult:
    """Result of a write operation."""

    success: bool
    path: Path
    mtime: float = 0.0
    error: Optional[str] = None
    preserved_sections: Dict[str, str] = field(default_factory=dict)


class KernelIOService:
    """
    Central I/O controller for all Kernel file operations.

    This is the ONLY authorized way to write files in VibeOS.
    Plugins produce content, the Kernel writes through this service.

    Thread-safe: Uses per-file locks to prevent race conditions.
    Atomic: All writes use temp file + rename pattern.
    Audited: All writes can be recorded to ledger.
    """

    def __init__(self, kernel: "RealVibeKernel", root_path: Optional[Path] = None):
        """
        Initialize the I/O Service.

        Args:
            kernel: The kernel instance (for ledger access)
            root_path: Root path for relative file operations (default: cwd)
        """
        self._kernel = kernel
        self._root = root_path or Path.cwd()
        self._locks: Dict[str, threading.Lock] = {}
        self._lock_manager = threading.Lock()

        # Sections to preserve in bidirectional documents
        self._preserve_patterns = {
            "quick_note": "## 📝 Quick Note",
            "pending_commands": "## ⚡ Pending Commands",
            "request": "## 💬 Request",
        }

        # Audit trail: track all writes
        self._write_count = 0
        self._audit_enabled = True  # Can be disabled for high-frequency internal writes

        logger.info(f"📁 Kernel I/O Service initialized (root: {self._root})")

    def _get_lock(self, name: str) -> threading.Lock:
        """Get or create a lock for a specific file."""
        with self._lock_manager:
            if name not in self._locks:
                self._locks[name] = threading.Lock()
            return self._locks[name]

    # =========================================================================
    # CART BREAKER: Sandbox Enforcement (SHAKATASURA FIX)
    # =========================================================================

    def _validate_sandbox(self, requested_path: str) -> Path:
        """
        THE CART BREAKER.
        
        Resolves paths and ensures they stay inside the workspace sandbox.
        This prevents symlink attacks and path traversal (..) escapes.
        
        Args:
            requested_path: The path requested by a plugin/agent
            
        Returns:
            Path: The validated, safe path
            
        Raises:
            PermissionError: If the path escapes the sandbox
        """
        # 1. Construct the target path
        target_path = self._root / requested_path

        # 2. RESOLVE - The Symlink Killer
        # This follows all symlinks to their true destination
        try:
            resolved_target = target_path.resolve()
            resolved_root = self._root.resolve()
        except FileNotFoundError:
            # File doesn't exist yet (common for writes)
            # Resolve the parent directory instead
            resolved_target = target_path.parent.resolve() / target_path.name
            resolved_root = self._root.resolve()

        # 3. THE CHECK - Prefix Match
        # Ensure the resolved path starts with the resolved sandbox root
        # We use os.path.commonpath for robust comparison
        try:
            common = Path(os.path.commonpath([resolved_target, resolved_root]))
            if common != resolved_root:
                raise PermissionError(
                    f"🛡️ SHAKATASURA BLOCKED: Sandbox escape detected! "
                    f"Path '{requested_path}' resolves to '{resolved_target}' "
                    f"which is outside sandbox '{resolved_root}'"
                )
        except ValueError:
            # Different drives on Windows, or other path issues
            raise PermissionError(
                f"🛡️ SHAKATASURA BLOCKED: Path '{requested_path}' is not "
                f"inside sandbox '{resolved_root}'"
            )

        # 4. Additional checks
        # Reject null bytes (injection attack)
        if "\x00" in requested_path:
            raise PermissionError(
                f"🛡️ SHAKATASURA BLOCKED: Null byte detected in path '{requested_path}'"
            )

        logger.debug(f"🛡️ Sandbox validated: {requested_path} -> {resolved_target}")
        return target_path

    def _record_write_audit(
        self,
        name: str,
        writer_id: str,
        doc_type: DocumentType,
        size: int,
        mtime: float,
        preserved_keys: List[str],
    ) -> None:
        """
        Record a write operation to the ledger for audit trail.

        This is called AFTER every successful write. The audit record includes:
        - What file was written
        - Who (which plugin/component) wrote it
        - Document type (readonly/bidirectional/snapshot)
        - Size in bytes
        - Timestamp (mtime)
        - Which user sections were preserved (for bidirectional docs)
        """
        if not self._audit_enabled:
            return

        self._write_count += 1

        # Record to ledger if available
        try:
            if self._kernel and hasattr(self._kernel, "_ledger") and self._kernel._ledger:
                self._kernel._ledger.record_event(
                    event_type="IO_WRITE",
                    agent_id=writer_id,
                    details={
                        "file": name,
                        "doc_type": doc_type.value,
                        "size_bytes": size,
                        "mtime": mtime,
                        "preserved_sections": preserved_keys,
                        "write_number": self._write_count,
                    },
                    result="success",  # GAD-000: Always fill result field
                )
                logger.debug(f"📝 Audit: IO_WRITE #{self._write_count} - {name} by {writer_id}")
        except Exception as e:
            # Audit failure should not break writes
            logger.warning(f"⚠️  Audit trail recording failed: {e}")

    def _notify_state_service(self, path: Path) -> None:
        """
        Notify StateService about a written file for unified auto-commit.

        This integrates IOService with the OS-level StateService auto-commit
        system. When StateService receives enough dirty file notifications,
        it triggers the Weaver to commit them to git.

        Args:
            path: Path to the written file
        """
        try:
            from vibe_core.state.state_service import get_state_service

            state_service = get_state_service(self._root)
            state_service.mark_dirty(path)
        except Exception as e:
            # StateService notification failure should not break writes
            logger.debug(f"📝 StateService notify skipped: {e}")

    def write_document(
        self,
        name: str,
        content: Union[str, List[str]],
        doc_type: DocumentType = DocumentType.READONLY,
        writer_id: str = "KERNEL",
        add_header: bool = True,
        preserve_user_content: bool = True,
    ) -> WriteResult:
        """
        Write a document through the I/O service.

        This is the PRIMARY method for all file writes in VibeOS.

        Args:
            name: Document name (e.g., "EPHEMERAL.md", "GIT.md")
            content: Content to write (str or list of lines)
            doc_type: READONLY, BIDIRECTIONAL, or SNAPSHOT
            writer_id: ID of the plugin/component writing
            add_header: Whether to add unified header (for markdown)
            preserve_user_content: Whether to preserve user sections (bidir)

        Returns:
            WriteResult with success status and new mtime
        """
        # =====================================================================
        # CART BREAKER: Validate sandbox BEFORE any operation
        # =====================================================================
        try:
            path = self._validate_sandbox(name)
        except PermissionError as e:
            logger.error(f"🛡️ SANDBOX ESCAPE BLOCKED: {name} by {writer_id}")
            return WriteResult(success=False, path=self._root / name, error=str(e))

        lock = self._get_lock(name)

        with lock:
            try:
                # Convert list to string if needed
                if isinstance(content, list):
                    content = "\n".join(content)

                # For bidirectional docs, preserve user sections
                preserved = {}
                if doc_type == DocumentType.BIDIRECTIONAL and preserve_user_content:
                    preserved = self._extract_preserved_sections(path)

                # Add unified header for markdown files
                if add_header and name.endswith(".md"):
                    header = self._generate_header(name, writer_id)
                    content = header + content

                # Restore preserved sections
                if preserved:
                    content = self._restore_preserved_sections(content, preserved)

                # Atomic write: temp file + rename
                self._atomic_write(path, content)

                # Get new mtime
                mtime = path.stat().st_mtime

                logger.debug(f"✅ I/O Write: {name} by {writer_id} ({len(content)} chars)")

                # AUDIT TRAIL: Record write to ledger
                self._record_write_audit(
                    name=name,
                    writer_id=writer_id,
                    doc_type=doc_type,
                    size=len(content),
                    mtime=mtime,
                    preserved_keys=list(preserved.keys()) if preserved else [],
                )

                # NOTIFY StateService for unified auto-commit tracking
                # This integrates IOService writes with the OS-level auto-commit system
                self._notify_state_service(path)

                return WriteResult(
                    success=True,
                    path=path,
                    mtime=mtime,
                    preserved_sections=preserved,
                )

            except Exception as e:
                logger.error(f"❌ I/O Write failed: {name} - {e}")
                return WriteResult(success=False, path=path, error=str(e))

    def read_document(self, name: str) -> Optional[str]:
        """
        Read a document's content.

        Args:
            name: Document name (e.g., "SETTINGS.md")

        Returns:
            Document content or None if not found
        """
        # CART BREAKER: Validate sandbox before read
        try:
            path = self._validate_sandbox(name)
        except PermissionError as e:
            logger.error(f"🛡️ SANDBOX ESCAPE BLOCKED (read): {name}")
            return None

        try:
            if path.exists():
                return path.read_text(encoding="utf-8")
            return None
        except Exception as e:
            logger.error(f"❌ I/O Read failed: {name} - {e}")
            return None

    def extract_user_section(self, name: str, section_marker: str) -> str:
        """
        Extract a specific user section from a document.

        Args:
            name: Document name
            section_marker: Section header to find (e.g., "## 📝 Quick Note")

        Returns:
            Section content or empty string
        """
        content = self.read_document(name)
        if not content:
            return ""

        return self._extract_section(content, section_marker)

    def write_snapshot(
        self,
        name: str,
        data: Dict[str, Any],
        writer_id: str = "KERNEL",
    ) -> WriteResult:
        """
        Write a JSON snapshot file.

        Args:
            name: File name (e.g., "vibe_snapshot.json")
            data: Dictionary to serialize as JSON
            writer_id: ID of the component writing

        Returns:
            WriteResult
        """
        import json

        content = json.dumps(data, indent=2, default=str)
        return self.write_document(
            name=name,
            content=content,
            doc_type=DocumentType.SNAPSHOT,
            writer_id=writer_id,
            add_header=False,
            preserve_user_content=False,
        )

    def _atomic_write(self, path: Path, content: str) -> None:
        """
        Perform an atomic write using temp file + rename.

        This prevents partial writes and ensures consistency.
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file in same directory (for same-filesystem rename)
        fd, tmp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.stem}_",
            suffix=path.suffix,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)

            # Atomic rename
            os.replace(tmp_path, path)

        except Exception:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _generate_header(self, name: str, writer_id: str) -> str:
        """Generate unified header from template."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # Get kernel status if available
        kernel_status = "NOT RUNNING"
        agent_count = 0
        if self._kernel:
            try:
                kernel_status = self._kernel.status.value
                agent_count = len(self._kernel.agent_registry)
            except Exception:
                pass

        # Load header config from InterfaceConfig (Phoenix Section)
        quick_start_command = "python -m vibe_core.cli boot"  # default
        try:
            from vibe_core.phoenix.sections.interface import InterfaceConfig

            config_path = str(self._root / "config" / "interface.yaml")
            interface_config = InterfaceConfig.from_yaml(config_path)
            quick_start_command = interface_config.header.quick_start_command
        except Exception as e:
            logger.debug(f"Could not load interface config for header: {e}")

        # Load from template
        try:
            from vibe_core.loaders import TemplateLoader

            loader = TemplateLoader()
            if loader.template_exists("header.md.j2"):
                return loader.render(
                    "header.md.j2",
                    writer_id=writer_id,
                    timestamp=timestamp,
                    kernel_status=kernel_status,
                    agent_count=agent_count,
                    quick_start_command=quick_start_command,
                )
        except Exception as e:
            logger.warning(f"Header template failed, using fallback: {e}")

        # Fallback if template not available
        return f"""<!--
AUTO-GENERATED by {writer_id}
Last Updated: {timestamp}
Kernel: {kernel_status} ({agent_count} agents)
Quick Start: {quick_start_command}
-->

"""

    def _extract_preserved_sections(self, path: Path) -> Dict[str, str]:
        """Extract sections that should be preserved across re-renders."""
        preserved = {}

        if not path.exists():
            return preserved

        try:
            content = path.read_text(encoding="utf-8")

            for key, marker in self._preserve_patterns.items():
                section_content = self._extract_section(content, marker)
                if section_content.strip():
                    preserved[key] = section_content

        except Exception as e:
            logger.warning(f"⚠️  Could not extract preserved sections from {path}: {e}")

        return preserved

    def _extract_section(self, content: str, marker: str) -> str:
        """Extract a section from content by its header marker."""
        lines = content.split("\n")
        in_section = False
        section_lines = []

        for line in lines:
            if marker in line:
                in_section = True
                continue

            if in_section:
                # Stop at next section header or separator
                if line.strip().startswith("## ") or line.strip() == "---":
                    break
                section_lines.append(line)

        # Trim trailing empty lines
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()

        return "\n".join(section_lines)

    def _restore_preserved_sections(self, content: str, preserved: Dict[str, str]) -> str:
        """Restore preserved sections into new content."""
        for key, marker in self._preserve_patterns.items():
            if key in preserved and preserved[key].strip():
                # Find the marker in new content and inject preserved content
                if marker in content:
                    # Replace placeholder content after marker
                    lines = content.split("\n")
                    new_lines = []
                    found_marker = False
                    skip_until_next_section = False

                    for line in lines:
                        if marker in line:
                            new_lines.append(line)
                            new_lines.append("")
                            new_lines.append(preserved[key])
                            found_marker = True
                            skip_until_next_section = True
                            continue

                        if skip_until_next_section:
                            if line.strip().startswith("## ") or line.strip() == "---":
                                skip_until_next_section = False
                                new_lines.append(line)
                            # Skip original content (it's replaced)
                            continue

                        new_lines.append(line)

                    if found_marker:
                        content = "\n".join(new_lines)

        return content

    def get_audit_stats(self) -> Dict[str, Any]:
        """
        Get audit statistics for this session.

        Returns:
            Dict with write_count, audit_enabled status, and ledger availability
        """
        ledger_available = bool(self._kernel and hasattr(self._kernel, "_ledger") and self._kernel._ledger)
        return {
            "write_count": self._write_count,
            "audit_enabled": self._audit_enabled,
            "ledger_available": ledger_available,
            "root_path": str(self._root),
        }

    def set_audit_enabled(self, enabled: bool) -> None:
        """
        Enable or disable audit trail recording.

        Use with caution - disabling audit loses visibility into writes.
        Typically only disabled for high-frequency internal operations.
        """
        self._audit_enabled = enabled
        logger.info(f"📝 Audit trail {'enabled' if enabled else 'disabled'}")


# Factory function for kernel integration
def create_io_service(kernel: "RealVibeKernel") -> KernelIOService:
    """Create an I/O service instance for a kernel."""
    return KernelIOService(kernel)
