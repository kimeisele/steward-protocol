#!/usr/bin/env python3
"""
HERALD DEPENDENCY MIGRATION SCRIPT
===================================

Migrates Herald's requirements.txt → pyproject.toml via DependencyManager.

This demonstrates the new system.add_dependency() API.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.dependency_manager import DependencyManager


def migrate_herald_dependencies():
    """Migrate Herald dependencies from requirements.txt to pyproject.toml."""

    print("🔄 Herald Dependency Migration")
    print("=" * 60)

    # Initialize Dependency Manager
    dm = DependencyManager()
    print(f"✅ DependencyManager initialized: {dm.pyproject_path}")

    # Herald dependencies from requirements.txt
    herald_deps = {
        "openai": ">=1.0.0",
        "python-dotenv": ">=1.0.0",
        "PyYAML": ">=6.0",
        "tavily-python": ">=0.3.0",
        "tweepy": ">=4.14.0",
        "praw": ">=7.7.0",
        "gitpython": ">=3.1.0",
        "Pillow": ">=10.0.0",
        "PyGithub": ">=2.1.1",
    }

    print(f"\n📦 Migrating {len(herald_deps)} dependencies...")

    for package, version in herald_deps.items():
        # Check if already exists
        if dm.has_dependency(package):
            current_version = dm.get_version_constraint(package)
            if current_version == version:
                print(f"   ✓ {package}{version} (already present)")
            else:
                print(f"   ⚠️  {package} exists with different version:")
                print(f"      Current: {current_version}")
                print(f"      Herald:  {version}")
                print("      → Keeping current version")
        else:
            dm.add_dependency(package, version)
            print(f"   ✅ Added: {package}{version}")

    print("\n✅ Migration complete!")
    print("📦 pyproject.toml now contains all Herald dependencies")
    print("\n💡 Next step: Delete steward/system_agents/herald/requirements.txt")


if __name__ == "__main__":
    migrate_herald_dependencies()
