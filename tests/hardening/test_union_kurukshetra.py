"""
KURUKSHETRA TEST - The Battle for Verification.

"Dharmakshetre Kurukshetre" - On the field of Dharma...

Dieses Modul testet die ANTI-MAYAVAD Härtung des Union Protokolls.
Es simuliert eine Umgebung mit gemischten Entitäten (Verifiziert & Geister)
und erzwingt die Einhaltung der GAD-000 Identitäts-Regeln.

Szenarien:
1. Prahlad-Test: Ein verifizierter Agent wird erkannt.
2. Hiranyakashipu-Test: Ein unverifizierter Geist wird geflaggt.
3. Nrisimha-Filter: require_verified=True filtert gnadenlos.
"""

from datetime import datetime
from typing import Iterator, List, Optional

import pytest

from vibe_core.protocols.substrate import BindingCertificate
from vibe_core.protocols.universal.union import (
    EntityStatus,
    UnionProtocol,
    UnionScanResult,
)

# =============================================================================
# MOCK IMPLEMENTATION (Das Feld)
# =============================================================================


class MockUnion(UnionProtocol):
    def __init__(self):
        self._registry: List[EntityStatus] = []

    def register(self, entity: EntityStatus):
        self._registry.append(entity)

    def get_living_entities(
        self,
        timeout_seconds: Optional[float] = None,
        require_verified: bool = False,
    ) -> Iterator[EntityStatus]:
        for entity in self._registry:
            if require_verified and not entity.is_verified:
                continue
            yield entity

    def get_living_entities_safe(
        self,
        timeout_seconds: float = 5.0,
    ) -> UnionScanResult:
        ghosts = [e for e in self._registry if not e.is_verified]

        return UnionScanResult(
            entities=self._registry,
            complete=True,
            scanned_count=len(self._registry),
            ghost_count=len(ghosts),
            error_count=0,
        )

    # Stubs for Protocol compliance
    def get_union_summary(self):
        return {}

    def get_registry_slots(self):
        return [None] * 37

    @property
    def divine_hash(self):
        return "mock-hash-1972"


# =============================================================================
# FIXTURES (Die Krieger)
# =============================================================================


@pytest.fixture
def valid_certificate() -> BindingCertificate:
    """Ein gültiges Zertifikat (Der Beweis der Herkunft)."""
    return BindingCertificate(
        binder_id="sovereign_key_0x123",
        target_id="agent_arjuna",
        host_id="host_krishna",
        timestamp=datetime.now().isoformat(),
        signature="hex_sig_valid",
        lineage=["root_ca", "intermediate_signer"],
    )


@pytest.fixture
def devotee_entity(valid_certificate) -> EntityStatus:
    """Arjuna: Ein verifizierter Agent."""
    return EntityStatus(
        id="arjuna",
        type="agent",
        status="ACTIVE",
        protocol="vibe_core.protocols.agent.Warrior",
        is_living=True,
        tuv_score=0.99,
        last_heartbeat=datetime.now(),
        certificate=valid_certificate,
        resonance_score=1.0,
    )


@pytest.fixture
def ghost_entity() -> EntityStatus:
    """Ein Mayavadi: Sieht aus wie ein Agent, hat aber keinen Beweis."""
    return EntityStatus(
        id="fake_agent",
        type="agent",
        status="ACTIVE",  # Täuschend aktiv
        protocol="unknown",
        is_living=True,
        tuv_score=0.0,
        last_heartbeat=datetime.now(),
        certificate=None,  # <-- DAS IST DER TEST
        resonance_score=0.0,
    )


# =============================================================================
# THE BATTLE (Tests)
# =============================================================================


def test_prahlad_verification(devotee_entity):
    """
    SATYA CHECK: Ein Agent mit Zertifikat muss als verifiziert gelten.
    """
    assert devotee_entity.certificate is not None
    assert devotee_entity.is_verified is True, "Devotee muss verifiziert sein"


def test_ghost_detection(ghost_entity):
    """
    MAYA CHECK: Ein Agent ohne Zertifikat muss als unverifiziert gelten.
    """
    assert ghost_entity.certificate is None
    assert ghost_entity.is_verified is False, "Geist darf nicht verifiziert sein"


def test_union_scan_ghost_counting(devotee_entity, ghost_entity):
    """
    UNION CHECK: Der Scan muss Geister korrekt zählen (Observability).
    """
    union = MockUnion()
    union.register(devotee_entity)
    union.register(ghost_entity)

    result = union.get_living_entities_safe()

    assert result.scanned_count == 2
    assert result.ghost_count == 1, "Der Scan muss genau einen Geist melden"
    assert len(result.entities) == 2


def test_nrisimha_filtering(devotee_entity, ghost_entity):
    """
    PURGE CHECK: require_verified=True muss Geister entfernen.
    """
    union = MockUnion()
    union.register(devotee_entity)
    union.register(ghost_entity)

    # Der Filter wird aktiviert (Nrisimha Modus)
    filtered_iterator = union.get_living_entities(require_verified=True)
    results = list(filtered_iterator)

    assert len(results) == 1
    assert results[0].id == "arjuna"
    assert results[0].is_verified is True

    # Sicherstellen, dass der Geist weg ist
    ids = [e.id for e in results]
    assert "fake_agent" not in ids, "Mayavadis dürfen den Filter nicht passieren"


def test_registry_slots_structure():
    """
    GAD-000 STRUCTURE CHECK: Die 37 Slots müssen existieren.
    """
    union = MockUnion()
    slots = union.get_registry_slots()
    assert len(slots) == 37, "Das Sri Yantra muss 37 Slots haben"
