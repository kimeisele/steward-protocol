"""
TESTS: MahaHardware - Silicon Altar Adapter
============================================

"ūrdhva-mūlam adhaḥ-śākham aśvatthaṁ prāhur avyayam"
"There is a banyan tree which has its roots upward and branches down."
— Bhagavad Gita 15.1

These tests make MahaHardware ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.hardware import (
    MahaHardware,
    HardwareSpec,
    PipelineStageInfo,
    VerificationResult,
    PipelineStage,
    # Constants
    DATA_WIDTH,
    NEXT_HOP_WIDTH,
    BRANCHING_FACTOR,
    NIBBLE_SIZE,
    PIPELINE_STAGES,
    ROOT_BASE_ADDRESS,
)
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    QUARTERS,
    AKSARA_COUNT,
    HARE_COUNT,
)


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestHardwareConstants:
    """Test constants are derived from seed."""

    def test_data_width_is_aksara(self):
        """DATA_WIDTH must equal AKSARA_COUNT (32)."""
        assert DATA_WIDTH == AKSARA_COUNT == 32

    def test_next_hop_width_is_words(self):
        """NEXT_HOP_WIDTH must equal WORDS (16)."""
        assert NEXT_HOP_WIDTH == WORDS == 16

    def test_branching_factor_is_words(self):
        """BRANCHING_FACTOR must equal WORDS (16)."""
        assert BRANCHING_FACTOR == WORDS == 16

    def test_nibble_size_is_quarters(self):
        """NIBBLE_SIZE must equal QUARTERS (4)."""
        assert NIBBLE_SIZE == QUARTERS == 4

    def test_pipeline_stages_is_hare_count(self):
        """PIPELINE_STAGES must equal HARE_COUNT (8)."""
        assert PIPELINE_STAGES == HARE_COUNT == 8

    def test_root_base_address_is_base(self):
        """ROOT_BASE_ADDRESS should encode 'BA5E'."""
        assert ROOT_BASE_ADDRESS == 0xBA5E_0000


# =============================================================================
# PIPELINE STAGE ENUM TESTS
# =============================================================================


class TestPipelineStageEnum:
    """Test PipelineStage enum."""

    def test_has_8_stages(self):
        """Must have exactly 8 pipeline stages."""
        assert len(PipelineStage) == 8

    def test_stages_are_sequential(self):
        """Stages must be 0-7."""
        for i, stage in enumerate(PipelineStage):
            assert stage.value == i

    def test_stage_names(self):
        """Stage names follow L0_NIBBLE to L7_NIBBLE pattern."""
        expected_names = [f"L{i}_NIBBLE" for i in range(8)]
        actual_names = [s.name for s in PipelineStage]
        assert actual_names == expected_names


# =============================================================================
# PIPELINE STAGE INFO TESTS
# =============================================================================


class TestPipelineStageInfo:
    """Test PipelineStageInfo dataclass."""

    def test_create_stage_info(self):
        """Can create PipelineStageInfo."""
        info = PipelineStageInfo(
            stage=0,
            name="L0_NIBBLE",
            bit_range="31-28",
            sanskrit="ceto-darpaṇa-mārjanaṁ",
            english="Cleanses the mirror of the heart",
            hardware_effect="Initialize: Clear cache, set root",
        )
        assert info.stage == 0
        assert info.name == "L0_NIBBLE"
        assert info.bit_range == "31-28"

    def test_high_bit(self):
        """high_bit calculates correctly."""
        info = PipelineStageInfo(
            stage=0,
            name="L0",
            bit_range="31-28",
            sanskrit="",
            english="",
            hardware_effect="",
        )
        assert info.high_bit == 31

        info = PipelineStageInfo(
            stage=7,
            name="L7",
            bit_range="3-0",
            sanskrit="",
            english="",
            hardware_effect="",
        )
        assert info.high_bit == 3

    def test_low_bit(self):
        """low_bit calculates correctly."""
        info = PipelineStageInfo(
            stage=0,
            name="L0",
            bit_range="31-28",
            sanskrit="",
            english="",
            hardware_effect="",
        )
        assert info.low_bit == 28

        info = PipelineStageInfo(
            stage=7,
            name="L7",
            bit_range="3-0",
            sanskrit="",
            english="",
            hardware_effect="",
        )
        assert info.low_bit == 0


# =============================================================================
# HARDWARE SPEC TESTS
# =============================================================================


class TestHardwareSpec:
    """Test HardwareSpec dataclass."""

    def test_create_spec(self):
        """Can create HardwareSpec."""
        spec = HardwareSpec(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0xBA5E0000,
        )
        assert spec.data_width == 32
        assert spec.next_hop_width == 16
        assert spec.branching_factor == 16
        assert spec.nibble_size == 4
        assert spec.pipeline_stages == 8

    def test_total_latency_cycles(self):
        """total_latency_cycles equals pipeline_stages."""
        spec = HardwareSpec(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0,
        )
        assert spec.total_latency_cycles == 8

    def test_is_verified_true(self):
        """is_verified returns True for Mahamantra-aligned spec."""
        spec = HardwareSpec(
            data_width=32,  # AKSARA
            next_hop_width=16,  # WORDS
            branching_factor=16,  # WORDS
            nibble_size=4,  # QUARTERS
            pipeline_stages=8,  # OCTET
            root_base_address=0xBA5E0000,
        )
        assert spec.is_verified is True

    def test_is_verified_false(self):
        """is_verified returns False for non-aligned spec."""
        spec = HardwareSpec(
            data_width=64,  # Not AKSARA
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0,
        )
        assert spec.is_verified is False

    def test_address_space(self):
        """address_space calculates 2^data_width."""
        spec = HardwareSpec(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0,
        )
        assert spec.address_space == 2**32

    def test_max_next_hops(self):
        """max_next_hops calculates 2^next_hop_width."""
        spec = HardwareSpec(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0,
        )
        assert spec.max_next_hops == 2**16 == 65536

    def test_to_dict(self):
        """to_dict returns correct dictionary."""
        spec = HardwareSpec(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
            root_base_address=0xBA5E0000,
        )
        d = spec.to_dict()
        assert d["data_width"] == 32
        assert d["pipeline_stages"] == 8
        assert d["is_verified"] is True
        assert d["root_base_address"] == "0xba5e0000"


# =============================================================================
# VERIFICATION RESULT TESTS
# =============================================================================


class TestVerificationResult:
    """Test VerificationResult dataclass."""

    def test_create_result_valid(self):
        """Can create valid VerificationResult."""
        result = VerificationResult(
            is_valid=True,
            checks=[
                ("check1", 32, 32, True),
                ("check2", 16, 16, True),
            ],
        )
        assert result.is_valid is True
        assert result.passed_count == 2
        assert result.total_count == 2

    def test_create_result_invalid(self):
        """Can create invalid VerificationResult."""
        result = VerificationResult(
            is_valid=False,
            checks=[
                ("check1", 32, 64, False),
                ("check2", 16, 16, True),
            ],
        )
        assert result.is_valid is False
        assert result.passed_count == 1
        assert result.total_count == 2

    def test_summary_contains_status(self):
        """summary contains PASSED/FAILED status."""
        passed = VerificationResult(is_valid=True, checks=[("x", 1, 1, True)])
        assert "PASSED" in passed.summary

        failed = VerificationResult(is_valid=False, checks=[("x", 1, 2, False)])
        assert "FAILED" in failed.summary


# =============================================================================
# MAHAHARDWARE CLASS TESTS
# =============================================================================


class TestMahaHardware:
    """Test MahaHardware main class."""

    @pytest.fixture
    def hw(self) -> MahaHardware:
        """Create MahaHardware instance."""
        return MahaHardware()

    def test_create_instance(self, hw: MahaHardware):
        """Can create MahaHardware instance."""
        assert hw is not None

    def test_class_constants(self, hw: MahaHardware):
        """Class constants match module constants."""
        assert hw.DATA_WIDTH == DATA_WIDTH
        assert hw.NEXT_HOP_WIDTH == NEXT_HOP_WIDTH
        assert hw.BRANCHING_FACTOR == BRANCHING_FACTOR
        assert hw.NIBBLE_SIZE == NIBBLE_SIZE
        assert hw.PIPELINE_STAGES == PIPELINE_STAGES
        assert hw.ROOT_BASE_ADDRESS == ROOT_BASE_ADDRESS

    def test_spec_returns_hardware_spec(self, hw: MahaHardware):
        """spec() returns HardwareSpec."""
        spec = hw.spec()
        assert isinstance(spec, HardwareSpec)
        assert spec.data_width == 32
        assert spec.is_verified is True

    def test_pipeline_stages_returns_8(self, hw: MahaHardware):
        """pipeline_stages() returns 8 stages."""
        stages = list(hw.pipeline_stages())
        assert len(stages) == 8

    def test_pipeline_stages_have_sanskrit(self, hw: MahaHardware):
        """Each pipeline stage has Sanskrit verse."""
        for stage in hw.pipeline_stages():
            assert stage.sanskrit != ""
            assert stage.english != ""
            assert stage.hardware_effect != ""

    def test_get_stage_valid(self, hw: MahaHardware):
        """get_stage() returns correct stage."""
        stage = hw.get_stage(0)
        assert stage is not None
        assert stage.stage == 0
        assert "31-28" in stage.bit_range

        stage = hw.get_stage(7)
        assert stage is not None
        assert stage.stage == 7
        assert "3-0" in stage.bit_range

    def test_get_stage_invalid(self, hw: MahaHardware):
        """get_stage() returns None for invalid index."""
        assert hw.get_stage(-1) is None
        assert hw.get_stage(8) is None
        assert hw.get_stage(100) is None


# =============================================================================
# VERIFICATION TESTS
# =============================================================================


class TestMahaHardwareVerification:
    """Test hardware verification."""

    @pytest.fixture
    def hw(self) -> MahaHardware:
        return MahaHardware()

    def test_verify_default_passes(self, hw: MahaHardware):
        """Default parameters pass verification."""
        result = hw.verify()
        assert result.is_valid is True
        assert result.passed_count == 5
        assert result.total_count == 5

    def test_verify_custom_valid(self, hw: MahaHardware):
        """Mahamantra-aligned custom params pass."""
        result = hw.verify(
            data_width=32,
            next_hop_width=16,
            branching_factor=16,
            nibble_size=4,
            pipeline_stages=8,
        )
        assert result.is_valid is True

    def test_verify_wrong_data_width(self, hw: MahaHardware):
        """Wrong data_width fails."""
        result = hw.verify(data_width=64)
        assert result.is_valid is False

    def test_verify_wrong_branching(self, hw: MahaHardware):
        """Wrong branching_factor fails."""
        result = hw.verify(branching_factor=8)
        assert result.is_valid is False

    def test_verify_partial_failure(self, hw: MahaHardware):
        """Partial failures tracked correctly."""
        result = hw.verify(
            data_width=64,  # Wrong
            next_hop_width=16,  # Correct
            branching_factor=8,  # Wrong
            nibble_size=4,  # Correct
            pipeline_stages=8,  # Correct
        )
        assert result.is_valid is False
        assert result.passed_count == 3
        assert result.total_count == 5


# =============================================================================
# CODE GENERATION TESTS
# =============================================================================


class TestMahaHardwareCodeGen:
    """Test code generation."""

    @pytest.fixture
    def hw(self) -> MahaHardware:
        return MahaHardware()

    def test_generate_verilog_params(self, hw: MahaHardware):
        """generate_verilog_params() returns valid SystemVerilog."""
        verilog = hw.generate_verilog_params()
        assert "module LotusRouterCore" in verilog
        assert "DATA_WIDTH = 32" in verilog
        assert "NEXT_HOP_WIDTH = 16" in verilog
        assert "PIPELINE_STAGES = 8" in verilog
        assert "0xBA5E0000" in verilog

    def test_generate_vhdl_params(self, hw: MahaHardware):
        """generate_vhdl_params() returns valid VHDL."""
        vhdl = hw.generate_vhdl_params()
        assert "entity LotusRouterCore" in vhdl
        assert "DATA_WIDTH" in vhdl
        assert "NEXT_HOP_WIDTH" in vhdl
        assert "BA5E0000" in vhdl

    def test_generate_c_defines(self, hw: MahaHardware):
        """generate_c_defines() returns valid C code."""
        c_code = hw.generate_c_defines()
        assert "#define LOTUS_DATA_WIDTH" in c_code
        assert "#define LOTUS_NEXT_HOP_WIDTH" in c_code
        assert "#define LOTUS_PIPELINE_STAGES" in c_code
        assert "0xBA5E0000" in c_code

    def test_explanation_property(self, hw: MahaHardware):
        """explanation property returns full explanation."""
        explanation = hw.explanation
        assert "SILICON ALTAR" in explanation
        assert "AKSARA" in explanation
        assert "SIKSASTAKAM" in explanation
        assert "ceto-darpaṇa" in explanation


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMahaHardwareIntegration:
    """Integration tests for MahaHardware."""

    def test_full_spec_flow(self):
        """Full specification flow works end-to-end."""
        hw = MahaHardware()

        spec = hw.spec()
        assert spec.is_verified is True
        assert spec.total_latency_cycles == 8
        assert spec.address_space == 2**32

    def test_full_pipeline_flow(self):
        """Full pipeline inspection flow works."""
        hw = MahaHardware()

        stages = list(hw.pipeline_stages())
        assert len(stages) == 8

        # First stage processes bits 31-28
        assert stages[0].high_bit == 31
        assert stages[0].low_bit == 28

        # Last stage processes bits 3-0
        assert stages[7].high_bit == 3
        assert stages[7].low_bit == 0

    def test_full_verification_flow(self):
        """Full verification flow works."""
        hw = MahaHardware()

        # Verify default
        result = hw.verify()
        assert result.is_valid is True

        # Verify custom incorrect
        result = hw.verify(data_width=48, pipeline_stages=6)
        assert result.is_valid is False
        # Should fail data_width and pipeline_stages checks
        assert result.passed_count == 3

    def test_all_code_generators_work(self):
        """All code generators produce non-empty output."""
        hw = MahaHardware()

        verilog = hw.generate_verilog_params()
        vhdl = hw.generate_vhdl_params()
        c_code = hw.generate_c_defines()
        explanation = hw.explanation

        # All should be substantial
        assert len(verilog) > 500
        assert len(vhdl) > 300
        assert len(c_code) > 300
        assert len(explanation) > 500
