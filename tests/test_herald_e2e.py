#!/usr/bin/env python3
"""
End-to-End Test: HERALD Generation Pipeline

Simulates the exact workflow that GitHub Actions runs:
1. Health Check (verify all dependencies)
2. Generate Content (brain + artist)
3. Generate Dashboard
4. Verify artifacts

This catches silent failures BEFORE pushing to GitHub Actions.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run_command(cmd, description):
    """Run command and return (success, result)."""
    print(f"🧪 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        print(f"STDERR:\n{result.stderr}")
        print(f"STDOUT:\n{result.stdout}")
        return False, result

    print(f"✅ {description}")
    return True, result


def test_health_check():
    """Test 1: Health Check (GAD-000)"""
    success, result = _run_command(
        "python3 examples/herald/health_check.py",
        "Health Check: Verify all dependencies",
    )
    assert success, f"Health check command failed: {result.stderr}"

    # Parse and validate JSON output
    result = subprocess.run(
        "python3 examples/herald/health_check.py",
        shell=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)

    assert report["status"] == "healthy", f"Health check CRITICAL: {report.get('missing_modules', 'unknown')}"
    print(f"   Dependencies OK: {list(report.keys())}")


def test_generate_content():
    """Test 2: Generate Content (requires API keys)"""
    # Check if API keys exist
    if not Path(".env").exists():
        pytest.skip("Skipping generate_only.py - no .env file (needs API keys)")

    success, result = _run_command("python3 examples/herald/generate_only.py", "Generate Content: Brain + Artist")
    assert success, f"Content generation failed: {result.stderr}"


def test_dashboard_generation():
    """Test 3: Dashboard generation (mock data if needed)"""
    # Create mock content.json if it doesn't exist
    dist_dir = Path("dist")
    content_file = dist_dir / "content.json"

    if not content_file.exists():
        print("⚠️  No dist/content.json - creating mock for dashboard test...")
        dist_dir.mkdir(exist_ok=True)
        mock_content = {
            "text": "Test tweet from HERALD pipeline",
            "image_filename": None,
        }
        with open(content_file, "w") as f:
            json.dump(mock_content, f)

    success, result = _run_command(
        "python3 examples/herald/generate_dashboard.py > /tmp/dashboard_test.md",
        "Dashboard Generation: Extract content for approval gate",
    )
    assert success, f"Dashboard generation failed: {result.stderr}"

    # Verify output is not empty
    with open("/tmp/dashboard_test.md") as f:
        output = f.read()
    assert output.strip(), "Dashboard generated empty output"
    print(f"   Dashboard output: {len(output)} chars")


def main():
    """Run all E2E tests (for standalone execution)."""
    print("\n" + "=" * 70)
    print("🦅 HERALD E2E TEST SUITE")
    print("=" * 70 + "\n")

    # When run directly, use pytest
    sys.exit(pytest.main([__file__, "-v"]))


if __name__ == "__main__":
    main()
