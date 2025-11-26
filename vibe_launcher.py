#!/usr/bin/env python3

"""
╔════════════════════════════════════════════════════════════════════════════╗
║                        🛸 PROJECT VIMANA: THE LAUNCHER 🛸                  ║
║                  "German Military Engineering Edition v2.0"                ║
║           Features: Port Rolling, Process Supervision, Zombie-Kill         ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import socket
import signal
import subprocess
import webbrowser
import argparse
import atexit
import requests
from contextlib import closing

# --- CONFIGURATION ---
DEFAULT_PORT = 8000
MAX_PORT_RETRIES = 10
HOST = "127.0.0.1"
HEALTH_CHECK_INTERVAL = 2.0  # Seconds

# Global process registry for cleanup
active_processes = []

def cleanup():
    """
    THE CLEANER: Guarantees no zombies are left behind.
    Runs on exit, crash, or interrupt.
    """
    if not active_processes:
        return

    print("\n🧹 CLEANUP PROTOCOL INITIATED...")
    for p in active_processes:
        if p.poll() is None:  # If process is still alive
            print(f"   • Terminating process PID {p.pid}...")
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print(f"   • KILLING process PID {p.pid} (Force)...")
                p.kill()
    print("✓ Workspace clean. Namaste.")

# Register cleanup to run NO MATTER WHAT
atexit.register(cleanup)

def signal_handler(sig, frame):
    print("\n🛑 MANUAL INTERRUPT RECEIVED.")
    sys.exit(0) # This triggers atexit.cleanup()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_port(port):
    """Returns True if port is FREE, False if BUSY."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((HOST, port)) == 0:
            return False
        return True

def find_available_port(start_port):
    print(f"➜ PORT RECONNAISSANCE (Starting at {start_port})...")
    for port in range(start_port, start_port + MAX_PORT_RETRIES):
        if check_port(port):
            return port
        print(f"   ⚠️  Port {port} occupied. Tactical shift to {port+1}...")

    print("❌ CRITICAL FAILURE: No ports available in range. System overloaded.")
    sys.exit(1)

def wait_for_health(port, timeout=10):
    """
    Offensive Health Check:
    Don't just hope it started. Verify it answers via HTTP.
    """
    print("   • Waiting for Gateway heartbeat...")
    start_time = time.time()
    url = f"http://{HOST}:{port}/" # Index check

    while time.time() - start_time < timeout:
        try:
            # Check if socket is bound first
            if not check_port(port):
                # Try actual HTTP request
                requests.get(url, timeout=1)
                print("   ✓ Pulse confirmed.")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            continue

    print("❌ TIMEOUT: Gateway process exists but is unresponsive.")
    return False

def start_gateway(port):
    print(f"➜ INITIATING GATEWAY on Port {port}")

    env = os.environ.copy()
    env["VIBE_PORT"] = str(port)
    env["PYTHONUNBUFFERED"] = "1" # Realtime logs

    try:
        # We use sys.executable to ensure we use the SAME python interpreter
        cmd = [
            sys.executable, "-m", "uvicorn",
            "gateway.api:app",
            "--host", HOST,
            "--port", str(port),
            "--log-level", "error" # Keep stdout clean
        ]

        p = subprocess.Popen(
            cmd,
            env=env,
            stdout=sys.stdout if os.environ.get("VIBE_DEBUG") else subprocess.DEVNULL,
            stderr=sys.stderr
        )
        active_processes.append(p)
        print(f"   ✓ Subprocess spawned (PID {p.pid})")

        if wait_for_health(port):
            return True
        else:
            p.terminate()
            return False

    except Exception as e:
        print(f"❌ CRITICAL: Launch failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="VibeOS Vimana Launcher")
    parser.add_argument("--port", type=int, help="Force specific port (Disables Rolling)")
    parser.add_argument("--no-browser", action="store_true", help="Headless mode")
    parser.add_argument("--debug", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.debug:
        os.environ["VIBE_DEBUG"] = "1"

    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                        🛸 PROJECT VIMANA: THE LAUNCHER 🛸                  ║")
    print("║                     System Status: ONLINE | Protocol: GAD-000              ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝\n")

    # 1. PORT STRATEGY
    if args.port:
        target_port = args.port
        if not check_port(target_port):
            print(f"❌ COMMAND ERROR: Requested port {target_port} is busy.")
            sys.exit(1)
    else:
        target_port = find_available_port(DEFAULT_PORT)

    os.environ["VIBE_PORT"] = str(target_port)

    # 2. IDENTITY CHECK & AUTO-GENERATION (SILENT KEY PROTOCOL)
    key_dir = "data/keys"
    key_path = os.path.join(key_dir, "private.pem")

    if not os.path.exists(key_path):
        print(f"➜ GENERATING NEW IDENTITY (Auto-Citizen)...")
        os.makedirs(key_dir, exist_ok=True)
        # Simple ECDSA Key Gen (using openssl command for speed/robustness if avail, or python)
        try:
            # Generate NIST P-256 Key
            subprocess.run(
                ["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", key_path],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            print(f"   ✓ Key forged at {key_path}")
        except:
            print(f"   ⚠️  OpenSSL not found. Please install or place key manually.")
            # Fallback logic later if needed, but for Mac/Linux usually openssl is there

    if os.path.exists(key_path):
        os.environ["VIBE_MODE"] = "CITIZEN"
        os.environ["VIBE_PRIVATE_KEY_PATH"] = key_path
        print(f"➜ IDENTITY VERIFIED: Citizen Mode 🔐 (Silent Key Active)")
    else:
        os.environ["VIBE_MODE"] = "GUEST"
        print(f"➜ IDENTITY UNVERIFIED: Guest Mode 👁️")

    # 3. LAUNCH
    if start_gateway(target_port):
        url = f"http://{HOST}:{target_port}"
        print(f"\n✅ SYSTEM OPERATIONAL at {url}")

        if not args.no_browser:
            print("➜ OPENING NEURAL LINK...")
            webbrowser.open(url)

        print("\n[ Supervisor Active. Press Ctrl+C to shutdown. ]\n")

        # SUPERVISOR LOOP
        try:
            while True:
                # Check if child processes are still alive
                for p in active_processes:
                    if p.poll() is not None:
                        print(f"\n❌ ALERT: Critical process (PID {p.pid}) died unexpectedly.")
                        sys.exit(1) # Triggers cleanup
                time.sleep(HEALTH_CHECK_INTERVAL)

        except KeyboardInterrupt:
            # Handled by signal_handler -> atexit
            pass
    else:
        print("❌ ABORT: Startup sequence failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
