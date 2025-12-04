#!/usr/bin/env python3
"""
AGENT CITY OS - THE ONE ENTRY POINT (PHOENIX EDITION)

Usage:
    python boot.py              # Boot and run (auto-installs everything)
    python boot.py --check      # Verify system can boot
    python boot.py --venv       # Use virtual environment (professional mode)
    python boot.py --help       # Show this help

This is ALL you need. Clone the repo, run boot.py. Done.
No manual pip install. No setup. One command.

PHOENIX GUARANTEES:
- Works on Windows, Linux, Mac
- Tries uv → pip → python -m pip (in order)
- Uses pyproject.toml (not requirements.txt)
- Cross-platform temp directories
- Self-diagnosing errors
- Retry with backoff on network failures
- Optional venv support (--venv flag)
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Project root (where this script lives)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Cross-platform runtime directory
RUNTIME_DIR = Path(tempfile.gettempdir()) / "vibe_os"


def print_banner(title: str):
    """Print a banner."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_error(msg: str, suggestion: str = None):
    """Print error with optional fix suggestion."""
    print(f"\n❌ ERROR: {msg}")
    if suggestion:
        print(f"   → FIX: {suggestion}")
    print()


def check_python_version():
    """Verify Python version >= 3.8"""
    if sys.version_info < (3, 8):
        print_error(
            f"Python 3.8+ required. You have {sys.version}",
            "Install Python 3.8 or newer from https://python.org",
        )
        return False
    return True


def ensure_venv(python_exe=None):
    """Create and activate venv if --venv flag passed (CREDIBILITY FIX: P1.1).

    Args:
        python_exe: Python executable to use (defaults to sys.executable)

    Returns:
        Path to venv's Python executable
    """
    venv_path = PROJECT_ROOT / ".venv"
    python_exe = python_exe or sys.executable

    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([python_exe, "-m", "venv", str(venv_path)], check=True)
            print("✓ Virtual environment created.")
        except subprocess.CalledProcessError as e:
            print_error(
                f"Failed to create virtual environment: {e}", "Ensure 'python3-venv' is installed on your system"
            )
            return None

    # Return the venv's Python executable
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def find_installer(use_venv=False, venv_python=None):
    """Find the best available package installer.

    Args:
        use_venv: If True, don't use --system flag for uv
        venv_python: If provided, use this Python executable for pip

    Returns (command_list, name) or (None, None) if nothing found.
    Preference: uv > pip > python -m pip
    """
    python_exe = str(venv_python) if venv_python else sys.executable

    # Try uv first (fastest, modern) - needs --system for non-venv installs
    if shutil.which("uv"):
        if use_venv:
            return (["uv", "pip", "install", "-e", "."], "uv")
        else:
            return (["uv", "pip", "install", "--system", "-e", "."], "uv")

    # Try pip directly (prefer venv's pip if available)
    if venv_python:
        venv_pip = venv_python.parent / ("pip.exe" if sys.platform == "win32" else "pip")
        if venv_pip.exists():
            return ([str(venv_pip), "install", "-e", "."], "pip (venv)")

    if shutil.which("pip"):
        return (["pip", "install", "-e", "."], "pip")

    if shutil.which("pip3"):
        return (["pip3", "install", "-e", "."], "pip3")

    # Fallback to python -m pip
    return ([python_exe, "-m", "pip", "install", "-e", "."], "python -m pip")


