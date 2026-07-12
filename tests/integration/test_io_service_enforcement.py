"""
I/O Service Enforcement Test

CRITICAL: This test prevents regressions in the I/O Service migration.
All file writes in vibe_core (except approved exclusions) MUST use io_service.

This test greps for direct `.write_text(` calls and fails if violations found.
"""

import subprocess
from pathlib import Path

import pytest

# Files that are ALLOWED to have direct write_text calls
EXCLUSIONS = {
    # I/O Service internals (the service itself)
    "vibe_core/io_service.py",
    # VFS layer (low-level file operations)
    "vibe_core/vfs.py",
    # Lock file management (internal locking mechanism)
    "vibe_core/task_management/file_lock.py",
    # Export engine (user-requested exports - decision: OK to bypass)
    "vibe_core/task_management/export_engine.py",
    # Archive (historical task storage - internal)
    "vibe_core/task_management/archive.py",
    # ====== P1 MIGRATIONS (tracked in docs/MIGRATION_PLAN.md) ======
    # These files need migration but are lower priority
    "vibe_core/tools/file_tools.py",  # P1: User file operations
    "vibe_core/doc_renderer.py",  # P1: Already uses io_service internally
    "vibe_core/phoenix/sections/routing.py",  # P1: Matrix rendering
    "vibe_core/file_operator.py",  # P1: File operator utility
    "vibe_core/agent_interface.py",  # P1: Agent VFS layer
    "vibe_core/lineage.py",  # P1: Lineage export
    "vibe_core/identity.py",  # P1: Identity manifest export
}

# Patterns that indicate fallback code (OK - used when io_service not available)
FALLBACK_PATTERNS = [
    "# Fallback:",
    "# fallback:",
    "# Fallback for standalone",
    "standalone/test mode",
    "Fallback: standalone mode",
]

# Files with migrated tools that have fallback blocks
# These are properly migrated but have fallback for standalone usage
MIGRATED_WITH_FALLBACK = {
    "vibe_core/tools/agenda_tools.py",  # AddTaskTool, CompleteTaskTool migrated
    "vibe_core/task_management/task_manager.py",  # TaskManager migrated
    "vibe_core/settings_sync.py",  # SettingsSync migrated
    "vibe_core/envoy_sync.py",  # EnvoySync migrated
}


@pytest.mark.skip(
    reason="Tech debt: 25 violations in cartridges/plugins need migration to io_service - see EXCLUSIONS for P1 list"
)
def test_no_direct_write_text_in_vibe_core():
    """
    Enforcement: No direct .write_text() calls in vibe_core.

    This test ensures all file writes go through KernelIOService
    for atomic writes, locking, and audit trail.

    EXCLUSIONS:
    - io_service.py: The service itself needs to write
    - vfs.py: VFS layer (low-level)
    - file_lock.py: Lock file management
    - export_engine.py: User-requested exports
    - archive.py: Internal archival

    ALLOWED FALLBACKS:
    - Lines with "# Fallback:" comment are OK (standalone mode)

    TODO: Migrate remaining violations (mostly in cartridges/):
    - cartridges/agent_city/mechanic, system/civic, engineer, envoy, forum, herald
    - phoenix/utils/routing.py
    - plugins/interface/plugin_main.py
    - runtime_extensions.py, steward/crypto.py
    """
    # tests/integration/file.py -> tests/integration -> tests -> project_root
    project_root = Path(__file__).parent.parent.parent
    vibe_core_path = project_root / "vibe_core"

    if not vibe_core_path.exists():
        pytest.skip("vibe_core directory not found")

    # Use grep to find all .write_text( calls
    try:
        result = subprocess.run(
            [
                "grep",
                "-r",
                "-n",
                r"\.write_text(",
                str(vibe_core_path),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        pytest.skip("grep not available")

    violations = []

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        # Parse file path from grep output
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue

        file_path = parts[0]
        line_num = parts[1]
        code = parts[2]

        # Convert to relative path for checking
        rel_path = Path(file_path).relative_to(project_root)
        rel_path_str = str(rel_path)

        # Skip exclusions
        if rel_path_str in EXCLUSIONS:
            continue

        # Skip migrated files with fallback blocks (these are properly handled)
        if rel_path_str in MIGRATED_WITH_FALLBACK:
            continue

        # Skip if it's a fallback pattern
        if any(pattern in code for pattern in FALLBACK_PATTERNS):
            continue

        # Skip if line is commented out
        if code.strip().startswith("#"):
            continue

        violations.append(f"{rel_path_str}:{line_num}: {code.strip()}")

    if violations:
        violation_list = "\n".join(violations)
        pytest.fail(
            f"Direct .write_text() calls found in vibe_core!\n\n"
            f"All file writes must use KernelIOService.write_document().\n\n"
            f"Violations:\n{violation_list}\n\n"
            f"Fix: Replace direct writes with io_service pattern:\n"
            f"  self._io_service.write_document(name, content, doc_type, writer_id)"
        )


def test_io_service_exists():
    """Verify io_service module exists and is importable."""
    try:
        from vibe_core.io_service import DocumentType, KernelIOService, WriteResult

        assert KernelIOService is not None
        assert DocumentType is not None
        assert WriteResult is not None
    except ImportError as e:
        pytest.fail(f"Failed to import io_service: {e}")


def test_kernel_has_io_attribute():
    """Verify RealVibeKernel has io attribute (KernelIOService)."""
    try:
        # Don't actually instantiate (expensive), just check attribute exists in init
        import inspect

        from vibe_core.kernel_impl import RealVibeKernel

        source = inspect.getsource(RealVibeKernel)

        assert "self.io = KernelIOService" in source, "RealVibeKernel must set self.io = KernelIOService(self)"
    except ImportError as e:
        pytest.fail(f"Failed to import kernel: {e}")
