#!/usr/bin/env python3
"""
WATCHMAN Shim - Vibe-OS Adapter for Standalone Execution.

Usage:
    python watchman/shim.py --action triage --issue_id 123
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WATCHMAN_SHIM")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchman.cartridge_main import WatchmanCartridge

def main():
    parser = argparse.ArgumentParser(description="WATCHMAN Agent - Shim")
    parser.add_argument("--action", choices=["triage"], required=True, help="Action to execute")
    parser.add_argument("--issue_id", type=int, help="GitHub Issue ID to triage")
    
    args = parser.parse_args()
    
    try:
        logger.info("👀 Booting WATCHMAN Cartridge...")
        cartridge = WatchmanCartridge()
        
        if args.action == "triage":
            if not args.issue_id:
                logger.error("❌ --issue_id required for triage")
                sys.exit(1)
                
            result = cartridge.triage_issue(args.issue_id)
            logger.info(f"✅ Triage result: {result}")
            
    except Exception as e:
        logger.error(f"❌ Critical failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
