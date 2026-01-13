"""
COMMIT COMMAND - BHISHMA's Oath
================================

MAHAJANA: BHISHMA (The Oath-Keeper)
OPCODE: COMMIT_LOG (Position 11)
PHASE: SERVE

WHY BHISHMA?
- Bhishma took the most famous oath in history (lifelong celibacy)
- Once he committed, he never broke his word
- COMMIT_LOG is about recording permanent changes
- Bhishma's commitment was irrevocable - like a git commit

MANTRA WORD: KRISHNA (Position 11)
"Krishna witnesses all commitments"

COMMIT_LOG = Record changes permanently in the log.
Bhishma commits and never wavers.

Usage:
    naga commit                   # Show commit status
    naga commit --log             # Show recent commits
    naga commit --staged          # Show staged changes
    naga commit --diff            # Show diff of staged
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xa74c7c10"  # GenesisByte: parampara % 37 == 0

import subprocess
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.LEDGER_SIGN,
    name="commit",
    help_text="Commit status and log (BHISHMA's oath - SERVE phase)")
class CommitCommand(NagaCommandBase):
    """
    Commit command implementation.

    BHISHMA oversees:
    - Git commit status
    - Staged changes
    - Recent commit log
    - Commit integrity

    Once committed, changes are sealed by Bhishma's oath.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute commit status check.

        Args:
            args: Command arguments
                --log: Show recent commits
                --staged: Show staged changes
                --diff: Show diff of staged changes

        Returns:
            NagaCommandResult with commit information
        """
        # Parse flags
        show_log = "--log" in args
        show_staged = "--staged" in args
        show_diff = "--diff" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "bhishma"),
            ("opcode", "COMMIT_LOG"),
            ("phase", "serve"),
            ("position", "11"),
        ]

        output_parts.append("[BHISHMA] Commit Status")
        output_parts.append("=" * 50)

        # Check if we're in a git repo
        if not self._is_git_repo():
            output_parts.append("")
            output_parts.append("  Not a git repository.")
            output_parts.append("  Bhishma requires git to track commitments.")
            return self.success(
                "\n".join(output_parts),
                data=tuple(data + [("git_repo", "false")]))

        data.append(("git_repo", "true"))

        # Show staged changes
        if show_staged or (not show_log and not show_diff):
            staged_result = self._get_staged()
            output_parts.append("")
            output_parts.append("  Staged Changes (Ready to Commit):")
            if staged_result["files"]:
                for f in staged_result["files"][:10]:
                    output_parts.append(f"    {f}")
                if len(staged_result["files"]) > 10:
                    output_parts.append(
                        f"    ... and {len(staged_result['files']) - 10} more"
                    )
            else:
                output_parts.append("    (no staged changes)")
            data.append(("staged_count", str(len(staged_result["files"]))))

        # Show diff
        if show_diff:
            diff_result = self._get_staged_diff()
            output_parts.append("")
            output_parts.append("  Staged Diff:")
            if diff_result["diff"]:
                lines = diff_result["diff"].split("\n")[:20]
                for line in lines:
                    output_parts.append(f"    {line}")
                if len(diff_result["diff"].split("\n")) > 20:
                    output_parts.append("    ... (truncated)")
            else:
                output_parts.append("    (no diff available)")

        # Show recent commits
        if show_log:
            log_result = self._get_recent_commits()
            output_parts.append("")
            output_parts.append("  Recent Commits (Bhishma's Ledger):")
            if log_result["commits"]:
                for commit in log_result["commits"][:8]:
                    output_parts.append(f"    {commit}")
            else:
                output_parts.append("    (no commits yet)")
            data.append(("commit_count", str(len(log_result["commits"]))))

        # Current branch info
        branch = self._get_current_branch()
        output_parts.append("")
        output_parts.append(f"  Current Branch: {branch}")
        data.append(("branch", branch))

        # Head commit
        head = self._get_head_commit()
        if head:
            output_parts.append(f"  HEAD: {head}")
            data.append(("head", head[:8]))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("COMMIT_LOG: Status recorded")

        return self.success(
            "\n".join(output_parts),
            data=tuple(data))

    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _get_staged(self) -> dict:
        """Get staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                files = result.stdout.strip().split("\n")
                return {"files": files}
            return {"files": []}

        except Exception:
            return {"files": []}

    def _get_staged_diff(self) -> dict:
        """Get diff of staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=10)

            if result.returncode == 0:
                return {"diff": result.stdout.strip()}
            return {"diff": ""}

        except Exception:
            return {"diff": ""}

    def _get_recent_commits(self, count: int = 8) -> dict:
        """Get recent commit log."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--oneline"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                commits = result.stdout.strip().split("\n")
                return {"commits": commits}
            return {"commits": []}

        except Exception:
            return {"commits": []}

    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=5)

            if result.returncode == 0:
                return result.stdout.strip() or "detached HEAD"
            return "unknown"

        except Exception:
            return "unknown"

    def _get_head_commit(self) -> str:
        """Get HEAD commit hash and message."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=5)

            if result.returncode == 0:
                return result.stdout.strip()
            return ""

        except Exception:
            return ""


# Export for direct import
__all__ = ["CommitCommand"]
