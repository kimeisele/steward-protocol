from pathlib import Path

import pytest

# We need to import the module to patch its global variables
import vibe_core.steward.crypto
from vibe_core.naga.orchestrator import NagaOrchestrator
from vibe_core.phoenix.sections.naga.section_main import NagaConfig


class TestNagaIdentityPersistence:
    """
    Real persistence test for NagaOrchestrator (IMPL-214).
    Redirects .steward/keys to a temp location to verify actual file I/O operations
    without touching the user's real keys.
    """

    @pytest.fixture
    def mock_crypto_storage(self, tmp_path, monkeypatch):
        """
        Redirect crypto storage to a temp directory.
        This allows us to test the REAL load_or_generate_keys logic.
        """
        # Create temp key dir
        temp_keys = tmp_path / "keys"
        temp_keys.mkdir()

        # Monkeypatch the module constants
        monkeypatch.setattr(vibe_core.steward.crypto, "KEY_DIR", temp_keys)
        monkeypatch.setattr(vibe_core.steward.crypto, "PRIVATE_KEY_PATH", temp_keys / "private.pem")
        monkeypatch.setattr(vibe_core.steward.crypto, "PUBLIC_KEY_PATH", temp_keys / "public.pem")

        return temp_keys

    @pytest.fixture
    def minimal_config(self):
        config = NagaConfig()
        # Disable all services
        config.sesha.enabled = False
        config.takshaka.enabled = False
        config.vasuki.enabled = False
        config.kaliya.enabled = False
        config.narada.enabled = False
        config.chitragupta.enabled = False
        config.prahlad.enabled = False
        config.ananta.enabled = False
        config.flood.enabled = False
        config.commit_watcher.enabled = False
        config.cortex.enabled = False
        return config

    class StubLedger:
        """Minimal stub."""

        pass

    class StubCorrection:
        """Minimal stub."""

        pass

    def test_identity_persistence_across_boots(self, mock_crypto_storage, minimal_config):
        """
        Punarjanma Test: Verify identity persists across two Orchestrator initializations.
        This uses real file I/O through the redirected crypto module.
        """

        # --- BOOT 1: Generating Identity ---
        orch1 = NagaOrchestrator()
        orch1._initialize(
            ledger=self.StubLedger(), correction_orchestrator=self.StubCorrection(), config=minimal_config
        )

        fingerprint1 = orch1._identity.fingerprint
        assert fingerprint1 is not None
        assert len(fingerprint1) == 16

        # Verify keys were actually written to disk in our temp dir
        assert (mock_crypto_storage / "private.pem").exists()
        assert (mock_crypto_storage / "public.pem").exists()

        # --- BOOT 2: Loading Identity ---
        # Create a FRESH instance, but it should read from the same mock_crypto_storage
        orch2 = NagaOrchestrator()
        orch2._initialize(
            ledger=self.StubLedger(), correction_orchestrator=self.StubCorrection(), config=minimal_config
        )

        fingerprint2 = orch2._identity.fingerprint

        # --- VERIFICATION ---
        assert fingerprint2 == fingerprint1, "Identity changed between boots! Amnesia detected."
        assert orch1._identity.public_key == orch2._identity.public_key
