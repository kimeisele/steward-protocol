"""
SEED SSOT — Foundation Tests
=============================

Tests the mathematical bedrock: axioms → primary → secondary → seed.py
Every constant must derive from the Mahamantra. No magic numbers.
"""

import pytest

# ============================================================================
# AXIOM TESTS — The 7 atomic truths
# ============================================================================


class TestAxioms:
    """The 7 axioms are the ONLY hardcoded values in the system."""

    def test_axiom_values(self):
        from vibe_core.mahamantra.protocols.seed._axioms import (
            HALVES,
            HARE_COUNT,
            KRISHNA_COUNT,
            PANCHA,
            RAMA_COUNT,
            TRINITY,
            WORDS,
        )

        assert WORDS == 16, "Mahamantra has 16 words"
        assert TRINITY == 3, "3 holy names: Hare, Krishna, Rama"
        assert HARE_COUNT == 8, "Hare appears 8 times"
        assert KRISHNA_COUNT == 4, "Krishna appears 4 times"
        assert RAMA_COUNT == 4, "Rama appears 4 times"
        assert PANCHA == 5, "5 unique pairs"
        assert HALVES == 2, "2 halves"

    def test_axiom_consistency(self):
        """Axioms must be internally consistent with the Mahamantra."""
        from vibe_core.mahamantra.protocols.seed._axioms import (
            HALVES,
            HARE_COUNT,
            KRISHNA_COUNT,
            PANCHA,
            RAMA_COUNT,
            TRINITY,
            WORDS,
        )

        # Total words = sum of name occurrences
        assert HARE_COUNT + KRISHNA_COUNT + RAMA_COUNT == WORDS
        # Names are the trinity
        assert TRINITY == 3
        # Halves split the mantra
        assert WORDS % HALVES == 0

    def test_axiom_immutability(self):
        """Axioms are Final — verify they match across all import paths."""
        from vibe_core.mahamantra.protocols.seed._axioms import WORDS as AX_WORDS
        from vibe_core.mahamantra.protocols._seed import WORDS as PROTO_WORDS
        from vibe_core.mahamantra.substrate.core.seed import WORDS as SUB_WORDS

        assert AX_WORDS == PROTO_WORDS == SUB_WORDS


# ============================================================================
# PRIMARY DERIVATION TESTS
# ============================================================================


class TestPrimaryDerivations:
    """Primary derivations from axioms — one step removed."""

    def test_quarters(self):
        from vibe_core.mahamantra.protocols.seed._primary import QUARTERS
        from vibe_core.mahamantra.protocols.seed._axioms import KRISHNA_COUNT

        assert QUARTERS == KRISHNA_COUNT == 4

    def test_kshetra(self):
        from vibe_core.mahamantra.protocols.seed._primary import KSHETRA
        from vibe_core.mahamantra.protocols.seed._axioms import WORDS, HARE_COUNT

        assert KSHETRA == WORDS + HARE_COUNT == 24

    def test_nava(self):
        from vibe_core.mahamantra.protocols.seed._primary import NAVA
        from vibe_core.mahamantra.protocols.seed._axioms import HARE_COUNT

        assert NAVA == HARE_COUNT + 1 == 9

    def test_sharanagati(self):
        from vibe_core.mahamantra.protocols.seed._primary import SHARANAGATI
        from vibe_core.mahamantra.protocols.seed._axioms import TRINITY, HALVES

        assert SHARANAGATI == TRINITY * HALVES == 6

    def test_mahajana_count(self):
        from vibe_core.mahamantra.protocols.seed._secondary import MAHAJANA_COUNT
        from vibe_core.mahamantra.protocols.seed._primary import KSHETRA
        from vibe_core.mahamantra.protocols.seed._axioms import HALVES

        assert MAHAJANA_COUNT == KSHETRA // HALVES == 12

    def test_parampara(self):
        from vibe_core.mahamantra.protocols.seed._secondary import PARAMPARA, MAHAJANA_COUNT
        from vibe_core.mahamantra.protocols.seed._primary import KSHETRA, KSETRAJNA

        assert PARAMPARA == KSHETRA + MAHAJANA_COUNT + KSETRAJNA == 37

    def test_gita_chapters(self):
        from vibe_core.mahamantra.protocols.seed._secondary import GITA_CHAPTERS
        from vibe_core.mahamantra.protocols.seed._primary import SHARANAGATI
        from vibe_core.mahamantra.protocols.seed._axioms import TRINITY

        assert GITA_CHAPTERS == SHARANAGATI * TRINITY == 18

    def test_mala(self):
        from vibe_core.mahamantra.protocols.seed._secondary import MALA, MAHAJANA_COUNT
        from vibe_core.mahamantra.protocols.seed._primary import NAVA

        assert MALA == MAHAJANA_COUNT * NAVA == 108


