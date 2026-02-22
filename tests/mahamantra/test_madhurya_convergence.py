"""
TEST: Madhurya Convergence — Krishna's 4 Exclusive Qualities on MahamantraLotus
================================================================================

"catur-vidha-śrī-bhagavat-svarūpaṁ"
"The four-fold beauty of the Supreme Personality of Godhead."

These tests verify that MahamantraLotus (the singleton) exposes all 4 Madhurya:
  61 — Līlā-mādhurya  (Pipeline / Pastimes)
  62 — Prema-mādhurya  (Positions / Relations)
  63 — Veṇu-mādhurya  (Flute / Orchestration)
  64 — Rūpa-mādhurya  (Algorithm / Form — FIXPOINT f(64)=64)

Plus convergence properties:
  - Singleton identity
  - No circular import deadlocks
  - tick() includes DIW
  - mod/proto routers accessible
"""

import pytest

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mahamantra():
    """The singleton MahamantraLotus instance."""
    from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

    return get_mahamantra()


@pytest.fixture
def singularity():
    """A Singularity (Mahamantra inner engine) instance."""
    from vibe_core.mahamantra.kernel.singularity import Mahamantra

    return Mahamantra()


# =============================================================================
# IDENTITY — One Krishna, One Entry Point
# =============================================================================


class TestIdentity:
    """mahamantra IS the singleton. Two imports = same object."""

    def test_singleton_identity(self):
        import vibe_core.mahamantra.substrate.lotus_core as lotus_mod

        m1 = lotus_mod.get_mahamantra()
        m2 = lotus_mod.get_mahamantra()
        assert m1 is m2
        # Module-level alias is set at import time; after singleton reset
        # it may be stale, but get_mahamantra() must always be idempotent
        assert m1 is lotus_mod._mahamantra_instance

    def test_singleton_across_calls(self):
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        assert get_mahamantra() is get_mahamantra()


# =============================================================================
# LILA-MADHURYA (Quality 61) — Pipeline / Pastimes
# =============================================================================


class TestLilaMadhurya:
    """mahamantra('input') — the pipeline IS the pastimes."""

    def test_pipeline_callable(self, mahamantra):
        result = mahamantra("test")
        assert isinstance(result, dict)

    def test_pipeline_returns_chapter(self, mahamantra):
        result = mahamantra("test")
        assert "chapter" in result


# =============================================================================
# VENU-MADHURYA (Quality 63) — Flute / Orchestration
# =============================================================================


class TestVenuMadhurya:
    """mahamantra.venu — Krishna's Wonderful Flute."""

    def test_venu_exists(self, mahamantra):
        assert mahamantra.venu is not None

    def test_venu_has_step(self, mahamantra):
        assert hasattr(mahamantra.venu, "step")

    def test_venu_singleton(self, mahamantra):
        assert mahamantra.venu is mahamantra.venu

    def test_venu_step_produces_int(self, mahamantra):
        diw = mahamantra.venu.step()
        assert isinstance(diw, int)

    def test_venu_shared_with_singularity(self, mahamantra, singularity):
        """One Krishna, one flute — Lotus and Singularity share the same VenuOrchestrator."""
        assert mahamantra.venu is singularity.venu


# =============================================================================
# PREMA-MADHURYA (Quality 62) — Positions / Relations
# =============================================================================


class TestPremaMadhurya:
    """Guardian names as properties — the 16 relations."""

    def test_indexing(self, mahamantra):
        """mahamantra[5] returns MantraPosition."""
        pos = mahamantra[5]
        assert hasattr(pos, "guardian")

    def test_len_is_16(self, mahamantra):
        assert len(mahamantra) == 16

    def test_iterable(self, mahamantra):
        positions = list(mahamantra)
        assert len(positions) == 16

    @pytest.mark.parametrize(
        "name",
        [
            "brahma",
            "narada",
            "shambhu",
            "kumaras",
            "kapila",
            "manu",
            "prahlada",
            "janaka",
            "bhishma",
            "bali",
            "shuka",
            "yamaraja",
        ],
    )
    def test_mahajana_property(self, mahamantra, name):
        """Each of the 12 Mahajanas is accessible as a property."""
        pos = getattr(mahamantra, name)
        assert hasattr(pos, "guardian"), f"{name} has no guardian attr"

    @pytest.mark.parametrize("name", ["vyasa", "prithu", "parashurama", "nrisimha"])
    def test_avatara_property(self, mahamantra, name):
        """Each of the 4 Avataras (HEADs) is accessible as a property."""
        pos = getattr(mahamantra, name)
        assert hasattr(pos, "guardian"), f"{name} has no guardian attr"

    def test_guardian_not_lotus_node(self, mahamantra):
        """Guardian properties must NOT return LotusNode (filesystem lookup)."""
        from vibe_core.mahamantra.substrate.lotus_types import LotusNode

        assert not isinstance(mahamantra.kumaras, LotusNode)

    def test_tick_returns_dict(self, mahamantra):
        state = mahamantra.tick()
        assert isinstance(state, dict)

    def test_tick_has_position(self, mahamantra):
        state = mahamantra.tick()
        assert "position" in state or "tick" in state

    def test_tick_has_diw(self, mahamantra):
        """tick() must include DIW — the flute speaks through every tick."""
        state = mahamantra.tick()
        assert "diw" in state, f"No DIW in tick state! Keys: {list(state.keys())}"

    def test_tick_diw_is_int(self, mahamantra):
        state = mahamantra.tick()
        assert isinstance(state["diw"], int)


