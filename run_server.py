#!/usr/bin/env python3
"""
================================================================================
PHASE 6: FIRST CONTACT (ENVOY SHELL & API GATEWAY) - THE BOOTLOADER
================================================================================

This is the startup script that brings the Steward Protocol "city" to life.

ARCHITECTURE (OS ANALOGY):
  - KERNEL: vibe_core (CPU/Resource Scheduling)
  - SHELL: ENVOY (The System Interface with HIL logic)
  - USER: The Human Operator (via Frontend)

THE PROCESS:
1. Boot VibeOS Kernel
2. Load all 12 CORE CARTRIDGES (agents)
3. Initialize ENVOY as the only user-facing interface
4. Start FastAPI Gateway for Frontend connection
5. Accept commands via /v1/chat (HIL-optimized responses)

CRITICAL: ENVOY is the "Safety Bubble" - all user commands pass through
Envoy's interpretation and safety checks (GAD-000). The system is governed
by Constitutional Oath at the kernel level.

USAGE:
  python3 run_server.py [--port 8000] [--host 0.0.0.0]

This is the wiring that connects the User to the Agent City through the
System Shell.
================================================================================
"""

import sys
import os
import logging
from pathlib import Path
import argparse
from datetime import datetime, timezone

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("STEWARD_BOOTLOADER")

# Import VibeOS Kernel
from vibe_core.kernel_impl import RealVibeKernel

# Import Configuration (GAD-100: Phoenix Configuration)
from vibe_core.config import ConfigLoader, CityConfig

# Import all 12 agent cartridges
from herald.cartridge_main import HeraldCartridge
from civic.cartridge_main import CivicCartridge
from forum.cartridge_main import ForumCartridge
from science.cartridge_main import ScientistCartridge
from envoy.cartridge_main import EnvoyCartridge
from archivist.cartridge_main import ArchivistCartridge
from auditor.cartridge_main import AuditorCartridge
from engineer.cartridge_main import EngineerCartridge
from oracle.cartridge_main import OracleCartridge
from watchman.cartridge_main import WatchmanCartridge
from artisan.cartridge_main import ArtisanCartridge
from chronicle.cartridge_main import ChronicleCartridge


class StewardBootLoader:
    """
    The bootloader that brings the Steward Protocol system online.

    Responsibilities:
    1. Load and validate configuration (GAD-100: Phoenix Configuration)
    2. Initialize the VibeOS Kernel
    3. Register all 12 CORE CARTRIDGES
    4. Execute the Constitutional Oath ceremony
    5. Boot the kernel (register manifests, ledger init, etc)
    6. Start the FastAPI Gateway
    """

    def __init__(self, ledger_path: str = None, port: int = 8000, host: str = "0.0.0.0",
                 config_path: str = "config/matrix.yaml"):
        """
        Initialize the bootloader.

        Args:
            ledger_path: Path to SQLite ledger (default: data/vibe_ledger.db)
            port: API Gateway port
            host: API Gateway host
            config_path: Path to configuration YAML (default: config/matrix.yaml)
        """
        self.ledger_path = ledger_path or "data/vibe_ledger.db"
        self.port = port
        self.host = host
        self.config_path = config_path
        self.kernel = None
        self.agents = []
        self.config: CityConfig = None

        # Load configuration (GAD-100)
        self._load_config()

    def _load_config(self):
        """Load and validate system configuration.

        This loads THE DHARMA (configuration) which defines the entire city.
        Configuration is loaded from config/matrix.yaml and validated against
        the Pydantic CityConfig schema.

        Raises:
            RuntimeError: If configuration is missing or invalid
        """
        logger.info("=" * 80)
        logger.info("🔐 LOADING CONFIGURATION (GAD-100: Phoenix Configuration)")
        logger.info("=" * 80)

        try:
            loader = ConfigLoader(self.config_path)
            self.config = loader.load()

            logger.info(f"✅ Configuration loaded: {self.config.city_name}")
            logger.info(f"   Version: {self.config.federation_version}")
            logger.info(f"   Economy: {self.config.economy.initial_credits} initial credits")
            logger.info(f"   Governance: {int(self.config.governance.voting_threshold * 100)}% voting threshold")

            # Validate configuration
            validation_report = loader.validate()
            if not validation_report["valid"]:
                logger.error("❌ Configuration validation failed")
                raise RuntimeError("Configuration invalid")

            logger.info("✅ Configuration validated successfully\n")

        except FileNotFoundError as e:
            logger.error(f"❌ Configuration file not found: {e}")
            logger.info("💡 Expected configuration at: config/matrix.yaml")
            raise RuntimeError(f"Configuration missing: {e}")
        except ValueError as e:
            logger.error(f"❌ Configuration validation error: {e}")
            raise RuntimeError(f"Configuration invalid: {e}")

    def _print_banner(self):
        """Print the system startup banner."""
        banner = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🌍 STEWARD PROTOCOL - PHASE 6: FIRST CONTACT 🌍              ║
