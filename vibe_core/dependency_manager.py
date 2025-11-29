"""
DEPENDENCY MANAGER - Central pyproject.toml Management
======================================================

Goal: Stop agents from creating requirements.txt
Strategy: Provide kernel-level API for dependency management

Philosophy:
"One source of truth: pyproject.toml. Everything else is hallucination."

Usage:
    dm = DependencyManager()
    dm.add_dependency("pandas", ">=2.0.0")
    dm.get_dependencies()  # Returns all deps
    dm.remove_dependency("pandas")

Critical: Uses tomlkit (NOT standard toml) to preserve formatting and comments.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, List
import tomlkit
from tomlkit.toml_document import TOMLDocument

logger = logging.getLogger("DEPENDENCY_MANAGER")


class DependencyManager:
    """
    Central manager for project dependencies.

    Reads and writes pyproject.toml using tomlkit to preserve formatting.
    Provides safe API for agents to declare dependencies without touching filesystem.
    """

    def __init__(self, pyproject_path: str = "pyproject.toml"):
        """
        Initialize DependencyManager.

        Args:
            pyproject_path: Path to pyproject.toml (default: root)
        """
        self.pyproject_path = Path(pyproject_path)

        if not self.pyproject_path.exists():
            raise FileNotFoundError(
                f"pyproject.toml not found at {self.pyproject_path}. "
                f"DependencyManager requires a valid pyproject.toml."
            )

        self.document: Optional[TOMLDocument] = None
        self._load()

        logger.info(f"📦 DependencyManager initialized: {self.pyproject_path}")

    def _load(self) -> None:
        """Load pyproject.toml using tomlkit (preserves formatting)."""
        with open(self.pyproject_path, "r") as f:
            self.document = tomlkit.load(f)

        # Validate structure
        if "project" not in self.document:
            raise ValueError("Invalid pyproject.toml: missing [project] section")

        if "dependencies" not in self.document["project"]:
            raise ValueError("Invalid pyproject.toml: missing [project.dependencies]")

    def _save(self) -> None:
        """Save pyproject.toml using tomlkit (preserves formatting)."""
        with open(self.pyproject_path, "w") as f:
            tomlkit.dump(self.document, f)

        logger.info(f"💾 pyproject.toml saved: {self.pyproject_path}")

    def add_dependency(self, package: str, version: Optional[str] = None) -> None:
        """
        Add a dependency to pyproject.toml.

        Args:
            package: Package name (e.g., "pandas")
            version: Version constraint (e.g., ">=2.0.0", None for latest)

        Example:
            dm.add_dependency("pandas", ">=2.0.0")
            dm.add_dependency("requests")  # No version constraint
        """
        # Format dependency string
        if version:
            dep_string = f"{package}{version}"
        else:
            dep_string = package

        # Get current dependencies
        deps = self.document["project"]["dependencies"]

        # Check if package already exists (case-insensitive check)
        package_lower = package.lower()
        existing_index = None

        for i, dep in enumerate(deps):
            # Extract package name from dep string (handle >=, ==, ~=, etc.)
            dep_name = (
                dep.split(">=")[0]
                .split("==")[0]
                .split("~=")[0]
                .split("<")[0]
                .split(">")[0]
                .strip()
            )
            if dep_name.lower() == package_lower:
                existing_index = i
                break

        if existing_index is not None:
            # Update existing dependency
            old_dep = deps[existing_index]
            deps[existing_index] = dep_string
            logger.info(f"📦 Updated dependency: {old_dep} → {dep_string}")
        else:
            # Add new dependency
            deps.append(dep_string)
            logger.info(f"📦 Added dependency: {dep_string}")

        self._save()

    def remove_dependency(self, package: str) -> bool:
        """
        Remove a dependency from pyproject.toml.

        Args:
            package: Package name to remove

        Returns:
            True if removed, False if not found
        """
        deps = self.document["project"]["dependencies"]
        package_lower = package.lower()

        for i, dep in enumerate(deps):
            dep_name = (
                dep.split(">=")[0]
                .split("==")[0]
                .split("~=")[0]
                .split("<")[0]
                .split(">")[0]
                .strip()
            )
            if dep_name.lower() == package_lower:
                removed_dep = deps.pop(i)
                logger.info(f"📦 Removed dependency: {removed_dep}")
                self._save()
                return True

        logger.warning(f"📦 Dependency not found: {package}")
        return False

    def get_dependencies(self) -> List[str]:
        """
        Get all dependencies from pyproject.toml.

        Returns:
            List of dependency strings (e.g., ["pandas>=2.0.0", "requests"])
        """
        return list(self.document["project"]["dependencies"])

    def get_dependency_dict(self) -> Dict[str, Optional[str]]:
        """
        Get dependencies as a dictionary.

        Returns:
            Dict mapping package names to version constraints
            Example: {"pandas": ">=2.0.0", "requests": None}
        """
        result = {}

        for dep in self.get_dependencies():
            # Parse dependency string
            if ">=" in dep:
                package, version = dep.split(">=", 1)
                result[package.strip()] = f">={version.strip()}"
            elif "==" in dep:
                package, version = dep.split("==", 1)
                result[package.strip()] = f"=={version.strip()}"
            elif "~=" in dep:
                package, version = dep.split("~=", 1)
                result[package.strip()] = f"~={version.strip()}"
            elif "<" in dep:
                package, version = dep.split("<", 1)
                result[package.strip()] = f"<{version.strip()}"
            elif ">" in dep:
                package, version = dep.split(">", 1)
                result[package.strip()] = f">{version.strip()}"
            else:
                # No version constraint
                result[dep.strip()] = None

        return result

    def has_dependency(self, package: str) -> bool:
        """
        Check if a dependency exists.

        Args:
            package: Package name to check

        Returns:
            True if dependency exists
        """
        package_lower = package.lower()
        deps = self.get_dependencies()

        for dep in deps:
            dep_name = (
                dep.split(">=")[0]
                .split("==")[0]
                .split("~=")[0]
                .split("<")[0]
                .split(">")[0]
                .strip()
            )
            if dep_name.lower() == package_lower:
                return True

        return False

    def get_version_constraint(self, package: str) -> Optional[str]:
        """
        Get version constraint for a specific package.

        Args:
            package: Package name

        Returns:
            Version constraint (e.g., ">=2.0.0") or None if not found
        """
        dep_dict = self.get_dependency_dict()

        for pkg, version in dep_dict.items():
            if pkg.lower() == package.lower():
                return version

        return None
