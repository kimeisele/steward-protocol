#!/usr/bin/env python3
"""
Test command parsing logic locally
"""
import sys
sys.path.insert(0, '/Users/ss/projects/steward-protocol')

# Test cases
test_commands = [
    "briefing",
    "status",
    "campaign",
    "Start a campaign for Agent City",
    "Create marketing for global scaling",
    "campaign make agent city famous",
    "Launch a campaign about trust and security",
]

def parse_command(command):
    """Simulate the parsing logic"""
    cmd_lower = command.lower().strip()
    
    if cmd_lower == "briefing":
        return {"command": "next_action", "args": {}}
    
    elif cmd_lower == "status":
        return {"command": "status", "args": {}}
    
    elif cmd_lower == "campaign" or "campaign" in cmd_lower:
        goal = None
        
        if cmd_lower == "campaign":
            return {"error": "Campaign goal required"}
        
        elif any(trigger in cmd_lower for trigger in ["start", "create", "launch"]):
            for marker in [" for ", " about ", " on ", " regarding "]:
                if marker in cmd_lower:
                    goal = command.split(marker, 1)[1].strip()
                    break
            if not goal:
                goal = command
        else:
            goal = command.replace("campaign", "").replace("Campaign", "").strip()
        
        if not goal:
            return {"error": "Could not extract goal"}
        
        return {"command": "campaign", "args": {"goal": goal}}
    
    else:
        return {"command": command, "args": {}}

print("Testing command parsing:\n")
for cmd in test_commands:
    result = parse_command(cmd)
    print(f"Input:  {cmd}")
    print(f"Output: {result}")
    print()
