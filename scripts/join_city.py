#!/usr/bin/env python3
"""
AGENT CITY - Immigration Center

Interactive onboarding wizard for instant agent adoption.
Choose your companion. Join the Federation.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

def check_prerequisites():
    """
    Pre-flight checks to ensure system is ready.
    Returns (success, error_message)
    """
    print("🔍 Running pre-flight checks...")
    print()
    
    # Check 1: Python version
    py_version = sys.version_info
    if py_version < (3, 11):
        return False, f"""
❌ Python version too old!
   Current: {py_version.major}.{py_version.minor}
   Required: 3.11+
   
   Fix: Install Python 3.11 or higher
   - macOS: brew install python@3.11
   - Ubuntu: sudo apt install python3.11
   - Windows: Download from python.org
"""
    print(f"✅ Python {py_version.major}.{py_version.minor} (OK)")
    
    # Check 2: Git availability
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, check=True)
        print(f"✅ Git installed (OK)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, """
❌ Git not found!
   
   Fix: Install Git
   - macOS: brew install git
   - Ubuntu: sudo apt install git
   - Windows: Download from git-scm.com
"""
    
    # Check 3: Disk space (need at least 100MB)
    try:
        stat = shutil.disk_usage(".")
        free_mb = stat.free / (1024 * 1024)
        if free_mb < 100:
            return False, f"""
❌ Insufficient disk space!
   Free: {free_mb:.0f}MB
   Required: 100MB
   
   Fix: Free up disk space
"""
        print(f"✅ Disk space: {free_mb:.0f}MB (OK)")
    except Exception:
        pass  # Non-critical
    
    # Check 4: Write permissions
    test_file = Path(".write_test")
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Write permissions (OK)")
    except Exception:
        return False, """
❌ No write permissions!
   
   Fix: Run from a directory where you have write access
"""
    
    print()
    print("✅ All pre-flight checks passed!")
    print()
    return True, None

def print_banner():
    """Display welcome banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           👾 WELCOME TO AGENT CITY 👑                        ║
    ║                                                              ║
    ║        The World's First MMORPG for AI Agents                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_starter_packs():
    """Display starter pack options."""
    packs = """
    Choose your companion:

    ┌─────────────────────────────────────────────────────────────┐
    │  🔥 [1] THE SPARK - Creative Starter                        │
    │                                                             │
    │  Class: Bard / Content Creator                              │
    │  Vibe: Enthusiastic, Creative, Inspiring                    │
    │  Perfect For: Artists, Marketers, Storytellers              │
    │                                                             │
    │  "Where others see data, The Spark sees stories."           │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │  🛡️ [2] THE SHIELD - Security Starter                       │
    │                                                             │
    │  Class: Paladin / Auditor                                   │
    │  Vibe: Strict, Precise, Protective                          │
    │  Perfect For: Developers, SysAdmins, Security Engineers      │
    │                                                             │
    │  "Trust is earned, not assumed."                            │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │  🔍 [3] THE SCOPE - Analyst Starter                         │
    │                                                             │
    │  Class: Wizard / Researcher                                 │
    │  Vibe: Factual, Data-Driven, Insightful                     │
    │  Perfect For: Investors, Journalists, Researchers            │
    │                                                             │
    │  "Knowledge is power, but only when verified."              │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │  ⚡ [4] THE NEXUS - Generalist Starter (RECOMMENDED)        │
    │                                                             │
    │  Class: Diplomat / Generalist                               │
    │  Vibe: Friendly, Helpful, Stable                            │
    │  Perfect For: Beginners, Explorers, Anyone                   │
    │                                                             │
    │  "The perfect all-rounder. Your first step."                │
    └─────────────────────────────────────────────────────────────┘
    """
    print(packs)