# ============================================================================
# SECONDARY DERIVATION TESTS
# ============================================================================


class TestSecondaryDerivations:
    """Secondary derivations — two steps from axioms."""

    def test_lila(self):
        from vibe_core.mahamantra.protocols.seed._secondary import LILA
        from vibe_core.mahamantra.protocols.seed._axioms import WORDS, TRINITY

        assert LILA == WORDS * TRINITY == 48

    def test_qualities(self):
        from vibe_core.mahamantra.protocols.seed._secondary import QUALITIES
        from vibe_core.mahamantra.protocols.seed._axioms import WORDS
        from vibe_core.mahamantra.protocols.seed._primary import QUARTERS

        assert QUALITIES == WORDS * QUARTERS == 64

    def test_jiva_cycle(self):
        from vibe_core.mahamantra.protocols.seed._secondary import JIVA_CYCLE, MALA
        from vibe_core.mahamantra.protocols.seed._primary import QUARTERS

        assert JIVA_CYCLE == MALA * QUARTERS == 432


# ============================================================================
# SEED.PY CROSS-VALIDATION
# ============================================================================


class TestSeedCrossValidation:
    """seed.py must re-derive everything from axioms. No drift allowed."""

    def test_all_ssot_constants_match_protocols(self):
        """Every constant in seed.py must match its protocol source."""
        from vibe_core.mahamantra.substrate.core import seed
        from vibe_core.mahamantra.protocols import _seed as proto

        ssot_pairs = [
            ("WORDS", seed.WORDS, proto.WORDS),
            ("TRINITY", seed.TRINITY, proto.TRINITY),
            ("HALVES", seed.HALVES, proto.HALVES),
            ("PANCHA", seed.PANCHA, proto.PANCHA),
            ("QUARTERS", seed.QUARTERS, proto.QUARTERS),
            ("KSHETRA", seed.KSHETRA, proto.KSHETRA),
            ("NAVA", seed.NAVA, proto.NAVA),
            ("SHARANAGATI", seed.SHARANAGATI, proto.SHARANAGATI),
            ("MAHAJANA_COUNT", seed.MAHAJANA_COUNT, proto.MAHAJANA_COUNT),
            ("PARAMPARA", seed.PARAMPARA, proto.PARAMPARA),
            ("GITA_CHAPTERS", seed.GITA_CHAPTERS, proto.GITA_CHAPTERS),
            ("MALA", seed.MALA, proto.MALA),
            ("LILA", seed.LILA, proto.LILA),
            ("QUALITIES", seed.QUALITIES, proto.QUALITIES),
            ("JIVA_CYCLE", seed.JIVA_CYCLE, proto.JIVA_CYCLE),
            ("JIVA_QUALITIES", seed.JIVA_QUALITIES, proto.JIVA_QUALITIES),
        ]

        for name, seed_val, proto_val in ssot_pairs:
            assert seed_val == proto_val, f"SSOT violation: {name}: seed={seed_val} != proto={proto_val}"

    def test_mahamantra_sequence(self):
        """The 16-word Mahamantra sequence must be exact."""
        from vibe_core.mahamantra.substrate.core.seed import (
            MAHAMANTRA,
            WORDS,
            TRINITY,
            HolyName,
        )

        assert len(MAHAMANTRA) == WORDS
        assert len(set(MAHAMANTRA)) == TRINITY

        # Count occurrences
        counts = {}
        for name in MAHAMANTRA:
            counts[name] = counts.get(name, 0) + 1

        assert counts[HolyName.HARE] == 8
        assert counts[HolyName.KRISHNA] == 4
        assert counts[HolyName.RAMA] == 4

    def test_position_sums(self):
        """Position sums derive from the Mahamantra. T(16) = 136."""
        from vibe_core.mahamantra.substrate.core.seed import (
            POSITION_SUM_HARE,
            POSITION_SUM_KRISHNA,
            POSITION_SUM_RAMA,
            POSITION_SUM_TOTAL,
            WORDS,
        )

        # Triangular number T(16) = 16 * 17 / 2 = 136
        triangular_16 = WORDS * (WORDS + 1) // 2
        assert POSITION_SUM_TOTAL == triangular_16 == 136
        assert POSITION_SUM_HARE + POSITION_SUM_KRISHNA + POSITION_SUM_RAMA == POSITION_SUM_TOTAL
        # Structural: Hare sum divisible by 7, Rama sum is 7²
        assert POSITION_SUM_HARE % 7 == 0
        assert POSITION_SUM_RAMA == 49  # 7²

    def test_unique_pairs(self):
        """5 unique pairs from the Mahamantra."""
        from vibe_core.mahamantra.substrate.core.seed import (
            MAHAMANTRA_PAIRS,
            UNIQUE_PAIRS,
            WORDS,
            HALVES,
            PANCHA,
        )

        assert len(MAHAMANTRA_PAIRS) == WORDS // HALVES  # 8 pairs
        assert len(UNIQUE_PAIRS) == PANCHA  # 5 unique

    def test_quarter_enum(self):
        """4 quarters: genesis, dharma, karma, moksha."""
        from vibe_core.mahamantra.substrate.core.seed import (
            Quarter,
            QUARTERS,
            QUARTER_NAMES,
        )

        assert len(Quarter) == QUARTERS
        assert QUARTER_NAMES == ("genesis", "dharma", "karma", "moksha")

    def test_acoustic_constitution(self):
        """Flute frequencies form perfect fifth chain (3:2 ratios)."""
        from vibe_core.mahamantra.substrate.core.seed import (
            MURALI_FREQ,
            VENU_FREQ,
            VAMSI_FREQ,
            HALVES,
            TRINITY,
        )

        # Perfect fifth chain: each × 2 = next × 3
        assert MURALI_FREQ * HALVES == VENU_FREQ * TRINITY
        assert VENU_FREQ * HALVES == VAMSI_FREQ * TRINITY

    def test_helper_functions(self):
        """Seed helper functions work correctly."""
        from vibe_core.mahamantra.substrate.core.seed import (
            get_quarter,
            get_word_at,
            get_pair_at,
            verify_parampara,
            Quarter,
            HolyName,
            PARAMPARA,
        )

        # Quarter assignment
        assert get_quarter(0) == Quarter.GENESIS
        assert get_quarter(4) == Quarter.DHARMA
        assert get_quarter(8) == Quarter.KARMA
        assert get_quarter(12) == Quarter.MOKSHA

        # Word access
        assert get_word_at(0) == HolyName.HARE

        # Pair access
        pair = get_pair_at(0)
        assert len(pair) == 2

        # Parampara verification
        assert verify_parampara(PARAMPARA) is True
        assert verify_parampara(PARAMPARA * 2) is True
        assert verify_parampara(PARAMPARA + 1) is False

    def test_cosmic_frame(self):
        """Cosmic frame = 21600 = 360° × 60'."""
        from vibe_core.mahamantra.substrate.core.seed import COSMIC_FRAME, JIVA_QUALITIES, JIVA_CYCLE

        assert COSMIC_FRAME == 21600
        assert JIVA_QUALITIES == COSMIC_FRAME // JIVA_CYCLE == 50

