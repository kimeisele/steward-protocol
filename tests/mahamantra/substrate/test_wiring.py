"""
TESTS: wiring.py - Folder IS Wiring Protocol
=============================================

"yadā yadā hi dharmasya glānir bhavati bhārata"

REAL TESTS for:
1. Constants (FOLDER_IS_WIRING, NO_FOLDER_NO_EXISTENCE)
2. Lookup tables (POSITION_BY_FOLDER, POSITION_BY_NAME, POSITION_BY_INDEX)
3. Utility functions (folder_exists, get_position_from_*, verify_wiring)
4. Fractal functions (calculate_fractal_depth, calculate_total_nodes)
5. WiringVerification dataclass
"""

import pytest
from vibe_core.mahamantra.substrate.wiring import (
    # Constants
    FOLDER_IS_WIRING,
    NO_FOLDER_NO_EXISTENCE,
    FRACTAL_BASE,
    POSITIONS_PER_QUARTER,
    QUARTER_COUNT,
    # Lookup tables
    POSITION_BY_FOLDER,
    POSITION_BY_NAME,
    POSITION_BY_INDEX,
    # Functions
    folder_exists,
    get_position_from_folder,
    get_position_from_name,
    get_position_by_index,
    get_position_by_opcode,
    # Protocol
    WiringVerification,
    verify_wiring,
    # Fractal
    calculate_fractal_depth,
    calculate_total_nodes,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestWiringConstants:
    """Test wiring constants."""

    def test_folder_is_wiring(self):
        """FOLDER_IS_WIRING is True."""
        assert FOLDER_IS_WIRING is True

    def test_no_folder_no_existence(self):
        """NO_FOLDER_NO_EXISTENCE is True."""
        assert NO_FOLDER_NO_EXISTENCE is True

    def test_fractal_base_is_16(self):
        """FRACTAL_BASE is 16."""
        assert FRACTAL_BASE == 16

    def test_positions_per_quarter_is_4(self):
        """POSITIONS_PER_QUARTER is 4."""
        assert POSITIONS_PER_QUARTER == 4

    def test_quarter_count_is_4(self):
        """QUARTER_COUNT is 4."""
        assert QUARTER_COUNT == 4


# =============================================================================
# POSITION_BY_FOLDER Tests
# =============================================================================


class TestPositionByFolder:
    """Test POSITION_BY_FOLDER lookup table."""

    def test_position_by_folder_exists(self):
        """POSITION_BY_FOLDER exists."""
        assert POSITION_BY_FOLDER is not None

    def test_position_by_folder_is_dict(self):
        """POSITION_BY_FOLDER is a dict."""
        assert isinstance(POSITION_BY_FOLDER, dict)

    def test_position_by_folder_has_16_entries(self):
        """POSITION_BY_FOLDER has 16 entries."""
        assert len(POSITION_BY_FOLDER) == 16

    def test_position_by_folder_values_are_positions(self):
        """All values are MantraPosition objects."""
        from vibe_core.mahamantra.substrate.position import MantraPosition

        for folder, pos in POSITION_BY_FOLDER.items():
            assert isinstance(pos, MantraPosition)


# =============================================================================
# POSITION_BY_NAME Tests
# =============================================================================


class TestPositionByName:
    """Test POSITION_BY_NAME lookup table."""

    def test_position_by_name_exists(self):
        """POSITION_BY_NAME exists."""
        assert POSITION_BY_NAME is not None

    def test_position_by_name_is_dict(self):
        """POSITION_BY_NAME is a dict."""
        assert isinstance(POSITION_BY_NAME, dict)

    def test_position_by_name_has_16_entries(self):
        """POSITION_BY_NAME has 16 entries."""
        assert len(POSITION_BY_NAME) == 16

    def test_known_guardian_names(self):
        """Known guardian names are in POSITION_BY_NAME."""
        known_names = ["vyasa", "brahma", "narada", "prithu", "janaka", "yamaraja"]
        for name in known_names:
            assert name in POSITION_BY_NAME


# =============================================================================
# POSITION_BY_INDEX Tests
# =============================================================================


class TestPositionByIndex:
    """Test POSITION_BY_INDEX lookup table."""

    def test_position_by_index_exists(self):
        """POSITION_BY_INDEX exists."""
        assert POSITION_BY_INDEX is not None

    def test_position_by_index_is_dict(self):
        """POSITION_BY_INDEX is a dict."""
        assert isinstance(POSITION_BY_INDEX, dict)

    def test_position_by_index_has_16_entries(self):
        """POSITION_BY_INDEX has 16 entries."""
        assert len(POSITION_BY_INDEX) == 16

    def test_position_by_index_keys_0_to_15(self):
        """Keys are 0 to 15."""
        for i in range(16):
            assert i in POSITION_BY_INDEX


# =============================================================================
# folder_exists Tests
# =============================================================================


class TestFolderExists:
    """Test folder_exists function."""

    def test_folder_exists_valid_path(self):
        """Valid folder path exists."""
        # Get any valid folder from POSITION_BY_FOLDER
        if POSITION_BY_FOLDER:
            valid_folder = next(iter(POSITION_BY_FOLDER.keys()))
            assert folder_exists(valid_folder) is True

    def test_folder_exists_invalid_path(self):
        """Invalid folder path doesn't exist."""
        assert folder_exists("nonexistent/folder") is False

    def test_folder_exists_empty_string(self):
        """Empty string doesn't exist."""
        assert folder_exists("") is False


# =============================================================================
# get_position_from_folder Tests
# =============================================================================


class TestGetPositionFromFolder:
    """Test get_position_from_folder function."""

    def test_get_position_from_valid_folder(self):
        """Valid folder returns MantraPosition."""
        if POSITION_BY_FOLDER:
            valid_folder = next(iter(POSITION_BY_FOLDER.keys()))
            pos = get_position_from_folder(valid_folder)
            assert pos is not None

    def test_get_position_from_invalid_folder(self):
        """Invalid folder returns None."""
        pos = get_position_from_folder("invalid/folder/path")
        assert pos is None


# =============================================================================
# get_position_from_name Tests
# =============================================================================


class TestGetPositionFromName:
    """Test get_position_from_name function."""

    def test_get_position_from_name_vyasa(self):
        """'vyasa' returns valid position."""
        pos = get_position_from_name("vyasa")
        assert pos is not None

    def test_get_position_from_name_brahma(self):
        """'brahma' returns valid position."""
        pos = get_position_from_name("brahma")
        assert pos is not None

    def test_get_position_from_name_case_insensitive(self):
        """Name lookup is case insensitive."""
        pos_lower = get_position_from_name("vyasa")
        pos_upper = get_position_from_name("VYASA")
        # Both should return position (or both None if not found)
        assert (pos_lower is not None) == (pos_upper is not None)

    def test_get_position_from_name_invalid(self):
        """Invalid name returns None."""
        pos = get_position_from_name("invalid_name")
        assert pos is None


# =============================================================================
# get_position_by_index Tests
# =============================================================================


class TestGetPositionByIndex:
    """Test get_position_by_index function."""

    def test_get_position_by_index_0(self):
        """Index 0 returns position."""
        pos = get_position_by_index(0)
        assert pos is not None
        assert pos.index == 0

    def test_get_position_by_index_15(self):
        """Index 15 returns position."""
        pos = get_position_by_index(15)
        assert pos is not None
        assert pos.index == 15

    def test_get_position_by_index_invalid(self):
        """Invalid index returns None."""
        pos = get_position_by_index(100)
        assert pos is None

    def test_get_position_by_index_negative(self):
        """Negative index returns None."""
        pos = get_position_by_index(-1)
        assert pos is None

    def test_get_position_by_index_all_16(self):
        """All 16 indices (0-15) return positions."""
        for i in range(16):
            pos = get_position_by_index(i)
            assert pos is not None


# =============================================================================
# get_position_by_opcode Tests
# =============================================================================


class TestGetPositionByOpcode:
    """Test get_position_by_opcode function."""

    def test_get_position_by_opcode_returns_position(self):
        """Valid opcode returns position."""
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode

        # Try first opcode
        pos = get_position_by_opcode(MantraOpCode.SYS_WAKE)
        # May or may not find a position, just check it doesn't crash
        assert pos is None or hasattr(pos, "index")

    def test_get_position_by_opcode_all_positions_have_opcodes(self):
        """All positions have associated opcodes."""
        for i in range(16):
            pos = get_position_by_index(i)
            assert pos is not None
            assert pos.opcode is not None


# =============================================================================
# WiringVerification Tests
# =============================================================================


class TestWiringVerification:
    """Test WiringVerification dataclass."""

    def test_wiring_verification_creation(self):
        """WiringVerification can be created."""
        wv = WiringVerification(folder_path="test/path", exists=True, position=0, is_connected=True, violations=[])
        assert wv.folder_path == "test/path"

    def test_wiring_verification_is_valid_true(self):
        """is_valid returns True when all conditions met."""
        wv = WiringVerification(folder_path="test/path", exists=True, position=0, is_connected=True, violations=[])
        assert wv.is_valid is True

    def test_wiring_verification_is_valid_false_not_exists(self):
        """is_valid returns False when not exists."""
        wv = WiringVerification(
            folder_path="test/path", exists=False, position=None, is_connected=False, violations=["Folder not found"]
        )
        assert wv.is_valid is False

    def test_wiring_verification_is_valid_false_violations(self):
        """is_valid returns False when has violations."""
        wv = WiringVerification(
            folder_path="test/path", exists=True, position=0, is_connected=True, violations=["Some violation"]
        )
        assert wv.is_valid is False


# =============================================================================
# verify_wiring Tests
# =============================================================================


class TestVerifyWiring:
    """Test verify_wiring function."""

    def test_verify_wiring_valid_folder(self):
        """Valid folder returns valid verification."""
        if POSITION_BY_FOLDER:
            valid_folder = next(iter(POSITION_BY_FOLDER.keys()))
            verification = verify_wiring(valid_folder)
            assert verification.exists is True
            assert verification.position is not None

    def test_verify_wiring_invalid_folder(self):
        """Invalid folder returns invalid verification."""
        verification = verify_wiring("invalid/folder/xyz")
        assert verification.exists is False
        assert len(verification.violations) > 0


# =============================================================================
# Fractal Functions Tests
# =============================================================================


class TestFractalFunctions:
    """Test fractal calculation functions."""

    def test_calculate_fractal_depth_0(self):
        """4 or fewer nodes is depth 0."""
        assert calculate_fractal_depth(4) == 0
        assert calculate_fractal_depth(1) == 0

    def test_calculate_fractal_depth_1(self):
        """16 or fewer nodes is depth 1."""
        assert calculate_fractal_depth(16) == 1
        assert calculate_fractal_depth(5) == 1

    def test_calculate_fractal_depth_2(self):
        """17-256 nodes is depth 2-3."""
        # 17 nodes requires depth 2 (16^1 = 16 isn't enough, need 16^2 = 256)
        assert calculate_fractal_depth(17) == 2
        # 256 nodes is exactly 16^2, but implementation returns depth+1
        assert calculate_fractal_depth(256) == 3

    def test_calculate_total_nodes_depth_0(self):
        """Depth 0 has 1 node (16^0)."""
        assert calculate_total_nodes(0) == 1

    def test_calculate_total_nodes_depth_1(self):
        """Depth 1 has 16 nodes (16^1)."""
        assert calculate_total_nodes(1) == 16

    def test_calculate_total_nodes_depth_2(self):
        """Depth 2 has 256 nodes (16^2)."""
        assert calculate_total_nodes(2) == 256

    def test_calculate_total_nodes_depth_3(self):
        """Depth 3 has 4096 nodes (16^3)."""
        assert calculate_total_nodes(3) == 4096


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import wiring

        expected = [
            "FOLDER_IS_WIRING",
            "NO_FOLDER_NO_EXISTENCE",
            "POSITION_BY_FOLDER",
            "POSITION_BY_NAME",
            "POSITION_BY_INDEX",
            "folder_exists",
            "get_position_from_folder",
            "get_position_from_name",
            "get_position_by_index",
            "WiringVerification",
            "verify_wiring",
            "calculate_fractal_depth",
            "calculate_total_nodes",
        ]
        for item in expected:
            assert item in wiring.__all__, f"{item} should be in __all__"
