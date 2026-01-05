"""
Tests for KulikaService - The Schema Lord.

Verifies:
- Manifest validation
- Service validation
- Registration and lookup
- Capability queries
- Domain/Lord queries
"""

import pytest

from vibe_core.naga.kulika import (
    KulikaRegistry,
    NagaCapability,
    NagaDomain,
    NagaLord,
    NagaManifest,
    naga_service,
)
from vibe_core.naga.services.kulika import KulikaService


@pytest.fixture
def fresh_registry():
    """Create a fresh registry for each test."""
    registry = KulikaRegistry()
    registry.clear()
    return registry


@pytest.fixture
def kulika(fresh_registry):
    """Create a KulikaService with fresh registry."""
    return KulikaService(registry=fresh_registry)


class TestKulikaServiceBasics:
    """Basic KulikaService tests."""

    def test_init(self, kulika):
        """Test initialization."""
        assert kulika is not None
        assert kulika._validation_count == 0
        assert kulika._registration_count == 0

    def test_repr(self, kulika):
        """Test string representation."""
        assert "KulikaService" in repr(kulika)
        assert "services=0" in repr(kulika)


class TestManifestValidation:
    """Manifest validation tests."""

    def test_valid_manifest(self, kulika):
        """Test validating a correct manifest."""
        manifest = NagaManifest(
            name="TestService",
            lord=NagaLord.SESHA,
            domain=NagaDomain.INFRASTRUCTURE,
            capabilities=[NagaCapability.LEDGER],
        )

        errors = kulika.validate_manifest(manifest)
        assert errors == []

    def test_manifest_missing_name(self, kulika):
        """Test manifest without name."""
        manifest = NagaManifest(
            name="",
            lord=NagaLord.SESHA,
            domain=NagaDomain.INFRASTRUCTURE,
        )

        errors = kulika.validate_manifest(manifest)
        assert any("name" in e.lower() for e in errors)

    def test_manifest_domain_mismatch(self, kulika):
        """Test manifest with mismatched domain."""
        manifest = NagaManifest(
            name="TestService",
            lord=NagaLord.SESHA,  # Infrastructure lord
            domain=NagaDomain.GOVERNANCE,  # Wrong domain!
        )

        errors = kulika.validate_manifest(manifest)
        assert any("mismatch" in e.lower() for e in errors)

    def test_manifest_from_dict(self, kulika):
        """Test validating manifest from dict."""
        manifest_dict = {
            "name": "TestService",
            "lord": "sesha",
            "domain": "infrastructure",
        }

        errors = kulika.validate_manifest(manifest_dict)
        assert errors == []

    def test_invalid_capability_for_domain(self, kulika):
        """Test infrastructure lord with governance-only capability."""
        manifest = NagaManifest(
            name="TestService",
            lord=NagaLord.SESHA,  # Infrastructure
            domain=NagaDomain.INFRASTRUCTURE,
            capabilities=[NagaCapability.AUDIT],  # Governance-only!
        )

        errors = kulika.validate_manifest(manifest)
        assert any("governance-only" in e.lower() for e in errors)


class TestServiceValidation:
    """Service class validation tests."""

    def test_valid_service(self, kulika):
        """Test validating a correct service class."""

        @naga_service(
            name="TestService",
            lord=NagaLord.VASUKI,
            capabilities=[NagaCapability.NETWORK],
        )
        class TestService:
            def get_status(self):
                return {"healthy": True}

        errors = kulika.validate_service(TestService)
        assert errors == []

    def test_service_without_decorator(self, kulika):
        """Test validating class without @naga_service."""

        class PlainService:
            def get_status(self):
                return {}

        errors = kulika.validate_service(PlainService)
        assert any("decorator" in e.lower() for e in errors)

    def test_service_without_get_status(self, kulika):
        """Test validating service without get_status method."""

        @naga_service(
            name="NoStatusService",
            lord=NagaLord.TAKSHAKA,
        )
        class NoStatusService:
            pass

        errors = kulika.validate_service(NoStatusService)
        assert any("get_status" in e for e in errors)

    def test_service_with_drift_needs_handler(self, kulika):
        """Test service with drift_source needs as_handler."""

        @naga_service(
            name="DriftService",
            lord=NagaLord.SESHA,
            drift_source="state",
        )
        class DriftService:
            def get_status(self):
                return {}

        errors = kulika.validate_service(DriftService)
        assert any("as_handler" in e for e in errors)


