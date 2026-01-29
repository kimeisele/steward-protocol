#!/usr/bin/env python3
"""
Steward Protocol - Dashboard Launcher

Usage:
    python run_dashboard.py

This script automatically:
1. Ensures all necessary web dependencies are installed.
2. Starts the FastAPI web server.
3. Opens the dashboard in your default web browser.

Press Ctrl+C to shut down the server.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xb5ed22c0"  # GenesisByte: parampara % 37 == 0

import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# --- Basic Setup ---
PROJECT_ROOT = Path(__file__).parent.resolve()


def print_banner(title: str):
    """Prints a clear, formatted banner."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_error(msg: str, suggestion: str = None):
    """Prints a formatted error message."""
    print(f"\n❌ ERROR: {msg}")
    if suggestion:
        print(f"   → FIX: {suggestion}")
    print()


def print_info(msg: str):
    """Prints an informational message."""
    print(f"✓ {msg}")


# --- Dependency Management (Inspired by boot.py) ---


def find_installer():
    """Finds the best available package installer (uv > pip > pip3)."""
    if shutil.which("uv"):
        return ["uv", "pip", "install"], "uv"
    if shutil.which("pip"):
        return ["pip", "install"], "pip"
    if shutil.which("pip3"):
        return ["pip3", "install"], "pip3"
    return [sys.executable, "-m", "pip", "install"], "python -m pip"


def ensure_web_dependencies():
    """
    Ensures that FastAPI, Uvicorn, and other web dependencies are installed.
    It reads them from pyproject.toml's 'dependencies' list.
    """
    from importlib.util import find_spec

    # Key web dependencies to check
    required_web_deps = ["fastapi", "uvicorn"]
    if all(find_spec(pkg) for pkg in required_web_deps):
        print_info("Web dependencies are already installed.")
        return True

    install_cmd, installer_name = find_installer()
    if not install_cmd:
        print_error(
            "No Python package installer (pip, uv) found.",
            "Please install pip: https://pip.pypa.io/en/stable/installation/",
        )
        return False

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        print_error("pyproject.toml not found.", "Ensure you are in the project root.")
        return False

    print(f"Installing web dependencies using {installer_name}...")

    # We install all dependencies to ensure the gateway can boot
    full_install_cmd = install_cmd + ["-e", "."]

    try:
        result = subprocess.run(
            full_install_cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=True, timeout=300
        )
        print_info("All dependencies successfully installed.")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print_error(f"Failed to install dependencies: {e.stderr or e}", "Check your internet connection and try again.")
        return False
    except FileNotFoundError:
        print_error(f"Installer '{installer_name}' not found.", "Please ensure Python and pip are correctly installed.")
        return False


import socket

# --- Utility Functions ---


def is_port_in_use(port: int) -> bool:
    """Checks if a local port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


# --- Main Application Logic ---


def main():
    """Main function to start the dashboard."""
    print_banner("Steward Protocol - Dashboard Launcher")

    # 1. Check if port is in use
    PORT = 8080
    if is_port_in_use(PORT):
        print_error(
            f"Port {PORT} is already in use.",
            f"Please stop the other process running on port {PORT} or change the port in this script.",
        )
        sys.exit(1)

    # 2. Check for dependencies
    if not ensure_web_dependencies():
        sys.exit(1)

    # 3. Define the server command
    # Use python -m uvicorn to ensure it runs from the correct environment
    uvicorn_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "gateway.api:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(PORT),
    ]

    print_info("Starting web server...")

    # Use Popen to run the server as a background process
    server_process = subprocess.Popen(uvicorn_command, cwd=PROJECT_ROOT)

    # Give the server a moment to start up
    time.sleep(3)

    # 3. Open the web browser
    dashboard_url = "http://localhost:8080"
    print("\n" + "=" * 60)
    print(f"  Dashboard should be live at: {dashboard_url}")
    print("  Opening in your default browser now...")
    print("  Press Ctrl+C in this terminal to shut down the server.")
    print("=" * 60 + "\n")

    try:
        webbrowser.open(dashboard_url)
    except Exception as e:
        print_error(f"Could not open web browser: {e}", f"Please open this URL manually: {dashboard_url}")

    # 4. Wait for user to exit (Ctrl+C)
    try:
        # Wait for the server process to complete, or for a keyboard interrupt
        server_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server_process.terminate()  # Politely ask the process to stop
        try:
            server_process.wait(timeout=5)  # Wait for graceful shutdown
        except subprocess.TimeoutExpired:
            server_process.kill()  # Forcefully stop if it doesn't respond
        print_info("Server shut down.")
        sys.exit(0)


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    main()