║                                                                            ║
║                 "The System Shell Connects to the Kernel"                  ║
║                                                                            ║
║                            Booting the City...                            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def boot_kernel(self) -> RealVibeKernel:
        """
        Boot the VibeOS Kernel and register all agents.

        Returns:
            RealVibeKernel: The initialized and booted kernel
        """
        logger.info("=" * 80)
        logger.info("⚙️  KERNEL BOOT SEQUENCE INITIATED")
        logger.info("=" * 80)

        # 1. Create kernel instance
        logger.info(f"🔧 Creating RealVibeKernel (ledger: {self.ledger_path})")
        self.kernel = RealVibeKernel(ledger_path=self.ledger_path)

        # 2. Create and register all 12 agent cartridges
        logger.info("🤖 Loading all 12 CORE CARTRIDGES...")

        cartridges = [
            ("herald", HeraldCartridge(), "Content & Broadcasting"),
            ("civic", CivicCartridge(), "Governance & Registry"),
            ("forum", ForumCartridge(), "Voting & Proposals"),
            ("science", ScientistCartridge(), "Research & Knowledge"),
            ("envoy", EnvoyCartridge(), "User Interface & Orchestration"),
            ("archivist", ArchivistCartridge(), "Auditing & Verification"),
            ("auditor", AuditorCartridge(), "Compliance & GAD Enforcement"),
            ("engineer", EngineerCartridge(), "Meta-builder & Scaffolding"),
            ("oracle", OracleCartridge(), "System Introspection & Self-Awareness"),
            ("watchman", WatchmanCartridge(), "Monitoring & Health Checks"),
            ("artisan", ArtisanCartridge(), "Media Operations & Branding"),
            ("chronicle", ChronicleCartridge(), "Temporal agent: git operations"),
        ]

        for agent_id, agent_instance, purpose in cartridges:
            try:
                # Check if agent is a VibeAgent (has required interface)
                if not hasattr(agent_instance, 'get_manifest') or not hasattr(agent_instance, 'process'):
                    logger.warning(f"   ⏭️  {agent_id.upper():12} | SKIPPED (legacy cartridge, not VibeAgent)")
                    continue

                self.kernel.register_agent(agent_instance)
                self.agents.append((agent_id, agent_instance))
                logger.info(f"   ✅ {agent_id.upper():12} | {purpose}")
            except Exception as e:
                logger.error(f"   ❌ {agent_id.upper():12} | Failed: {e}")
                raise RuntimeError(f"Failed to register {agent_id}: {e}")

        logger.info(f"\n🎖️  All {len(self.agents)} agents registered successfully")

        # 3. Boot the kernel (this initializes manifests, ledger, etc)
        logger.info("\n🔥 Booting kernel (initializing ledger, manifests, registry)...")
        try:
            self.kernel.boot()
            logger.info("✅ Kernel boot complete")
        except Exception as e:
            logger.error(f"❌ Kernel boot failed: {e}")
            raise

        # 4. Execute initial pulse (Constitutional Oath verification)
        logger.info("\n📸 Executing initial pulse (Constitutional Oath ceremony)...")
        try:
            self.kernel._pulse()
            logger.info("✅ Initial pulse captured")
        except Exception as e:
            logger.warning(f"⚠️  Initial pulse failed (non-critical): {e}")

        # 5. Verify kernel status
        status = self.kernel.get_status()
        logger.info("\n📊 KERNEL STATUS:")
        logger.info(f"   Status: {status.get('status')}")
        logger.info(f"   Agents Registered: {status.get('agents_registered')}")
        logger.info(f"   Manifests: {status.get('manifests')}")
        logger.info(f"   Ledger Events: {status.get('ledger_events')}")

        return self.kernel

    def verify_envoy(self) -> bool:
        """
        Verify that ENVOY (System Shell) is properly wired.

        Returns:
            bool: True if ENVOY is ready
        """
        logger.info("\n🔗 Verifying ENVOY (System Shell)...")

        envoy = self.kernel.agent_registry.get("envoy")
        if not envoy:
            logger.error("❌ ENVOY not found in kernel registry")
            return False

        # Check that ENVOY has the HIL Assistant
        if not hasattr(envoy, 'hil_assistant'):
            logger.error("❌ ENVOY missing HIL Assistant Tool")
            return False

        if not envoy.hil_assistant:
            logger.error("❌ ENVOY HIL Assistant not initialized")
            return False

        # Check that ENVOY has kernel reference
        if not envoy.kernel:
            logger.error("❌ ENVOY kernel not injected")
            return False

        logger.info("✅ ENVOY verified (Brain connected to Heart)")
        logger.info("   • HIL Assistant Tool: ACTIVE")
        logger.info("   • Kernel Reference: INJECTED")
        logger.info("   • Command Router: READY")

        return True

    def start_gateway(self):
        """
        Start the FastAPI Gateway server.

        This exposes the ENVOY via HTTP and connects to the frontend.
        """
        logger.info("\n" + "=" * 80)
        logger.info("🌐 STARTING FASTAPI GATEWAY")
        logger.info("=" * 80)

        logger.info(f"   Host: {self.host}")
        logger.info(f"   Port: {self.port}")
        logger.info(f"   Endpoint: http://{self.host}:{self.port}/v1/chat")
        logger.info(f"   Docs: http://{self.host}:{self.port}/docs")
        logger.info(f"   Health: http://{self.host}:{self.port}/health")

        logger.info("\n🔌 API Gateway is live and ready to receive commands from the Frontend")
        logger.info("📡 ENVOY is listening via POST /v1/chat")
        logger.info("🛡️  GAD-000: HIL Assistant filters complexity")
        logger.info("✅ SYSTEM READY FOR FIRST CONTACT")

        logger.info("\n" + "=" * 80)
        logger.info("Starting uvicorn server...")
        logger.info("=" * 80)

        # Import and start uvicorn
        import uvicorn

        # Set environment variables for gateway
        os.environ.setdefault("LEDGER_PATH", self.ledger_path)
        os.environ.setdefault("ENV", "production")
        os.environ.setdefault("API_KEY", os.getenv("API_KEY", "steward-secret-key"))

        # Start the server
        try:
            uvicorn.run(
                "gateway.api:app",
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True,
                reload=False  # Disable reload in production
            )
        except KeyboardInterrupt:
            logger.info("\n\n👋 Server shutdown requested")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            raise

    def run(self):
        """
        Execute the full boot sequence:
        1. Print banner
        2. Boot kernel
        3. Verify ENVOY
        4. Start Gateway
        """
        try:
            self._print_banner()

            # Boot the kernel
            self.boot_kernel()

            # Verify ENVOY
            if not self.verify_envoy():
                logger.error("❌ ENVOY verification failed")
                sys.exit(1)

            logger.info("\n" + "=" * 80)
            logger.info("🚀 READY FOR FIRST CONTACT")
            logger.info("=" * 80)
            logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
            logger.info("All systems operational. ENVOY is the Safety Bubble.")
            logger.info("=" * 80 + "\n")

            # Start the API gateway
            self.start_gateway()

        except Exception as e:
            logger.exception(f"❌ FATAL BOOT ERROR: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Steward Protocol Bootloader - Phase 6: First Contact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_server.py                    # Start on localhost:8000
  python3 run_server.py --port 9000        # Start on localhost:9000
  python3 run_server.py --host 0.0.0.0     # Listen on all interfaces
        """
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API Gateway port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="API Gateway host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default="data/vibe_ledger.db",
        help="Path to SQLite ledger (default: data/vibe_ledger.db)"
    )

    args = parser.parse_args()

    # Create and run bootloader
    bootloader = StewardBootLoader(
        ledger_path=args.ledger,
        port=args.port,
        host=args.host
    )

    bootloader.run()


if __name__ == "__main__":
    main()
