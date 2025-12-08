import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.cli.unified_cli import UnifiedCLI


def test_unified_cli():
    print("Testing UnifiedCLI...")
    cli = UnifiedCLI()

    # Test capabilities (GAD-000)
    caps = cli.get_capabilities()
    print("Capabilities:", caps)

    if "status" not in caps["system_commands"]:
        print("❌ 'status' command missing")
        sys.exit(1)

    print("✅ Capabilities OK")

    # Test dispatch (help)
    print("\nTesting 'help' dispatch...")
    cli.run(["help"])
    print("✅ Dispatch OK")


if __name__ == "__main__":
    test_unified_cli()
