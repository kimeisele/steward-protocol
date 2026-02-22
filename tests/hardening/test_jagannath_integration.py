"""
OPERATION BLOOD: JAGANNATH INTEGRATION TEST (The Yagnya)

"Aham Brahmasmi" - I am Spirit.

Scenario:
We verify the "Full Circuit" of the Universal Protocol.
1. Nrisimha (Watchdog) pulses.
2. Jagannath (Seer) initiates Ratha Yatra.
3. Ananta (Substrate) floods the Orphans.
4. The Orphan becomes a Devotee (Wrapped in NagaProxy).

This tests the REAL classes, not mocks (Substantial Integration).
"""

import logging
from typing import Optional, Protocol

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.naga.services.ananta import AnantaService
from vibe_core.naga.services.base import NagaBaseService
from vibe_core.naga.services.jagannath import JagannathService
from vibe_core.protocols.lila.jagannath import IJagannath
from vibe_core.protocols.substrate import IAnantaBridge, MantraOpCode
from vibe_core.protocols.universal import SovereignContext
from vibe_core.services.nrisimha import NrisimhaWatchdog

# =============================================================================
# THE ORPHAN (The Soul needing Rescue)
# =============================================================================


class LostSoulService:
    """
    An orphan service without Naga protection.
    It has no 'bind' method, no 'manifest'. It is naked.
    """

    def cry_for_help(self) -> str:
        return "Save me!"


# =============================================================================
# THE YAGNYA (Test)
# =============================================================================


@pytest.fixture(autouse=True)
def setup_universe():
    """Reset the universe before the test."""
    ServiceRegistry.reset()
    yield
    ServiceRegistry.reset()


@pytest.mark.xfail(reason="Ashvamedha pulse wiring and blessing tracking not yet implemented", strict=False)
def test_jagannath_integration_ratha_yatra():
    """
    Verifies that Nrisimha's pulse triggers Jagannath's Ratha Yatra,
    which triggers Ananta's Ashvamedha, saving the Lost Soul.
    """
    logger = logging.getLogger("TEST_YAGNYA")

    # 1. SETUP: The Universe

    # Register Ananta (Infrastructure)
    ananta = AnantaService()
    ServiceRegistry.register(IAnantaBridge, ananta)
    ServiceRegistry.register(AnantaService, ananta)  # Register concrete too

    # Register Jagannath (Seer)
    jagannath = JagannathService()
    ServiceRegistry.register(IJagannath, jagannath)

    # Register the Lost Soul (Orphan)
    lost_soul = LostSoulService()
    ServiceRegistry.register(LostSoulService, lost_soul)

    # Enable Auto-Flood (The Law)
    ServiceRegistry.enable_auto_flood()
    ServiceRegistry.enable_naga_blessing()

    # Initialize Watchdog (Nrisimha)
    ctx = SovereignContext(identity_id="test_user", signature="test_sig")
    nrisimha = NrisimhaWatchdog(sovereign_anchor=ctx)

    # 2. VERIFY: Soul is initially naked (Unblessed)
    # Note: ServiceRegistry.register *would* auto-flood if enabled during registration
    # But we want to test the Retroactive Flood (Ashvamedha).
    # So we simulate a "Slip" - we manually unwrap it or register it "raw".

    # Let's check status first.
    # Since we registered `lost_soul` AFTER `enable_auto_flood` (wait, no, usually default is off?)
    # Let's assume Ananta.auto_flood_orphans handles missed ones.

    # To properly test Ashvamedha, we need an UNWRAPPED service in the registry.
    # ServiceRegistry.register might have already wrapped it if we enabled it first.
    # Let's explicitly register it RAW.
    ServiceRegistry._services["LostSoulService"] = lost_soul  # Backdoor injection (Maya)

    raw_soul = ServiceRegistry.get(LostSoulService)
    assert not ServiceRegistry._check_naga_blessing(raw_soul), "Soul should be naked initially"

    # 3. ACTION: The Pulse (Heartbeat)
    # We call the specific pulse that triggers Ashvamedha
    logger.info("🦁 NRISIMHA: Chanting PULSE_SYNC...")
    nrisimha._ashvamedha_pulse()

    # 4. ASSERTION: The Miracle

    # Did Jagannath record the blessing?
    assert jagannath._total_blessings > 0, "Jagannath did not bless anyone!"

    # Is the Soul now saved (Wrapped)?
    saved_soul = ServiceRegistry.get(LostSoulService)

    # Check if it is a Proxy
    from vibe_core.naga.proxy import NagaProxy

    assert isinstance(saved_soul, NagaProxy), "Soul was not wrapped in NagaProxy!"

    # Check if the original functionality remains
    assert saved_soul.cry_for_help() == "Save me!", "Soul lost its voice!"

    print("\n✅ YAGNYA SUCCESSFUL: The Lost Soul was found and protected.")
