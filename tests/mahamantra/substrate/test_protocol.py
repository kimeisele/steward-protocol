"""
TEST PROTOCOL - substrate/protocol.py
=====================================

Tests for MantraProtocol base classes (SSOT).
"""

import pytest

from vibe_core.mahamantra.substrate import (
    MantraProtocol,
    WorkerProtocol,
    HeadProtocol,
    MantraAware,
    ProtocolRegistry,
    MantraOpCode,
    Mahajana,
    Avatara,
    Quarter,
    PARAMPARA,
)


class TestMantraProtocol:
    """Test MantraProtocol base class."""

    def test_position_index_required(self) -> None:
        """Subclass must set _position_index."""
        class BadProtocol(MantraProtocol):
            pass  # No _position_index

        with pytest.raises(ValueError):
            BadProtocol.position()

    def test_derived_properties(self) -> None:
        """All properties derive from position."""
        class TestProtocol(MantraProtocol):
            _position_index = 5  # Kumaras

        assert TestProtocol.position().index == 5
        assert TestProtocol.guardian() == Mahajana.KUMARAS
        assert TestProtocol.opcode() == MantraOpCode.BIND_SYMBOL
        assert TestProtocol.quarter() == Quarter.DHARMA
        assert not TestProtocol.is_head()
        assert TestProtocol.parampara_vector() == 6 * PARAMPARA  # (5+1) * 37

    def test_validate_valid(self) -> None:
        """validate returns True for valid protocol."""
        class ValidProtocol(MantraProtocol):
            _position_index = 7

        assert ValidProtocol.validate()

    def test_validate_invalid(self) -> None:
        """validate returns False for invalid position."""
        class InvalidProtocol(MantraProtocol):
            _position_index = 99

        assert not InvalidProtocol.validate()

    def test_protocol_id(self) -> None:
        """protocol_id returns formatted identifier."""
        class TestProtocol(MantraProtocol):
            _position_index = 11  # Bhishma

        pid = TestProtocol.protocol_id()
        assert "karma" in pid
        assert "bhishma" in pid


class TestWorkerProtocol:
    """Test WorkerProtocol for Mahajana positions."""

    def test_worker_position(self) -> None:
        """WorkerProtocol works at worker positions."""
        class BrahmaProtocol(WorkerProtocol):
            _position_index = 1

        assert BrahmaProtocol.mahajana() == Mahajana.BRAHMA
        assert BrahmaProtocol.validate()

    def test_worker_at_head_fails(self) -> None:
        """WorkerProtocol at HEAD position raises."""
        class BadWorker(WorkerProtocol):
            _position_index = 0  # HEAD position

        with pytest.raises(TypeError):
            BadWorker.mahajana()

    def test_worker_validate_head_fails(self) -> None:
        """WorkerProtocol.validate fails at HEAD position."""
        class BadWorker(WorkerProtocol):
            _position_index = 4  # HEAD position

        assert not BadWorker.validate()


class TestHeadProtocol:
    """Test HeadProtocol for Avatara positions."""

    def test_head_position(self) -> None:
        """HeadProtocol works at HEAD positions."""
        class PrithuProtocol(HeadProtocol):
            _position_index = 0

        assert PrithuProtocol.avatara() == Avatara.PRITHU
        assert PrithuProtocol.validate()

    def test_head_at_worker_fails(self) -> None:
        """HeadProtocol at WORKER position raises."""
        class BadHead(HeadProtocol):
            _position_index = 1  # WORKER position

        with pytest.raises(TypeError):
            BadHead.avatara()

    def test_head_validate_worker_fails(self) -> None:
        """HeadProtocol.validate fails at WORKER position."""
        class BadHead(HeadProtocol):
            _position_index = 5  # WORKER position

        assert not BadHead.validate()


class TestProtocolRegistry:
    """Test ProtocolRegistry."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        ProtocolRegistry.clear()

    def test_register(self) -> None:
        """Register adds protocol to registry."""
        @ProtocolRegistry.register
        class TestProtocol(WorkerProtocol):
            _position_index = 1

        assert ProtocolRegistry.get(1) is TestProtocol

    def test_register_duplicate_fails(self) -> None:
        """Cannot register two protocols at same position."""
        @ProtocolRegistry.register
        class FirstProtocol(WorkerProtocol):
            _position_index = 2

        with pytest.raises(ValueError):
            @ProtocolRegistry.register
            class SecondProtocol(WorkerProtocol):
                _position_index = 2

    def test_get_by_guardian(self) -> None:
        """get_by_guardian finds protocol by guardian."""
        @ProtocolRegistry.register
        class NaradaProtocol(WorkerProtocol):
            _position_index = 2

        found = ProtocolRegistry.get_by_guardian(Mahajana.NARADA)
        assert found is NaradaProtocol

    def test_coverage(self) -> None:
        """coverage returns registration stats."""
        @ProtocolRegistry.register
        class P1(WorkerProtocol):
            _position_index = 1

        @ProtocolRegistry.register
        class P2(WorkerProtocol):
            _position_index = 2

        count, total = ProtocolRegistry.coverage()
        assert count == 2
        assert total == 16

    def test_missing_positions(self) -> None:
        """missing_positions returns unregistered positions."""
        @ProtocolRegistry.register
        class P0(HeadProtocol):
            _position_index = 0

        missing = ProtocolRegistry.missing_positions()
        assert 0 not in missing
        assert 1 in missing
        assert len(missing) == 15


class TestMantraAware:
    """Test MantraAware protocol interface."""

    def test_protocol_is_mantra_aware(self) -> None:
        """MantraProtocol implements MantraAware."""
        class TestProtocol(MantraProtocol):
            _position_index = 3

        # Runtime check
        assert isinstance(TestProtocol, type)
        # Has required methods
        assert hasattr(TestProtocol, 'position')
        assert hasattr(TestProtocol, 'guardian')
        assert hasattr(TestProtocol, 'opcode')
