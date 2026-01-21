"""
TEST THE 37TH - The Venu-Gita (Divine Override)
===============================================
"Law is for the Servants. Love is for the Master."

Proves that Dwarapala yields to The37th Principle.
"""

import pytest
from vibe_core.protocols.governance.dwarapala import DwarapalaGate, AccessDenied
from vibe_core.protocols.universal.purusha import ParamaPurusha
from tests.common.avatars import TestDevotee, TestService


@pytest.fixture
def gate():
    return DwarapalaGate()


@pytest.fixture
def govinda():
    """The Supreme Person (Has No Capabilities, Needs None)."""
    return ParamaPurusha()


@pytest.fixture
def jiva():
    """Ordinary Living Entity."""
    return TestDevotee(name="Bound_Soul")


def test_law_applies_to_jiva(gate, jiva):
    """
    Standard Logic: No Capability -> No Access.
    """
    resource = "Vaikuntha_Secret"

    # Jiva has no capabilities
    with pytest.raises(AccessDenied) as exc:
        gate.verify_accessor(jiva, "enter_rasa_dance")

    assert "Adhikara Failure" in str(exc.value)


def test_love_overrides_law(gate, govinda):
    """
    The 37th Logic: The Flute Player enters everywhere.
    He has NO capabilities in his list.
    He enters by *revealing* who He is.
    """
    resource = "Rasa_Dance"

    # 1. Verify Govinda has no explicit capability
    assert len(govinda.capabilities) == 0

    # 2. Access Forbidden Realm
    # Should PASS because he is The37th and reveal() is True
    accessor = gate.verify_accessor(govinda, "enter_rasa_dance")

    assert accessor == govinda
    assert gate.open_gate(accessor, resource) == resource

    print("\n🕉️  VENU-GITA HEARD: Dwarapala are sleeping in Bliss.")


def test_impostor_cannot_play_flute(gate):
    """
    A Demon cannot fake the 37th Protocol simply by name.
    (Python typing enforces protocol implementation, but at runtime
    we rely on the class structure/isinstance).
    """

    class DemonImpostor:
        name = "Paundraka"
        capabilities = set()

        def reveal(self):
            return False  # Can't play the note

    impostor = DemonImpostor()

    # Dwarapala checks isinstance(The37th).
    # DemonImpostor does NOT inherit The37th or satisfy strict check if registered.
    # Even if it Duck Types, 'reveal' is false?
    # Actually, Dwarapala checks `isinstance(accessor, The37th)`.
    # Since DemonImpostor is not an instance of The37th (Protocol), it falls through to Person check.
    # It fails Person check (Identity Crisis) if it's not PersonProtocol.

    with pytest.raises(AccessDenied) as exc:
        gate.verify_accessor(impostor, "enter_rasa_dance")  # type: ignore

    assert "Identity Crisis" in str(exc.value)
