"""
ACINTYA — Foundation Tests
==========================

Tests acintya-bheda-abheda-tattva: simultaneous oneness and difference.
Krishna is the source. The module must encode this correctly.
"""

import pytest


class TestPurushaTattva:
    """PurushaTattva = PARAMPARA. The integer that is Krishna."""

    def test_purusha_value(self):
        from vibe_core.mahamantra.substrate.core.acintya import PURUSHA
        from vibe_core.mahamantra.protocols._seed import PARAMPARA

        assert int(PURUSHA) == PARAMPARA == 37

    def test_purusha_is_int(self):
        from vibe_core.mahamantra.substrate.core.acintya import PurushaTattva, PURUSHA

        assert isinstance(PURUSHA, PurushaTattva)
        assert isinstance(PURUSHA, int)


class TestKrishnaPresence:
    """Krishna is always present, always the source."""

    def test_krishna_constants(self):
        from vibe_core.mahamantra.substrate.core.acintya import (
            KRISHNA,
            KRISHNA_ASPECT,
            KRISHNA_SMALLEST,
            KRISHNA_LARGEST,
            KrishnaPresence,
        )

        assert isinstance(KRISHNA, KrishnaPresence)
        assert KRISHNA.is_present is True
        assert isinstance(KRISHNA_ASPECT, int)
        assert isinstance(KRISHNA_SMALLEST, int)
        assert isinstance(KRISHNA_LARGEST, int)

    def test_krishna_presence_class(self):
        from vibe_core.mahamantra.substrate.core.acintya import KrishnaPresence

        kp = KrishnaPresence()
        assert kp.is_present is True
        assert bool(kp) is True
        assert kp.encompasses_all is True
        assert isinstance(kp.smallest, int)
        assert isinstance(kp.largest, int)


class TestProtocolLevel:
    """Protocol levels derive from seed constants."""

    def test_protocol_levels_exist(self):
        from vibe_core.mahamantra.substrate.core.acintya import ProtocolLevel

        # Must have well-defined levels
        assert len(ProtocolLevel) > 0
        # All values are integers (IntEnum)
        for level in ProtocolLevel:
            assert isinstance(level.value, int)


class TestAcintyaAspect:
    """Aspects of acintya-bheda-abheda."""

    def test_aspects(self):
        from vibe_core.mahamantra.substrate.core.acintya import AcintyaAspect

        # Must have BHEDA (difference), ABHEDA (oneness), ACINTYA (inconceivable)
        assert hasattr(AcintyaAspect, "BHEDA")
        assert hasattr(AcintyaAspect, "ABHEDA")
        assert hasattr(AcintyaAspect, "ACINTYA")


class TestJivaState:
    """Jiva's condition relative to Krishna."""

    def test_jiva_conditions(self):
        from vibe_core.mahamantra.substrate.core.acintya import JivaCondition

        assert hasattr(JivaCondition, "CONNECTED")
        assert hasattr(JivaCondition, "DISCONNECTED")
        assert hasattr(JivaCondition, "ABSORBED")

    def test_jiva_state_class(self):
        from vibe_core.mahamantra.substrate.core.acintya import JivaState, JivaCondition

        js = JivaState()
        assert js.condition == JivaCondition.DISCONNECTED  # default: jiva drifted
        assert js.has_sovereign is False
        assert js.krishna_present is True  # Krishna IS, always

    def test_jiva_connect_disconnect(self):
        from vibe_core.mahamantra.substrate.core.acintya import JivaState, JivaCondition

        js = JivaState()
        js.connect()
        assert js.condition == JivaCondition.CONNECTED
        assert js.has_sovereign is True
        assert js.remembers_krishna is True

        js.disconnect()
        assert js.condition == JivaCondition.DISCONNECTED
        assert js.has_sovereign is False
        assert js.remembers_krishna is False
        assert js.krishna_present is True  # Krishna IS STILL


class TestBhedaAbheda:
    """Functional tests for bheda-abheda checking."""

    def test_vibration_is_krishna(self):
        from vibe_core.mahamantra.substrate.core.acintya import vibration_is_krishna

        assert vibration_is_krishna() is True

    def test_mantra_is_krishna(self):
        from vibe_core.mahamantra.substrate.core.acintya import mantra_is_krishna

        assert mantra_is_krishna() is True

    def test_mantra_not_different(self):
        from vibe_core.mahamantra.substrate.core.acintya import mantra_not_different_from_source

        assert mantra_not_different_from_source() is True

    def test_bheda_abheda_check(self):
        from vibe_core.mahamantra.substrate.core.acintya import check_bheda_abheda

        # Soul present, not claiming supreme → simultaneous (correct)
        result, msg = check_bheda_abheda(has_soul=True, claims_supreme=False)
        assert result is True

        # Soul present, claiming supreme → mayavada
        result, msg = check_bheda_abheda(has_soul=True, claims_supreme=True)
        assert result is False


class TestParamparaConnection:
    """Parampara connection tracking."""

    def test_verify_parampara(self):
        from vibe_core.mahamantra.substrate.core.acintya import verify_parampara

        assert verify_parampara(37) is True
        assert verify_parampara(37 * 3) is True
        assert verify_parampara(38) is False

    def test_parampara_connection(self):
        from vibe_core.mahamantra.substrate.core.acintya import ParamparaConnection

        # Connected via Guru (3×4)
        pc = ParamparaConnection.from_guru()
        assert pc.is_connected is True
        assert pc.mutation_vector == 444  # 37 × 12

        # Disconnected (4×3 = Mayavad)
        pc_bad = ParamparaConnection.from_mayavad()
        assert pc_bad.is_connected is False

        # Custom connected
        pc_custom = ParamparaConnection(mutation_vector=37 * 5)
        assert pc_custom.is_connected is True
        assert pc_custom.lineage_factor == 5

    def test_guru_entropy(self):
        from vibe_core.mahamantra.substrate.core.acintya import get_guru_entropy

        entropy = get_guru_entropy()
        assert isinstance(entropy, float)
        assert entropy > 0

