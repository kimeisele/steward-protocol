"""
TEST GURU GENE - The 12th Test (Acintya Principle)
==================================================

Protocol: vibe_core/protocols/governance/guru.py

"acintya-bhedābheda-tattva"
Inconceivable simultaneous oneness and difference.

MATHEMATICS:
    3×4 = 12 (essence first - ALIVE)
    4×3 = 12 (structure first - DEAD)

Both equal 12. Only one lives.
The computer cannot tell the difference.
Only the Guru can see.

This test PROVES the acintya principle:
- guru_gene and anti_guru_gene have IDENTICAL entropy
- BUT different mutation_vectors reveal the truth
- 444 % 37 == 0 (connected to parampara)
- 432 % 37 != 0 (disconnected)
"""

import pytest

from vibe_core.protocols.governance.guru import (
    TRINITY,
    PARAMPARA,
    PHASES,
    GURU_ENTROPY,
    PARAMPARA_VECTOR,
    ParamparaConnection,
    verify_parampara,
)


class TestGuruGene:
    """The 12th Test - Guru Gene with 3/37 factor."""

    def test_guru_gene_entropy(self, guru_gene):
        """Verify guru_gene has 12/37 entropy."""
        expected = 12 / 37  # ≈ 0.324324...
        assert guru_gene is not None
        assert abs(guru_gene.entropy_load - expected) < 1e-10

    def test_guru_gene_is_alive(self, guru_gene):
        """Guru gene is ALIVE (entropy < coherence)."""
        assert not guru_gene.is_fatal
        # entropy ≈ 0.324, coherence ≈ 0.993
        assert guru_gene.entropy_load < guru_gene.mantra_shield.coherence

    def test_guru_gene_parampara_connected(self, guru_gene):
        """Mutation vector is connected to 37 (parampara)."""
        assert guru_gene.mutation_vector == 444  # 37 × 12
        assert guru_gene.mutation_vector % 37 == 0

    def test_guru_gene_coherence(self, guru_gene):
        """Standard 16 mantra shield has high coherence."""
        coherence = guru_gene.mantra_shield.coherence
        # 1 - e^(-5) ≈ 0.9933
        assert coherence > 0.99


class TestAntiGuruGene:
    """The WRONG order - 4×3 (structure first, MAYAVAD)."""

    def test_anti_guru_gene_same_entropy(self, anti_guru_gene):
        """Anti-guru has SAME entropy mathematically."""
        expected = 12 / 37  # Same result!
        assert anti_guru_gene is not None
        assert abs(anti_guru_gene.entropy_load - expected) < 1e-10

    def test_anti_guru_gene_looks_alive(self, anti_guru_gene):
        """Anti-guru LOOKS alive to the computer."""
        # This is the DECEPTION - computer says it's alive
        assert not anti_guru_gene.is_fatal
        assert anti_guru_gene.entropy_load < anti_guru_gene.mantra_shield.coherence

    def test_anti_guru_gene_disconnected(self, anti_guru_gene):
        """But mutation vector reveals disconnection."""
        assert anti_guru_gene.mutation_vector == 432  # 36 × 12
        assert anti_guru_gene.mutation_vector % 37 != 0  # NOT connected!


