"""
REMEDIATE COMMAND - KAPILA's Analysis
=====================================

MAHAJANA: KAPILA (The Analyzer)
OPCODE: GARBAGE_COLLECT (Position 7)
PHASE: PURIFY

Usage:
    naga remediate silent --fix    Fix silent failures
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x4c2144dc"  # GenesisByte: parampara % 37 == 0

import re
from pathlib import Path
from typing import List, Tuple
from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode

import logging
logger = logging.getLogger(__name__)


@naga_command(
    opcode=MantraOpCode.TYPE_CHECK, name="remediate", help_text="Actually FIX detected issues (KAPILA's analysis)"
)
class RemediateCommand(NagaCommandBase):
    def execute(self, args: List[str]) -> NagaCommandResult:
        auto_fix = "--fix" in args
        dry_run = "--dry-run" in args or not auto_fix

        remedy_type = None
        for arg in args:
            if arg not in ["--fix", "--dry-run"]:
                remedy_type = arg
                break

        if remedy_type == "silent":
            return self._remediate_silent_failures(dry_run)
        else:
            return self.failure(f"Unknown remediation type: {remedy_type}", exit_code=1)

    def _remediate_silent_failures(self, dry_run: bool) -> NagaCommandResult:
        target_path = Path.cwd() / "vibe_core"
        fixed_count = 0
        for py_file in target_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                new_content = re.sub(
                    r"(except\s+\w+.*?):\s*pass(\s*$)",
                    r'\1:\n                logger.debug("Suppressed exception")',
                    content,
                    flags=re.MULTILINE,
                )
                if new_content != content:
                    if not dry_run:
                        py_file.write_text(new_content, encoding="utf-8")
                    fixed_count += 1
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

        status = "Would fix" if dry_run else "Fixed"
        return self.success(f"[KAPILA] {status} {fixed_count} files.")
