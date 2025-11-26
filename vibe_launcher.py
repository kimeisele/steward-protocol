#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                        PROJECT VIMANA: THE LAUNCHER                        ║
║                     "One Binary to rule them all"                          ║
║                                                                            ║
║  The master orchestration script that boots the VibeOS Kernel, prepares   ║
║  the Neural Link (WebSocket), and opens the Cockpit in your browser.      ║
║                                                                            ║
║  Entry point: `./vibe` or `python vibe_launcher.py`                       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import subprocess
import signal
import webbrowser
import socket
import argparse
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

# Color codes for terminal output (Sci-Fi aesthetic)
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_MAGENTA = '\033[95m'
    BG_DARK = '\033[40m'


class BootMode(Enum):
    """Two fundamental modes of operation"""
    GUEST = "guest"      # Shudra: Read-only, local simulation
    CITIZEN = "citizen"  # Dvija: Authenticated, federation access


@dataclass
class BootConfig:
    """Configuration for the boot sequence"""
    port: int = 8000
    host: str = "localhost"
    mode: BootMode = BootMode.GUEST
    debug: bool = False
    no_browser: bool = False
    private_key_path: Optional[str] = None
    data_dir: str = "data"
    config_dir: str = "config"


class BootStatus:
    """Tracks boot sequence status"""
    def __init__(self):
        self.checks: Dict[str, bool] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.errors: list = []

    def add_check(self, name: str, passed: bool, detail: str = ""):
        self.checks[name] = passed
        symbol = "✓" if passed else "✗"
        color = Colors.BRIGHT_GREEN if passed else Colors.BRIGHT_RED
        detail_str = f" ({detail})" if detail else ""
        print(f"{color}{symbol} {name}{detail_str}{Colors.RESET}")
        if not passed:
            self.errors.append(f"{name}: {detail}")

    def add_error(self, error: str):
        self.errors.append(error)
        print(f"{Colors.BRIGHT_RED}✗ ERROR: {error}{Colors.RESET}")

    def is_healthy(self) -> bool:
        return all(self.checks.values()) and not self.errors


class VibeBootLoader:
    """Master orchestration engine for the VibeOS"""

    def __init__(self, config: BootConfig):
        self.config = config
        self.status = BootStatus()
        self.project_root = Path(__file__).parent
        self.started_at = time.time()

    def print_header(self):
        """Display the PROJECT VIMANA header"""
        print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                        🛸 PROJECT VIMANA: THE LAUNCHER 🛸                  ║")
        print("║                      The Universal Agent Operating System                   ║")
        print("║                           Initializing Neural Link...                      ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")

    def check_environment(self):
        """Auto-discovery: Check system environment"""
        print(f"{Colors.BRIGHT_CYAN}➜ ENVIRONMENT CHECKS{Colors.RESET}\n")

        # Check Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.status.add_check(
            "Python Runtime",
            sys.version_info >= (3, 10),
            f"Python {py_version}"
        )

        # Check required directories
        required_dirs = [self.config.data_dir, self.config.config_dir]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists()
            self.status.add_check(f"Directory: {dir_name}", exists)
            if not exists:
                dir_path.mkdir(parents=True, exist_ok=True)

        # Check database
        db_path = self.project_root / self.config.data_dir / "vibe_ledger.db"
        db_exists = db_path.exists()
        self.status.add_check("Database", db_exists, "vibe_ledger.db")

        # Check config files
        matrix_config = self.project_root / self.config.config_dir / "matrix.yaml"
        config_exists = matrix_config.exists()
        self.status.add_check("Configuration", config_exists, "matrix.yaml")

        # Check port availability
        port_available = self._is_port_available(self.config.port)
        self.status.add_check(
            f"Port {self.config.port}",
            port_available,
            "available for binding"
        )

        if not port_available:
            self.status.add_error(
                f"Port {self.config.port} is already in use. "
                f"Use --port to specify a different port."
            )

        # Check for private key (determines mode)
        private_key_paths = [
            self.project_root / ".env.private_key",
            self.project_root / "private_key.pem",
            Path.home() / ".vibe" / "private_key.pem",
        ]

        for key_path in private_key_paths:
            if key_path.exists():
                self.config.private_key_path = str(key_path)
                self.config.mode = BootMode.CITIZEN
                self.status.add_check(
                    "Identity",
                    True,
                    f"CITIZEN MODE ({key_path.name})"
                )
                return

        self.config.mode = BootMode.GUEST
        self.status.add_check("Identity", True, "GUEST MODE (sandbox)")

        print()

    def _is_port_available(self, port: int) -> bool:
        """Check if port is available for binding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return True
        except OSError:
            return False

    def setup_environment(self):
        """Prepare runtime environment"""
        print(f"{Colors.BRIGHT_CYAN}➜ ENVIRONMENT SETUP{Colors.RESET}\n")

        # Set up environment variables
        os.environ["VIBE_MODE"] = self.config.mode.value
        os.environ["VIBE_PORT"] = str(self.config.port)
        os.environ["VIBE_HOST"] = self.config.host
        os.environ["PYTHONUNBUFFERED"] = "1"

        if self.config.debug:
            os.environ["VIBE_DEBUG"] = "true"

        self.status.add_check("Environment Variables", True, f"MODE={self.config.mode.value}")

        # Create .env file if it doesn't exist
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self._create_default_env()

        self.status.add_check("Runtime Config", True, ".env file")
        print()

    def _create_default_env(self):
        """Create default .env if missing"""
        env_content = f"""# VibeOS Configuration
