"""
Unified Loader System - VEDA-4 Pattern for ALL Item Types.

FRAKTAL PRINCIPLE:
    Agents, Plugins, Sections, Circuits - ALL follow the same pattern.
    One loader to rule them all.

VEDA-4 LOADER PATTERN:
    SHABDA   → scan_directory() + load_manifest()
    ARTHA    → validate_manifest()
    PRATYAYA → load_config() + check_dependencies()
    KARMA    → instantiate()

Usage:
    from vibe_core.loaders import UnifiedLoader, CircuitLoader

    # Discover all circuits from knowledge/circuits/
    circuits, meta = CircuitLoader.discover_and_load()

    # Get circuits for a trigger
    test_circuits = CircuitLoader.get_circuits_for_trigger("file_modified")
"""

from .action_loader import ActionLoader, ActionLoadError, ActionMetadata, ActionRegistry, IntentHandlerMap
from .analyzer_loader import AnalyzerLoader, AnalyzerLoadError, AnalyzerMetadata, AnalyzerRegistry
from .base_loader import ItemMeta, LoaderRegistry, UnifiedLoader
from .bridge_loader import BridgeLoader, BridgeLoadError, BridgeMetadata, BridgeRegistry
from .circuit_loader import CircuitLoader, CircuitMeta, CircuitMetadata, CircuitRegistry
from .code_module_loader import CodeMetadata, CodeModuleLoader, CodeModuleLoadError, CodeModuleMeta, CodeRegistry
from .handler_loader import HandlerLoader, HandlerLoadError, HandlerMetadata, HandlerRegistry
from .playbook_loader import PlaybookLoader, PlaybookMeta, PlaybookMetadata, PlaybookRegistry, PlaybookStage
from .sense_loader import SenseLoader, SenseLoadError, SenseMetadata, SenseRegistry
from .template_loader import TemplateLoader
from .tool_loader import ToolLoader, ToolLoadError, ToolMetadata, ToolRegistry

__all__ = [
    "UnifiedLoader",
    "ItemMeta",
    "LoaderRegistry",
    # Code Module Loader (VEDA-4 code-only pattern)
    "CodeModuleLoader",
    "CodeModuleMeta",
    "CodeModuleLoadError",
    "CodeRegistry",
    "CodeMetadata",
    # Action Loader (OPUS-100)
    "ActionLoader",
    "ActionLoadError",
    "ActionRegistry",
    "ActionMetadata",
    "IntentHandlerMap",
    # Analyzer Loader (OPUS-098)
    "AnalyzerLoader",
    "AnalyzerLoadError",
    "AnalyzerRegistry",
    "AnalyzerMetadata",
    # Sense Loader (OPUS-099)
    "SenseLoader",
    "SenseLoadError",
    "SenseRegistry",
    "SenseMetadata",
    # Bridge Loader (OPUS-171)
    "BridgeLoader",
    "BridgeLoadError",
    "BridgeRegistry",
    "BridgeMetadata",
    # Handler Loader (OPUS-171 Phase 5)
    "HandlerLoader",
    "HandlerLoadError",
    "HandlerRegistry",
    "HandlerMetadata",
    # Circuit Loader
    "CircuitLoader",
    "CircuitMeta",
    "CircuitRegistry",
    "CircuitMetadata",
    # Playbook Loader
    "PlaybookLoader",
    "PlaybookMeta",
    "PlaybookRegistry",
    "PlaybookMetadata",
    "PlaybookStage",
    # Template Loader
    "TemplateLoader",
    # Tool Loader (VEDA-4 wrapper around ToolDiscovery)
    "ToolLoader",
    "ToolLoadError",
    "ToolRegistry",
    "ToolMetadata",
]
