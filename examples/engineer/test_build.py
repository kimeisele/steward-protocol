"""
Test script for The Engineer Agent.
Asks the Engineer to build a 'Greeter' agent.
"""
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from steward.system_agents.engineer.cartridge_main import EngineerCartridge

def test_engineer():
    # Setup
    agent_name = "greeter"
    mission = "Say hello to the world when run."
    
    # Clean up previous run
    if Path(agent_name).exists():
        shutil.rmtree(agent_name)
    
    print(f"🧪 Testing Engineer with agent: {agent_name}")
    
    # Initialize Engineer
    engineer = EngineerCartridge()
    
    # Run
    print("🔨 Requesting agent creation...")
    result_path = engineer.create_agent(agent_name, mission)
    
    # Verify
    print(f"📝 Result: {result_path}")
    
    if "Error" in result_path:
        print("❌ Creation failed")
        sys.exit(1)
        
    path = Path(result_path)
    if path.exists():
        print("✅ File created successfully")
        print("-" * 40)
        print(path.read_text())
        print("-" * 40)
        
        # Verify content
        content = path.read_text()
        if "GreeterCartridge" in content and "run" in content:
            print("✅ Code looks valid (Class and run method found)")
        else:
            print("❌ Code validation failed")
    else:
        print("❌ File not found")

    # Cleanup (optional, maybe keep it to inspect)
    # shutil.rmtree(agent_name)

if __name__ == "__main__":
    test_engineer()
