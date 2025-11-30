#!/usr/bin/env python3
"""
Security Scan - CI/CD Script

Simple grep-based secret detection scan.
Extracted from inline YAML for maintainability.
"""

import sys
import subprocess


def run_scan():
    print("🔒 Running Security Scan (Secrets Detection)...")
    # Simple grep based scan (Fail fast)
    # Exclude tests and dummy data
    patterns = [
        "api_key\\s*=\\s*['\"][^'\"]*['\"]",
        "password\\s*=\\s*['\"][^'\"]*['\"]",
        "private_key\\s*=\\s*['\"][^'\"]*['\"]",
    ]

    found_secrets = False
    for pattern in patterns:
        try:
            # Grep recursive, ignore case, show line number
            # Using subprocess to use grep power (linux environment in CI)
            cmd = f'grep -r -i -E "{pattern}" vibe_core steward scripts --include="*.py" || true'
            result = subprocess.check_output(cmd, shell=True, text=True)

            if result.strip():
                print(f"⚠️  POTENTIAL SECRET FOUND (Pattern: {pattern}):")
                print(result)
                found_secrets = True
        except Exception as e:
            print(f"Error executing grep: {e}")

    if found_secrets:
        print("❌ Secrets detected in codebase. Build failed.")
        return False

    print("✅ No hardcoded secrets found.")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_scan() else 1)
