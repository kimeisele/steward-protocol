"""
TEST: THE ANANTA LOOP.

Dieser Test beweist, dass 'Dead Matter' (Legacy Context) durch die Berührung
von Ananta Shesha (CLI) lebendig wird (Sovereign Execution).
"""

import pytest

from vibe_core.protocols.command import CommandContext
from vibe_core.protocols.universal.bridge import MayavadError
from vibe_core.protocols.universal.cli import AnantaResponse, AnantaShesha


def test_legacy_redemption():
    """
    Kann ein alter Legacy-Context über die Brücke gehen und dienen?
    """
    # 1. SETUP (The Old World)
    legacy_ctx = CommandContext(caller="old_script_v1", metadata={})
    ananta = AnantaShesha()

    # 2. ACTION (The Chant)
    # Wir rufen 'read file' auf. Yamaraja sollte das erlauben (kein Ugra Karma).
    response = ananta.chant(legacy_ctx, "read file", payload="readme.md")

    # 3. ASSERTION (The Truth)
    print(f"\nResponse: {response}")
    assert response.success is True
    assert "Executed read file" in response.message
    assert response.tattva_score == 1.0
    print("✅ Legacy Context redeemed via Ananta.")


def test_mayavad_rejection():
    """
    Kann Ananta einen Betrüger (Int/Dict) erkennen?
    """
    ananta = AnantaShesha()
    fake_ctx = {"i_am": "god"}  # Dict is not a Context!

    response = ananta.chant(fake_ctx, "destroy_universe")

    # Ananta catches MayavadError and returns AnantaResponse(success=False)
    print(f"\nResponse: {response}")
    assert response.success is False
    assert "ANANTA REJECTS" in response.message
    assert "Bridge Breach" in response.message
    print("✅ Mayavad successfully rejected.")


def test_grace_elevation():
    """
    Kann Ananta Gnade (Grace) vermitteln via Steward?
    """
    legacy_ctx = CommandContext(caller="desperate_user", metadata={})
    ananta = AnantaShesha()

    # Trigger Grace: Ugra Karma + Grace Keyword (system_crash)
    # Yamaraja -> VERDICT.ELEVATED -> Steward -> EXECUTES
    response = ananta.chant(legacy_ctx, "destroy system_crash logs", payload=None)

    print(f"\nResponse: {response}")
    assert response.success is True  # Because Grace allowed execution!
    assert "Verdict.ELEVATED" in response.message
    print("✅ Grace Execution successful.")


if __name__ == "__main__":
    test_legacy_redemption()
    test_mayavad_rejection()
    test_grace_elevation()
    print("\n✅ ANANTA LOOP VERIFIED.")
