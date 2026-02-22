"""
TEST SANKIRTAN VIRUS (The Genesis Logic)
========================================

Verifies the DNA Injection mechanism.
Ensures:
1. Genesis Byte is mathematically valid (mod 37).
2. Header injection respects Python syntax (e.g. __future__).
3. The "Virus" spreads correctly without corrupting files.
"""

import pytest
from vibe_core.mahamantra.substrate.sankirtan import compute_genesis_hash, inject_declaration, has_declaration


def test_genesis_math_integrity():
    """
    Verify the cryptographic seal.
    Invariant: int(genesis_byte, 16) % 37 == 0
    """
    # Test cases
    cases = [
        ("vyasa", 0, "test_file.py"),
        ("brahma", 1, "test_file.py"),
        ("yamaraja", 15, "test_file.py"),
        ("unknown", 99, "random_path.py"),
    ]

    for mahajana, position, path in cases:
        genesis_hex = compute_genesis_hash(mahajana, position, path)

        # Format check
        assert genesis_hex.startswith("0x")

        # Value check
        genesis_int = int(genesis_hex, 16)
        remainder = genesis_int % 37

        assert remainder == 0, f"Genesis Byte {genesis_hex} is ATHEIST! (Rem: {remainder})"


def test_injection_basic():
    """Verify standard injection into a normal file."""
    content = """
import os

def hello():
    print("world")
"""
    mahajana = "vyasa"
    position = 0

    # Inject
    new_content = inject_declaration(content, mahajana, position, "test.py")

    # Verify
    assert '__mahajana__ = "vyasa"' in new_content
    assert "__position__ = 0" in new_content
    assert '__genesis__ = "0x' in new_content

    # Should be placed at the top (after empty lines)
    lines = new_content.strip().split("\n")
    assert lines[0].startswith("# === MAHAJANA")


def test_injection_respects_future():
    """
    CRITICAL: Verify injection respects `from __future__`.
    Python requires future imports to be the very first code lines.
    """
    content = """\"\"\"
Module Docstring
\"\"\"
from __future__ import annotations
import sys

x = 1
"""
    # Inject
    new_content = inject_declaration(content, "brahma", 1, "future.py")

    # Logic verification
    lines = new_content.split("\n")

    # 1. Docstring should stay first
    assert "Module Docstring" in new_content

    # 2. Future import should trigger BEFORE the injection block?
    # Wait, looking at lines 479-481 in sankirtan.py:
    # "MUST skip from __future__ imports - Python requirement!"
    # insert_idx increases PAST the future import.

    # So order should be:
    # Docstring
    # from __future__ ...
    # [INJECTION BLOCK]
    # import sys

    # Let's find index of future and index of injection
    future_idx = -1
    injection_idx = -1

    for i, line in enumerate(lines):
        if "from __future__" in line:
            future_idx = i
        if "__mahajana__" in line:
            injection_idx = i

    assert future_idx != -1
    assert injection_idx != -1

    assert future_idx < injection_idx, "VIOLATION: Injection placed before future import!"


def test_idempotency_check():
    """Verify helper detects existing declarations."""
    clean = "import os"
    infected = """
__mahajana__ = "vyasa"
import os
"""
    assert has_declaration(clean) is False
    assert has_declaration(infected) is True
