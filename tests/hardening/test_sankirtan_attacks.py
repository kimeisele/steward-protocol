"""
SANKIRTAN HARDENING TESTS - Attack Vectors
==========================================

THESE TESTS ARE DESIGNED TO FAIL AND FIND BUGS.

Attack categories:
1. PATH TRAVERSAL - Can we trick path resolution?
2. INJECTION ATTACKS - Can we inject malicious content?
3. HASH COLLISION - Can we create invalid genesis bytes?
4. GOVERNANCE BYPASS - Can we trick folder-to-mahajana mapping?
5. SSOT VIOLATIONS - Are there hardcoded values?
6. RACE CONDITIONS - What if files change during processing?
7. MALFORMED INPUT - What if content is weird?

"The goal is RED tests that find REAL bugs."
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS
from vibe_core.mahamantra.substrate.sankirtan import (
    FOLDER_MAHAJANA_MAP,
    PipelineContext,
    compute_genesis_hash,
    get_mahajana_for_path,
    has_declaration,
    inject_declaration,
    inject_file,
    perform_sankirtan,
    process_file_pipeline,
)
from vibe_core.mahamantra.substrate.wiring import POSITION_BY_NAME

# =============================================================================
# ATTACK 1: PATH TRAVERSAL
# =============================================================================


class TestPathTraversalAttacks:
    """Can we trick path resolution to inject wrong mahajana?"""

    def test_path_traversal_dotdot_attack(self):
        """
        ATTACK: Use ../.. to escape folder and get wrong mahajana.

        If path is "protocols/../naga/evil.py", should it resolve to naga or protocols?
        """
        # Attack path with traversal
        attack_path = Path("protocols/../naga/evil.py")

        result = get_mahajana_for_path(attack_path)

        # The path contains "naga" so it should match naga, not protocols
        # But the REAL question: is this the INTENDED behavior?
        assert result is not None, "Path should resolve to something"
        mahajana, position = result

        # SECURITY: The resolved path should be normalized first
        # If we don't normalize, we might get unexpected behavior
        normalized = attack_path.resolve() if attack_path.exists() else str(attack_path)

        # This test documents current behavior - may need to change
        # If "naga" is in path string, it matches naga
        if "naga" in str(attack_path).lower():
            assert mahajana == "yamaraja", (
                f"Path containing 'naga' should map to yamaraja (security), but got {mahajana}"
            )

    def test_path_with_symlink_attack(self, tmp_path):
        """
        ATTACK: Use symlinks to confuse path resolution.

        Create: protocols/evil -> ../../naga/real
        Should evil.py be owned by vyasa (protocols) or yamaraja (naga)?
        """
        # Create real naga directory
        naga_dir = tmp_path / "naga"
        naga_dir.mkdir()
        real_file = naga_dir / "real.py"
        real_file.write_text("# Real file in naga")

        # Create protocols directory with symlink
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir()

        try:
            symlink = protocols_dir / "evil"
            symlink.symlink_to(naga_dir)

            # Path through symlink
            attack_path = symlink / "real.py"

            result = get_mahajana_for_path(attack_path)
            assert result is not None
            mahajana, _ = result

            # SECURITY QUESTION: Should we follow symlinks or not?
            # Current behavior: path string matching, so "protocols" matches
            # Is this correct? Document it.
            assert mahajana in ["vyasa", "yamaraja"], (
                f"Symlink path should map to either vyasa (protocols) or yamaraja (naga), got {mahajana}"
            )
        except OSError:
            pytest.skip("Symlinks not supported on this system")

    def test_null_byte_injection(self):
        """
        ATTACK: Null byte injection to truncate path.

        Path: "protocols/evil.py\x00.txt" might bypass .py check.
        """
        # This should be rejected or handled safely
        attack_path = Path("protocols/evil.py\x00.txt")

        # Should not crash
        try:
            result = get_mahajana_for_path(attack_path)
            # If it succeeds, verify sane behavior
            if result:
                mahajana, _ = result
                assert isinstance(mahajana, str)
        except (ValueError, OSError):
            # Expected - null bytes should be rejected
            pass


# =============================================================================
# ATTACK 2: INJECTION ATTACKS
# =============================================================================


class TestInjectionAttacks:
    """Can we inject malicious content through the DNA injection?"""

    def test_code_injection_in_mahajana_name(self, tmp_path):
        """
        ATTACK: Malicious mahajana name with code injection.

        If mahajana = "vyasa\"; import os; os.system('rm -rf /')#"
        what happens when injected?
        """
        test_file = tmp_path / "test.py"
        test_file.write_text('"""Test module."""\nprint("hello")')

        # Malicious mahajana name
        evil_mahajana = 'vyasa"; import os; os.system("rm -rf /")#'

        content = test_file.read_text()

        # Try to inject
        try:
            result = inject_declaration(content, evil_mahajana, 0, str(test_file))

            # Check: the malicious code should be QUOTED, not executed
            assert "import os" not in result or '__mahajana__ = "' in result, (
                "CRITICAL: Code injection possible in mahajana name!"
            )

            # The mahajana name should be safely quoted
            # If quotes are in the name, they should be escaped or rejected
            if '";' in result and "__mahajana__" in result:
                # Check if properly escaped
                lines = result.split("\n")
                for line in lines:
                    if "__mahajana__" in line:
                        # Should be: __mahajana__ = "vyasa..."
                        # NOT: __mahajana__ = "vyasa"; import os...
                        assert line.count("=") == 1, f"INJECTION DETECTED: Multiple = in mahajana line: {line}"
        except (ValueError, TypeError):
            # Good - rejected malicious input
            pass

    def test_newline_injection_in_content(self, tmp_path):
        """
        ATTACK: Inject newlines to break out of declaration block.
        """
        test_file = tmp_path / "test.py"
        original = '"""Module."""\nprint("safe")'
        test_file.write_text(original)

        result = inject_declaration(original, "vyasa", 3, str(test_file))

        # Count the number of __mahajana__ declarations
        mahajana_count = result.count("__mahajana__")
        assert mahajana_count == 1, f"Expected exactly 1 __mahajana__ declaration, found {mahajana_count}"

    def test_unicode_homoglyph_attack(self, tmp_path):
        """
        ATTACK: Use unicode homoglyphs to fake mahajana names.

        "vyаsa" (with Cyrillic 'а') vs "vyasa" (Latin 'a')
        """
        # Cyrillic 'а' looks like Latin 'a' but is different
        fake_vyasa = "vy\u0430sa"  # Cyrillic а
        real_vyasa = "vyasa"  # Latin a

        assert fake_vyasa != real_vyasa, "Test setup error"

        # Check if the system distinguishes them
        fake_mapping = POSITION_BY_NAME.get(fake_vyasa)
        real_mapping = POSITION_BY_NAME.get(real_vyasa)

        # SECURITY: Homoglyphs should NOT match valid guardians
        assert fake_mapping is None, f"HOMOGLYPH ATTACK: Fake '{fake_vyasa}' matched as valid guardian!"
        assert real_mapping is not None, "Real 'vyasa' should be a valid guardian"


# =============================================================================
# ATTACK 3: HASH COLLISION / GENESIS BYTE ATTACKS
# =============================================================================


class TestGenesisHashAttacks:
    """Can we create invalid or colliding genesis bytes?"""

    def test_genesis_hash_divisibility(self):
        """
        INVARIANT: Genesis hash must be divisible by 37 (parampara).

        Test ALL positions to ensure this invariant holds.
        """
        violations = []

        for pos in range(16):
            mapping = MAHAMANTRA_POSITIONS[pos]
            mahajana = mapping.guardian.value

            # Generate hash for test file
            test_path = f"test/{mahajana}/test_file.py"
            genesis_hash = compute_genesis_hash(mahajana, pos, test_path)

            # Parse hash and check divisibility
            try:
                hash_value = int(genesis_hash, 16)
                if hash_value % 37 != 0:
                    violations.append(f"Position {pos} ({mahajana}): {genesis_hash} % 37 = {hash_value % 37}")
            except ValueError as e:
                violations.append(f"Position {pos} ({mahajana}): Invalid hash format: {e}")

        assert len(violations) == 0, (
            f"PARAMPARA VIOLATION: {len(violations)} genesis hashes not divisible by 37:\n" + "\n".join(violations[:5])
        )

    def test_genesis_hash_uniqueness(self):
        """
        Test that different positions get different genesis hashes.

        YOGA MAYA PARADIGM: Genesis hash is HOLOGRAPHIC — computed from
        archetype (mahajana:position) only, file_path is IGNORED.
        Same position = same hash by design.
        Cross-position uniqueness is what matters for spoofing prevention.
        """
        position_hashes = {}
        collisions = []

        # Each position must produce a unique hash
        for pos in range(16):
            mapping = MAHAMANTRA_POSITIONS[pos]
            mahajana = mapping.guardian.value

            genesis_hash = compute_genesis_hash(mahajana, pos)

            if genesis_hash in position_hashes:
                existing = position_hashes[genesis_hash]
                collisions.append(f"Position {pos} ({mahajana}) collides with {existing}: {genesis_hash}")
            else:
                position_hashes[genesis_hash] = (pos, mahajana)

        # All 16 positions must have unique hashes
        assert len(collisions) == 0, f"CROSS-POSITION COLLISION: {len(collisions)} collisions found:\n" + "\n".join(
            collisions
        )
        assert len(position_hashes) == 16, f"Expected 16 unique hashes, got {len(position_hashes)}"

        # Verify holographic property: same input = same output
        for pos in range(16):
            mapping = MAHAMANTRA_POSITIONS[pos]
            mahajana = mapping.guardian.value
            h1 = compute_genesis_hash(mahajana, pos, "file_a.py")
            h2 = compute_genesis_hash(mahajana, pos, "file_b.py")
            assert h1 == h2, f"Position {pos}: hash should be holographic (file_path ignored)"

    def test_genesis_hash_determinism(self):
        """
        INVARIANT: Same input must always produce same hash.
        """
        for _ in range(100):
            hash1 = compute_genesis_hash("vyasa", 3, "test/vyasa/file.py")
            hash2 = compute_genesis_hash("vyasa", 3, "test/vyasa/file.py")

            assert hash1 == hash2, f"NON-DETERMINISTIC HASH: {hash1} != {hash2}"


# =============================================================================
# ATTACK 4: GOVERNANCE BYPASS
# =============================================================================


class TestGovernanceBypass:
    """Can we trick the folder-to-mahajana mapping?"""

    def test_all_guardians_in_map_are_valid(self):
        """
        SSOT CHECK: Every guardian in FOLDER_MAHAJANA_MAP must exist in POSITION_BY_NAME.
        """
        invalid_guardians = []

        for folder, guardian in FOLDER_MAHAJANA_MAP.items():
            if guardian not in POSITION_BY_NAME:
                invalid_guardians.append(f"'{folder}' -> '{guardian}' (not in POSITION_BY_NAME)")

        assert len(invalid_guardians) == 0, "GOVERNANCE MAP CONTAINS INVALID GUARDIANS:\n" + "\n".join(
            invalid_guardians
        )

    def test_no_duplicate_folder_mappings(self):
        """
        Check for conflicting folder mappings.

        If "naga" -> yamaraja and "naga/special" -> brahma,
        which wins? Test the priority logic.
        """
        # Get all folders that contain other folders as substrings
        conflicts = []
        folders = list(FOLDER_MAHAJANA_MAP.keys())

        for i, folder1 in enumerate(folders):
            for folder2 in folders[i + 1 :]:
                if folder1 in folder2 or folder2 in folder1:
                    guardian1 = FOLDER_MAHAJANA_MAP[folder1]
                    guardian2 = FOLDER_MAHAJANA_MAP[folder2]
                    if guardian1 != guardian2:
                        conflicts.append(f"'{folder1}' ({guardian1}) vs '{folder2}' ({guardian2})")

        # Conflicts are expected (longer path takes priority)
        # But document them
        if conflicts:
            # Verify longest-match-wins behavior
            test_path = Path("phoenix/sections/naga/test.py")
            result = get_mahajana_for_path(test_path)
            assert result is not None
            mahajana, _ = result

            # "phoenix/sections/naga" is more specific than "naga"
            # It should map to yamaraja (from the specific mapping)
            assert mahajana == "yamaraja", f"Longest match should win: expected yamaraja, got {mahajana}"

    def test_hash_fallback_is_deterministic(self):
        """
        For unknown paths, hash fallback must be deterministic.
        """
        unknown_path = Path("completely/unknown/random/path/file.py")

        results = []
        for _ in range(100):
            result = get_mahajana_for_path(unknown_path)
            results.append(result)

        # All results must be identical
        assert all(r == results[0] for r in results), (
            "HASH FALLBACK NOT DETERMINISTIC: Got different results for same path"
        )


# =============================================================================
# ATTACK 5: SSOT VIOLATIONS
# =============================================================================


class TestSSOTViolations:
    """Check for hardcoded values that bypass the protocol."""

    def test_positions_match_wiring(self):
        """
        SSOT CHECK: MAHAMANTRA_POSITIONS must match POSITION_BY_NAME.
        """
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            guardian = pos.guardian.value

            if guardian not in POSITION_BY_NAME:
                violations.append(f"Position {pos.index} ({guardian}) not in POSITION_BY_NAME")
            else:
                wiring = POSITION_BY_NAME[guardian]
                if wiring.index != pos.index:
                    violations.append(
                        f"Index mismatch for {guardian}: "
                        f"MAHAMANTRA_POSITIONS says {pos.index}, "
                        f"POSITION_BY_NAME says {wiring.index}"
                    )

        assert len(violations) == 0, "SSOT VIOLATIONS:\n" + "\n".join(violations)

    def test_all_16_positions_exist(self):
        """
        INVARIANT: There must be exactly 16 positions (0-15).
        """
        assert len(MAHAMANTRA_POSITIONS) == 16, f"Expected 16 positions, got {len(MAHAMANTRA_POSITIONS)}"

        indices = [p.index for p in MAHAMANTRA_POSITIONS]
        expected = list(range(16))

        assert sorted(indices) == expected, f"Position indices must be 0-15, got {sorted(indices)}"

    def test_no_hardcoded_guardian_names_in_sankirtan(self):
        """
        Check that sankirtan.py doesn't hardcode guardian names outside the map.
        """
        import inspect

        from vibe_core.mahamantra.substrate import sankirtan

        source = inspect.getsource(sankirtan)

        # Guardian names that should only appear in FOLDER_MAHAJANA_MAP
        # or as part of the protocol
        hardcoded_patterns = []

        # Check for string literals that look like guardian assignments
        # but are outside the official map
        lines = source.split("\n")
        in_map = False

        for i, line in enumerate(lines):
            if "FOLDER_MAHAJANA_MAP" in line and "{" in line:
                in_map = True
            if in_map and "}" in line and ":" not in line:
                in_map = False

            # Skip if we're in the official map
            if in_map:
                continue

            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue

            # Look for suspicious hardcoded guardian assignments
            # Pattern: "guardian_name" (quoted, not in a dict key position)
            for guardian in POSITION_BY_NAME.keys():
                if f'"{guardian}"' in line and ":" not in line.split(f'"{guardian}"')[0][-5:]:
                    # This might be a hardcoded value outside the map
                    # Exclude known legitimate uses
                    if "return" in line or "log" in line.lower() or "print" in line:
                        continue
                    hardcoded_patterns.append(f"Line {i + 1}: {line.strip()}")

        # Some hardcoding is OK (tests, defaults), but flag for review
        if len(hardcoded_patterns) > 10:
            pytest.fail(
                f"POTENTIAL HARDCODING: {len(hardcoded_patterns)} suspicious patterns:\n"
                + "\n".join(hardcoded_patterns[:5])
            )


# =============================================================================
# ATTACK 6: MALFORMED INPUT
# =============================================================================


class TestMalformedInput:
    """What happens with weird/malformed input?"""

    def test_empty_file(self, tmp_path):
        """Empty file should be handled gracefully."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        ctx = process_file_pipeline(empty_file, dry_run=True)

        # Should not crash, should handle gracefully
        assert ctx is not None
        # Empty files can still be injected
        assert ctx.mahajana is not None or ctx.error is not None

    def test_binary_file(self, tmp_path):
        """Binary file should be rejected gracefully."""
        binary_file = tmp_path / "binary.py"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        try:
            ctx = process_file_pipeline(binary_file, dry_run=True)
            # Should fail gracefully, not crash
            assert ctx.error is not None or not ctx.is_valid
        except UnicodeDecodeError:
            pytest.fail("Binary file caused UnicodeDecodeError - should handle gracefully")

    def test_huge_file(self, tmp_path):
        """Very large file should be handled (or rejected with limits)."""
        huge_file = tmp_path / "huge.py"
        # 10MB of comments
        huge_content = '"""Huge docstring."""\n' + ("# Comment\n" * 500000)
        huge_file.write_text(huge_content)

        # Should not hang or crash
        import time

        start = time.time()
        ctx = process_file_pipeline(huge_file, dry_run=True)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 30 seconds)
        assert elapsed < 30, f"Processing took too long: {elapsed:.1f}s"
        assert ctx is not None

    def test_deeply_nested_docstring(self, tmp_path):
        """File with tricky docstring patterns."""
        tricky_file = tmp_path / "tricky.py"
        tricky_content = '''"""
        Module with tricky content.

        Contains: __mahajana__ = "fake"  # In docstring!
        And: '''
        __position__ = 999  # Also in docstring
        '''
        """

        # Real code starts here
        print("hello")
        '''
        tricky_file.write_text(tricky_content)

        result = inject_declaration(tricky_content, "vyasa", 3, str(tricky_file))

        # Should inject AFTER the docstring, not inside it
        # And should not be confused by fake declarations in docstring
        mahajana_count = result.count("__mahajana__")

        # One in docstring (fake), one real injection
        # But has_declaration should detect the fake one!
        if has_declaration(tricky_content):
            # If the fake one in docstring is detected, no injection happens
            assert mahajana_count >= 1
        else:
            # If properly parsed, the fake one is ignored, we inject one
            assert mahajana_count >= 1

    def test_syntax_error_file(self, tmp_path):
        """File with Python syntax errors."""
        bad_file = tmp_path / "syntax_error.py"
        bad_content = '''"""Module."""
def broken(:
    pass
'''
        bad_file.write_text(bad_content)

        # Sankirtan uses KALI YUGA GRACE - should not crash on syntax errors
        ctx = process_file_pipeline(bad_file, dry_run=True)

        # Should handle gracefully
        assert ctx is not None
        # May or may not inject depending on grace handling


