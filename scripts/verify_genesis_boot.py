import logging
import sys

from vibe_core.cartridges.agent_city.dhruva.tools.genesis_keeper import GenesisKeeper

# Configure partial logging to see the "VEDIC BOOT" message
logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_hard_fork_boot():
    print("🔮 INVOKING GENESIS KEEPER...")
    keeper = GenesisKeeper()

    state = keeper.get_genesis_state()
    genesis_id = state.get("genesis_id")

    print(f"\n✨ BOOT REVEALED: {genesis_id}")

    if genesis_id == "GEN-001-HOLOGRAPHIC":
        print("✅ SUCCESS: System booted into v2.0 Holographic Reality.")
        sys.exit(0)
    else:
        print(f"❌ FAILURE: System trapped in Legacy Reality ({genesis_id}).")
        sys.exit(1)


if __name__ == "__main__":
    test_hard_fork_boot()
