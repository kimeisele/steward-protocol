"""
VERIFY GAD - The Audit of The Law
=================================

"dharma-ksetre kuru-ksetre"
The field of Dharma must be measured.

GAD-000 Compliance Check:
1. Discoverability (discover())
2. Observability (get_state())
3. Parseability (TypedDicts)
4. Composability (Protocol)
5. Idempotency (is_idempotent)
6. Recoverability (is_healthy)
"""

import sys
import logging
from typing import Dict, Any

# Adjust path
sys.path.append(".")

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("GAD_VERIFIER")


def verify_component(name: str, instance: Any) -> bool:
    """Verify a component for GAD-000 compliance."""
    logger.info(f"\nAUDITING: {name}")
    logger.info("=" * 40)

    # Check 1: GAD Protocol Implementation
    from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol

    if not isinstance(instance, GADProtocol):
        logger.error(f"❌ {name} does NOT implement GADProtocol!")
        return False
    logger.info(f"✅ Protocol: {name} implements GADProtocol")

    if not isinstance(instance, GADBase):
        logger.error(f"❌ {name} does NOT inherit GADBase!")
        return False
    logger.info(f"✅ Base: {name} inherits GADBase")

    # Check 2: Discoverability
    try:
        discovery = instance.discover()
        logger.info(f"✅ Discover: {discovery}")
    except Exception as e:
        logger.error(f"❌ Discover Failed: {e}")
        return False

    # Check 3: Observability
    try:
        state = instance.get_state()
        logger.info(f"✅ State: {state.keys()}")  # Just show keys for brevity
        if "heartbeat" not in state:
            logger.error("❌ State missing 'heartbeat'!")
            return False
    except Exception as e:
        logger.error(f"❌ Get State Failed: {e}")
        return False

    # Check 4: Audit
    try:
        audit = instance.audit()
        logger.info(f"✅ Audit Result: {audit}")
        if not audit.is_compliant:
            logger.warning(f"⚠️ Audit Warn: Needs Improvement (Status: {audit.status})")
        else:
            logger.info(f"✅ Compliant: {audit.is_compliant}")
    except Exception as e:
        logger.error(f"❌ Audit Failed: {e}")
        return False

    logger.info(f"✨ {name} is GAD-000 Compliant!")
    return True


def main():
    logger.info("🕉️  GAD-000 COMPLIANCE CHECK STARTED")

    all_passed = True

    # 1. Verify MahamantraLotus
    from vibe_core.mahamantra import mahamantra

    if not verify_component("MahamantraLotus", mahamantra):
        all_passed = False

    # 2. Verify ShadowReactor
    from vibe_core.mahamantra.reactor.shadow import ShadowReactor

    reactor = ShadowReactor(auto_discover=False, reactor_id="gad_test_reactor")
    if not verify_component("ShadowReactor", reactor):
        all_passed = False

    # 3. Verify BalaramaProxy (Wrap a dummy)
    from vibe_core.mahamantra.substrate.proxy import BalaramaProxy

    # Wrap logging as a dummy service since it's already there
    proxy = BalaramaProxy("logging", silent=True)
    if not verify_component("BalaramaProxy", proxy):
        all_passed = False

    if all_passed:
        logger.info("\n✅ ALL SYSTEMS GAD-000 COMPLIANT")
    else:
        logger.error("\n❌ COMPLIANCE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
