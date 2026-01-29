#!/usr/bin/env python3
"""
WATCHMAN Hook Self-Healing System

Checks if git hooks are installed and installs them if missing.
Runs automatically in CI/CD and can be triggered manually.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xcf956ed4"  # GenesisByte: parampara % 37 == 0

import os
import subprocess
import sys
from pathlib import Path


def check_hooks_installed(repo_root: Path) -> dict:
    """Check which hooks are installed."""
    git_hooks_dir = repo_root / ".git" / "hooks"
    source_hooks_dir = repo_root / ".githooks"

    status = {
        "pre-commit": {
            "installed": False,
            "source_exists": False,
            "is_symlink": False,
            "valid": False,
        }
    }

    # Check source exists
    source_hook = source_hooks_dir / "pre-commit"
    if source_hook.exists():
        status["pre-commit"]["source_exists"] = True

    # Check installed
    installed_hook = git_hooks_dir / "pre-commit"
    if installed_hook.exists():
        status["pre-commit"]["installed"] = True
        status["pre-commit"]["is_symlink"] = installed_hook.is_symlink()

        # Verify it's valid (symlink points to right place or content matches)
        if installed_hook.is_symlink():
            target = installed_hook.resolve()
            status["pre-commit"]["valid"] = target == source_hook.resolve()
        else:
            # Compare content
            if source_hook.exists():
                status["pre-commit"]["valid"] = installed_hook.read_text() == source_hook.read_text()

    return status


def install_hook(repo_root: Path, hook_name: str, use_symlink: bool = True) -> bool:
    """Install a git hook."""
    git_hooks_dir = repo_root / ".git" / "hooks"
    source_hook = repo_root / ".githooks" / hook_name
    target_hook = git_hooks_dir / hook_name

    if not source_hook.exists():
        print(f"❌ Source hook not found: {source_hook}")
        return False

    # Ensure .git/hooks directory exists
    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing if present
    if target_hook.exists():
        target_hook.unlink()

    if use_symlink:
        # Create relative symlink
        relative_source = os.path.relpath(source_hook, git_hooks_dir)
        target_hook.symlink_to(relative_source)
        print(f"✅ Symlinked: {hook_name} -> {relative_source}")
    else:
        # Copy file
        target_hook.write_text(source_hook.read_text())
        target_hook.chmod(0o755)
        print(f"✅ Copied: {hook_name}")

    return True


def self_heal_hooks(repo_root: Path, fix: bool = False) -> bool:
    """Check hooks and optionally fix them."""
    print("🔍 WATCHMAN: Checking git hooks...")

    status = check_hooks_installed(repo_root)

    all_ok = True

    for hook_name, info in status.items():
        if not info["source_exists"]:
            print(f"❌ {hook_name}: Source not found in .githooks/")
            all_ok = False
            continue

        if not info["installed"]:
            print(f"⚠️  {hook_name}: NOT INSTALLED")
            all_ok = False

            if fix:
                print(f"   🔧 Installing {hook_name}...")
                if install_hook(repo_root, hook_name, use_symlink=True):
                    print(f"   ✅ {hook_name} installed")
                else:
                    print(f"   ❌ Failed to install {hook_name}")
                    return False

        elif not info["valid"]:
            print(f"⚠️  {hook_name}: INVALID (outdated or broken)")
            all_ok = False

            if fix:
                print(f"   🔧 Reinstalling {hook_name}...")
                if install_hook(repo_root, hook_name, use_symlink=True):
                    print(f"   ✅ {hook_name} reinstalled")
                else:
                    print(f"   ❌ Failed to reinstall {hook_name}")
                    return False

        else:
            symlink_status = "symlink" if info["is_symlink"] else "copy"
            print(f"✅ {hook_name}: OK ({symlink_status})")

    return all_ok


def main():
    """Main entry point."""
    # Try to find repo root via git
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        sys.exit(1)

    # Parse args
    fix = "--fix" in sys.argv or "-f" in sys.argv

    if fix:
        print("🛠️  WATCHMAN: Self-healing mode ENABLED")

    # Run check
    result = self_heal_hooks(repo_root, fix=fix)

    if result:
        print("\n✅ All hooks OK")
        sys.exit(0)
    else:
        if fix:
            print("\n❌ Hook healing FAILED")
            sys.exit(1)
        else:
            print("\n⚠️  Hooks missing or invalid")
            print("   Run with --fix to auto-install")
            sys.exit(1)


if __name__ == "__main__":
    main()
