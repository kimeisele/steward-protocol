#!/usr/bin/env python3
"""
GAD-000 Health Check: Pre-flight validation for HERALD system.

This script validates that all required dependencies are installed
and returns machine-readable JSON output for automated operators.

Used in: GitHub Actions (health-check job before main workflow)
Output: JSON status report with missing modules (if any)
Exit Code: 0 (healthy) or 1 (critical)
"""

import sys
import json
import importlib.util


def check_module(import_name):
    """Check if a Python module is available."""
    return importlib.util.find_spec(import_name) is not None


def main():
    """Perform dependency health check and report status."""

    # Mapping: pip package name -> Python import name
    dependencies = {
        "PyYAML": "yaml",
        "openai": "openai",
        "tweepy": "tweepy",
        "tavily-python": "tavily",
        "gitpython": "git",
        "python-dotenv": "dotenv",
    }

    report = {
        "system": "HERALD",
        "status": "healthy",
        "dependencies": "ok",
        "missing_modules": [],
        "checked_at": "pre-flight"
    }

    # Check each dependency
    for pip_name, import_name in dependencies.items():
        if not check_module(import_name):
            report["missing_modules"].append(pip_name)
            report["status"] = "critical"
            report["dependencies"] = "missing"

    # Machine-readable JSON output
    print(json.dumps(report, indent=2))

    # GAD-000: Clear exit code for orchestration
    if report["status"] == "critical":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
