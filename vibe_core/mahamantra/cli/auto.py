"""
CLI AUTO - Krishna Discovers Everything
=======================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

ZERO REGISTRATION. ZERO MANUAL WIRING.

Krishna ALREADY KNOWS:
1. Position → Guardian (from _source.py truth table)
2. Guardian → Protocol (from mahamantra.protocols)
3. Protocol → Methods (introspection)
4. Methods → TypedDict returns (type hints)
5. TypedDict → CLIOutput fields (introspection)

Why would we TELL Krishna what He already knows?

USAGE:
    from vibe_core.mahamantra import cli_auto

    # Auto-discover ALL CLI capabilities from Protocol definitions
    cli_auto.discover_all()

    # Execute - routing is automatic
    result = cli_auto.execute("analyze", ["system"])

COMPARISON:
    BEFORE (manual registration - 1200+ lines):
        cli_engine.register(
            position=6,
            capabilities=[CLICapability(name="analyze", ...)],
            handlers={"analyze": handle_analyze}
        )
        # × 16 positions × 5+ commands each = ENTROPY

    AFTER (auto-discovery - 0 lines):
        cli_auto.discover_all()  # Called ONCE at boot
        # DONE. Krishna does the rest.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xb3e04d0e"  # GenesisByte: parampara % 37 == 0

import inspect
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    Union,
    get_type_hints,
    runtime_checkable,
)

logger = logging.getLogger(__name__)

# =============================================================================
# WATERTIGHT TYPE ALIASES - No Any allowed
# =============================================================================

# CLI-safe primitive types (what CLI args become)
CLIPrimitive = Union[str, int, float, bool]

# Method call arguments (converted from CLI strings)
CLICallArgs = Dict[str, CLIPrimitive]

# Method result types (what protocol methods return)
# Recursive definition for nested structures
MethodResultLeaf = Union[str, int, float, bool, None]
MethodResultList = List[Union[MethodResultLeaf, Dict[str, "MethodResultLeaf"]]]
MethodResultDict = Dict[str, Union[MethodResultLeaf, List[MethodResultLeaf]]]
MethodResult = Union[None, MethodResultDict, MethodResultList, Tuple[MethodResultLeaf, ...], str, int, float, bool]

# FIX: MahamantraLotus hat __call__ UND __getitem__ (Singularity nur __getitem__)
from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.cli.protocol import (
    # Chaitanya Lila Boundaries
    NAVADVIPA_LIMIT,
    PURI_LIMIT,
    CLICapability,
    CLIContext,
    CLIErrorCode,
    CLIOutput,
    CLIParameter,
    CLIResult,
)
from vibe_core.mahamantra.substrate.seed import MAHA_QUANTUM, PARAMPARA, WORDS

# =============================================================================
# VIBRATION ROUTING - MahaKirtan Orchestration (THE KING)
# =============================================================================
# Lazy-loaded to avoid circular imports at module load time
# Type hints use strings because these are lazy-loaded
_COMPRESSOR = None  # type: MahaCompression | None
_KIRTAN = None  # type: MahaKirtan | None


def _get_kirtan_orchestrator():  # returns tuple[MahaCompression, MahaKirtan]
    """
    Get the KING orchestration infrastructure (lazy singleton).

    MahaCompression → seed extraction (Kolmogorov complexity)
    MahaKirtan → full vibration compute (16-step × 7-beat orchestration)

    This is 512-bit Chaitanya Computing. Everything vibrates.
    """
    global _COMPRESSOR, _KIRTAN
    if _COMPRESSOR is None:
        from vibe_core.mahamantra.adapters.compression import MahaCompression
        from vibe_core.mahamantra.substrate.mantra import MahaKirtan

        _COMPRESSOR = MahaCompression()
        _KIRTAN = MahaKirtan(mod_space=MAHA_QUANTUM)
    return _COMPRESSOR, _KIRTAN


# =============================================================================
# AUTO-DISCOVERED METHOD INFO
# =============================================================================


@dataclass
class DiscoveredMethod:
    """
    A method discovered from a Protocol.

    This is DERIVED, not configured.
    """

    name: str
    position: int
    guardian: str
    parameters: List[CLIParameter]
    return_fields: List[str]  # TypedDict field names
    doc: str


# =============================================================================
# THE DISCOVERY ENGINE
# =============================================================================


class CLIAutoDiscovery:
    """
    Auto-discover CLI capabilities from Protocol definitions.

    ZERO MANUAL WIRING. Krishna knows everything.
    """

    def __init__(self) -> None:
        # Discovered methods: position → {method_name → DiscoveredMethod}
        self._methods: Dict[int, Dict[str, DiscoveredMethod]] = {}

        # Null implementations: position → instance
        self._nulls: Dict[int, object] = {}

        # Keywords → position (for routing)
        self._keywords: Dict[str, int] = {}

        # Discovered?
        self._discovered: bool = False

    # =========================================================================
    # DISCOVERY (One-time at boot)
    # =========================================================================

    def discover_all(self) -> int:
        """
        Discover ALL CLI capabilities from 16 positions (12 mahajanas + 4 avataras).

        Returns number of methods discovered.

        This is called ONCE at boot. Krishna does the work.
        """
        if self._discovered:
            return sum(len(m) for m in self._methods.values())

        total = 0
        for position in range(WORDS):
            count = self._discover_position(position)
            total += count

        self._discovered = True
        return total

    def _discover_position(self, position: int) -> int:
        """Discover methods for a single position via Royal Hunt."""
        import importlib

        # Get guardian name from truth table
        pos_info = mahamantra[position]
        guardian_name = pos_info.guardian.value

        # 1. THE ROYAL HUNT - Find the service class and its module
        service_class = None
        service_class_name = f"{guardian_name.capitalize()}Service"

        jungles = [
            f"vibe_core.mahamantra.{pos_info.quarter.name.lower()}.{guardian_name}",
            f"vibe_core.protocols.mahajanas.{guardian_name}.service",
            f"vibe_core.naga.services.{guardian_name}",
            f"vibe_core.services.{guardian_name}",
            f"vibe_core.protocols.mahajanas.{guardian_name}",
        ]

        target_module = None
        for jungle in jungles:
            try:
                module = importlib.import_module(jungle)
                candidate = getattr(module, service_class_name, None)
                if candidate and isinstance(candidate, type):
                    service_class = candidate
                    target_module = module
                    break
                # If no class found, maybe it's a protocol module
                if not target_module:
                    target_module = module
            except ImportError:
                continue

        if not target_module:
            print(f"DEBUG: Failed to load module for position {position}: {guardian_name}")
            return 0

        # 2. Find Null implementation (for CLI execution without side effects)
        null_class_name = f"Null{guardian_name.capitalize()}"
        null_class = getattr(target_module, null_class_name, None)
        if null_class is None:
            # Try alternate naming
            for name in dir(target_module):
                if name.startswith("Null") and name != "NullCognitive":
                    null_class = getattr(target_module, name)
                    break

        if null_class is not None:
            try:
                self._nulls[position] = null_class()
            except Exception as e:
                print(f"DEBUG: Failed to instantiate Null class for position {position}: {e}")

        # 3. Find Protocol class
        protocol_class = self._find_protocol(target_module, guardian_name)
        if protocol_class is None:
            # Try finding protocol in the protocol base module explicitly
            try:
                proto_base_mod = importlib.import_module(f"vibe_core.protocols.mahajanas.{guardian_name}")
                protocol_class = self._find_protocol(proto_base_mod, guardian_name)
            except ImportError as _exc:
                logger.exception("Unexpected error: %s", _exc)

        if protocol_class is None:
            return 0

        # Discover methods from Protocol
        self._methods[position] = {}
        count = 0

        for method_name in self._get_protocol_methods(protocol_class):
            method_info = self._introspect_method(
                protocol_class,
                method_name,
                position,
                guardian_name,
            )
            if method_info:
                self._methods[position][method_name] = method_info
                # Priority Routing: If multiple Mahajanas have the same intent,
                # the one earlier in the 16-step cycle wins (unless weighted).
                if method_name not in self._keywords:
                    self._keywords[method_name] = position
                count += 1

        return count

    def _find_protocol(self, module: object, guardian_name: str) -> Optional[Type]:
        """Find the Protocol class in a module."""
        # Try standard naming: {Guardian}Protocol
        protocol_name = f"{guardian_name.capitalize()}Protocol"
        protocol_class = getattr(module, protocol_name, None)

        if protocol_class is not None and self._is_protocol(protocol_class):
            return protocol_class

        # Scan for any Protocol
        for name in dir(module):
            if name.endswith("Protocol") and not name.startswith("_"):
                cls = getattr(module, name)
                if self._is_protocol(cls) and name != "WorkerProtocol":
                    return cls

        return None

    def _is_protocol(self, cls: Type) -> bool:
        """Check if class is a typing.Protocol."""
        return hasattr(cls, "__protocol_attrs__") or (
            hasattr(cls, "__mro__") and Protocol in getattr(cls, "__mro__", [])
        )

    def _get_protocol_methods(self, protocol_class: Type) -> List[str]:
        """Get method names from a Protocol class."""
        methods = []

        # Get all methods that aren't dunder or private
        for name in dir(protocol_class):
            if name.startswith("_"):
                continue
            attr = getattr(protocol_class, name, None)
            if callable(attr) or isinstance(attr, property):
                # Skip class methods and properties used for metadata
                if name in ("position_index", "guardian", "opcode", "quarter"):
                    continue
                methods.append(name)

        return methods

    def _introspect_method(
        self,
        protocol_class: Type,
        method_name: str,
        position: int,
        guardian_name: str,
    ) -> Optional[DiscoveredMethod]:
        """Introspect a method from Protocol to build DiscoveredMethod."""
        method = getattr(protocol_class, method_name, None)
        if method is None:
            return None

        # Get signature
        try:
            sig = inspect.signature(method)
        except (ValueError, TypeError):
            return None

        # Build parameters (skip self)
        parameters: List[CLIParameter] = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = "string"  # default
            annotation = param.annotation
            if annotation is not inspect.Parameter.empty:
                if annotation is int:
                    param_type = "integer"
                elif annotation is float:
                    param_type = "float"
                elif annotation is bool:
                    param_type = "boolean"

            required = param.default == inspect.Parameter.empty
            default = None if required else param.default

            parameters.append(
                CLIParameter(
                    name=param_name,
                    param_type=param_type,
                    required=required,
                    default=default,
                )
            )

        # Get return type fields (if TypedDict)
        return_fields: List[str] = []
        try:
            hints = get_type_hints(method)
            return_type = hints.get("return")
            if return_type and hasattr(return_type, "__annotations__"):
                return_fields = list(return_type.__annotations__.keys())
        except Exception as _exc:
            logger.exception("Unexpected error: %s", _exc)

        # Get docstring
        doc = method.__doc__ or f"{method_name} - auto-discovered"

        return DiscoveredMethod(
            name=method_name,
            position=position,
            guardian=guardian_name,
            parameters=parameters,
            return_fields=return_fields,
            doc=doc.strip().split("\n")[0],  # First line only
        )

    # =========================================================================
    # EXECUTION (Krishna routes and executes)
    # =========================================================================

    def execute(
        self,
        command: str,
        args: Optional[List[str]] = None,
    ) -> CLIResult:
        """
        Execute a CLI command via auto-discovered method.

        Krishna routes to the right mahajana and calls the Protocol method.
        """
        if not self._discovered:
            self.discover_all()

        args = args or []
        cmd_lower = command.lower()

        # Find position and method
        position = self._get_position(cmd_lower)
        if position is None:
            return CLIResult.fail(
                CLIErrorCode.UNKNOWN_COMMAND,
                f"Unknown command: {command}",
                command=command,
            )

        method_name = self._get_method_name(position, cmd_lower)
        if method_name is None:
            return CLIResult.fail(
                CLIErrorCode.UNKNOWN_COMMAND,
                f"No method for command: {command}",
                command=command,
                position=str(position),
            )

        # Get null implementation
        null_impl = self._nulls.get(position)
        if null_impl is None:
            return CLIResult.fail(
                CLIErrorCode.NOT_IMPLEMENTED,
                f"No implementation at position {position}",
                command=command,
                position=str(position),
            )

        # Get method
        method = getattr(null_impl, method_name, None)
        if method is None:
            return CLIResult.fail(
                CLIErrorCode.NOT_IMPLEMENTED,
                f"Method not found: {method_name}",
                command=command,
                method=method_name,
            )

        # Build arguments from CLI args
        method_info = self._methods[position].get(method_name)
        call_args = self._build_call_args(args, method_info)

        # Execute
        try:
            result = method(**call_args)
        except Exception as e:
            return CLIResult.fail(
                CLIErrorCode.INTERNAL_ERROR,
                str(e),
                command=command,
                method=method_name,
            )

        # Convert result to CLIOutput
        output = self._result_to_output(result)

        return CLIResult.ok(output)

    def _get_position(self, command: str) -> Optional[int]:
        """
        Get position via FULL MAHA COMPUTING PIPELINE.

        THE REAL FLOW:
            Input → MahaCompression (with MahaLLM + MahaKirtan + MahaResonator)
                  → Seed with embedded SEMANTIC CATEGORY
                  → Position = Category (semantic routing!)

        Same semantic intent = Same category = Same position.
        "analyze this" and "please analyze" → BOTH to ANALYZE position!
        """
        compressor, kirtan = _get_kirtan_orchestrator()

        # 1. FULL MAHA COMPRESSION (now uses MahaLLM + MahaKirtan + MahaResonator!)
        compression_result = compressor.compress(command)
        seed = compression_result.seed

        # 2. Extract SEMANTIC CATEGORY from seed (embedded in top 8 bits)
        # Category comes from MahaLLM.route_text() - SEMANTIC classification!
        category = (seed >> 24) & 0xF  # Top 4 bits = category (0-15)

        # 3. Position = Category (SEMANTIC ROUTING!)
        # MahaKirtan transform adds nuance but Category determines PRIMARY routing
        position = category % WORDS

        # The full pipeline is:
        # - MahaLLM classifies intent → Category (SEMANTIC)
        # - MahaKirtan transforms → adds harmonic texture
        # - MahaResonator finds attractor → adds stability
        # - Category determines Position → CONSISTENT SEMANTIC ROUTING

        return position

    def _get_method_name(self, position: int, command: str) -> Optional[str]:
        """Get method name for a command at a position."""
        methods = self._methods.get(position, {})

        # Exact match
        if command in methods:
            return command

        # Substring match
        for name in methods:
            if name in command or command.startswith(name):
                return name

        # Default to first method if any
        if methods:
            return list(methods.keys())[0]

        return None

    def _build_call_args(
        self,
        args: List[str],
        method_info: Optional[DiscoveredMethod],
    ) -> CLICallArgs:
        """Build method call arguments from CLI args."""
        if not method_info or not method_info.parameters:
            return {}

        call_args: CLICallArgs = {}

        for i, param in enumerate(method_info.parameters):
            if i < len(args):
                value = args[i]
                # Convert type
                if param.param_type == "integer":
                    value = int(value)
                elif param.param_type == "float":
                    value = float(value)
                elif param.param_type == "boolean":
                    value = value.lower() in ("true", "1", "yes")
                call_args[param.name] = value
            elif param.default is not None:
                call_args[param.name] = param.default
            elif not param.required:
                # Optional param without default
                pass

        return call_args

    def _result_to_output(self, result: MethodResult) -> CLIOutput:
        """
        Convert method result to CLIOutput with Chaitanya Lila Boundaries.

        LILA ENFORCEMENT:
            - Max NAVADVIPA_LIMIT (24) items per response
            - CLIOutput.add() automatically enforces this
            - has_more flag indicates truncation
        """
        output = CLIOutput()

        if result is None:
            output.add("status", "complete")
            return output

        # If dict-like (TypedDict result)
        if isinstance(result, dict):
            for key, value in result.items():
                # Check capacity before adding
                if output.is_at_capacity:
                    break

                # Convert to CLI-safe types
                if isinstance(value, (str, int, float, bool)):
                    output.add(key, value)
                elif isinstance(value, list):
                    output.add(key, len(value))
                    # Lila boundary: max NAVADVIPA_LIMIT items in preview
                    preview_items = value[:NAVADVIPA_LIMIT]
                    output.add(f"{key}_items", ",".join(str(v) for v in preview_items))
                    if len(value) > NAVADVIPA_LIMIT:
                        output.add(f"{key}_truncated", True)
                elif value is None:
                    output.add(key, "null")
                else:
                    output.add(key, str(value))
            return output

        # If list - Lila boundary enforced automatically by output.add()
        if isinstance(result, (list, tuple)):
            output.add("count", len(result))
            output.add("lila_limit", NAVADVIPA_LIMIT)
            for i, item in enumerate(result):
                # CLIOutput.add() will stop at NAVADVIPA_LIMIT and set has_more
                output.add(f"item_{i}", str(item))
            return output

        # Scalar
        output.add("result", result)
        return output

    # =========================================================================
    # INTROSPECTION (GAD-000 Discoverability)
    # =========================================================================

    def get_capabilities(self, position: Optional[int] = None) -> List[CLICapability]:
        """Get auto-discovered capabilities."""
        if not self._discovered:
            self.discover_all()

        capabilities: List[CLICapability] = []

        positions = [position] if position is not None else range(WORDS)

        for pos in positions:
            methods = self._methods.get(pos, {})
            for method_info in methods.values():
                cap = CLICapability(
                    name=method_info.name,
                    purpose=method_info.doc,
                    parameters=method_info.parameters,
                    mahajana_position=method_info.position,
                    keywords=[method_info.name, method_info.guardian],
                )
                capabilities.append(cap)

        return capabilities

    def get_stats(self) -> Dict[str, int]:
        """Get discovery statistics."""
        return {
            "positions_discovered": len(self._methods),
            "total_methods": sum(len(m) for m in self._methods.values()),
            "total_keywords": len(self._keywords),
            "null_implementations": len(self._nulls),
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"CLIAutoDiscovery(methods={stats['total_methods']}, discovered={self._discovered})"


# =============================================================================
# SINGLETON
# =============================================================================

cli_auto = CLIAutoDiscovery()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def discover() -> int:
    """Discover all CLI capabilities. Returns count."""
    return cli_auto.discover_all()


def execute(command: str, args: Optional[List[str]] = None) -> CLIResult:
    """Execute a CLI command via auto-discovery."""
    return cli_auto.execute(command, args)


def capabilities(position: Optional[int] = None) -> List[CLICapability]:
    """Get discovered capabilities."""
    return cli_auto.get_capabilities(position)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CLIAutoDiscovery",
    "cli_auto",
    "DiscoveredMethod",
    "discover",
    "execute",
    "capabilities",
]
