import logging
import sys

from vibe_core.cli.unified_cli import UnifiedCLI

# Configure basic logging for the binary
logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    """
    VibeOS Binary Entry Point.
    """
    cli = UnifiedCLI()
    exit_code = cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
