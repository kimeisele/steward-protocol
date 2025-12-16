#!/usr/bin/env python3
"""
VibeOS Binary Entry Point.

LAZY BOOT ARCHITECTURE:
- Check for quick commands (--help, -h, version) BEFORE heavy imports
- Extend runtime with user extensions (~/.steward/lib/) BEFORE heavy imports
- Only load UnifiedCLI when actually needed
- Target: <0.5s for help display

RUNTIME EXTENSION PHILOSOPHY:
- Binary ships THIN (no numpy/torch bloat)
- User installs extensions: `steward install-semantic`
- Extensions load from ~/.steward/lib/ at runtime
- No rebuild required - true OS behavior
"""

# PyInstaller multiprocessing support (MUST be at top level)
import multiprocessing
import sys

multiprocessing.freeze_support()

# === RUNTIME EXTENSION: Load user packages from ~/.steward/lib/ ===
# This MUST happen before any optional imports (numpy, torch, etc.)
try:
    from vibe_core.runtime_extensions import extend_runtime

    extend_runtime()
except ImportError:
    pass  # Extensions module not available (minimal install)

# === LAZY CLI: Instant Response for Basic Commands ===
QUICK_COMMANDS = {"--help", "-h", "help", "--version", "-V", "version"}


def print_static_help():
    """Print help without loading the full kernel."""
    print("""🎛️  VIBE OS - Unified CLI
========================

USAGE: vibe <command> [options]

QUICK COMMANDS:
  --help, -h        Show this help message
  --version, -V     Show version information

SYSTEM COMMANDS:
  boot              Start the kernel daemon
  stop              Stop the kernel daemon
  status            Show system health
  ps                List running agents
  discover          Discover registered agents
  introspect        Show kernel state details
  lineage           Show blockchain history
  verify <agent>    Verify agent passport
  init <agent>      Initialize new agent
  delegate          Submit task to agent

STATE COMMANDS:
  state             Show unified system state
  diff              Git diff (Proof of Work)
  plugins           List loaded plugins
  update <name>     Update container to library/
  install <path>    Install .vibe file to library/

EXTENSION COMMANDS:
  install-llm       Download local LLM (~400MB)
  install-semantic  Install neural intelligence (numpy, torch)
  extensions        Show runtime extension status

PLUGIN COMMANDS:
  Run 'vibe capabilities' for full plugin command list.

For more info: https://github.com/kimeisele/steward-protocol
""")


def print_version():
    """Print version without loading the kernel."""
    print("VibeOS v2.0.0 (Singularity)")
    print("The Thin Kernel - Binary Distribution")


def main():
    """VibeOS Binary Entry Point with Lazy Loading."""
    # Check for quick commands BEFORE any heavy imports
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd in {"--help", "-h", "help"}:
            print_static_help()
            return 0
        if cmd in {"--version", "-V", "version"}:
            print_version()
            return 0

    # Only import heavy modules when actually needed
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    from vibe_core.cli.unified_cli import UnifiedCLI

    cli = UnifiedCLI()
    return cli.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
