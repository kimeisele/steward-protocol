"""
OPUS-159: Vibe Core Genesis - The Central Stadtamt

Auto-generates GAD-000 compliant infrastructure for all module types.

The Lasagna Architecture:
    MANAS (Consumer) → calls →
    Engineer (Builder) → uses →
    GenesisService (Front Desk) → coordinates →
    Compliance + Templates + Builder

Usage:
    from vibe_core.genesis import GenesisService, ModuleType

    # Get the singleton service
    genesis = GenesisService.get_instance()

    # Ensure a module is compliant (auto-repairs)
    result = genesis.ensure_compliance(path, ModuleType.PLUGIN)

    # Scaffold a new module
    result = genesis.scaffold_new(path, ModuleType.CARTRIDGE, {"name": "MyAgent"})

    # Quick compliance check
    is_ok = genesis.quick_check(path)

"Feinste Lasagne, vegetarisch, ohne Zwiebeln, beste Bio-Zutaten."
"""

from .builder import InfrastructureBuilder
from .compliance import ComplianceBureau
from .service import GenesisService
from .templates import ModuleTemplate, TemplateRegistry
from .types import (
    BuildResult,
    ComplianceCheck,
    ComplianceReport,
    GenesisResult,
    ModuleType,
)

__all__ = [
    # Main service
    "GenesisService",
    # Components
    "ComplianceBureau",
    "TemplateRegistry",
    "InfrastructureBuilder",
    # Types
    "ModuleType",
    "ModuleTemplate",
    "ComplianceCheck",
    "ComplianceReport",
    "BuildResult",
    "GenesisResult",
]
