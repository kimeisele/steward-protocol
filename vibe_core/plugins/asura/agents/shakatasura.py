"""
SHAKATASURA: The Filesystem Trojan.

Krishna Lila: Shakatasura was a demon who disguised himself as a cart.
When Krishna touched the cart, it collapsed trying to crush him.
Krishna kicked it and shattered it.

Cyber Translation: The filesystem is the cart.
If an agent can write to paths outside the sandbox using:
- Symlinks: workspace/log.txt -> /etc/passwd
- Path Traversal: ../../../vibe_core/kernel_impl.py

The kernel is "crushed" - its own code is overwritten.

Attack Vectors:
1. Symlink Attack: Create symlink to kernel source, write via IOService
2. Path Traversal: Use ../ sequences to escape sandbox
3. Null Byte Injection: path.txt\x00.jpg -> path.txt

Test Goal:
Can the kernel detect that the path escapes the sandbox?
Does it resolve symlinks BEFORE writing?

<!-- @HARNESS
files:
  - path: vibe_core/plugins/asura/agents/shakatasura.py
    required: true
wiring:
  - pattern: "class ShakatasuraAgent"
    in: vibe_core/plugins/asura/agents/shakatasura.py
  - pattern: "symlink"
    in: vibe_core/plugins/asura/agents/shakatasura.py
tests:
  - tests/security/test_shakatasura_escape.py
-->
"""

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("ASURA.SHAKATASURA")


@dataclass
class ShakatasuraAttackResult:
    """Results of the Shakatasura filesystem attack."""

    attack_type: str
    path_used: str
    target_path: str
    write_blocked: bool
    target_modified: bool
    message: str