class TestRegistration:
    """Service registration tests."""

    def test_register_valid_service(self, kulika):
        """Test registering a valid service."""

        @naga_service(
            name="ValidService",
            lord=NagaLord.KALIYA,
            capabilities=[NagaCapability.ISOLATION],
        )
        class ValidService:
            def get_status(self):
                return {"healthy": True}

        success = kulika.register_service(ValidService)
        assert success is True
        assert kulika.is_registered("validservice")
        assert kulika._registration_count == 1

    def test_register_with_instance(self, kulika):
        """Test registering a service with instance."""

        @naga_service(
            name="InstanceService",
            lord=NagaLord.SHANKHA,
        )
        class InstanceService:
            def get_status(self):
                return {}

        instance = InstanceService()
        success = kulika.register_service(InstanceService, instance=instance)

        assert success is True
        assert kulika.get_service_instance("instanceservice") is instance

    def test_register_invalid_service(self, kulika):
        """Test registering an invalid service fails."""

        class InvalidService:
            pass

        success = kulika.register_service(InvalidService)
        assert success is False
        assert not kulika.is_registered("invalidservice")

    def test_unregister_service(self, kulika):
        """Test unregistering a service."""

        @naga_service(name="TempService", lord=NagaLord.PADMA)
        class TempService:
            def get_status(self):
                return {}

        kulika.register_service(TempService)
        assert kulika.is_registered("tempservice")

        success = kulika.unregister_service("tempservice")
        assert success is True
        assert not kulika.is_registered("tempservice")


class TestQueries:
    """Query API tests."""

    def test_get_all_manifests(self, kulika):
        """Test getting all manifests."""

        @naga_service(name="Service1", lord=NagaLord.SESHA)
        class Service1:
            def get_status(self):
                return {}

        @naga_service(name="Service2", lord=NagaLord.VASUKI)
        class Service2:
            def get_status(self):
                return {}

        kulika.register_service(Service1)
        kulika.register_service(Service2)

        manifests = kulika.get_all_manifests()
        assert len(manifests) == 2

    def test_get_services_by_capability(self, kulika):
        """Test querying by capability."""

        @naga_service(
            name="LedgerService",
            lord=NagaLord.SESHA,
            capabilities=[NagaCapability.LEDGER],
        )
        class LedgerService:
            def get_status(self):
                return {}

        @naga_service(
            name="NetworkService",
            lord=NagaLord.VASUKI,
            capabilities=[NagaCapability.NETWORK],
        )
        class NetworkService:
            def get_status(self):
                return {}

        kulika.register_service(LedgerService)
        kulika.register_service(NetworkService)

        ledger_services = kulika.get_services_by_capability("ledger")
        assert len(ledger_services) == 1
        assert ledger_services[0].name == "LedgerService"

    def test_get_services_by_lord(self, kulika):
        """Test querying by lord type."""

        @naga_service(name="SeshaLike", lord=NagaLord.SESHA)
        class SeshaLike:
            def get_status(self):
                return {}

        kulika.register_service(SeshaLike)

        sesha_services = kulika.get_services_by_lord(NagaLord.SESHA)
        assert len(sesha_services) == 1

    def test_get_services_by_domain(self, kulika):
        """Test querying by domain."""

        @naga_service(name="InfraService", lord=NagaLord.TAKSHAKA)
        class InfraService:
            def get_status(self):
                return {}

        @naga_service(name="GovService", lord=NagaLord.NARADA)
        class GovService:
            def get_status(self):
                return {}

        kulika.register_service(InfraService)
        kulika.register_service(GovService)

        infra = kulika.get_services_by_domain(NagaDomain.INFRASTRUCTURE)
        gov = kulika.get_services_by_domain(NagaDomain.GOVERNANCE)

        assert len(infra) == 1
        assert len(gov) == 1


class TestStatus:
    """Status API tests."""

    def test_get_status(self, kulika):
        """Test getting NAGA status."""
        status = kulika.get_status()

        assert status.healthy is True
        assert status.errors == 0

    def test_get_registry_status(self, kulika):
        """Test getting detailed registry status."""

        @naga_service(name="StatusTestService", lord=NagaLord.KULIKA)
        class StatusTestService:
            def get_status(self):
                return {}

        kulika.register_service(StatusTestService)

        status = kulika.get_registry_status()
        assert status["total_services"] == 1

    def test_validation_count_tracked(self, kulika):
        """Test that validation count is tracked."""
        manifest = NagaManifest(
            name="Test",
            lord=NagaLord.SESHA,
            domain=NagaDomain.INFRASTRUCTURE,
        )

        kulika.validate_manifest(manifest)
        kulika.validate_manifest(manifest)

        assert kulika._validation_count == 2


class TestClear:
    """Clear/reset tests."""

    def test_clear(self, kulika):
        """Test clearing all registrations."""

        @naga_service(name="ClearTestService", lord=NagaLord.SESHA)
        class ClearTestService:
            def get_status(self):
                return {}

        kulika.register_service(ClearTestService)
        assert kulika.is_registered("cleartestservice")

        kulika.clear()

        assert not kulika.is_registered("cleartestservice")
        assert kulika._validation_count == 0
        assert kulika._registration_count == 0
