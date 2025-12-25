"""
OPUS-307 D+++: Unified Capability Registry

THE SINGLE SOURCE OF TRUTH for all executable capabilities.
No more "is this a tool or circuit?" - just ask the registry.

Shabda → UnifiedRegistry.get(id) → Pratyaya → Karma

This unifies:
- Tools (ATOMIC) - single actions
- Circuits (MOLECULAR) - state machines
- Agents (ORGANIC) - autonomous entities (future)
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.capability import (
    CapabilityMeta,
    CapabilityResult,
    CapabilityType,
)

logger = logging.getLogger("UNIFIED_REGISTRY")


@dataclass
class ToolCapabilityAdapter:
    """Adapts a Tool to the Capability protocol."""

    tool: Any  # vibe_core.tools.tool_protocol.Tool

    @property
    def capability_id(self) -> str:
        return self.tool.name

    @property
    def capability_type(self) -> CapabilityType:
        return CapabilityType.ATOMIC

    @property
    def description(self) -> str:
        return self.tool.description

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return self.tool.parameters_schema

    def validate(self, parameters: Dict[str, Any]) -> None:
        return self.tool.validate(parameters)

    def execute(self, parameters: Dict[str, Any]) -> CapabilityResult:
        import time

        start = time.time()
        try:
            result = self.tool.execute(parameters)
            return CapabilityResult(
                success=result.success,
                output=result.output,
                error=result.error if hasattr(result, "error") else None,
                capability_id=self.capability_id,
                capability_type=self.capability_type,
                execution_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return CapabilityResult(
                success=False,
                error=str(e),
                capability_id=self.capability_id,
                capability_type=self.capability_type,
                execution_time_ms=(time.time() - start) * 1000,
            )


@dataclass
class CircuitCapabilityAdapter:
    """Adapts a Circuit to the Capability protocol."""

    circuit_id: str
    circuit_def: Dict[str, Any]
    meta: Any  # CircuitMeta

    @property
    def capability_id(self) -> str:
        return self.circuit_id

    @property
    def capability_type(self) -> CapabilityType:
        return CapabilityType.MOLECULAR

    @property
    def description(self) -> str:
        return self.meta.description if self.meta else ""

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return self.circuit_def.get("input_schema", {})

    def validate(self, parameters: Dict[str, Any]) -> None:
        pass

    def execute(self, parameters: Dict[str, Any]) -> CapabilityResult:
        import time

        start = time.time()
        try:
            from vibe_core.cortex.engines.circuit_engine import create_circuit_executor

            executor = create_circuit_executor(
                circuit_definition=self.circuit_def,
                kernel=None,
            )
            user_input = parameters.get("input", parameters.get("user_input", ""))
            result = executor.execute(user_input=user_input)

            return CapabilityResult(
                success=result.success,
                output=result.output,
                error=result.error if hasattr(result, "error") else None,
                capability_id=self.capability_id,
                capability_type=self.capability_type,
                execution_time_ms=(time.time() - start) * 1000,
                metadata={"final_state": result.final_state},
            )
        except Exception as e:
            return CapabilityResult(
                success=False,
                error=str(e),
                capability_id=self.capability_id,
                capability_type=self.capability_type,
                execution_time_ms=(time.time() - start) * 1000,
            )


class UnifiedRegistry:
    """
    THE UNIFIED REGISTRY - Discovers and manages all capabilities.

    FRACTAL PRINCIPLE: Tool, Circuit, Agent are all just "capabilities".
    The user shouldn't need to know the implementation type.

    Usage:
        registry = UnifiedRegistry.get_instance()
        registry.discover_all()

        # Get capability (don't care if tool or circuit)
        cap = registry.get("heal_codebase")
        result = cap.execute({"file": "main.py"})

        # List all capabilities
        for meta in registry.list_all():
            print(meta.capability_id, meta.capability_type)
    """

    _instance: Optional["UnifiedRegistry"] = None

    def __init__(self):
        self._capabilities: Dict[str, Any] = {}
        self._metadata: Dict[str, CapabilityMeta] = {}
        self._discovered = False

    @classmethod
    def get_instance(cls) -> "UnifiedRegistry":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def discover_all(self, force: bool = False) -> int:
        """
        Discover all capabilities from all sources.

        Returns total count.
        """
        if self._discovered and not force:
            return len(self._capabilities)

        self._capabilities.clear()
        self._metadata.clear()

        tool_count = self._discover_tools()
        circuit_count = self._discover_circuits()

        self._discovered = True
        total = tool_count + circuit_count
        logger.info(f"Discovered {total} capabilities ({tool_count} tools, {circuit_count} circuits)")
        return total

    def _discover_tools(self) -> int:
        """Discover all tools and adapt them."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.tool_discovery import ToolDiscovery

            discovery = ToolDiscovery(root_path=Path("."), services=ServiceRegistry)
            tools = discovery.discover_all_tools()

            count = 0
            for tool in tools:
                try:
                    adapter = ToolCapabilityAdapter(tool=tool)
                    cap_id = adapter.capability_id.lower()
                    self._capabilities[cap_id] = adapter
                    self._metadata[cap_id] = CapabilityMeta(
                        capability_id=adapter.capability_id,
                        capability_type=CapabilityType.ATOMIC,
                        description=adapter.description,
                        parameters_schema=adapter.parameters_schema,
                        tags=["tool"],
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to adapt tool {tool.name}: {e}")

            return count
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return 0

    def _discover_circuits(self) -> int:
        """Discover all circuits and adapt them."""
        try:
            from vibe_core.loaders.circuit_loader import CircuitLoader

            circuits, metadata = CircuitLoader.discover_and_load()

            count = 0
            for circuit_id, circuit_def in circuits.items():
                try:
                    meta = metadata.get(circuit_id)
                    adapter = CircuitCapabilityAdapter(
                        circuit_id=circuit_id,
                        circuit_def=circuit_def,
                        meta=meta,
                    )
                    cap_id = circuit_id.lower()
                    self._capabilities[cap_id] = adapter
                    self._metadata[cap_id] = CapabilityMeta(
                        capability_id=circuit_id,
                        capability_type=CapabilityType.MOLECULAR,
                        description=adapter.description,
                        parameters_schema=adapter.parameters_schema,
                        source_file=str(meta.file_path) if meta else "",
                        tags=["circuit", meta.circuit_type if meta else "unknown"],
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to adapt circuit {circuit_id}: {e}")

            return count
        except Exception as e:
            logger.error(f"Circuit discovery failed: {e}")
            return 0

    def get(self, capability_id: str) -> Optional[Any]:
        """
        Get a capability by ID.

        Pratyaya doesn't care if it's a tool or circuit.
        """
        if not self._discovered:
            self.discover_all()

        cap_id = capability_id.lower()
        return self._capabilities.get(cap_id)

    def get_meta(self, capability_id: str) -> Optional[CapabilityMeta]:
        """Get metadata for a capability."""
        if not self._discovered:
            self.discover_all()

        return self._metadata.get(capability_id.lower())

    def list_all(self) -> List[CapabilityMeta]:
        """List all capability metadata."""
        if not self._discovered:
            self.discover_all()

        return list(self._metadata.values())

    def list_by_type(self, capability_type: CapabilityType) -> List[CapabilityMeta]:
        """List capabilities of a specific type."""
        return [m for m in self.list_all() if m.capability_type == capability_type]

    def search(self, query: str) -> List[CapabilityMeta]:
        """Search capabilities by name or description."""
        query_lower = query.lower()
        return [
            m for m in self.list_all() if query_lower in m.capability_id.lower() or query_lower in m.description.lower()
        ]

    def exists(self, capability_id: str) -> bool:
        """Check if a capability exists."""
        return self.get(capability_id) is not None