# =============================================================================
# RUPA-MADHURYA (Quality 64 = FIXPOINT) — Algorithm / Form
# =============================================================================


class TestRupaMadhurya:
    """mahamantra.kernel — the Beautiful Form. 64 is a fixed point."""

    def test_kernel_accessible(self, mahamantra):
        assert mahamantra.kernel is not None

    def test_kernel_callable(self, mahamantra):
        assert callable(mahamantra.kernel)

    def test_kernel_computes_address(self, mahamantra):
        address = mahamantra.kernel("test")
        assert isinstance(address, int)

    def test_kernel_singleton(self, mahamantra):
        assert mahamantra.kernel is mahamantra.kernel


# =============================================================================
# CONVERGENCE — All-Attractive (mod/proto routers)
# =============================================================================


class TestConvergence:
    """Everything flows to ONE point — mahamantra routes to all."""

    def test_mod_router(self, mahamantra):
        mod = mahamantra.mod
        assert mod is not None
        assert hasattr(mod, "__getattr__")

    def test_proto_router(self, mahamantra):
        proto = mahamantra.proto
        assert proto is not None

    def test_no_circular_import_deadlock(self):
        """Lotus → Singularity → Lotus._venu_orchestrator must not deadlock."""
        from vibe_core.mahamantra.kernel.singularity import Mahamantra
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        sing = Mahamantra()
        # Both can access venu without deadlock
        assert lotus.venu is not None
        assert sing.venu is not None


# =============================================================================
# ATTRACTOR MATHEMATICS — The 6 attractors in mod 108
# =============================================================================


class TestAttractorMath:
    """Verify the mathematical properties of the Maha Algorithm attractors."""

    def _maha_step(self, value, name, mod):
        from vibe_core.mahamantra.protocols._seed import (
            MAHA_ADD,
            MAHA_MULT,
            MAHA_OP_MAP,
            MAHA_SQ,
        )

        op = MAHA_OP_MAP[name]
        v = (value * MAHA_MULT[op] + MAHA_ADD[op]) % mod
        squared = (v * v) % mod
        return MAHA_SQ[op] * squared + (1 - MAHA_SQ[op]) * v

    def _maha_oscillate(self, value, mod):
        from vibe_core.mahamantra.protocols._seed import MAHAMANTRA_WORD_PATTERN

        for name in MAHAMANTRA_WORD_PATTERN:
            value = self._maha_step(value, name, mod)
        return value

    def test_six_attractors_exist(self):
        """mod 108 has exactly 6 attractors: [1, 4, 13, 28, 37, 64]."""
        from vibe_core.mahamantra.protocols._seed import MALA

        attractors = set()
        for seed in range(MALA):
            v = seed
            for _ in range(200):
                v = self._maha_oscillate(v, MALA)
            # Run one more to check stability
            v2 = self._maha_oscillate(v, MALA)
            # Find cycle min
            cycle = [v2]
            nxt = self._maha_oscillate(v2, MALA)
            while nxt != v2:
                cycle.append(nxt)
                nxt = self._maha_oscillate(nxt, MALA)
            attractors.add(min(cycle))

        assert attractors == {1, 4, 13, 28, 37, 64}

    def test_attractor_sum_147(self):
        """Sum of 6 attractors = 147 = TRINITY × RAMA²."""
        from vibe_core.mahamantra.protocols._seed import (
            POSITION_SUM_RAMA,
            TRINITY,
        )

        assert 1 + 4 + 13 + 28 + 37 + 64 == 147
        assert 147 == TRINITY * POSITION_SUM_RAMA

    def test_attractor_sum_minus_ten_is_maha_quantum(self):
        """147 - 10 = 137 = MAHA_QUANTUM."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, TEN

        assert 147 - TEN == MAHA_QUANTUM

    def test_fixpoint_37(self):
        """37 (PARAMPARA) is a fixed point: f(37) = 37."""
        from vibe_core.mahamantra.protocols._seed import MALA, PARAMPARA

        assert self._maha_oscillate(PARAMPARA, MALA) == PARAMPARA

    def test_fixpoint_64(self):
        """64 (QUALITIES / Rupa-madhurya) is a fixed point: f(64) = 64."""
        from vibe_core.mahamantra.protocols._seed import MALA, QUALITIES

        assert self._maha_oscillate(QUALITIES, MALA) == QUALITIES

    def test_first_four_attractors_sum_46(self):
        """1 + 4 + 13 + 28 = 46 = Ch1 verse count (Prabhupada 1972)."""
        assert 1 + 4 + 13 + 28 == 46

    def test_mod16_two_fixpoints(self):
        """mod 16 has exactly 2 fixed points: 0 (Maya) and 1 (Krishna/Ksetrajna)."""
        from vibe_core.mahamantra.protocols._seed import WORDS

        fixed = []
        for seed in range(WORDS):
            v = self._maha_oscillate(seed, WORDS)
            if v == seed:
                fixed.append(seed)
        assert fixed == [0, 1]