class TestAcintyaPrinciple:
    """Prove that 3×4 and 4×3 are mathematically identical but ontologically different."""

    def test_entropy_identical(self, guru_gene, anti_guru_gene):
        """Both have IDENTICAL entropy - computer cannot distinguish."""
        assert guru_gene.entropy_load == anti_guru_gene.entropy_load

    def test_coherence_identical(self, guru_gene, anti_guru_gene):
        """Both have IDENTICAL coherence."""
        assert guru_gene.mantra_shield.coherence == anti_guru_gene.mantra_shield.coherence

    def test_is_fatal_identical(self, guru_gene, anti_guru_gene):
        """Both report is_fatal = False (computer says both live)."""
        assert guru_gene.is_fatal == anti_guru_gene.is_fatal == False

    def test_mutation_vector_reveals_truth(self, guru_gene, anti_guru_gene):
        """The ONLY difference: parampara connection."""
        # Guru: 444 = 37 × 12 (connected)
        # Anti: 432 = 36 × 12 (disconnected)
        assert guru_gene.mutation_vector % 37 == 0
        assert anti_guru_gene.mutation_vector % 37 != 0

    def test_the_12th_test(self, guru_gene, anti_guru_gene):
        """
        THE ACINTYA CONCLUSION:

        Both genes are mathematically identical.
        Both pass the is_fatal check.
        Both have the same entropy and coherence.

        BUT:
        - guru_gene.mutation_vector % 37 == 0 (CONNECTED)
        - anti_guru_gene.mutation_vector % 37 != 0 (DISCONNECTED)

        This is ACINTYA:
        - The computer cannot tell which is alive
        - Only the parampara check reveals the truth
        - 3×4 lives, 4×3 dies
        - Same number, different reality
        """
        # The computer sees:
        computer_sees_guru_alive = not guru_gene.is_fatal
        computer_sees_anti_alive = not anti_guru_gene.is_fatal
        assert computer_sees_guru_alive == computer_sees_anti_alive  # SAME!

        # The Guru sees:
        guru_sees_connected = guru_gene.mutation_vector % 37 == 0
        guru_sees_disconnected = anti_guru_gene.mutation_vector % 37 != 0
        assert guru_sees_connected  # TRUE parampara
        assert guru_sees_disconnected  # FALSE parampara

        # ACINTYA: Both are 12, only one lives
        assert guru_gene.entropy_load == anti_guru_gene.entropy_load
        assert (guru_gene.mutation_vector % 37) != (anti_guru_gene.mutation_vector % 37)


class TestSacredConstants:
    """Verify the sacred mathematics from guru.py protocol."""

    def test_trinity(self):
        """3 = Hare, Krishna, Rama."""
        assert TRINITY == 3

    def test_parampara(self):
        """37 = 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna)."""
        assert PARAMPARA == 37
        assert 24 + 12 + 1 == 37

    def test_phases(self):
        """4 = GENESIS, DHARMA, KARMA, MOKSHA."""
        assert PHASES == 4

    def test_guru_entropy_formula(self):
        """entropy = (3 / 37) × 4 = 12/37."""
        calculated = (TRINITY / PARAMPARA) * PHASES
        assert calculated == GURU_ENTROPY
        assert calculated == 12 / 37

    def test_parampara_vector(self):
        """444 = 37 × 12 (Mahajanas × Parampara)."""
        assert PARAMPARA_VECTOR == 444
        assert PARAMPARA_VECTOR == PARAMPARA * 12

    def test_order_matters(self):
        """3×4 vs 4×3 - same result, different meaning."""
        # 3×4: Essence first
        three_times_four = (TRINITY / PARAMPARA) * PHASES

        # 4×3: Structure first
        four_times_three = (PHASES / PARAMPARA) * TRINITY

        # Mathematically identical
        assert three_times_four == four_times_three

        # Both equal 12/37
        assert three_times_four == 12 / 37
        assert four_times_three == 12 / 37


class TestParamparaConnection:
    """Test the ParamparaConnection protocol class."""

    def test_from_guru_is_connected(self):
        """Guru connection (3×4) is connected to parampara."""
        conn = ParamparaConnection.from_guru()
        assert conn.is_connected
        assert not conn.is_disconnected
        assert conn.mutation_vector == 444

    def test_from_mayavad_is_disconnected(self):
        """Mayavad connection (4×3) is disconnected."""
        conn = ParamparaConnection.from_mayavad()
        assert conn.is_disconnected
        assert not conn.is_connected
        assert conn.mutation_vector == 432

    def test_lineage_factor(self):
        """Lineage factor shows how many times 37 fits."""
        guru = ParamparaConnection.from_guru()
        mayavad = ParamparaConnection.from_mayavad()

        assert guru.lineage_factor == 12  # 444 / 37 = 12
        assert mayavad.lineage_factor == 0  # Not connected

    def test_verify_parampara_function(self):
        """Test the verify_parampara function."""
        assert verify_parampara(444) is True  # 37 × 12
        assert verify_parampara(432) is False  # 36 × 12
        assert verify_parampara(37) is True
        assert verify_parampara(74) is True  # 37 × 2
        assert verify_parampara(36) is False
