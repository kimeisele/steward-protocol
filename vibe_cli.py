#!/usr/bin/env python3

"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      🛡️ PROJECT IRON SHELL 🛡️                              ║
║                Direct Neural Link Interface (CLI Mode)                     ║
║                                                                            ║
║  "The GUI is illusion. The Terminal is truth." - GAD-000                   ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime

# CONFIGURATION
# Liest den Port aus der Umgebung oder nutzt Default
PORT = os.environ.get("VIBE_PORT", "8000")
BASE_URL = f"http://localhost:{PORT}"
API_KEY = "steward-secret-key"

# ANSI COLORS (The Vedic Palette)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"  # Thoughts / Akasha
GREEN = "\033[92m"  # Action / Earth
GOLD = "\033[93m"  # Mercy / Truth
RED = "\033[91m"  # Error / Fire
BLUE = "\033[94m"  # Deep System


def check_connection():
    """Ping the Milk Ocean Router"""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=1)
        return r.status_code == 200
    except:
        return False


def print_header():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║               VIBE OS - IRON SHELL v1.0                      ║{RESET}")
    print(f"{BLUE}║          Connected to Node: {BASE_URL}                     ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}")
    print(f"\nType '{BOLD}exit{RESET}' to quit. Type '{BOLD}status{RESET}' for system health.\n")


def send_prayer(message, agent_id="guest"):
    """Sents a request to the Milk Ocean Router"""
    url = f"{BASE_URL}/v1/chat"

    # GAD-1000 Identity Stub (Simulated for CLI)
    payload = {
        "message": message,
        "agent_id": agent_id,
        "signature": "cli_override",
        "public_key": "cli_key",
        "timestamp": int(time.time() * 1000),
    }

    try:
        # VISUAL FEEDBACK: Sending
        sys.stdout.write(f"{DIM}📡 Transmitting prayer...{RESET}\r")
        sys.stdout.flush()

        r = requests.post(url, json=payload, headers={"X-API-Key": API_KEY})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"\n{RED}❌ TRANSMISSION ERROR: {e}{RESET}")
        return None


def parse_response(data):
    """Parses the intelligent JSON output from UniversalProvider"""
    if not data:
        return

    # 1. Check for Queue
    if data.get("status") == "queued":
        print(f"\n{BLUE}🌊 MILK OCEAN:{RESET} {data.get('message')}")
        return

    # 2. Check for Error
    if data.get("error"):
        print(f"\n{RED}🛑 ERROR:{RESET} {data.get('error')}")
        return

    # 3. Extract Content
    # Der Provider packt die Antwort manchmal tief in 'data' oder 'result'
    content = ""
    intent = "unknown"

    if "data" in data and isinstance(data["data"], dict):
        content = data["data"].get("summary", "")
        intent = data["data"].get("intent", "")
    elif "result" in data:
        content = data["result"]
    else:
        content = str(data)

    # 4. Render Output (The Darshan)
    print(f"\n{CYAN}🧠 THOUGHT ({intent}):{RESET} Analyzing reality structure...")
    time.sleep(0.2)
    print(f"{GREEN}⚡ ACTION:{RESET} Executing dharmic will...")
    time.sleep(0.2)

    print(f"\n{BOLD}🤖 ENVOY:{RESET}")
    print(f"{GOLD}{content}{RESET}\n")


def main():
    # 1. Wait for Kernel
    print(f"{DIM}Waiting for VibeOS Kernel at {BASE_URL}...{RESET}")
    retries = 0
    while not check_connection():
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
        retries += 1
        if retries > 10:
            print(f"\n{RED}❌ KERNEL NOT FOUND. Did you run './vibe' in another tab?{RESET}")
            sys.exit(1)

    print_header()

    # 2. Identity Check
    identity = "guest"
    if os.path.exists("data/keys/private.pem"):
        identity = "HIL"  # Human In Loop
        print(f"{GREEN}🔐 IDENTITY VERIFIED: CITIZEN MODE{RESET}")
    else:
        print(f"{DIM}👁️  IDENTITY UNVERIFIED: GUEST MODE{RESET}")

    # 3. Main Loop
    while True:
        try:
            user_input = input(f"{BLUE}YOU > {RESET}")

            if user_input.lower() in ["exit", "quit"]:
                print(f"{DIM}Closing Neural Link...{RESET}")
                break

            if not user_input.strip():
                continue

            response = send_prayer(user_input, identity)
            parse_response(response)

        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"{RED}CRASH: {e}{RESET}")


if __name__ == "__main__":
    main()
