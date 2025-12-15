#!/usr/bin/env python3
"""
OPUS-081: Git Gatekeeper
========================
The authority on whether a repository state is 'clean' or 'dirty'.
Distinguishes between SOURCE CODE (human) and RUNTIME STATE (machine).

Usage:
    python scripts/git_gatekeeper.py

Exit codes:
    0 = Clean (or only runtime state dirty)
    1 = Dirty source code detected
"""

import sys
from pathlib import Path

# Add repo root to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

try:
    from vibe_core.state.git_state import GitState
except ImportError as e:
    # Fail open if we can't load (don't block user)
    print(f"⚠️  GitState import failed: {e}")
    sys.exit(0)


def main():
    git = GitState(repo_root)

    if not git.is_git_repo():
        sys.exit(0)

    # The Core Check: is SOURCE CODE dirty?
    if git.is_source_dirty():
        print("🚫 STOP: Uncommitted SOURCE CODE changes detected.")

        files = git.get_dirty_source_files()
        if files:
            print("\nDirty source files:")
            for f in files[:10]:
                print(f"  - {f}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more.")

        print("\n💡 Runtime state files (dashboards/logs) are IGNORED.")
        print("   See: docs/architecture/OPUS/081-RUNTIME-STATE-MANIFEST.md")
        sys.exit(1)

    # Clean enough for exit
    sys.exit(0)


if __name__ == "__main__":
    main()