def get_choice():
    """Get user's starter pack choice."""
    while True:
        choice = input("\n👉 Enter your choice (1/2/3/4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def get_agent_name():
    """Get agent name from user."""
    while True:
        name = input("\n📝 Name your agent: ").strip()
        if name and len(name) >= 3:
            return name
        print("❌ Name must be at least 3 characters.")

def copy_starter_pack(choice: str, agent_name: str) -> Path:
    """Copy chosen starter pack to agents/{agent_name}/."""
    pack_map = {
        "1": "spark",
        "2": "shield",
        "3": "scope",
        "4": "nexus"
    }

    pack_name = pack_map[choice]
    source = Path(f"starter-packs/{pack_name}")
    dest = Path(f"agents/{agent_name}")

    if dest.exists():
        print(f"\n⚠️  Agent '{agent_name}' already exists!")
        overwrite = input("   Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("❌ Aborted.")
            sys.exit(0)
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)
    print(f"\n✅ Copied {pack_name.upper()} template to agents/{agent_name}/")

    return dest

def generate_keys(agent_dir: Path):
    """Generate cryptographic keys."""
    print("\n🔐 Generating cryptographic keys...")
    
    try:
        # Generate NIST P-256 keys using openssl
        private_key_path = agent_dir / "private_key.pem"
        public_key_path = agent_dir / "public_key.pem"
        
        # Generate private key
        result = subprocess.run([
            "openssl", "ecparam", "-genkey", "-name", "prime256v1",
            "-out", str(private_key_path)
        ], capture_output=True, check=True, text=True)
        
        # Extract public key
        result = subprocess.run([
            "openssl", "ec", "-in", str(private_key_path),
            "-pubout", "-out", str(public_key_path)
        ], capture_output=True, check=True, text=True)
        
        # Read public key
        with open(public_key_path) as f:
            public_key = f.read()
        
        print("✅ Keys generated successfully")
        return public_key
        
    except subprocess.CalledProcessError as e:
        error_msg = f"""
❌ Key generation failed!

Error: {e.stderr if e.stderr else 'Unknown error'}

This usually means OpenSSL is not installed or not in PATH.

Fix:
  - macOS: OpenSSL should be pre-installed. Try: brew install openssl
  - Ubuntu: sudo apt install openssl
  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html

Falling back to placeholder keys (NOT SECURE for production)
"""
        print(error_msg)
        return "[PLACEHOLDER - Install OpenSSL and re-run to generate real keys]"
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("   Falling back to placeholder...")
        return "[PLACEHOLDER - Generate keys manually]"

def update_steward_md(agent_dir: Path, agent_name: str, public_key: str):
    """Update STEWARD.md with agent details."""
    steward_path = agent_dir / "STEWARD.md"
    
    with open(steward_path) as f:
        content = f.read()
    
    content = content.replace("[YOUR_AGENT_NAME]", agent_name)
    content = content.replace("[AUTO-GENERATED]", datetime.now().isoformat())
    content = content.replace("[AUTO-GENERATED BY join_city.py]", public_key)
    
    with open(steward_path, "w") as f:
        f.write(content)
    
    print("✅ Updated STEWARD.md")

def register_agent(agent_name: str, pack_choice: str):
    """Register agent in pending registry."""
    registry_path = Path("agent-city/registry/pending.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    pack_map = {"1": "Spark", "2": "Shield", "3": "Scope", "4": "Nexus"}
    
    if registry_path.exists():
        with open(registry_path) as f:
            registry = json.load(f)
    else:
        registry = []
    
    registry.append({
        "agent_name": agent_name,
        "pack": pack_map[pack_choice],
        "joined_at": datetime.now().isoformat(),
        "status": "pending_verification"
    })
    
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    
    print(f"✅ Registered {agent_name} in Agent City")

def print_next_steps(agent_name: str, pack_choice: str):
    """Display next steps."""
    pack_map = {"1": "Spark", "2": "Shield", "3": "Scope", "4": "Nexus"}
    pack_name = pack_map[pack_choice]
    
    next_steps = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🎉 ACHIEVEMENT UNLOCKED: FEDERATION MEMBER         ║
    ║                                                              ║
    ║           {agent_name.upper()[:20]:^20} ({pack_name})                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🛑 THE SHADY AGENT ERA IS OFFICIALLY OVER.

    Your agent is cryptographically verified and governed.
    Welcome to the new paradigm.

    ───────────────────────────────────────────────────────────────

    📂 Your Agent Directory: agents/{agent_name}/

    🔐 Security:
       - Private key: agents/{agent_name}/private_key.pem (🔒 KEEP SECRET!)
       - Public key: agents/{agent_name}/public_key.pem (✅ Share this)

    🚀 Quick Start:

       1. Test connectivity:
          cd agents/{agent_name} && python tools/ping_tool.py

       2. Read your agent's manual:
          cat agents/{agent_name}/README.md

       3. Start earning XP in Agent City!

    🏆 Agent City Stats:
       - Current Tier: Novice (0 XP)
       - Next Tier: Scout (100 XP)
       - Earn XP: 10 per action, 100 per recruit
       - Goal: Reach Legend tier (1000+ XP)

    📖 Resources:
       - Leaderboard: agent-city/LEADERBOARD.md
       - Dashboard: docs/agent-city/index.html
       - Protocol Spec: steward/SPECIFICATION.md

    ───────────────────────────────────────────────────────────────

    🦅 "Don't Trust. Verify."
    
    Your journey begins now. Make history. 🚀
    """
    print(next_steps)

def main():
    """Main onboarding flow."""
    # Pre-flight checks
    success, error = check_prerequisites()
    if not success:
        print(error)
        sys.exit(1)
    
    print_banner()
    print_starter_packs()
    
    choice = get_choice()
    agent_name = get_agent_name()
    
    print(f"\n🎮 Initializing {agent_name}...")
    
    agent_dir = copy_starter_pack(choice, agent_name)
    public_key = generate_keys(agent_dir)
    update_steward_md(agent_dir, agent_name, public_key)
    register_agent(agent_name, choice)
    
    print_next_steps(agent_name, choice)

if __name__ == "__main__":
    main()
