"""
DIW SUBSCRIBER DISCOVERY - The Flute Finds Its Dancers
======================================================

Auto-discovers all DIWSubscriberProtocol implementations.
Registers them in ServiceRegistry for VenuService.discover_subscribers().

Same pattern as beat_discovery.py — FOLDER=EXISTENCE.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x4a7e1c8a"

import importlib
import logging
from typing import List, Tuple, Type

from vibe_core.mahamantra.protocols._venu import DIWSubscriberProtocol

logger = logging.getLogger("DIW.DISCOVERY")

# Known locations where DIW subscribers live.
_SUBSCRIBER_MODULES: List[Tuple[str, str]] = [
    ("vibe_core.services.diw_telemetry", "DIWTelemetrySubscriber"),
]


def discover_diw_subscriber_classes() -> List[Type]:
    """Discover all DIWSubscriberProtocol classes from known locations."""
    classes = []
    for module_path, class_name in _SUBSCRIBER_MODULES:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name, None)
            if cls is None:
                continue
            if not all(hasattr(cls, attr) for attr in ("subscriber_name", "on_diw")):
                logger.warning("Skipping %s.%s: missing DIWSubscriberProtocol methods", module_path, class_name)
                continue
            classes.append(cls)
        except ImportError as e:
            logger.debug("Module %s not available: %s", module_path, e)
        except Exception as e:
            logger.warning("Failed to load %s.%s: %s", module_path, class_name, e)
    return classes


def discover_and_register_diw_subscribers() -> int:
    """Discover, instantiate, and register all DIW subscribers in ServiceRegistry."""
    from vibe_core.di import ServiceRegistry

    classes = discover_diw_subscriber_classes()
    registered = 0

    for cls in classes:
        try:
            instance = cls()
            ServiceRegistry.register(
                type(instance),
                instance,
                protocols=[DIWSubscriberProtocol],
            )
            logger.info("DIW subscriber registered: %s", instance.subscriber_name)
            registered += 1
        except Exception as e:
            logger.warning("Failed to instantiate %s: %s", cls.__name__, e)

    # NaradaBridge: singleton — connects VenuOrchestrator ↔ EventBus.
    # Must use get_narada_bridge() to ensure one instance per process.
    try:
        from vibe_core.services.narada_bridge import NaradaBridge, get_narada_bridge

        bridge = get_narada_bridge()
        ServiceRegistry.register(
            NaradaBridge,
            bridge,
            protocols=[DIWSubscriberProtocol],
        )
        logger.info("DIW subscriber registered: %s", bridge.subscriber_name)
        registered += 1
    except Exception as e:
        logger.warning("Failed to register NaradaBridge: %s", e)

    if registered:
        logger.info("%d DIW subscribers auto-discovered and registered", registered)

    return registered


__all__ = ["discover_and_register_diw_subscribers", "discover_diw_subscriber_classes"]
