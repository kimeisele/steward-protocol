"""
TEST SSOT INTEGRITY - seed.py connection
========================================

Verifies that seed.py is the Single Source of Truth (SSOT) for all 
mathematical constants across the mahamantra protocols.

"The seed is the origin of everything."
"""

import pytest
from vibe_core.mahamantra.substrate import seed, byte, mahajana, wiring, position, opcode
from vibe_core.mahamantra.protocols import _core, _singularity, _lila, _sense, _steward, _lotus, _gad
from vibe_core.mahamantra.kernel import singularity


class TestSeedIntegrity:
    """Verify that seed.py contains the fundamental truths."""

    def test_sacred_numbers(self) -> None:
        """Seed constants must match sacred mathematics."""
        assert seed.WORDS == 16
        assert seed.PARAMPARA == 37
        assert seed.LILA == 48
        assert seed.KSHETRA == 24
        assert seed.MAHAJANAS == 12
        assert seed.KSETRAJNA == 1


class TestCoreIntegrity:
    """Verify that _core.py serves the seed."""

    def test_core_imports_from_seed(self) -> None:
        """Core constants must equal seed constants."""
        assert _core.PARAMPARA == seed.PARAMPARA
        assert _core.KSETRA_COUNT == seed.KSHETRA
        assert _core.MAHAJANA_COUNT == seed.MAHAJANAS
        assert _core.KSETRAJNA_COUNT == seed.KSETRAJNA

    def test_core_verification_logic(self) -> None:
        """Core must maintain the 37 formula."""
        assert _core.KSETRA_COUNT + _core.MAHAJANA_COUNT + _core.KSETRAJNA_COUNT == _core.PARAMPARA


class TestSingularityIntegrity:
    """Verify that _singularity.py serves the seed."""

    def test_singularity_imports_from_seed(self) -> None:
        """Singularity constants must equal seed constants."""
        assert _singularity.MAHAMANTRA_DIMENSION == seed.WORDS
        assert _singularity.LILA_CYCLES == seed.CYCLES
        assert _singularity.LILA_LIMIT == seed.LILA
        assert _singularity.NAVADVIPA_PHASE == seed.NAVADVIPA
        assert _singularity.PURI_PHASE == seed.PURI

    def test_rudra_bridge_derivation(self) -> None:
        """Rudra bridge (11) must connect Parampara (37) to Lila (48)."""
        assert _singularity.PARAMPARA == seed.PARAMPARA
        assert _singularity.RUDRA_BRIDGE == seed.LILA - seed.PARAMPARA
        assert _singularity.PARAMPARA + _singularity.RUDRA_BRIDGE == _singularity.LILA_LIMIT


class TestLilaIntegrity:
    """Verify that _lila.py serves the seed."""

    def test_lila_imports_from_seed(self) -> None:
        """Lila constants must equal seed constants."""
        assert _lila.LILA_LIMIT == seed.LILA
        assert _lila.LILA_CYCLES == seed.CYCLES
        assert _lila.LILA_BOUNDARY == seed.NAVADVIPA
        assert _lila.PARAMPARA == seed.PARAMPARA

    def test_lila_transcendence(self) -> None:
        """Lila (48) must be transcendental to Parampara (37)."""
        # 48 % 37 != 0
        assert _lila.LILA_LIMIT % _lila.PARAMPARA != 0
        assert _lila.LILA_BOUNDARY == 24
        assert _lila.LILA_LIMIT == 48


class TestByteIntegrity:
    """Verify that byte.py serves the seed."""

    def test_byte_imports_from_seed(self) -> None:
        """Byte constants must equal seed constants."""
        assert byte.MAHAMANTRA_DIMENSION == seed.WORDS
        assert byte.LILA_CYCLES == seed.CYCLES
        assert byte.LILA_LIMIT == seed.LILA
        assert byte.PARAMPARA == seed.PARAMPARA

    def test_genesis_byte_defaults(self) -> None:
        """GenesisByte must use seed defaults."""
        gb = byte.GenesisByte()
        assert gb.dimension == seed.WORDS
        assert gb.lila_limit == seed.LILA


class TestMahajanaIntegrity:
    """Verify that mahajana.py serves the seed."""

    def test_mahajana_imports_from_seed(self) -> None:
        """Mahajana constants must equal seed constants."""
        assert mahajana.MAHAJANA_COUNT == seed.MAHAJANAS
        assert mahajana.AVATARA_COUNT == seed.AVATARS
        assert mahajana.TOTAL_POSITIONS == seed.WORDS


class TestWiringIntegrity:
    """Verify that wiring.py serves the seed."""

    def test_wiring_imports_from_seed(self) -> None:
        """Wiring constants must equal seed constants."""
        assert wiring.QUARTER_COUNT == seed.QUARTERS
        assert wiring.POSITIONS_PER_QUARTER == seed.WORDS_PER_QUARTER
        assert wiring.FRACTAL_BASE == seed.WORDS
        assert wiring.PARAMPARA == seed.PARAMPARA


class TestPositionIntegrity:
    """Verify that position.py serves the seed."""

    def test_position_imports_from_seed(self) -> None:
        """Position constants must equal seed constants."""
        assert position.WORDS == seed.WORDS
        assert position.WORDS_PER_QUARTER == seed.WORDS_PER_QUARTER
        assert position.PARAMPARA == seed.PARAMPARA

    def test_position_table_size(self) -> None:
        """Position table must have exactly WORDS entries."""
        assert len(position.MAHAMANTRA_POSITIONS) == seed.WORDS


