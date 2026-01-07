import pytest

from vibe_core.naga.kulika import KulikaRegistry, NagaCapability, NagaDomain, NagaLord, naga_service


# Mock Service
@naga_service(
    name="TestService", lord=NagaLord.SESHA, domain=NagaDomain.INFRASTRUCTURE, capabilities=[NagaCapability.LEDGER]
)
class TestService:
    def get_status(self):
        return "OK"


class TestRegistryProtection:
    """Test Kulika Registry hardening."""

    def setup_method(self):
        self.registry = KulikaRegistry()
        self.registry.clear()

    def test_register_basic(self):
        """Service can be registered."""
        success = self.registry.register(TestService)
        assert success is True
        assert self.registry.is_registered("TestService")

    def test_register_overwrite_checks(self):
        """Registry prevents overwrites unless forced."""
        # 1. Register first time
        self.registry.register(TestService)

        # 2. Try to register again (default force=False)
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(TestService)

        # 3. Register with force=True
        success = self.registry.register(TestService, force=True)
        assert success is True

    def test_kulika_service_wrapper(self):
        """KulikaService wrapper catches checks."""
        from vibe_core.naga.services.kulika import KulikaService

        service = KulikaService(registry=self.registry)

        # 1. Register
        assert service.register_service(TestService) is True

        # 2. Re-register (should return False, catch ValueError)
        assert service.register_service(TestService) is False

        # 3. Force (should work)
        assert service.register_service(TestService, force=True) is True
