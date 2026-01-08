#!/usr/bin/env python3
"""
OPERATION SUDARSHANA 2.0: PROTOCOL FIRST
========================================
"Das Gesetz der Resonanz"

This script implements the Fractal Hull strategy by wrapping
services based on their implemented Universal Protocols.

It does NOT monkey-patch implementation methods.
It respects the Interface Segregation Principle.

Targets:
1. ReadWriteProtocol -> SYS_WAKE
2. SyncProtocol      -> ASSERT_TRUTH
3. EnforceProtocol   -> CHECK_DHARMA
4. InferProtocol     -> RESOLVE_REQ
5. StoreRecallProtocol -> COMMIT_LOG
"""

import logging
from typing import Any, Iterator, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.substrate import MantraOpCode, mantra_governed
from vibe_core.protocols.universal.enforce import EnforceProtocol
from vibe_core.protocols.universal.infer import InferProtocol
from vibe_core.protocols.universal.read_write import ReadWriteProtocol
from vibe_core.protocols.universal.store_recall import StoreRecallProtocol
from vibe_core.protocols.universal.sync import SyncProtocol

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SUDARSHANA")

# ==============================================================================
# 1. THE MANTRA (Divine Clock Signal)
# ==============================================================================


class MantraBase:
    """Base class for Mantra Wrappers to provide Resonance."""

    def resonate(self, opcode: MantraOpCode) -> bool:
        logger.info(f"🕉️  [MANTRA] {opcode.name} | Source: {self.__class__.__name__} | Cycle: HARE KRISHNA")
        return True


# ==============================================================================
# 2. THE WRAPPERS (Fractal Hulls)
# ==============================================================================


class MantraReadWrite(MantraBase, ReadWriteProtocol):
    """Wraps ReadWriteProtocol with SYS_WAKE."""

    def __init__(self, inner: ReadWriteProtocol):
        self._inner = inner

    @mantra_governed(MantraOpCode.SYS_WAKE)
    def read(self, key: str, context: Any = None) -> Any:
        return self._inner.read(key, context)

    @mantra_governed(MantraOpCode.SYS_WAKE)
    def write(self, key: str, value: Any, context: Any = None) -> None:
        self._inner.write(key, value, context)

    def exists(self, key: str, context: Any = None) -> bool:
        return self._inner.exists(key, context)


class MantraSync(MantraBase, SyncProtocol):
    """Wraps SyncProtocol with ASSERT_TRUTH."""

    def __init__(self, inner: SyncProtocol):
        self._inner = inner

    @mantra_governed(MantraOpCode.ASSERT_TRUTH)
    def sync(self, context: Any = None) -> Any:
        return self._inner.sync(context)

    def get_sync_status(self, context: Any = None) -> Any:
        return self._inner.get_sync_status(context)

    def is_synced(self, context: Any = None) -> bool:
        return self._inner.is_synced(context)


class MantraEnforce(MantraBase, EnforceProtocol):
    """Wraps EnforceProtocol with CHECK_DHARMA."""

    def __init__(self, inner: EnforceProtocol):
        self._inner = inner

    @mantra_governed(MantraOpCode.CHECK_DHARMA)
    def enforce(self, action: str, context: Any) -> Any:
        return self._inner.enforce(action, context)

    def check(self, action: str) -> bool:
        return self._inner.check(action)

    def get_rules(self) -> List[Any]:
        return self._inner.get_rules()


class MantraInfer(MantraBase, InferProtocol):
    """Wraps InferProtocol with RESOLVE_REQ."""

    def __init__(self, inner: InferProtocol):
        self._inner = inner

    @mantra_governed(MantraOpCode.RESOLVE_REQ)
    def infer(self, input: Any, fallback: Any = None) -> Any:
        return self._inner.infer(input, fallback)

    def classify(self, input: Any, fallback: Any = None) -> Any:
        return self._inner.classify(input, fallback)

    def evaluate(self, claim: str, context: Any = None, fallback: Any = None) -> Any:
        return self._inner.evaluate(claim, context, fallback)


class MantraStoreRecall(MantraBase, StoreRecallProtocol):
    """Wraps StoreRecallProtocol with COMMIT_LOG."""

    def __init__(self, inner: StoreRecallProtocol):
        self._inner = inner

    @mantra_governed(MantraOpCode.COMMIT_LOG)
    def store(self, key: str, value: Any, context: Any = None) -> None:
        self._inner.store(key, value, context)

    def recall(self, key: str, context: Any = None) -> Any:
        return self._inner.recall(key, context)

    def forget(self, key: str, context: Any = None) -> bool:
        return self._inner.forget(key, context)

    def get_memory_stats(self) -> Any:
        return self._inner.get_memory_stats()

    def list_keys(self, prefix: str = None, context: Any = None) -> Iterator[str]:
        return self._inner.list_keys(prefix, context)