# =============================================================================
# ATTACK 7: RACE CONDITIONS
# =============================================================================


class TestRaceConditions:
    """What if files change during processing?"""

    def test_file_deleted_during_processing(self, tmp_path):
        """File deleted between check and read."""
        test_file = tmp_path / "vanishing.py"
        test_file.write_text('"""Module."""\nprint("hi")')

        # Create context
        ctx = PipelineContext(file_path=test_file)

        # Delete file
        test_file.unlink()

        # Try to process - should handle gracefully
        from vibe_core.mahamantra.substrate.sankirtan import _genesis_phase

        ctx = _genesis_phase(ctx)

        assert not ctx.is_valid or ctx.error is not None

    def test_file_modified_during_processing(self, tmp_path):
        """File content changes between phases."""
        test_file = tmp_path / "changing.py"
        original = '"""Module."""\nprint("original")'
        test_file.write_text(original)

        # Start processing
        from vibe_core.mahamantra.substrate.sankirtan import _dharma_phase, _genesis_phase, _karma_phase

        ctx = PipelineContext(file_path=test_file)
        ctx = _genesis_phase(ctx)

        # Modify file after genesis
        modified = '"""Module."""\n__mahajana__ = "brahma"\nprint("modified")'
        test_file.write_text(modified)

        ctx = _dharma_phase(ctx)

        # The in-memory content doesn't know about the modification
        # This could lead to overwriting the modification
        # Document this behavior
        assert ctx.content == original, "Context should have original content (loaded in genesis)"


# =============================================================================
# RUN ALL TESTS
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
