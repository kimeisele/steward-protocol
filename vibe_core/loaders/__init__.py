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

from .analyzer_loader import AnalyzerLoader, AnalyzerLoadError, AnalyzerMetadata, AnalyzerRegistry
from .base_loader import ItemMeta, LoaderRegistry, UnifiedLoader
from .circuit_loader import CircuitLoader, CircuitMeta, CircuitMetadata, CircuitRegistry
from .playbook_loader import PlaybookLoader, PlaybookMeta, PlaybookMetadata, PlaybookRegistry, PlaybookStage
from .sense_loader import SenseLoader, SenseLoadError, SenseMetadata, SenseRegistry
from .template_loader import TemplateLoader

__all__ = [
    "UnifiedLoader",
    "ItemMeta",
    "LoaderRegistry",
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
]