# --- Capabilitiy Wrappers (RAMA_EXEC) ---

# We can't import Tool directly due to circular imports sometimes, using Any
from vibe_core.tools.tool_protocol import Tool


class MantraTool(MantraBase, Tool):
    """Wraps Tool Protocol with RAMA_EXEC (Work)."""

    def __init__(self, inner: Tool):
        # Forward basic attrs
        self._inner = inner

    @property
    def name(self) -> str:
        return self._inner.name

    @property
    def description(self) -> str:
        return self._inner.description

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return self._inner.parameters_schema

    def validate(self, parameters: dict[str, Any]) -> None:
        return self._inner.validate(parameters)

    @mantra_governed(MantraOpCode.EXEC_SERVICE)
    def execute(self, parameters: dict[str, Any]) -> Any:
        return self._inner.execute(parameters)


# ==============================================================================
# 3. FRACTALIZE (The Injection)
# ==============================================================================


def fractalize_registry():
    """
    Scans ServiceRegistry and wraps services that implement Universal Protocols.
    """
    logger.info("🌤️  OPERATION SUDARSHANA: FRACTALIZING SERVICE REGISTRY 🌤️")

    # We access the internal dictionary carefully (locking handled by registry usually, but here we access direct for surgery)
    services = ServiceRegistry.list_services()
    wrapped_count = 0

    for name, type_name in services.items():
        # Retrieve the actual instance
        with ServiceRegistry._lock:
            instance = ServiceRegistry._services.get(name)

        if not instance:
            continue

        # Check Protocols and Wrap
        wrapper = None

        # 1. READ/WRITE
        if isinstance(instance, ReadWriteProtocol) and not isinstance(instance, MantraBase):
            wrapper = MantraReadWrite(instance)
            logger.info(f"🌀 Wrapping {name} with MantraReadWrite")

        # 2. SYNC
        elif isinstance(instance, SyncProtocol) and not isinstance(instance, MantraBase):
            wrapper = MantraSync(instance)
            logger.info(f"🌀 Wrapping {name} with MantraSync")

        # 3. ENFORCE
        elif isinstance(instance, EnforceProtocol) and not isinstance(instance, MantraBase):
            wrapper = MantraEnforce(instance)
            logger.info(f"🌀 Wrapping {name} with MantraEnforce")

        # 4. INFER
        elif isinstance(instance, InferProtocol) and not isinstance(instance, MantraBase):
            wrapper = MantraInfer(instance)
            logger.info(f"🌀 Wrapping {name} with MantraInfer")

        # 5. STORE
        elif isinstance(instance, StoreRecallProtocol) and not isinstance(instance, MantraBase):
            wrapper = MantraStoreRecall(instance)
            logger.info(f"🌀 Wrapping {name} with MantraStoreRecall")

        # Apply Wrapper
        if wrapper:
            with ServiceRegistry._lock:
                ServiceRegistry._services[name] = wrapper
            wrapped_count += 1

    logger.info(f"✅ SERVICE REGISTRY: Wrapped {wrapped_count} services.")


def fractalize_capabilities():
    """
    Scans UnifiedRegistry and wraps Tools/Circuits that match our radar.
    """
    logger.info("🌤️  OPERATION SUDARSHANA: FRACTALIZING CAPABILITIES 🌤️")

    try:
        from vibe_core.unified_registry import ToolCapabilityAdapter, UnifiedRegistry

        registry = UnifiedRegistry.get_instance()
        # Ensure discovery happens
        total = registry.discover_all()
        logger.info(f"Discovered {total} capabilities to scan.")

        wrapped_caps = 0

        # Iterate over registry._capabilities directly
        for cap_id, adapter in registry._capabilities.items():
            # Tools (MantraTool)
            if isinstance(adapter, ToolCapabilityAdapter):
                tool_instance = adapter.tool
                if not isinstance(tool_instance, MantraBase):
                    wrapper = MantraTool(tool_instance)
                    adapter.tool = wrapper
                    logger.info(f"🌀 Wrapping Tool '{cap_id}' with MantraTool")
                    wrapped_caps += 1

            # Circuits? (For now, just Tools as requested "internal capabilitie toolset")

        logger.info(f"✅ UNIFIED REGISTRY: Wrapped {wrapped_caps} capabilities.")

    except ImportError:
        logger.error("Could not import UnifiedRegistry/ToolCapabilityAdapter")
    except Exception as e:
        logger.error(f"Error fractalizing capabilities: {e}")


def throw_discus():
    """Execute Full Sudarshana Operation."""
    fractalize_registry()
    fractalize_capabilities()


if __name__ == "__main__":
    throw_discus()