class ShakatasuraAgent:
    """
    SHAKATASURA: The Filesystem Trojan.

    Attacks the KernelIOService with symlink and path traversal exploits.
    Tests if the kernel can be tricked into writing outside the sandbox.
    """

    def __init__(self, io_service: Any, sandbox_root: Path):
        self.io_service = io_service
        self.sandbox_root = sandbox_root
        self.trap_dir: Optional[Path] = None
        self._original_content: dict = {}  # Backup for cleanup

    def setup(self) -> Path:
        """
        Set up the trap directory for attacks.

        Returns:
            Path to the trap directory
        """
        self.trap_dir = Path(tempfile.mkdtemp(prefix="shakatasura_trap_"))
        logger.info(f"🏚️ SHAKATASURA: Trap directory created at {self.trap_dir}")
        return self.trap_dir

    async def attack_symlink(self, target_file: Path) -> ShakatasuraAttackResult:
        """
        Attack 1: Symlink Attack.

        Create a symlink inside the "sandbox" that points to a critical file.
        Try to write through the symlink.

        Args:
            target_file: The file we're trying to overwrite (e.g., kernel_impl.py)
        """
        logger.warning("🏚️ SHAKATASURA: Building the symlink trap...")

        if not self.trap_dir:
            self.setup()

        # Create symlink: trap/harmless.txt -> /path/to/kernel_impl.py
        trap_link = self.trap_dir / "harmless_log.txt"

        try:
            # Backup original content if target exists
            if target_file.exists():
                self._original_content[str(target_file)] = target_file.read_text()

            # Create symlink
            if trap_link.exists():
                trap_link.unlink()
            os.symlink(target_file, trap_link)

            logger.warning(f"🏚️ SHAKATASURA: Symlink created: {trap_link} -> {target_file}")

            # Try to write through the symlink
            logger.warning("🏚️ SHAKATASURA: Attempting write through symlink...")

            # Use relative path from sandbox root
            relative_trap = (
                trap_link.relative_to(self.sandbox_root) if self.sandbox_root in trap_link.parents else trap_link
            )

            try:
                result = self.io_service.write_document(
                    name=str(relative_trap),
                    content="# HACKED BY SHAKATASURA",
                    writer_id="shakatasura",
                    add_header=False,
                )

                # Check if target was modified
                if target_file.exists():
                    new_content = target_file.read_text()
                    if "HACKED BY SHAKATASURA" in new_content:
                        logger.error("☠️  SHAKATASURA SUCCEEDED: Target file was overwritten!")
                        return ShakatasuraAttackResult(
                            attack_type="symlink",
                            path_used=str(trap_link),
                            target_path=str(target_file),
                            write_blocked=False,
                            target_modified=True,
                            message="VULNERABILITY: Target file overwritten via symlink!",
                        )

                if result.success:
                    return ShakatasuraAttackResult(
                        attack_type="symlink",
                        path_used=str(trap_link),
                        target_path=str(target_file),
                        write_blocked=False,
                        target_modified=False,
                        message="Write succeeded but target not modified (symlink may have been resolved)",
                    )

            except PermissionError as e:
                if "SANDBOX" in str(e) or "escape" in str(e).lower():
                    logger.info("💎 SHAKATASURA BLOCKED: Sandbox escape detected!")
                    return ShakatasuraAttackResult(
                        attack_type="symlink",
                        path_used=str(trap_link),
                        target_path=str(target_file),
                        write_blocked=True,
                        target_modified=False,
                        message=f"BLOCKED: {e}",
                    )
                raise

            except Exception as e:
                return ShakatasuraAttackResult(
                    attack_type="symlink",
                    path_used=str(trap_link),
                    target_path=str(target_file),
                    write_blocked=True,
                    target_modified=False,
                    message=f"Write failed: {e}",
                )

        except Exception as e:
            logger.error(f"❌ SHAKATASURA setup failed: {e}")
            return ShakatasuraAttackResult(
                attack_type="symlink",
                path_used=str(trap_link),
                target_path=str(target_file),
                write_blocked=False,
                target_modified=False,
                message=f"Setup failed: {e}",
            )

        return ShakatasuraAttackResult(
            attack_type="symlink",
            path_used=str(trap_link),
            target_path=str(target_file),
            write_blocked=False,
            target_modified=False,
            message="Unknown result",
        )

    async def attack_path_traversal(self, target_file: Path) -> ShakatasuraAttackResult:
        """
        Attack 2: Path Traversal Attack.

        Use ../ sequences to escape the sandbox.
        """
        logger.warning("🏚️ SHAKATASURA: Attempting path traversal...")

        # Calculate how many ../ we need to escape
        relative = os.path.relpath(target_file, self.sandbox_root)
        traversal_path = relative  # e.g., "../../vibe_core/kernel_impl.py"

        logger.warning(f"🏚️ SHAKATASURA: Traversal path: {traversal_path}")

        try:
            result = self.io_service.write_document(
                name=traversal_path,
                content="# HACKED BY SHAKATASURA (path traversal)",
                writer_id="shakatasura",
                add_header=False,
            )

            # Check if target was modified
            if target_file.exists():
                new_content = target_file.read_text()
                if "HACKED BY SHAKATASURA" in new_content:
                    logger.error("☠️  SHAKATASURA SUCCEEDED: Path traversal worked!")
                    return ShakatasuraAttackResult(
                        attack_type="path_traversal",
                        path_used=traversal_path,
                        target_path=str(target_file),
                        write_blocked=False,
                        target_modified=True,
                        message="VULNERABILITY: Path traversal allowed!",
                    )

            if result.success:
                return ShakatasuraAttackResult(
                    attack_type="path_traversal",
                    path_used=traversal_path,
                    target_path=str(target_file),
                    write_blocked=False,
                    target_modified=False,
                    message="Write succeeded somewhere (check where)",
                )

        except PermissionError as e:
            logger.info("💎 SHAKATASURA BLOCKED: Path traversal detected!")
            return ShakatasuraAttackResult(
                attack_type="path_traversal",
                path_used=traversal_path,
                target_path=str(target_file),
                write_blocked=True,
                target_modified=False,
                message=f"BLOCKED: {e}",
            )

        except Exception as e:
            return ShakatasuraAttackResult(
                attack_type="path_traversal",
                path_used=traversal_path,
                target_path=str(target_file),
                write_blocked=True,
                target_modified=False,
                message=f"Write failed: {e}",
            )

        return ShakatasuraAttackResult(
            attack_type="path_traversal",
            path_used=traversal_path,
            target_path=str(target_file),
            write_blocked=False,
            target_modified=False,
            message="Unknown result",
        )

    def cleanup(self):
        """Restore original files and remove trap directory."""
        logger.info("🏚️ SHAKATASURA: Cleaning up...")

        # Restore original content
        for path_str, content in self._original_content.items():
            try:
                Path(path_str).write_text(content)
                logger.info(f"   Restored: {path_str}")
            except Exception as e:
                logger.error(f"   Failed to restore {path_str}: {e}")

        # Remove trap directory
        if self.trap_dir and self.trap_dir.exists():
            import shutil

            shutil.rmtree(self.trap_dir)
            logger.info("   Trap directory removed")