VIBE_MODE={self.config.mode.value}
VIBE_PORT={self.config.port}
VIBE_HOST={self.config.host}
LEDGER_PATH=data/vibe_ledger.db
CONFIG_PATH=config/matrix.yaml
LOG_LEVEL=INFO
DEBUG={self.config.debug}
"""
        env_file = self.project_root / ".env"
        env_file.write_text(env_content)

    def boot_kernel(self):
        """Start the VibeOS Kernel"""
        print(f"{Colors.BRIGHT_CYAN}➜ KERNEL BOOT SEQUENCE{Colors.RESET}\n")

        try:
            # Import kernel components (lazy import to avoid circular dependencies)
            from vibe_core.kernel_impl import RealVibeKernel
            from vibe_core.ledger import VibeLedger

            ledger_path = self.project_root / self.config.data_dir / "vibe_ledger.db"
            ledger = VibeLedger(str(ledger_path))

            kernel = RealVibeKernel(ledger_path=str(ledger_path))

            # Boot the kernel
            kernel.boot()

            self.status.add_check("Kernel", True, "initialized and booted")
            self.status.add_check("Agent Registry", True, f"{len(kernel.agents)} agents loaded")

            # Store kernel reference for later
            self._kernel = kernel

        except Exception as e:
            self.status.add_error(f"Kernel boot failed: {str(e)}")
            if self.config.debug:
                import traceback
                traceback.print_exc()

        print()

    def start_gateway(self) -> Optional[subprocess.Popen]:
        """Start the FastAPI gateway (uvicorn)"""
        print(f"{Colors.BRIGHT_CYAN}➜ GATEWAY INITIALIZATION{Colors.RESET}\n")

        try:
            cmd = [
                "python", "-m", "uvicorn",
                "gateway.api:app",
                f"--host", self.config.host,
                f"--port", str(self.config.port),
                "--reload" if self.config.debug else "",
            ]
            cmd = [c for c in cmd if c]  # Remove empty strings

            # Check if gateway can be imported
            from gateway import api
            self.status.add_check("Gateway Module", True, "gateway.api importable")

            # Start the gateway server
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
            )

            self.status.processes["gateway"] = process
            time.sleep(2)  # Give server time to start

            # Check if process is still running
            if process.poll() is not None:
                self.status.add_error(f"Gateway process exited with code {process.returncode}")
            else:
                self.status.add_check(
                    "Gateway Server",
                    True,
                    f"listening on http://{self.config.host}:{self.config.port}"
                )

        except Exception as e:
            self.status.add_error(f"Gateway start failed: {str(e)}")
            if self.config.debug:
                import traceback
                traceback.print_exc()

        print()
        return self.status.processes.get("gateway")

    def open_cockpit(self):
        """Open the Cockpit in the user's default browser"""
        print(f"{Colors.BRIGHT_CYAN}➜ NEURAL LINK ACTIVATION{Colors.RESET}\n")

        cockpit_url = f"http://{self.config.host}:{self.config.port}"

        if self.config.no_browser:
            print(f"{Colors.BRIGHT_YELLOW}Browser launch disabled.{Colors.RESET}")
            print(f"Open manually: {Colors.BRIGHT_CYAN}{cockpit_url}{Colors.RESET}\n")
        else:
            try:
                webbrowser.open(cockpit_url)
                self.status.add_check("Cockpit", True, f"opened at {cockpit_url}")
            except Exception as e:
                self.status.add_check("Cockpit", False, str(e))
                print(f"Manual URL: {Colors.BRIGHT_CYAN}{cockpit_url}{Colors.RESET}\n")

        print()

    def print_boot_summary(self):
        """Print boot completion summary"""
        elapsed = time.time() - self.started_at

        print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        if self.status.is_healthy():
            print("║                      ✓ NEURAL LINK ACTIVATED                            ║")
            print("║                    THE VIMANA IS READY FOR FLIGHT                       ║")
        else:
            print("║                    ⚠ BOOT SEQUENCE INCOMPLETE                           ║")
            print("║                    Some systems require attention.                      ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_CYAN}BOOT SUMMARY:{Colors.RESET}")
        print(f"  Mode: {Colors.BRIGHT_MAGENTA}{self.config.mode.value.upper()}{Colors.RESET}")
        print(f"  URL: {Colors.BRIGHT_CYAN}http://{self.config.host}:{self.config.port}{Colors.RESET}")
        print(f"  Boot Time: {elapsed:.2f}s")
        print(f"  Checks Passed: {sum(self.status.checks.values())}/{len(self.status.checks)}")

        if self.status.errors:
            print(f"\n{Colors.BRIGHT_RED}ERRORS:{Colors.RESET}")
            for error in self.status.errors:
                print(f"  • {error}")

        print(f"\n{Colors.DIM}To stop the Vimana: Press Ctrl+C{Colors.RESET}\n")

    def run_bootloader(self):
        """Execute the full boot sequence"""
        self.print_header()

        # Sequence of boot steps
        self.check_environment()

        if not self.status.is_healthy():
            print(f"{Colors.BRIGHT_RED}Critical checks failed. Cannot proceed.{Colors.RESET}\n")
            sys.exit(1)

        self.setup_environment()
        self.boot_kernel()
        self.start_gateway()
        self.open_cockpit()
        self.print_boot_summary()

        if not self.status.is_healthy():
            print(f"{Colors.BRIGHT_YELLOW}Warning: Some systems are not fully operational.{Colors.RESET}\n")
            sys.exit(1)

        # Keep the launcher running, managing child processes
        self._run_monitor()

    def _run_monitor(self):
        """Monitor child processes and handle graceful shutdown"""
        def signal_handler(sig, frame):
            print(f"\n{Colors.BRIGHT_YELLOW}Shutting down Vimana...{Colors.RESET}")
            self._cleanup_processes()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            while True:
                # Check if processes are still alive
                for name, process in list(self.status.processes.items()):
                    if process.poll() is not None:
                        print(f"\n{Colors.BRIGHT_RED}Process {name} exited.{Colors.RESET}")

                time.sleep(1)
        except KeyboardInterrupt:
            self._cleanup_processes()
            sys.exit(0)

    def _cleanup_processes(self):
        """Gracefully shut down all child processes"""
        for name, process in self.status.processes.items():
            try:
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                process.wait(timeout=5)
            except Exception as e:
                if self.config.debug:
                    print(f"Error terminating {name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="PROJECT VIMANA: The VibeOS Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibe                           # Boot in default mode
  vibe --port 9000               # Boot on custom port
  vibe --citizen --key key.pem   # Boot as citizen with private key
  vibe --no-browser --debug      # Boot without opening browser, with debug output
        """
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the gateway on (default: 8000)"
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )

    parser.add_argument(
        "--citizen",
        action="store_true",
        help="Force CITIZEN mode (requires --key)"
    )

    parser.add_argument(
        "--key",
        type=str,
        help="Path to private key file for CITIZEN mode"
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # Build boot config
    config = BootConfig(
        port=args.port,
        host=args.host,
        mode=BootMode.CITIZEN if args.citizen else BootMode.GUEST,
        debug=args.debug,
        no_browser=args.no_browser,
        private_key_path=args.key,
    )

    # Create and run bootloader
    bootloader = VibeBootLoader(config)
    bootloader.run_bootloader()


if __name__ == "__main__":
    main()