class TestOpcodeIntegrity:
    """Verify that opcode.py serves the seed."""

    def test_opcode_imports_from_seed(self) -> None:
        """Opcode constants must equal seed constants."""
        assert opcode.PARAMPARA == seed.PARAMPARA

    def test_opcode_count(self) -> None:
        """Must have exactly WORDS opcodes."""
        assert len(opcode.MantraOpCode) == seed.WORDS


class TestGADIntegrity:
    """Verify that _gad.py reflects the Sad-Aishvarya."""

    def test_gad_criteria_mapping(self) -> None:
        """GAD criteria must map to the 6 Opulences."""
        # 1. Discoverability = Yashas (Fame)
        assert _gad.GADCriterion.DISCOVERABILITY.name == "DISCOVERABILITY"
        assert _gad.SadAishvarya.YASHAS == "yashas"

        # 2. Observability = Jnana (Knowledge)
        assert _gad.GADCriterion.OBSERVABILITY.name == "OBSERVABILITY"
        assert _gad.SadAishvarya.JNANA == "jnana"

        # 3. Parseability = Vairagya (Renunciation)
        assert _gad.GADCriterion.PARSEABILITY.name == "PARSEABILITY"
        assert _gad.SadAishvarya.VAIRAGYA == "vairagya"

        # 4. Composability = Shri (Beauty)
        assert _gad.GADCriterion.COMPOSABILITY.name == "COMPOSABILITY"
        assert _gad.SadAishvarya.SHRI == "shri"

        # 5. Idempotency = Aishvarya (Control)
        assert _gad.GADCriterion.IDEMPOTENCY.name == "IDEMPOTENCY"
        assert _gad.SadAishvarya.AISHVARYA == "aishvarya"

        # 6. Recoverability = Virya (Strength)
        assert _gad.GADCriterion.RECOVERABILITY.name == "RECOVERABILITY"
        assert _gad.SadAishvarya.VIRYA == "virya"

    def test_gad_counts(self) -> None:
        """Must have exactly 6 criteria."""
        assert len(_gad.GADCriterion) == 6
        assert _gad.CRITERIA_COUNT == 6


class TestSenseIntegrity:
    """Verify that _sense.py serves the seed."""

    def test_sense_imports_from_seed(self) -> None:
        """Sense constants must equal seed constants."""
        assert _sense.PARAMPARA == seed.PARAMPARA
        assert _sense.KSETRA_COUNT == seed.KSHETRA
        assert _sense.TATTVA_COUNT == seed.KSHETRA


class TestStewardIntegrity:
    """Verify that _steward.py serves the seed."""

    def test_steward_imports_from_seed(self) -> None:
        """Steward constants must equal seed constants."""
        assert _steward.PARAMPARA == seed.PARAMPARA
        assert _steward.KSETRA == seed.KSHETRA
        assert _steward.KSETRAJNA == seed.KSETRAJNA
        assert _steward.MAHAJANAS == seed.MAHAJANAS
        assert _steward.POSITIONS == seed.WORDS

    def test_steward_version(self) -> None:
        """Steward version must include Parampara."""
        assert str(seed.PARAMPARA) in _steward.STEWARD_VERSION


class TestLotusIntegrity:
    """Verify that _lotus.py serves the seed."""

    def test_lotus_imports_from_seed(self) -> None:
        """Lotus constants must equal seed constants."""
        assert _lotus.LOTUS_PETALS == seed.WORDS
        assert _lotus.LOTUS_QUARTERS == seed.QUARTERS
        assert _lotus.PETALS_PER_QUARTER == seed.WORDS_PER_QUARTER
        assert _lotus.MALA_BEADS == seed.MALA
        assert _lotus.TRINITY == seed.TRINITY


class TestKernelSingularityIntegrity:
    """Verify that kernel singularity serves the seed."""

    def test_kernel_singularity_imports_from_seed(self) -> None:
        """Kernel singularity constants must equal seed constants."""
        assert singularity.PARAMPARA == seed.PARAMPARA
        assert singularity.WORDS == seed.WORDS

    def test_mahamantra_instance_limits(self) -> None:
        """Mahamantra instance must use seed limits."""
        from vibe_core.mahamantra import mahamantra
        assert len(mahamantra) == seed.WORDS
        assert mahamantra.PARAMPARA == seed.PARAMPARA


class TestProtocolCompliance:
    """Verify protocols are watertight and correctly identified."""

    def test_singularity_protocol_identity(self) -> None:
        """SingularityProtocol must be correctly identified."""
        from vibe_core.mahamantra.protocols._singularity import SingularityProtocol
        identity = SingularityProtocol.get_identity()
        assert identity.name == "SingularityProtocol"
        assert identity.position == 0
        assert identity.parampara_vector % seed.PARAMPARA == 0

    def test_lila_protocol_identity(self) -> None:
        """LilaProtocol must be correctly identified."""
        from vibe_core.mahamantra.protocols._lila import LilaProtocol
        identity = LilaProtocol.get_identity()
        assert identity.name == "LilaProtocol"
        assert identity.position == 6
        assert identity.parampara_vector % seed.PARAMPARA == 0
