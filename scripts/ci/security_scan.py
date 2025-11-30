#!/usr/bin/env python3
"""
Security Scan - CI/CD Script

Check for potential security issues:
- Hardcoded API keys
- Hardcoded passwords
- Other security anti-patterns

Extracted from inline YAML script for maintainability.
"""
import sys
import subprocess
from pathlib import Path


def scan_for_pattern(pattern, description):
    """Scan Python files for a security pattern"""
    print(f"\nScanning for {description}...")

    try:
        result = subprocess.run(
            [
                "grep",
                "-r",
                "-i",
                "-n",
                "-E",
                pattern,
                "--include=*.py",
                "vibe_core",
                "steward",
                "scripts"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            print(f"⚠️  Warning: {description} found:")
            print(result.stdout)
            return True
        else:
            print(f"✅ No {description} detected")
            return False

    except Exception as e:
        print(f"⚠️  Could not scan for {description}: {e}")
        return False


if __name__ == "__main__":
    print("🔒 Starting Security Scan...")
    print("="*70)

    warnings = []

    # Scan for hardcoded API keys
    if scan_for_pattern(r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded API keys"):
        warnings.append("Potential hardcoded API keys")

    # Scan for hardcoded passwords
    if scan_for_pattern(r'password\s*=\s*["\'][^"\']+["\']', "hardcoded passwords"):
        warnings.append("Potential hardcoded passwords")

    # Scan for hardcoded tokens
    if scan_for_pattern(r'token\s*=\s*["\'][^"\']+["\']', "hardcoded tokens"):
        warnings.append("Potential hardcoded tokens")

    print("\n" + "="*70)
    print("Security Scan Complete")
    print("="*70)

    if warnings:
        print(f"\n⚠️  Found {len(warnings)} potential security issue(s):")
        for warning in warnings:
            print(f"  - {warning}")
        print("\nNote: These are warnings, not failures.")
        print("Review the findings and ensure secrets use environment variables.")
    else:
        print("\n✅ No security issues detected")

    # Security scan never fails the build, only warns
    sys.exit(0)
