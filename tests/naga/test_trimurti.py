from unittest.mock import MagicMock, patch

import pytest

from vibe_core.naga.components.bootloader import NagaBootloader
from vibe_core.naga.components.destructor import NagaDestructor
from vibe_core.naga.components.kernel import NagaKernel
from vibe_core.naga.identity import NagaIdentity
from vibe_core.naga.kulika import KulikaRegistry
from vibe_core.phoenix.sections.naga.section_main import NagaConfig


class TestTrimurti:
    @pytest.fixture
    def mock_identity(self):
        identity = MagicMock(spec=NagaIdentity)
        identity.fingerprint = "mock_fingerprint"
        return identity

    @pytest.fixture
    def mock_registry(self):
        return MagicMock(spec=KulikaRegistry)

    def test_vishnu_kernel_is_immutable_dataclass(self, mock_identity, mock_registry):
        """Verify NagaKernel acts as an immutable container."""
        # Create kernel
        kernel = NagaKernel(identity=mock_identity, registry=mock_registry, sesha=MagicMock())

        # Verify attributes
        assert kernel.identity == mock_identity
        assert kernel.registry == mock_registry
        assert kernel.sesha is not None
        assert kernel.vasuki is None

        # Verify immutability (frozen dataclass)
        with pytest.raises(FrozenInstanceError):
            kernel.vasuki = MagicMock()

    def test_brahma_bootloader_creation(self):
        """Verify NagaBootloader creates a valid Kernel."""
        # Mock load_or_generate_keys and NagaIdentity.from_keys to avoid disk I/O
        with (
            patch("vibe_core.naga.components.bootloader.load_or_generate_keys") as mock_keys,
            patch("vibe_core.naga.components.bootloader.NagaIdentity") as mock_naga_identity_cls,
            patch("vibe_core.naga.scanner.NaradaScanner"),
        ):
            mock_keys.return_value = (b"priv", b"pub")
            mock_identity = MagicMock()
            mock_naga_identity_cls.from_keys.return_value = mock_identity

            config = NagaConfig()
            # Disable most services for speed/mocking simplicity
            config.sesha.enabled = False
            config.vasuki.enabled = False
            config.takshaka.enabled = False
            config.cortex.enabled = False

            kernel = NagaBootloader.boot(config)

            assert isinstance(kernel, NagaKernel)
            assert kernel.identity == mock_identity
            assert kernel.registry is not None
            # Sesha disabled
            assert kernel.sesha is None

    def test_shiva_destructor_shutdown(self, mock_identity, mock_registry):
        """Verify NagaDestructor calls stop on services."""
        # Mock services
        mock_flood = MagicMock()
        mock_watcher = MagicMock()

        kernel = NagaKernel(
            identity=mock_identity, registry=mock_registry, flood_manager=mock_flood, commit_watcher=mock_watcher
        )

        destructor = NagaDestructor(kernel)

        # Execute Tandava
        with patch("vibe_core.naga.components.destructor.get_state_service") as mock_get_state:
            mock_state_service = MagicMock()
            mock_get_state.return_value = mock_state_service

            destructor.stop()

            # Verify stops called
            mock_flood.stop.assert_called_once()
            mock_watcher.stop.assert_called_once()
            mock_state_service.commit.assert_called_once()


# Need to import FrozenInstanceError from dataclasses
from dataclasses import FrozenInstanceError
