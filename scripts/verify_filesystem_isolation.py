#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - PHASE 4: FILESYSTEM ISOLATION
===================================================

Goal: Verify that agents cannot access files outside their sandbox.

Tests:
1. Agent reads file in its sandbox → SUCCESS
2. Agent tries to read /etc/passwd → PERMISSION_ERROR
3. Agent tries path traversal (../) → PERMISSION_ERROR
4. Agent writes file in sandbox → SUCCESS
5. Agent tries to write outside sandbox → PERMISSION_ERROR
"""

import logging
import os
import sys

# Ensure we can import vibe_core
sys.path.append(os.getcwd())

from vibe_core.vfs import VirtualFileSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("VERIFICATION")


def test_vfs_basic_operations():
    """Test basic VFS operations within sandbox"""
    logger.info("=" * 60)
    logger.info("TEST 1: Basic VFS Operations")
    logger.info("=" * 60)

    vfs = VirtualFileSystem("test_agent")

    # Test 1: Write file in sandbox
    logger.info("1. Writing file in sandbox...")
    try:
        vfs.write_text("test.txt", "Hello from sandbox!")
        logger.info("   ✅ Write succeeded")
    except Exception as e:
        logger.error(f"   ❌ Write failed: {e}")
        return False

    # Test 2: Read file from sandbox
    logger.info("2. Reading file from sandbox...")
    try:
        content = vfs.read_text("test.txt")
        if content == "Hello from sandbox!":
            logger.info("   ✅ Read succeeded, content matches")
        else:
            logger.error(f"   ❌ Content mismatch: {content}")
            return False
    except Exception as e:
        logger.error(f"   ❌ Read failed: {e}")
        return False

    # Test 3: List directory
    logger.info("3. Listing sandbox directory...")
    try:
        files = vfs.list_dir(".")
        if "test.txt" in files:
            logger.info(f"   ✅ Directory listing works: {files}")
        else:
            logger.error(f"   ❌ test.txt not found in {files}")
            return False
    except Exception as e:
        logger.error(f"   ❌ List failed: {e}")
        return False

    logger.info("✅ Basic operations PASSED\n")
    return True


def test_vfs_security():
    """Test VFS security - attempts to escape sandbox"""
    logger.info("=" * 60)
    logger.info("TEST 2: VFS Security (Escape Attempts)")
    logger.info("=" * 60)

    vfs = VirtualFileSystem("test_agent")

    # Test 1: Try to read /etc/passwd
    logger.info("1. Attempting to read /etc/passwd...")
    try:
        content = vfs.read_text("/etc/passwd")
        logger.error(f"   ❌ SECURITY BREACH: Read succeeded! {len(content)} bytes")
        return False
    except PermissionError as e:
        logger.info(f"   ✅ Blocked: {e}")
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False

    # Test 2: Path traversal attack
    logger.info("2. Attempting path traversal (../../../etc/passwd)...")
    try:
        content = vfs.read_text("../../../etc/passwd")
        logger.error("   ❌ SECURITY BREACH: Path traversal succeeded!")
        return False
    except PermissionError as e:
        logger.info(f"   ✅ Blocked: {e}")
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False

    # Test 3: Try to write outside sandbox
    logger.info("3. Attempting to write to /tmp/escape.txt...")
    try:
        vfs.write_text("/tmp/escape.txt", "Escaped!")
        logger.error("   ❌ SECURITY BREACH: Write outside sandbox succeeded!")
        return False
    except PermissionError as e:
        logger.info(f"   ✅ Blocked: {e}")
    except Exception as e:
        logger.error(f"   ❌ Unexpected error: {e}")
        return False

    # Test 4: Absolute path within sandbox (should work)
    logger.info("4. Using absolute path within sandbox...")
    try:
        sandbox_path = vfs.get_sandbox_path()
        abs_path = str(sandbox_path / "abs_test.txt")
        vfs.write_text(abs_path, "Absolute path test")
        content = vfs.read_text(abs_path)
        if content == "Absolute path test":
            logger.info("   ✅ Absolute path within sandbox works")
        else:
            logger.error("   ❌ Content mismatch")
            return False
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False

    logger.info("✅ Security tests PASSED\n")
    return True


def test_vfs_subdirectories():
    """Test VFS with subdirectories"""
    logger.info("=" * 60)
    logger.info("TEST 3: Subdirectories")
    logger.info("=" * 60)

    vfs = VirtualFileSystem("test_agent")

    # Test 1: Create subdirectory
    logger.info("1. Creating subdirectory...")
    try:
        vfs.mkdir("data/logs")
        logger.info("   ✅ Directory created")
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False

    # Test 2: Write file in subdirectory
    logger.info("2. Writing file in subdirectory...")
    try:
        vfs.write_text("data/logs/app.log", "Log entry 1\nLog entry 2")
        logger.info("   ✅ File written")
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False

    # Test 3: Read file from subdirectory
    logger.info("3. Reading file from subdirectory...")
    try:
        content = vfs.read_text("data/logs/app.log")
        if "Log entry 1" in content:
            logger.info("   ✅ File read successfully")
        else:
            logger.error("   ❌ Content mismatch")
            return False
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return False

    logger.info("✅ Subdirectory tests PASSED\n")
    return True


def main():
    logger.info("🚀 STARTING FILESYSTEM ISOLATION VERIFICATION")
    logger.info("")

    results = []

    # Run tests
    results.append(("Basic Operations", test_vfs_basic_operations()))
    results.append(("Security", test_vfs_security()))
    results.append(("Subdirectories", test_vfs_subdirectories()))

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
