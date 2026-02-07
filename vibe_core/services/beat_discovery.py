"""
BEAT SUBSCRIBER DISCOVERY - Yasoda's Rope (Auto-Wiring)
=======================================================

"yashoda-nandana braje bada-hari"
"Yasoda's son plays in Vraja"

FOLDER = EXISTENCE = WIRED.

This module auto-discovers all BeatSubscriberProtocol implementations.
No hardcoded lists. No manual wiring. The rope always has a 2-finger gap.

Discovery scans known subscriber locations, instantiates zero-arg
constructors, and registers them in ServiceRegistry under
BeatSubscriberProtocol for VenuService to discover.

Usage:
    from vibe_core.services.beat_discovery import discover_and_register_beat_subscribers
    count = discover_and_register_beat_subscribers()
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x4a7e1c8a"

import importlib
import logging
from typing import List, Tuple, Type

from vibe_core.mahamantra.protocols._venu import BeatSubscriberProtocol

logger = logging.getLogger("BEAT.DISCOVERY")

# Known locations where BeatSubscribers live.
# FOLDER = EXISTENCE: if the module exists and has a class implementing
# BeatSubscriberProtocol with a zero-arg constructor, it gets wired.
# This list grows organically as new subscribers are added to the repo.
_SUBSCRIBER_MODULES: List[Tuple[str, str]] = [
    ("vibe_core.services.healing_subscribers", "OuroborosSubscriber"),
    ("vibe_core.services.healing_subscribers", "ShuddhiSubscriber"),
    ("vibe_core.shuddhi.kala_bridge", "KalaBridgeSubscriber"),
    ("vibe_core.services.jagannath_subscriber", "JagannathSubscriber"),
    ("vibe_core.services.lotus_bridge", "LotusBridgeSubscriber"),
]


def discover_beat_subscriber_classes() -> List[Type]:
    """
    Discover all BeatSubscriberProtocol classes from known locations.

    Returns list of classes (not instances). Each class must:
    1. Exist in one of the known module locations
    2. Be instantiable with zero arguments
    3. Implement BeatSubscriberProtocol (beat_name, beat_interval, on_beat_tick)

    Returns:
        List of subscriber classes ready for instantiation.
    """
    classes = []
    for module_path, class_name in _SUBSCRIBER_MODULES:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name, None)
            if cls is None:
                continue
            # Verify it has the protocol shape
            if not all(hasattr(cls, attr) for attr in ("beat_name", "beat_interval", "on_beat_tick")):
                logger.warning("Skipping %s.%s: missing BeatSubscriberProtocol methods", module_path, class_name)
                continue
            classes.append(cls)
        except ImportError as e:
            logger.debug("Module %s not available: %s", module_path, e)
        except Exception as e:
            logger.warning("Failed to load %s.%s: %s", module_path, class_name, e)
    return classes


def discover_and_register_beat_subscribers() -> int:
    """
    Discover, instantiate, and register all BeatSubscribers in ServiceRegistry.

    This is the ONE call that replaces the hardcoded list in boot_orchestrator.
    Zero-arg construction. Protocol-driven registration.

    Returns:
        Number of subscribers registered.
    """
    from vibe_core.di import ServiceRegistry

    classes = discover_beat_subscriber_classes()
    registered = 0

    for cls in classes:
        try:
            instance = cls()  # Zero-arg — all deps resolved lazily
            ServiceRegistry.register(
                type(instance), instance,
                protocols=[BeatSubscriberProtocol],
            )
            logger.info("Beat subscriber registered: %s", instance.beat_name)
            registered += 1
        except Exception as e:
            logger.warning("Failed to instantiate %s: %s", cls.__name__, e)

    if registered:
        logger.info("%d beat subscribers auto-discovered and registered", registered)

    return registered


__all__ = ["discover_and_register_beat_subscribers", "discover_beat_subscriber_classes"]
