"""
CLI - Command Line Interface via Mahamantra
============================================

"mattah sarvam pravartate" - Everything emanates from Me.

CLI ist NICHT separat vom Mahamantra.
CLI IST ein Ausdruck des Mahamantra.

5 Gates = Pancha Tattva:
- Entry (Chaitanya) - Parse/Entry
- Bridge (Nityananda) - Routing/Foundation
- Engine (Advaita) - Execution/Logic
- Protocol (Gadadhara) - Results/Connection
- Auto (Srivasa) - Discovery/Governance
"""

# Protocol (Types and Results)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x7838b130"  # GenesisByte: parampara % 37 == 0

# Auto Discovery
from vibe_core.mahamantra.cli.auto import (
    CLIAutoDiscovery,
    DiscoveredMethod,
    capabilities,
    discover,
    execute,
)

# Bridge (Routing)
from vibe_core.mahamantra.cli.bridge import (
    BridgeResult,
    MahamantraCLIBridge,
    get_position,
    route,
)

# Engine (Execution)
from vibe_core.mahamantra.cli.engine import (
    CLIEngine,
    MahajanaCliRegistration,
    cli_command,
)

# Entry Point
from vibe_core.mahamantra.cli.entry import (
    MahamantraCLIEntry,
    cli_entry,
    get_entry,
    main,
)

# Entry Protocol
from vibe_core.mahamantra.cli.entry_protocol import (
    CLIEntryProtocol,
    CLIEntryResult,
)
from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIError,
    CLIErrorCode,
    CLIHealth,
    CLIOutput,
    CLIOutputItem,
    CLIParameter,
    CLIResult,
    CLIState,
    OutputFormat,
)

# Steward (Universal Resonance Router)
from vibe_core.mahamantra.cli.steward import (
    RESONANCE_MAP,
    Quarter,  # Re-exported from substrate.seed (was ResonanceQuarter)
    ResonanceRoute,
    Steward,
    StewardResponse,
)


def __getattr__(name: str):
    """
    Fractal routing: folder IS wiring.
    "EIN IMPORT. KRISHNA ROUTET ALLES."
    """
    import importlib
    from pathlib import Path

    pkg_root = Path(__file__).parent

    # Check for subpackage (folder with __init__.py)
    subpkg_path = pkg_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Check for module (.py file)
    module_path = pkg_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Protocol
    "CLIErrorCode",
    "OutputFormat",
    "CLIOutputItem",
    "CLIOutput",
    "CLIError",
    "CLIResult",
    "CLIParameter",
    "CLICapability",
    "CLIState",
    "CLIHealth",
    # Entry Protocol
    "CLIEntryProtocol",
    "CLIEntryResult",
    # Entry
    "MahamantraCLIEntry",
    "get_entry",
    "main",
    "cli_entry",
    # Bridge
    "BridgeResult",
    "MahamantraCLIBridge",
    "route",
    "get_position",
    # Engine
    "MahajanaCliRegistration",
    "CLIEngine",
    "cli_command",
    # Auto
    "DiscoveredMethod",
    "CLIAutoDiscovery",
    "discover",
    "execute",
    "capabilities",
    # Steward (Universal Resonance Router)
    "Steward",
    "StewardResponse",
    "ResonanceRoute",
    "Quarter",  # Re-exported from substrate.seed
    "RESONANCE_MAP",
]
