#!/usr/bin/env python3
"""
VISHNU GUARD - The Watertight Integrity Enforcer (Layer 0)
==========================================================
GAD-000 COMPLIANT: ✓D ✓O ✓P ✓C ✓I ✓R

Enforces the "Ring 0" Protection Policy:
1. Ring 0 files are IMMUTABLE on branches.
2. They can ONLY be modified directly on 'main' (Sovereign Act).
3. Deviations trigger NUCLEAR RESTORE.

Usage:
    python3 scripts/governance/vishnu_guard.py [--json]
"""
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from vibe_core.protocols.integrity import VishnuIntegrityGuardian
except ImportError as e:
    # Fallback JSON output for GAD-000 compliance even on crash
    print(json.dumps({
        "guard": "VISHNU_GUARD",
        "status": "CRASHED",
        "error": str(e),
        "solution": "Fix imports in vibe_core/protocols/integrity.py"
    }))
    sys.exit(1)

def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def main():
    guardian = VishnuIntegrityGuardian()
    branch = get_current_branch()
    
    # 1. OBSERVABILITY (GAD-000)
    # Are we allowed to modify Ring 0?
    # Only 'main' is Sovereign. All other branches are Maya relative to Ring 0.
    is_sovereign_context = (branch == "main")
    
    # 2. VERIFICATION
    # Check if Ring 0 files differ from origin/main
    # Note: verify_ring_0 fetches origin/main internally
    is_intact = guardian.verify_ring_0()
    
    report = {
        "guard": "VISHNU_GUARD",
        "timestamp": str(subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"])).decode().strip(),
        "branch": branch,
        "is_sovereign": is_sovereign_context,
        "ring_0_status": "INTACT" if is_intact else "MODIFIED",
        "protected_files": guardian.get_protected_files(),
        "action": "NONE",
        "restored": []
    }

    # 3. ENFORCEMENT (The Law)
    if is_intact:
        # All good. The foundation is solid.
        print(json.dumps(report, indent=2))
        sys.exit(0)
        
    else:
        # Ring 0 is modified.
        if is_sovereign_context:
            # We are on main. This is a Sovereign Act. ALLOW.
            report["action"] = "ALLOWED_SOVEREIGN_MODIFICATION"
            print(json.dumps(report, indent=2))
            # Warn the user in stderr (human readable)
            print(f"\n⚠️  WARNING: You are modifying RING 0 on '{branch}'. Ensure this is intentional.", file=sys.stderr)
            sys.exit(0)
        else:
            # We are on a branch. This is Rebellion. RESTORE.
            print(f"\n🚫 BLOCK: Ring 0 modification detected on '{branch}'. Initiating VISHNU RESTORE...", file=sys.stderr)
            
            try:
                restored_files = guardian.restore_kernel()
                report["action"] = "NUCLEAR_RESTORE"
                report["restored"] = restored_files
                report["status"] = "RESTORED"
                
                print(json.dumps(report, indent=2))
                
                # Human readable trailer
                print("\n╔══════════════════════════════════════════════════════════════╗", file=sys.stderr)
                print("║  ☢️  NUCLEAR RESET EXECUTED (GAD-000 PROTECTION)              ║", file=sys.stderr)
                print("║  Violations reverted to origin/main.                         ║", file=sys.stderr)
                print(f"║  Branch '{branch}' is not authorized to touch Ring 0.       ║", file=sys.stderr)
                print("╚══════════════════════════════════════════════════════════════╝\n", file=sys.stderr)
                
                # EXIT 1 to STOP the commit of the *modified* (now reverted) files?
                # Actually, if we restored, the files on disk are now clean (origin/main).
                # But the INDEX might still have the changes staged!
                # restore_kernel does 'git add', so the index now matches origin/main.
                # If we exit 0, the commit proceeds with the RESTORED (old) files.
                # If we exit 1, the commit stops, user sees the revert.
                # Exiting 1 is safer (fail fast).
                sys.exit(1) 
                
            except Exception as e:
                report["status"] = "FAILED"
                report["error"] = str(e)
                print(json.dumps(report, indent=2))
                sys.exit(1)

if __name__ == "__main__":
    main()