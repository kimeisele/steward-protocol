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

import subprocess
import json
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run command and report failure with context."""
    print(f"🧪 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        print(f"STDERR:\n{result.stderr}")
        print(f"STDOUT:\n{result.stdout}")
        return False

    print(f"✅ {description}")
    return True


def test_health_check():
    """Test 1: Health Check (GAD-000)"""
    success = run_command(
        "python3 examples/herald/health_check.py",
        "Health Check: Verify all dependencies",
    )

    if success:
        # Parse and validate JSON output
        result = subprocess.run(
            "python3 examples/herald/health_check.py",
            shell=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)

        if report["status"] != "healthy":
            print(f"❌ Health check CRITICAL: {report['missing_modules']}")
            return False

        print(f"   Dependencies OK: {list(report.keys())}")

    return success


def test_generate_content():
    """Test 2: Generate Content (requires API keys)"""
    # Check if API keys exist
    if not Path(".env").exists():
        print("⚠️  Skipping generate_only.py - no .env file (needs API keys)")
        return True

    return run_command(
        "python3 examples/herald/generate_only.py", "Generate Content: Brain + Artist"
    )


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

    success = run_command(
        "python3 examples/herald/generate_dashboard.py > /tmp/dashboard_test.md",
        "Dashboard Generation: Extract content for approval gate",
    )

    if success:
        # Verify output is not empty
        with open("/tmp/dashboard_test.md") as f:
            output = f.read()
            if output.strip():
                print(f"   Dashboard output: {len(output)} chars")
            else:
                print("❌ Dashboard generated empty output")
                return False

    return success


def main():
    """Run all E2E tests."""
    print("\n" + "=" * 70)
    print("🦅 HERALD E2E TEST SUITE")
    print("=" * 70 + "\n")

    tests = [
        ("Health Check", test_health_check),
        ("Content Generation", test_generate_content),
        ("Dashboard Generation", test_dashboard_generation),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        print("-" * 70)
        results.append((name, test_func()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🟢 All tests PASSED - safe to commit!")
        return 0
    else:
        print("\n🔴 Some tests FAILED - fix before pushing!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
