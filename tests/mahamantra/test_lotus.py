"""
TEST LOTUS - mahamantra/__init__.py
===================================

Tests for the LOTUS SINGULARITY pattern.
"""

from vibe_core.mahamantra import mahamantra


class TestMahamantraLotus:
    """Test the mahamantra singularity instance."""

    def test_mahamantra_exists(self) -> None:
        """mahamantra instance exists."""
        assert mahamantra is not None

    def test_repr(self) -> None:
        """Repr is 'mahamantra'."""
        assert repr(mahamantra) == "mahamantra"


class TestQuarterAccess:
    """Test quarter access via properties."""

    def test_genesis(self) -> None:
        """Can access genesis quarter."""
        assert mahamantra.genesis is not None
        assert "genesis" in repr(mahamantra.genesis)

    def test_dharma(self) -> None:
        """Can access dharma quarter."""
        assert mahamantra.dharma is not None
        assert "dharma" in repr(mahamantra.dharma)

    def test_karma(self) -> None:
        """Can access karma quarter."""
        assert mahamantra.karma is not None
        assert "karma" in repr(mahamantra.karma)

    def test_moksha(self) -> None:
        """Can access moksha quarter."""
        assert mahamantra.moksha is not None
        assert "moksha" in repr(mahamantra.moksha)

    def test_substrate(self) -> None:
        """Can access substrate."""
        assert mahamantra.substrate is not None


class TestPositionAutoDiscovery:
    """Test position auto-discovery from folder structure."""

    def test_genesis_positions(self) -> None:
        """Can auto-discover genesis positions (0-3)."""
        # TRUTH from seed.py: GENESIS = vyasa, brahma, narada, shambhu
        assert mahamantra.genesis.vyasa is not None
        assert mahamantra.genesis.brahma is not None
        assert mahamantra.genesis.narada is not None
        assert mahamantra.genesis.shambhu is not None

    def test_dharma_positions(self) -> None:
        """Can auto-discover dharma positions (4-7)."""
        # TRUTH from seed.py: DHARMA = prithu, kumaras, kapila, manu
        assert mahamantra.dharma.prithu is not None
        assert mahamantra.dharma.kumaras is not None
        assert mahamantra.dharma.kapila is not None
        assert mahamantra.dharma.manu is not None

    def test_karma_positions(self) -> None:
        """Can auto-discover karma positions."""
        assert mahamantra.karma.parashurama is not None
        assert mahamantra.karma.prahlada is not None
        assert mahamantra.karma.janaka is not None
        assert mahamantra.karma.bhishma is not None

    def test_moksha_positions(self) -> None:
        """Can auto-discover moksha positions."""
        assert mahamantra.moksha.nrisimha is not None
        assert mahamantra.moksha.bali is not None
        assert mahamantra.moksha.shuka is not None
        assert mahamantra.moksha.yamaraja is not None


class TestPositionModuleExports:
    """Test that position modules export correct values."""

    def test_position_constants(self) -> None:
        """Position modules have POSITION constant."""
        from vibe_core.mahamantra.genesis import brahma

        assert hasattr(brahma, "POSITION")
        assert brahma.POSITION == 1

    def test_opcode_constants(self) -> None:
        """Position modules have OPCODE constant."""
        from vibe_core.mahamantra.moksha import yamaraja

        assert hasattr(yamaraja, "OPCODE")
        assert yamaraja.OPCODE == "AUDIT_SEAL"

    def test_parampara_vectors(self) -> None:
        """Position modules have correct PARAMPARA_VECTOR."""
        from vibe_core.mahamantra.moksha import bali

        assert hasattr(bali, "PARAMPARA_VECTOR")
        # Position 13: (13+1) * 37 = 518
        assert bali.PARAMPARA_VECTOR == 518
        assert bali.PARAMPARA_VECTOR % 37 == 0


class TestTabCompletion:
    """Test __dir__ for tab completion."""

    def test_root_dir(self) -> None:
        """Root has quarters in dir."""
        items = dir(mahamantra)
        assert "genesis" in items
        assert "dharma" in items
        assert "karma" in items
        assert "moksha" in items
        assert "substrate" in items

    def test_quarter_dir(self) -> None:
        """Quarter has positions in dir."""
        # TRUTH from seed.py: GENESIS = vyasa, brahma, narada, shambhu
        items = dir(mahamantra.genesis)
        assert "vyasa" in items
        assert "brahma" in items
        assert "narada" in items
        assert "shambhu" in items


class TestNonExistentPath:
    """Test behavior for non-existent paths."""

    def test_invalid_quarter_raises(self) -> None:
        """Invalid quarter raises AttributeError."""
        import pytest

        with pytest.raises(AttributeError):
            _ = mahamantra.nonexistent

    def test_invalid_position_raises(self) -> None:
        """Invalid position raises AttributeError."""
        import pytest

        with pytest.raises(AttributeError):
            _ = mahamantra.genesis.nonexistent


class TestCaching:
    """Test that node caching works."""

    def test_same_node_returned(self) -> None:
        """Same node returned on repeated access."""
        node1 = mahamantra.genesis.brahma
        node2 = mahamantra.genesis.brahma
        assert node1 is node2

    def test_quarter_cached(self) -> None:
        """Quarter nodes are cached."""
        q1 = mahamantra.genesis
        q2 = mahamantra.genesis
        assert q1 is q2
