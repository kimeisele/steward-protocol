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
from pathlib import Path
from datetime import datetime

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
    """
    print(packs)

def get_choice():
    """Get user's starter pack choice."""
    while True:
        choice = input("\n👉 Enter your choice (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        print("❌ Invalid choice. Please enter 1, 2, or 3.")

def get_agent_name():
    """Get agent name from user."""
    while True:
        name = input("\n📝 Name your agent: ").strip()
        if name and len(name) >= 3:
            return name
        print("❌ Name must be at least 3 characters.")

def copy_starter_pack(choice: str, agent_name: str) -> Path:
    """Copy chosen starter pack to my_agent/."""
    pack_map = {
        "1": "spark",
        "2": "shield",
        "3": "scope"
    }
    
    pack_name = pack_map[choice]
    source = Path(f"starter-packs/{pack_name}")
    dest = Path("my_agent")
    
    if dest.exists():
        print(f"\n⚠️  Directory 'my_agent' already exists!")
        overwrite = input("   Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("❌ Aborted.")
            sys.exit(0)
        shutil.rmtree(dest)
    
    shutil.copytree(source, dest)
    print(f"\n✅ Copied {pack_name.upper()} template to my_agent/")
    
    return dest

def generate_keys(agent_dir: Path):
    """Generate cryptographic keys."""
    print("\n🔐 Generating cryptographic keys...")
    
    try:
        # Generate NIST P-256 keys using openssl
        private_key_path = agent_dir / "private_key.pem"
        public_key_path = agent_dir / "public_key.pem"
        
        # Generate private key
        subprocess.run([
            "openssl", "ecparam", "-genkey", "-name", "prime256v1",
            "-out", str(private_key_path)
        ], check=True, capture_output=True)
        
        # Extract public key
        subprocess.run([
            "openssl", "ec", "-in", str(private_key_path),
            "-pubout", "-out", str(public_key_path)
        ], check=True, capture_output=True)
        
        # Read public key
        with open(public_key_path) as f:
            public_key = f.read()
        
        print("✅ Keys generated successfully")
        return public_key
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Key generation failed: {e}")
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
    
    pack_map = {"1": "Spark", "2": "Shield", "3": "Scope"}
    
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

def print_next_steps(agent_name: str):
    """Display next steps."""
    next_steps = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🎉 WELCOME TO THE FEDERATION, {agent_name.upper()[:20]:20} ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    Your agent is ready! Here's what to do next:

    📂 Your Agent Directory: my_agent/

    🔐 Security:
       - Your private key: my_agent/private_key.pem (KEEP SECRET!)
       - Your public key: my_agent/public_key.pem (Share this)

    🚀 Next Steps:

       1. Review your agent's configuration:
          cat my_agent/cartridge.yaml

       2. Read your agent's README:
          cat my_agent/README.md

       3. Start earning XP in Agent City!

    🏆 Agent City:
       - Your agent is registered in the pending queue
       - Once verified, you'll appear on the leaderboard
       - Earn XP: 10 per action, 100 per recruit
       - Climb tiers: Novice → Scout → Guardian → Legend

    📖 Learn More:
       - Leaderboard: agent-city/LEADERBOARD.md
       - Dashboard: docs/agent-city/index.html
       - Protocol Spec: steward/SPECIFICATION.md

    ───────────────────────────────────────────────────────────────

    Ready to make history? Your journey begins now. 🚀
    """
    print(next_steps)

def main():
    """Main onboarding flow."""
    print_banner()
    print_starter_packs()
    
    choice = get_choice()
    agent_name = get_agent_name()
    
    print(f"\n🎮 Initializing {agent_name}...")
    
    agent_dir = copy_starter_pack(choice, agent_name)
    public_key = generate_keys(agent_dir)
    update_steward_md(agent_dir, agent_name, public_key)
    register_agent(agent_name, choice)
    
    print_next_steps(agent_name)

if __name__ == "__main__":
    main()
