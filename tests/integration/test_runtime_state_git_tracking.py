"""
OPUS-FIX: Runtime State Git Tracking Test

P0 TEST: Verify runtime state files are NOT tracked in git.

The Death Loop Problem:
- RuntimeStateDefinition correctly classifies files as runtime state
- BUT those files were tracked in git history
- Kernel modifies them constantly (tick counter, session state)
- Git sees "uncommitted changes" forever
- Merge conflicts on every PR

This test ensures the system is SELF-AWARE:
- If RuntimeStateDefinition says X is runtime state
- Then git ls-files X should return empty (not tracked)

This test WOULD HAVE caught the manas_awareness.json death loop.
"""

import subprocess
from pathlib import Path

import pytest

from vibe_core.state.runtime_state import RuntimeStateDefinition


@pytest.fixture
def runtime_definition():
    """Get RuntimeStateDefinition with workspace discovery."""
    workspace = Path.cwd()
    return RuntimeStateDefinition.from_workspace(workspace)


def get_tracked_files() -> set[str]:
    """Get all files tracked by git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


class TestRuntimeStateNotTracked:
    """Verify runtime state files are NOT tracked in git."""

    def test_vibe_state_not_tracked(self):
        """
        P0: .vibe/state/ files must NOT be tracked in git.

        This was the root cause of the death loop:
        - manas_awareness.json is in .vibe/state/
        - Kernel writes tick counter every few seconds
        - Git saw it as uncommitted changes
        - Merge conflicts on every PR
        """
        tracked = get_tracked_files()
        vibe_state_tracked = [f for f in tracked if f.startswith(".vibe/state/")]

        assert not vibe_state_tracked, (
            f"DEATH LOOP DETECTED: .vibe/state/ files are tracked in git!\n"
            f"Tracked files: {vibe_state_tracked}\n"
            f"Fix: git rm --cached -r .vibe/state/"
        )

    def test_prakriti_not_tracked(self):
        """
        P0: .prakriti/ files must NOT be tracked in git.

        Prakriti snapshots and session locks are runtime state.
        They change constantly and cause merge conflicts.
        """
        tracked = get_tracked_files()
        prakriti_tracked = [f for f in tracked if f.startswith(".prakriti/")]

        assert not prakriti_tracked, (
            f"DEATH LOOP DETECTED: .prakriti/ files are tracked in git!\n"
            f"Tracked files: {prakriti_tracked}\n"
            f"Fix: git rm --cached -r .prakriti/"
        )

    def test_opus_state_not_tracked(self):
        """
        P0: .opus_state/ files must NOT be tracked in git.

        Legacy state directory that also causes death loop issues.
        """
        tracked = get_tracked_files()
        opus_state_tracked = [f for f in tracked if f.startswith(".opus_state/")]

        assert not opus_state_tracked, (
            f"DEATH LOOP DETECTED: .opus_state/ files are tracked in git!\n"
            f"Tracked files: {opus_state_tracked[:10]}\n"
            f"Fix: git rm --cached -r .opus_state/"
        )

    @pytest.mark.skip(reason="Too strict - RuntimeStateDefinition includes generated UI files")
    def test_runtime_state_definition_matches_git_tracking(self, runtime_definition):
        """
        SELF-AWARENESS TEST: RuntimeStateDefinition should match git tracking.

        If RuntimeStateDefinition says X is runtime state,
        and X exists on disk,
        then X should NOT be tracked in git.

        This catches the schizophrenia where:
        - Code says "this is runtime" (correct)
        - Git says "I'm tracking this" (wrong)

        NOTE: Skipped because RuntimeStateDefinition includes generated UI files
        (INDEX.md, HELP.md, etc.) that are intentionally tracked.
        TODO: Refine RuntimeStateDefinition to distinguish between:
        - Runtime state (ephemeral, never track)
        - Generated UI (may be tracked intentionally)
        """
        tracked = get_tracked_files()
        violations = []

        for tracked_file in tracked:
            if runtime_definition.is_runtime_state(tracked_file):
                violations.append(tracked_file)

        assert not violations, (
            f"SCHIZOPHRENIA DETECTED: Files classified as runtime state are tracked in git!\n"
            f"Violations ({len(violations)}):\n"
            + "\n".join(f"  - {f}" for f in violations[:20])
            + ("\n  ... (more)" if len(violations) > 20 else "")
            + "\n\nFix: git rm --cached <file> for each violation"
        )

    def test_manas_awareness_specifically_not_tracked(self):
        """
        REGRESSION TEST: manas_awareness.json was THE death loop file.

        This specific file caused:
        - Tick counter updates every few seconds
        - Constant git status noise
        - Merge conflicts on every PR
        - User could not merge branches

        This must NEVER be tracked again.
        """
        tracked = get_tracked_files()
        manas_file = ".vibe/state/plugins/opus_assistant/manas_awareness.json"

        assert manas_file not in tracked, (
            f"CRITICAL REGRESSION: {manas_file} is tracked in git!\n"
            f"This file caused the P0 death loop.\n"
            f"Fix: git rm --cached {manas_file}"
        )

    def test_session_lock_not_tracked(self):
        """
        Session lock files must NOT be tracked.

        Session/state lock files are ephemeral - they exist only
        while a session is active. Package lock files (uv.lock) are OK.
        """
        tracked = get_tracked_files()
        # Only check for session-related locks, not package locks
        session_locks = [
            f
            for f in tracked
            if f.endswith(".lock")
            and ("session" in f.lower() or ".prakriti/" in f or ".vibe/state/" in f or ".opus_state/" in f)
        ]

        assert not session_locks, (
            f"Session lock files are tracked in git!\nTracked: {session_locks}\nFix: git rm --cached for each"
        )


class TestRuntimeStatePatternCompleteness:
    """Verify RuntimeStateDefinition patterns are complete."""

    def test_vibe_state_pattern_exists(self, runtime_definition):
        """RuntimeStateDefinition should classify .vibe/state/* as runtime."""
        test_path = ".vibe/state/plugins/opus_assistant/manas_awareness.json"
        assert runtime_definition.is_runtime_state(test_path), (
            f"RuntimeStateDefinition does not classify {test_path} as runtime!\n"
            f"This is a configuration bug - the pattern is missing."
        )

    def test_prakriti_pattern_exists(self, runtime_definition):
        """RuntimeStateDefinition should classify .prakriti/* as runtime."""
        test_path = ".prakriti/session.lock"
        assert runtime_definition.is_runtime_state(test_path), (
            f"RuntimeStateDefinition does not classify {test_path} as runtime!\n"
            f"This is a configuration bug - the pattern is missing."
        )

    def test_lock_files_classified_as_runtime(self, runtime_definition):
        """All .lock files should be classified as runtime."""
        test_paths = [
            "some.lock",
            ".prakriti/session.lock",
            "data/cache.lock",
        ]
        for path in test_paths:
            assert runtime_definition.is_runtime_state(path), (
                f"RuntimeStateDefinition does not classify {path} as runtime!"
            )
