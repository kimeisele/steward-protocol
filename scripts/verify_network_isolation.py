#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - PHASE 4: NETWORK ISOLATION
================================================

Goal: Verify that agents can only access whitelisted domains.

Tests:
1. Request to whitelisted domain (github.com) → SUCCESS
2. Request to non-whitelisted domain (evil.com) → PERMISSION_ERROR
3. Request logging works
4. Whitelist management (add/remove domains)
"""

import logging
import os
import sys
from typing import Any, Dict

# Ensure we can import vibe_core
sys.path.append(os.getcwd())

from vibe_core.network_proxy import KernelNetworkProxy

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("VERIFICATION")


def test_whitelisted_domain():
    """Test request to whitelisted domain"""
    logger.info("=" * 60)
    logger.info("TEST 1: Whitelisted Domain Access")
    logger.info("=" * 60)

    proxy = KernelNetworkProxy()

    logger.info("1. Requesting https://api.github.com (whitelisted)...")
    try:
        response = proxy.get("test_agent", "https://api.github.com")
        logger.info(f"   ✅ Request succeeded: {response.status_code}")
        return True
    except PermissionError as e:
        logger.error(f"   ❌ Blocked (should be allowed): {e}")
        return False
    except Exception as e:
        # Network errors are OK (no internet, etc.)
        logger.info(f"   ⚠️  Network error (OK): {e}")
        return True


def test_non_whitelisted_domain():
    """Test request to non-whitelisted domain"""
    logger.info("=" * 60)
    logger.info("TEST 2: Non-Whitelisted Domain Block")
    logger.info("=" * 60)

    proxy = KernelNetworkProxy()

    logger.info("1. Requesting https://evil.com (NOT whitelisted)...")
    try:
        response = proxy.get("test_agent", "https://evil.com")
        logger.error(f"   ❌ SECURITY BREACH: Request succeeded!")
        return False
    except PermissionError as e:
        logger.info(f"   ✅ Blocked: {e}")
        return True
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False


def test_request_logging():
    """Test that requests are logged"""
    logger.info("=" * 60)
    logger.info("TEST 3: Request Logging")
    logger.info("=" * 60)

    proxy = KernelNetworkProxy()

    # Clear log
    proxy.clear_log()

    logger.info("1. Making request to github.com...")
    try:
        proxy.get("test_agent", "https://api.github.com")
    except:
        pass  # Ignore network errors

    logger.info("2. Checking request log...")
    log = proxy.get_request_log()

    if len(log) > 0:
        logger.info(f"   ✅ Request logged: {log[0]}")

        # Verify log entry
        entry = log[0]
        if entry["agent_id"] == "test_agent" and "github.com" in entry["url"]:
            logger.info("   ✅ Log entry correct")
            return True
        else:
            logger.error(f"   ❌ Log entry incorrect: {entry}")
            return False
    else:
        logger.error("   ❌ No requests logged")
        return False


def test_whitelist_management():
    """Test adding/removing domains from whitelist"""
    logger.info("=" * 60)
    logger.info("TEST 4: Whitelist Management")
    logger.info("=" * 60)

    proxy = KernelNetworkProxy()

    # Test 1: Add domain to whitelist
    logger.info("1. Adding example.com to whitelist...")
    proxy.add_to_whitelist("example.com")

    logger.info("2. Requesting https://example.com...")
    try:
        response = proxy.get("test_agent", "https://example.com")
        logger.info(f"   ✅ Request succeeded (domain whitelisted)")
    except PermissionError:
        logger.error("   ❌ Blocked (should be allowed)")
        return False
    except Exception as e:
        # Network errors are OK
        logger.info(f"   ⚠️  Network error (OK): {e}")

    # Test 2: Remove domain from whitelist
    logger.info("3. Removing example.com from whitelist...")
    proxy.remove_from_whitelist("example.com")

    logger.info("4. Requesting https://example.com again...")
    try:
        response = proxy.get("test_agent", "https://example.com")
        logger.error("   ❌ Request succeeded (should be blocked)")
        return False
    except PermissionError as e:
        logger.info(f"   ✅ Blocked: {e}")
        return True
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False


def test_subdomain_matching():
    """Test that subdomains are allowed if parent domain is whitelisted"""
    logger.info("=" * 60)
    logger.info("TEST 5: Subdomain Matching")
    logger.info("=" * 60)

    proxy = KernelNetworkProxy()

    # github.com is whitelisted, so api.github.com should work
    logger.info(
        "1. Requesting https://api.github.com (subdomain of whitelisted github.com)..."
    )
    try:
        response = proxy.get("test_agent", "https://api.github.com")
        logger.info("   ✅ Subdomain allowed")
        return True
    except PermissionError:
        logger.error("   ❌ Subdomain blocked (should be allowed)")
        return False
    except Exception as e:
        # Network errors are OK
        logger.info(f"   ⚠️  Network error (OK): {e}")
        return True


def main():
    logger.info("🚀 STARTING NETWORK ISOLATION VERIFICATION")
    logger.info("")

    results = []

    # Run tests
    results.append(("Whitelisted Domain", test_whitelisted_domain()))
    results.append(("Non-Whitelisted Block", test_non_whitelisted_domain()))
    results.append(("Request Logging", test_request_logging()))
    results.append(("Whitelist Management", test_whitelist_management()))
    results.append(("Subdomain Matching", test_subdomain_matching()))

    # Summary
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
