#!/usr/bin/env python3
"""
AGENT CITY OS - THE ONE ENTRY POINT

Usage:
    python boot.py              # Boot and run (auto-installs everything)
    python boot.py --check      # Verify system can boot
    python boot.py --help       # Show this help

This is ALL you need. Clone the repo, run boot.py. Done.
No manual pip install. No setup. One command.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.resolve()


def print_banner(title: str):
    """Print a banner."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_python_version():
    """Verify Python version >= 3.8"""
    if sys.version_info < (3, 8):
        print(f"ERROR: Python 3.8+ required. You have {sys.version}")
        return False
    return True


def ensure_dependencies():
    """Auto-install dependencies if missing."""
    # Check if key dependencies exist using find_spec (no import side effects)
    from importlib.util import find_spec

    if all(find_spec(pkg) for pkg in ["jinja2", "pydantic", "yaml"]):
        return True  # Already installed

    # Auto-install from requirements.txt
    req_file = PROJECT_ROOT / "requirements.txt"
    if not req_file.exists():
        print("ERROR: requirements.txt not found")
        return False

    print("Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        print("Dependencies installed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False


def ensure_directories():
    """Create necessary runtime directories."""
    dirs = [
        PROJECT_ROOT / "data",
        Path("/tmp/vibe_os"),
        Path("/tmp/vibe_os/agents"),
        Path("/tmp/vibe_os/tasks"),
        Path("/tmp/vibe_os/kernel"),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    return True


def setup_environment():
    """Setup environment for boot."""
    # Add project root to path
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Set working directory
    os.chdir(PROJECT_ROOT)
    return True


def setup_git_hooks():
    """Activate git pre-commit hooks (ruff auto-format).

    This is the UNIVERSAL solution - works for any agent, any editor, any human.
    No vendor lock-in. Just git.
    """
    githooks_dir = PROJECT_ROOT / ".githooks"
    if not githooks_dir.exists():
        return True  # No hooks to set up

    try:
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", ".githooks"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo or git not installed - that's fine
        return True


def boot_check():
    """Quick boot verification - boots system but doesn't run operator loop."""
    # Import here after dependencies are installed
    from vibe_core.boot_orchestrator import BootOrchestrator

    print_banner("AGENT CITY OS - BOOT CHECK")

    orchestrator = BootOrchestrator()
    try:
        kernel = orchestrator.boot()
        status = kernel.get_status()
        agents = status.get("agents_registered", 0)
        has_ritual = hasattr(kernel, "daily_ritual") and kernel.daily_ritual is not None

        print()
        print(f"  Python:        {sys.version.split()[0]}")
        print(f"  Agents:        {agents}")
        print(f"  Daily Ritual:  {'Active' if has_ritual else 'MISSING'}")
        print("  Status:        OPERATIONAL")
        print()
        print_banner("BOOT CHECK: PASSED")
        return True
    except Exception as e:
        print(f"\nBOOT CHECK: FAILED - {e}")
        return False


def boot_and_run():
    """Full boot with interactive operator loop."""
    import asyncio

    from vibe_core.boot_orchestrator import boot_and_run as _boot_and_run

    print_banner("AGENT CITY OS - STARTING")
    print("  Press Ctrl+C to shutdown")
    print()

    try:
        asyncio.run(_boot_and_run())
    except KeyboardInterrupt:
        print("\nShutdown complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Agent City OS - One Command Boot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Clone. Run. Done.

    git clone <repo>
    cd steward-protocol
    python boot.py

No pip install needed. No setup. This script handles everything.
        """,
    )
    parser.add_argument("--check", action="store_true", help="Verify boot works (quick test, no operator loop)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check (for CI/pre-installed envs)")

    args = parser.parse_args()

    # Setup logging
    import logging

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(asctime)s [%(name)s] %(message)s", datefmt="%H:%M:%S")

    # STEP 1: Check Python version
    if not check_python_version():
        sys.exit(1)

    # STEP 2: Auto-install dependencies
    if not args.skip_deps:
        if not ensure_dependencies():
            sys.exit(1)

    # STEP 3: Setup environment
    setup_environment()

    # STEP 4: Create directories
    ensure_directories()

    # STEP 5: Setup git hooks (universal - no vendor lock-in)
    setup_git_hooks()

    # STEP 6: Run
    if args.check:
        success = boot_check()
        sys.exit(0 if success else 1)
    else:
        boot_and_run()


if __name__ == "__main__":
    main()
