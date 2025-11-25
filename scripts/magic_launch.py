#!/usr/bin/env python3
"""
================================================================================
MAGIC BUTTON - ONE CLICK LAUNCH
================================================================================

The "One Click" launcher that brings the entire Steward Protocol experience
to life with ZERO configuration required.

WHAT IT DOES:
1. Kills any existing server instances
2. Starts the Steward bootloader in the background
3. Waits for "SYSTEM READY" message (server is live)
4. Opens your browser to the frontend (pre-configured with defaults)

USAGE:
    python3 scripts/magic_launch.py

Then lean back. The browser opens. Envoy is ready. Done.

NO IPs. NO Keys. NO Config. Just magic.
================================================================================
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import psutil
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MAGIC_LAUNCH")


def kill_existing_servers():
    """Kill any existing run_server.py or uvicorn processes."""
    logger.info("🧹 Checking for existing server instances...")

    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])

            # Kill if it's a run_server.py or uvicorn process (but not this script)
            if ('run_server.py' in cmdline or 'uvicorn' in cmdline) and 'magic_launch' not in cmdline:
                logger.info(f"   Killing PID {proc.info['pid']}: {proc.info['name']}")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed_count > 0:
        logger.info(f"✅ Killed {killed_count} existing server instance(s)")
        time.sleep(1)  # Give processes time to clean up
    else:
        logger.info("   (no existing instances found)")


def start_server():
    """Start the Steward bootloader in the background."""
    logger.info("\n🚀 Starting Steward Bootloader...")

    # Get the project root
    project_root = Path(__file__).parent.parent

    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, 'run_server.py'],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffering
        )

        logger.info(f"   Process started (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


def wait_for_ready(process, timeout=60):
    """
    Wait for the server to be ready (looking for "SYSTEM READY" message).

    Args:
        process: The subprocess
        timeout: Maximum seconds to wait

    Returns:
        bool: True if server is ready, False if timeout
    """
    logger.info("\n⏳ Waiting for server to be ready (max 60 seconds)...")

    start_time = time.time()

    try:
        for line in process.stdout:
            elapsed = time.time() - start_time

            # Print server output for transparency
            print(f"   [Server] {line.rstrip()}")

            # Check for ready signals
            if "SYSTEM READY" in line or "✅ SYSTEM READY" in line:
                logger.info(f"✅ Server is READY! (took {elapsed:.1f}s)")
                return True

            # Also accept these as "ready" signals
            if "API Gateway is live" in line or "ENVOY is listening" in line:
                logger.info(f"✅ Server is READY! (took {elapsed:.1f}s)")
                return True

            # Check timeout
            if elapsed > timeout:
                logger.error(f"❌ Timeout waiting for server ({timeout}s)")
                return False

    except Exception as e:
        logger.error(f"Error monitoring server: {e}")
        return False

    return False


def open_browser():
    """Open the frontend in the default browser."""
    logger.info("\n🌐 Opening browser...")

    # Use absolute file path for frontend
    project_root = Path(__file__).parent.parent
    html_path = project_root / "docs" / "public" / "index.html"

    if not html_path.exists():
        logger.error(f"❌ Frontend not found at {html_path}")
        return False

    # Convert to file:// URL
    file_url = html_path.as_uri()

    try:
        webbrowser.open(file_url)
        logger.info(f"✅ Browser opened: {file_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to open browser: {e}")
        logger.info(f"   💡 Try opening manually: {file_url}")
        return False


def main():
    """Execute the magic button sequence."""

    print("\n" + "=" * 80)
    print("🎩 THE MAGIC BUTTON - ONE CLICK LAUNCH")
    print("=" * 80)
    print()

    try:
        # Step 1: Kill existing servers
        kill_existing_servers()

        # Step 2: Start the server
        process = start_server()

        # Step 3: Wait for ready
        if not wait_for_ready(process):
            logger.error("\n❌ Server failed to start")
            process.kill()
            sys.exit(1)

        # Step 4: Open browser
        open_browser()

        print("\n" + "=" * 80)
        print("✨ MAGIC COMPLETE!")
        print("=" * 80)
        print()
        print("The frontend is ready at: docs/public/index.html")
        print("Default URL: http://127.0.0.1:8000")
        print("Default Key: steward-secret-key")
        print()
        print("The server is running. Press Ctrl+C to stop.")
        print("=" * 80 + "\n")

        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("\n\n👋 Shutdown requested")
            process.terminate()
            process.wait(timeout=5)

    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
