"""
TEST DWARAPALA - The Gatekeepers (Jaya & Vijaya)
================================================
"Identity Check: Are you a Person or a Thing?"

Refactored to strictly enforce PersonProtocol via TestDevotee.
"""

import pytest
from vibe_core.protocols.governance.dwarapala import DwarapalaGate, AccessDenied
from tests.common.avatars import TestDevotee, TestService


@pytest.fixture
def gate():
    return DwarapalaGate()


@pytest.fixture
def jaya():
    """A Devotee with the right capability."""
    devotee = TestDevotee(name="Jaya")
    devotee.grant_capability("enter_vaikuntha")
    return devotee


@pytest.fixture
def stranger():
    """A Person without capability."""
    return TestDevotee(name="Stranger")


@pytest.fixture
def robot():
    """A Service (Not a Person)."""
    return TestService()


def test_gate_opens_for_authorized_person(gate, jaya):
    """
    Happy Path: Person + Capability = Access.
    """
    resource = "Vaikuntha_Map"

    # 1. Verify Accessor
    verified_person = gate.verify_accessor(jaya, "enter_vaikuntha")
    assert verified_person == jaya

    # 2. Access Resource
    result = gate.open_gate(verified_person, resource)
    assert result == resource


def test_gate_blocks_unauthorized_person(gate, stranger):
    """
    Adhikara Failure: Person exists, but lacks Rights.
    """
    with pytest.raises(AccessDenied) as exc:
        gate.verify_accessor(stranger, "enter_vaikuntha")

    assert "Adhikara Failure" in str(exc.value)


def test_gate_blocks_non_person_service(gate, robot):
    """
    Ontological Failure: Services cannot hold capabilities directly.
    They must act on behalf of a Person.
    """
    # Even if we hacked capabilities into the robot...
    robot.capabilities.append("enter_vaikuntha")

    # ...Dwarapala checks 'isinstance(PersonProtocol)' first.
    with pytest.raises(AccessDenied) as exc:
        gate.verify_accessor(robot, "enter_vaikuntha")

    assert "Identity Crisis" in str(exc.value)
    assert "Service/Object, not a Person" in str(exc.value)