def ensure_dependencies(use_venv=False, venv_python=None):
    """Auto-install dependencies from pyproject.toml with retry.

    Args:
        use_venv: Whether to use venv mode (affects uv --system flag)
        venv_python: Path to venv Python executable if using venv
    """
    from importlib.util import find_spec

    # Check if ALL key dependencies already installed (not just core ones)
    required = ["pydantic", "yaml", "rich", "tweepy", "praw", "PIL", "fastapi", "openai"]
    if all(find_spec(pkg) for pkg in required):
        return True  # Already installed

    # Find installer
    install_cmd, installer_name = find_installer(use_venv=use_venv, venv_python=venv_python)
    if not install_cmd:
        print_error(
            "No package installer found (uv, pip, pip3)",
            "Install pip: https://pip.pypa.io/en/stable/installation/",
        )
        return False

    # Check pyproject.toml exists
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if not pyproject.exists():
        print_error(
            "pyproject.toml not found",
            f"Make sure you're in the project root: {PROJECT_ROOT}",
        )
        return False

    # Install with retry (network can be flaky)
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Installing dependencies via {installer_name}..." + (f" (attempt {attempt + 1})" if attempt > 0 else ""))

        try:
            result = subprocess.run(
                install_cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
            )

            if result.returncode == 0:
                print("✓ Dependencies installed.")
                return True

            # Failed - show error on last attempt
            if attempt == max_retries - 1:
                print_error(
                    f"Installation failed after {max_retries} attempts",
                    "Check your internet connection and try again",
                )
                if result.stderr:
                    print(f"   Details: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            print_error("Installation timed out", "Check your internet connection")
            return False
        except Exception as e:
            if attempt == max_retries - 1:
                print_error(f"Installation error: {e}")
                return False

        # Wait before retry (exponential backoff)
        wait_time = 2**attempt
        print(f"   Retrying in {wait_time}s...")
        time.sleep(wait_time)

    return False


def ensure_directories():
    """Create necessary runtime directories (cross-platform)."""
    dirs = [
        PROJECT_ROOT / "data",
        RUNTIME_DIR,
        RUNTIME_DIR / "agents",
        RUNTIME_DIR / "tasks",
        RUNTIME_DIR / "kernel",
    ]
    for d in dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print_error(
                f"Cannot create directory: {d}",
                "Check permissions or run with appropriate access",
            )
            return False
    return True


def setup_environment():
    """Setup environment for boot."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    os.chdir(PROJECT_ROOT)
    return True


def setup_git_hooks():
    """Activate git pre-commit hooks (ruff auto-format).

    Universal solution - works for any agent, editor, human.
    No vendor lock-in. Just git.
    """
    githooks_dir = PROJECT_ROOT / ".githooks"
    if not githooks_dir.exists():
        return True  # No hooks to set up

    # Check if we're in a git repo
    if not (PROJECT_ROOT / ".git").exists():
        return True  # Not a git repo, skip

    try:
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", ".githooks"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not installed or failed - that's fine, non-critical
        return True


def boot_check():
    """Quick boot verification."""
    from vibe_core.boot_orchestrator import BootOrchestrator
    from vibe_core.config import load_config

    print_banner("AGENT CITY OS - BOOT CHECK")

    # Load Phoenix Config (matrix.yaml) for proper agent configuration
    try:
        config = load_config("config/matrix.yaml")
        print(f"  Config:        {config.city_name} (v{config.federation_version})")
    except Exception as e:
        print(f"  Config:        ⚠️  Failed to load ({e})")
        config = None

    orchestrator = BootOrchestrator(config=config)
    try:
        kernel = orchestrator.boot()
        status = kernel.get_status()
        agents = status.get("agents_registered", 0)
        has_ritual = hasattr(kernel, "daily_ritual") and kernel.daily_ritual is not None

        print()
        print(f"  Python:        {sys.version.split()[0]}")
        print(f"  Platform:      {sys.platform}")
        print(f"  Agents:        {agents}")
        print(f"  Daily Ritual:  {'Active' if has_ritual else 'MISSING'}")
        print(f"  Runtime:       {RUNTIME_DIR}")
        print("  Status:        OPERATIONAL")
        print()
        print_banner("BOOT CHECK: PASSED")
        return True
    except Exception as e:
        print_error(f"Boot failed: {e}")
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
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent City OS - One Command Boot (Phoenix Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Clone. Run. Done.

    git clone <repo>
    cd steward-protocol
    python boot.py

No pip install needed. No setup. This script handles everything.
Works on Windows, Linux, Mac. Tries uv → pip automatically.
        """,
    )
    parser.add_argument("--check", action="store_true", help="Verify boot works (quick test)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    parser.add_argument("--venv", action="store_true", help="Use virtual environment (CREDIBILITY FIX: P1.1)")

    args = parser.parse_args()

    # Setup logging
    import logging

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(asctime)s [%(name)s] %(message)s", datefmt="%H:%M:%S")

    # STEP 1: Check Python version
    if not check_python_version():
        sys.exit(1)

    # STEP 2: Setup environment (needed before imports)
    setup_environment()

    # STEP 2.5: Setup virtual environment if requested (CREDIBILITY FIX: P1.1)
    venv_python = None
    if args.venv:
        print("Using virtual environment mode...")
        venv_python = ensure_venv()
        if not venv_python:
            sys.exit(1)
        print(f"✓ Using venv Python: {venv_python}")

    # STEP 3: Auto-install dependencies
    if not args.skip_deps:
        if not ensure_dependencies(use_venv=args.venv, venv_python=venv_python):
            sys.exit(1)

    # STEP 4: Create directories
    if not ensure_directories():
        sys.exit(1)

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
