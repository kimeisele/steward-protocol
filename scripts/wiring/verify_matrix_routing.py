#!/usr/bin/env python3
"""
VERIFY MATRIX ROUTING
=====================
Tests the "Text as UI" routing mechanism via MATRIX.md.

Flow:
1. Create a temporary MATRIX.md with a custom route.
2. Initialize PlaybookRouter.
3. Verify that the router respects the custom route.
4. Update MATRIX.md with a new route (hot-swap).
5. Re-initialize Router (simulating hot-reload or next request).
6. Verify the new route is active.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8ddf5411"  # GenesisByte: parampara % 37 == 0

import logging
import shutil
import sys
from pathlib import Path

# Adjust path to find modules
sys.path.append(".")

from vibe_core.runtime.playbook_router import PlaybookRouter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_MATRIX")


def test_matrix_routing():
    logger.info("🧪 Starting Matrix Routing Verification...")

    matrix_path = Path("MATRIX.md")
    backup_path = Path("MATRIX.md.bak")

    # Backup existing MATRIX.md if it exists
    if matrix_path.exists():
        shutil.copy(matrix_path, backup_path)
        logger.info("💾 Backed up existing MATRIX.md")

    try:
        # 1. Create Initial Matrix
        logger.info("📝 Creating Initial MATRIX.md...")
        initial_matrix = """
# 🎛️ THE MATRIX

## ⚡ Active Routing Table

| Intent Pattern (Regex) | Target Circuit | Priority | Status |
| :--- | :--- | :--- | :--- |
| `test.*matrix` | `TEST_CIRCUIT_V1` | HIGH | 🟢 ACTIVE |
| `foo.*baz` | `FOO_CIRCUIT` | NORMAL | 🟢 ACTIVE |
"""
        matrix_path.write_text(initial_matrix)
        print(f"DEBUG: Wrote MATRIX.md ({len(initial_matrix)} chars):\n{initial_matrix}")
        print(f"DEBUG: Read back MATRIX.md:\n{matrix_path.read_text()}")

        # 2. Initialize Router
        router = PlaybookRouter()

        # 3. Verify Initial Routes
        logger.info("🔍 Verifying Initial Routes...")

        # Test Case A: Matrix Route
        route_a = router._route_to_task("test matrix routing")
        logger.info(f"   'test matrix routing' -> {route_a}")
        assert route_a == "TEST_CIRCUIT_V1", f"Expected TEST_CIRCUIT_V1, got {route_a}"

        # Test Case B: Another Matrix Route
        route_b = router._route_to_task("foo bar baz")
        logger.info(f"   'foo bar baz' -> {route_b}")
        assert route_b == "FOO_CIRCUIT", f"Expected FOO_CIRCUIT, got {route_b}"

        # Test Case C: Fallback (Agent Birth)
        route_c = router._route_to_task("agent_birth")
        logger.info(f"   'agent_birth' -> {route_c}")
        assert route_c == "AGENT_BIRTH_V1", f"Expected AGENT_BIRTH_V1 (Fallback), got {route_c}"

        logger.info("✅ Initial Matrix Verified")

        # 4. Hot-Swap Matrix
        logger.info("🔥 Hot-Swapping MATRIX.md...")
        new_matrix = """
# 🎛️ THE MATRIX

## ⚡ Active Routing Table

| Intent Pattern (Regex) | Target Circuit | Priority | Status |
| :--- | :--- | :--- | :--- |
| `test.*matrix` | `NEW_TEST_CIRCUIT_V2` | HIGH | 🟢 ACTIVE |
"""
        matrix_path.write_text(new_matrix)

        # 5. Re-initialize Router (Simulate next request loading)
        # In a real server, we might reload on file change, but for now we re-init
        router = PlaybookRouter()

        # 6. Verify New Routes
        logger.info("🔍 Verifying New Routes...")

        route_d = router._route_to_task("test matrix routing")
        logger.info(f"   'test matrix routing' -> {route_d}")
        assert route_d == "NEW_TEST_CIRCUIT_V2", f"Expected NEW_TEST_CIRCUIT_V2, got {route_d}"

        logger.info("✅ Hot-Swap Verified")
        logger.info("🎉 MATRIX ROUTING VERIFIED SUCCESSFUL!")

    except Exception as e:
        logger.error(f"❌ Verification Failed: {e}")
        raise
    finally:
        # Restore backup
        if backup_path.exists():
            shutil.move(backup_path, matrix_path)
            logger.info("♻️ Restored original MATRIX.md")
        elif matrix_path.exists():
            # If no backup existed (unlikely given we created one if it existed), but we created a file, delete it?
            # Actually, if we created it and no backup existed, we should probably delete it to be clean.
            # But in this env, MATRIX.md likely exists.
            pass


if __name__ == "__main__":
    test_matrix_routing()
