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

from vibe_core.mahamantra.cli.protocol import (
    CLIErrorCode,
    OutputFormat,
    CLIOutputItem,
    CLIOutput,
    CLIError,
    CLIResult,
    CLIParameter,
    CLICapability,
    CLIState,
    CLIHealth,
)

# Entry Protocol
from vibe_core.mahamantra.cli.entry_protocol import (
    CLIEntryProtocol,
    CLIEntryResult,
)

# Entry Point
from vibe_core.mahamantra.cli.entry import (
    MahamantraCLIEntry,
    get_entry,
    main,
    cli_entry,
)

# Bridge (Routing)
from vibe_core.mahamantra.cli.bridge import (
    BridgeResult,
    MahamantraCLIBridge,
    route,
    get_position,
)

# Engine (Execution)
from vibe_core.mahamantra.cli.engine import (
    MahajanaCliRegistration,
    CLIEngine,
    cli_command,
)

# Auto Discovery
from vibe_core.mahamantra.cli.auto import (
    DiscoveredMethod,
    CLIAutoDiscovery,
    discover,
    execute,
    capabilities,
)

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
]
