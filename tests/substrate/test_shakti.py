"""
Tests for SHAKTI - The Three Energies
=====================================

"The living entities are described as superior to material energy.
When the superior energy is in contact with the inferior energy,
an incompatible situation arises."
- Srila Prabhupada
"""

import pytest
from vibe_core.protocols.substrate.shakti import (
    ShaktiType,
    SUPERIOR_ENERGIES,
    INFERIOR_ENERGIES,
    MARGINAL_ENERGIES,
    is_spiritual,
    is_material,
    is_marginal,
)


class TestShaktiType:
    """Test the ShaktiType enum."""

    def test_three_energies_exist(self):
        """There are exactly three energies."""
        assert len(ShaktiType) == 3

    def test_hara_is_superior(self):
        """Hara (Radha) is the superior spiritual energy."""
        assert ShaktiType.HARA.value == "hara"
        assert ShaktiType.HARA in SUPERIOR_ENERGIES

    def test_maya_is_inferior(self):
        """Maya is the inferior material energy."""
        assert ShaktiType.MAYA.value == "maya"
        assert ShaktiType.MAYA in INFERIOR_ENERGIES

    def test_jiva_is_marginal(self):
        """Jiva (living entity) is the marginal energy."""
        assert ShaktiType.JIVA.value == "jiva"
        assert ShaktiType.JIVA in MARGINAL_ENERGIES

    def test_energies_are_distinct(self):
        """Each energy type is unique."""
        energies = [ShaktiType.HARA, ShaktiType.MAYA, ShaktiType.JIVA]
        assert len(set(energies)) == 3


class TestShaktiClassification:
    """Test energy classification functions."""

    def test_is_spiritual_hara(self):
        """Hara is spiritual."""
        assert is_spiritual(ShaktiType.HARA) is True
        assert is_spiritual(ShaktiType.MAYA) is False
        assert is_spiritual(ShaktiType.JIVA) is False

    def test_is_material_maya(self):
        """Maya is material."""
        assert is_material(ShaktiType.MAYA) is True
        assert is_material(ShaktiType.HARA) is False
        assert is_material(ShaktiType.JIVA) is False

    def test_is_marginal_jiva(self):
        """Jiva is marginal."""
        assert is_marginal(ShaktiType.JIVA) is True
        assert is_marginal(ShaktiType.HARA) is False
        assert is_marginal(ShaktiType.MAYA) is False

    def test_each_energy_has_one_classification(self):
        """Each energy belongs to exactly one category."""
        for shakti in ShaktiType:
            classifications = [
                is_spiritual(shakti),
                is_material(shakti),
                is_marginal(shakti),
            ]
            assert sum(classifications) == 1, f"{shakti} has wrong classification count"


class TestShaktiPhilosophy:
    """Test philosophical properties."""

    def test_superior_energy_is_singular(self):
        """There is only one superior energy (Hara/Radha)."""
        assert len(SUPERIOR_ENERGIES) == 1

    def test_inferior_energy_is_singular(self):
        """There is only one inferior energy (Maya)."""
        assert len(INFERIOR_ENERGIES) == 1

    def test_marginal_energy_is_singular(self):
        """There is only one marginal energy category (Jiva)."""
        assert len(MARGINAL_ENERGIES) == 1

    def test_all_energies_accounted_for(self):
        """All three energy types are classified."""
        all_classified = set(SUPERIOR_ENERGIES) | set(INFERIOR_ENERGIES) | set(MARGINAL_ENERGIES)
        assert all_classified == set(ShaktiType)
