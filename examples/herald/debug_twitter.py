#!/usr/bin/env python3
"""
HERALD Twitter API Diagnostic Tool
Performs critical health checks on Twitter API integration.

This is a "Fail Fast" script that catches configuration problems
BEFORE they cause silent failures in production.

Run before every twitter publish attempt to ensure:
1. API Key exists and is valid
2. Read access works (can authenticate)
3. Write access works (can post tweets)
"""

import os
import sys
import requests
from datetime import datetime


def check_key_presence():
    """Step 1: Check that TWITTER_API_KEY environment variable exists."""
    print("\n[1/4] 🔑 Checking API Key Presence...")

    token = os.getenv("TWITTER_API_KEY")
    if not token:
        print("    ❌ CRITICAL: TWITTER_API_KEY is missing from environment!")
        print("    💡 Set this in GitHub Secrets or .env file")
        return False

    if len(token) < 50:
        print(f"    ⚠️  WARNING: Token looks suspiciously short ({len(token)} chars)")
        print("    ℹ️  Twitter Bearer tokens are typically 100+ characters")

    print(f"    ✅ Key found ({len(token)} characters)")
    return True


def check_read_access(token):
    """Step 2: Test READ access using /users/me endpoint."""
    print("\n[2/4] 📖 Checking READ Access (authenticate)...")

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "HERALD-Diagnostic/1.0",
    }

    try:
        response = requests.get("https://api.twitter.com/2/users/me", headers=headers, timeout=10)

        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get("data", {}).get("username", "unknown")
            name = user_data.get("data", {}).get("name", "unknown")
            print(f"    ✅ READ Access Confirmed")
            print(f"    ℹ️  Authenticated as: {name} (@{username})")
            return True

        elif response.status_code == 401:
            print(f"    ❌ AUTHENTICATION FAILED: 401 Unauthorized")
            print(f"    💡 Your API Key is invalid or expired")
            print(f"    💡 Regenerate it in Twitter Developer Portal")
            return False

        elif response.status_code == 403:
            print(f"    ❌ ACCESS DENIED: 403 Forbidden")
            print(f"    💡 Your token has READ access but something is blocked")
            print(f"    ℹ️  Response: {response.text[:200]}")
            return False

        else:
            print(f"    ❌ UNEXPECTED ERROR: {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return False

    except requests.RequestException as e:
        print(f"    ❌ NETWORK ERROR: {e}")
        return False


def check_write_access(token):
    """Step 3: Test WRITE access by attempting a test tweet."""
    print("\n[3/4] ✏️  Checking WRITE Access (can post)...")
    print("    ℹ️  Attempting to post a test tweet...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "HERALD-Diagnostic/1.0",
    }

    # Test payload - a diagnostic tweet
    payload = {"text": f"🧪 HERALD Diagnostic Test - {datetime.now().isoformat()}\n\n#StewardProtocol #HERALD"}

    try:
        response = requests.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 201:
            tweet_data = response.json()
            tweet_id = tweet_data.get("data", {}).get("id", "unknown")
            print(f"    ✅ WRITE Access Confirmed - Test tweet posted!")
            print(f"    📍 Tweet ID: {tweet_id}")
            print(f"    🔗 https://twitter.com/i/web/status/{tweet_id}")
            return True

        elif response.status_code == 403:
            print(f"    ❌ WRITE ACCESS DENIED: 403 Forbidden")
            print(f"    🚨 THIS IS THE CLASSIC ISSUE:")
            print(f"    💡 Your app is set to 'READ ONLY'")
            print(f"    ")
            print(f"    📋 HOW TO FIX (Twitter Developer Portal):")
            print(f"       1. Go to: https://developer.twitter.com/en/portal/dashboard")
            print(f"       2. Select your Project & App")
            print(f"       3. Go to: Settings → User authentication settings")
            print(f"       4. Find: 'App permissions'")
            print(f"       5. Change: 'Read' → 'Read and Write'")
            print(f"       6. REGENERATE your Bearer Token")
            print(f"       7. Update GitHub Secrets with new token")
            print(f"    ")
            print(f"    Response: {response.text[:200]}")
            return False

        elif response.status_code == 401:
            print(f"    ❌ AUTHENTICATION FAILED: 401 Unauthorized")
            print(f"    💡 Token is expired or invalid")
            return False

        elif response.status_code == 429:
            print(f"    ⚠️  RATE LIMITED: 429 Too Many Requests")
            print(f"    💡 You're posting too fast. Slow down.")
            return False

        else:
            print(f"    ❌ UNEXPECTED ERROR: {response.status_code}")
            print(f"    Response: {response.text[:300]}")
            return False

    except requests.RequestException as e:
        print(f"    ❌ NETWORK ERROR: {e}")
        return False


def print_header():
    """Print diagnostic header."""
    print("\n" + "=" * 70)
    print("🕵️  HERALD TWITTER API DIAGNOSTIC")
    print("=" * 70)
    print("Running critical health checks on Twitter integration...")
    print(f"Time: {datetime.now().isoformat()}")


def print_summary(results):
    """Print final summary."""
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC RESULTS")
    print("=" * 70)

    checks = [
        ("Key Presence", results["key"]),
        ("Read Access", results["read"]),
        ("Write Access", results["write"]),
    ]

    all_pass = all(r for r in results.values())

    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")

    print("=" * 70)

    if all_pass:
        print("🚀 All checks passed! Twitter publishing is ready.")
        return 0
    else:
        print("❌ One or more checks failed. Fix issues above before publishing.")
        return 1


def main():
    """Run all diagnostic checks."""
    print_header()

    results = {
        "key": False,
        "read": False,
        "write": False,
    }

    # Check 1: Key presence
    if not check_key_presence():
        return print_summary(results)
    results["key"] = True

    token = os.getenv("TWITTER_API_KEY")

    # Check 2: Read access
    if not check_read_access(token):
        return print_summary(results)
    results["read"] = True

    # Check 3: Write access
    if not check_write_access(token):
        return print_summary(results)
    results["write"] = True

    return print_summary(results)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
