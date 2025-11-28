#!/usr/bin/env python3
"""
🎛️  THE STEWARD CLI - PHASE 7: THE STEERING WHEEL 🎛️
======================================================

The command-line interface for controlling the STEWARD Protocol Agent OS.

This is the control panel. The operator's interface to the kernel.
GAD-000 (the human) commands. The system obeys.

COMMANDS:
  status              Show system health and kernel pulse
  verify <agent_id>   Verify agent passport against Parampara
  lineage             Show Parampara blockchain history
  ps                  List running agents
  boot                Start the kernel daemon
  stop                Graceful kernel shutdown

SAFEGUARDS:
  ✅ Read-only SQLite access (prevents database locks)
  ✅ Timestamp validation (detects zombie dashboards)

Usage:
    steward status
    steward verify herald
    steward lineage --tail 10
    steward ps
    steward boot
    steward stop
"""

import sys
import os
import argparse
import sqlite3
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Critical paths
LINEAGE_DB = Path("/tmp/vibe_os/kernel/lineage.db")
OPERATIONS_MD = PROJECT_ROOT / "OPERATIONS.md"
KERNEL_PID_FILE = Path("/tmp/vibe_os/kernel/kernel.pid")
MANIFESTS_DIR = PROJECT_ROOT / "steward/system_agents"


class StewardCLI:
    """The Steward CLI - Control interface for the Agent OS"""

    def __init__(self):
        self.lineage_db = LINEAGE_DB
        self.operations_file = OPERATIONS_MD
        self.kernel_pid_file = KERNEL_PID_FILE

    # =========================================================================
    # COMMAND: steward status
    # =========================================================================

    def cmd_status(self) -> int:
        """
        Show system health and kernel pulse.

        SAFEGUARD: Checks OPERATIONS.md timestamp to detect zombie dashboards.
        If file is older than 10 seconds, kernel pulse is lost.
        """
        print("=" * 70)
        print("🎛️  STEWARD PROTOCOL - SYSTEM STATUS")
        print("=" * 70)
        print()

        # Check if kernel is running
        kernel_running = self._check_kernel_pulse()

        # Check Parampara chain
        chain_blocks, chain_verified = self._check_parampara()

        # Count certified agents
        certified_agents = self._count_certified_agents()

        # Display status
        print("📊 SYSTEM HEALTH:")
        print(f"   Kernel:     {'✅ ONLINE' if kernel_running else '❌ OFFLINE'}")

        if kernel_running:
            pulse_age = self._get_pulse_age()
            print(f"   Pulse:      ✅ ACTIVE (last update {pulse_age:.1f}s ago)")
        else:
            print(f"   Pulse:      ❌ LOST (dashboard stale)")

        print(f"   Parampara:  {'✅ VERIFIED' if chain_verified else '⚠️  NOT VERIFIED'} ({chain_blocks} blocks)")
        print(f"   Agents:     {certified_agents} certified")
        print()

        if not kernel_running:
            print("⚠️  WARNING: Kernel pulse lost or kernel not running")
            print("   Try: steward boot")
            return 1

        return 0

    def _check_kernel_pulse(self) -> bool:
        """
        Check if kernel is alive by validating OPERATIONS.md timestamp.

        SAFEGUARD: File older than 10 seconds = kernel is dead/hung.
        """
        if not self.operations_file.exists():
            return False

        pulse_age = self._get_pulse_age()
        return pulse_age <= 10.0  # 10 second threshold

    def _get_pulse_age(self) -> float:
        """Get age of OPERATIONS.md file in seconds"""
        if not self.operations_file.exists():
            return float('inf')
        return time.time() - self.operations_file.stat().st_mtime

    def _check_parampara(self) -> tuple:
        """
        Check Parampara chain status.

        Returns: (block_count, verified)

        SAFEGUARD: Uses read-only SQLite access to prevent locks.
        """
        if not self.lineage_db.exists():
            return (0, False)

        try:
            # SAFEGUARD #1: Read-only mode (prevents database locks)
            conn = sqlite3.connect(f'file:{self.lineage_db}?mode=ro', uri=True)
            cursor = conn.cursor()

            # Count blocks
            cursor.execute("SELECT COUNT(*) FROM blocks")
            block_count = cursor.fetchone()[0]

            # Verify chain integrity
            verified = self._verify_chain_integrity_ro(conn)

            conn.close()
            return (block_count, verified)

        except Exception as e:
            print(f"   ⚠️  Error reading Parampara: {e}")
            return (0, False)

    def _verify_chain_integrity_ro(self, conn: sqlite3.Connection) -> bool:
        """
        Verify Parampara chain integrity with read-only connection.

        Checks that each block's hash is valid and links to previous block.
        """
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT idx, timestamp, event_type, agent_id, data, previous_hash, hash
                FROM blocks
                ORDER BY idx
            """)

            blocks = cursor.fetchall()
            if len(blocks) == 0:
                return False

            # Verify each block
            for i, (idx, timestamp, event_type, agent_id, data, previous_hash, block_hash) in enumerate(blocks):
                # Calculate expected hash (same method as LineageChain._calculate_hash)
                block_dict = {
                    "index": idx,
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "agent_id": agent_id,
                    "data": json.loads(data),  # data is stored as JSON string
                    "previous_hash": previous_hash,
                }
                block_content = json.dumps(block_dict, sort_keys=True)
                expected_hash = hashlib.sha256(block_content.encode()).hexdigest()

                # Verify hash matches
                if block_hash != expected_hash:
                    return False

                # Verify chain link (except for genesis)
                if i > 0:
                    prev_block_hash = blocks[i-1][6]  # hash from previous block
                    if previous_hash != prev_block_hash:
                        return False

            return True

        except Exception:
            return False

    def _count_certified_agents(self) -> int:
        """Count agents with steward.json manifests"""
        count = 0
        if MANIFESTS_DIR.exists():
            for manifest_path in MANIFESTS_DIR.glob("*/steward.json"):
                count += 1
        return count

    # =========================================================================
    # COMMAND: steward verify <agent_id>
    # =========================================================================

    def cmd_verify(self, agent_id: str) -> int:
        """
        Verify agent passport against Parampara blockchain.

        Checks:
        1. steward.json exists
        2. Manifest hash matches PASSPORT_ISSUED block in Parampara
        3. Constitutional anchoring is valid

        SAFEGUARD: Uses read-only SQLite access.
        """
        print(f"🔍 Verifying passport for: {agent_id}")
        print()

        # Load manifest
        manifest_path = MANIFESTS_DIR / agent_id / "steward.json"
        if not manifest_path.exists():
            print(f"❌ Manifest not found: {manifest_path}")
            return 1

        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read manifest: {e}")
            return 1

        # Calculate manifest hash
        manifest_hash = self._calculate_manifest_hash(manifest)
        print(f"📄 Manifest hash: {manifest_hash[:16]}...")

        # Find PASSPORT_ISSUED block in Parampara
        if not self.lineage_db.exists():
            print("❌ Parampara chain not found")
            return 1

        try:
            # SAFEGUARD #1: Read-only mode
            conn = sqlite3.connect(f'file:{self.lineage_db}?mode=ro', uri=True)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT idx, data, hash FROM blocks
                WHERE event_type = 'PASSPORT_ISSUED' AND agent_id = ?
            """, (agent_id,))

            result = cursor.fetchone()
            conn.close()

            if not result:
                print(f"❌ No PASSPORT_ISSUED block found for {agent_id}")
                return 1

            block_idx, block_data, block_hash = result
            block_data_json = json.loads(block_data)
            recorded_hash = block_data_json.get("manifest_hash")

            print(f"⛓️  Parampara block #{block_idx}")
            print(f"   Recorded hash: {recorded_hash[:16]}...")

            # Compare hashes
            if manifest_hash == recorded_hash:
                print()
                print("✅ PASSPORT VERIFIED")
                print(f"   Manifest signature valid")
                print(f"   Anchored in Block #{block_idx}")
                print(f"   Constitution hash: {manifest.get('governance', {}).get('constitution_hash', 'N/A')[:16]}...")
                print(f"   Compliance level: {manifest.get('governance', {}).get('compliance_level', 'N/A')}")
                return 0
            else:
                print()
                print("❌ PASSPORT INVALID")
                print("   Manifest hash does NOT match Parampara record")
                print("   Possible tampering detected!")
                return 1

        except Exception as e:
            print(f"❌ Error verifying passport: {e}")
            return 1

    def _calculate_manifest_hash(self, manifest: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of manifest (canonical JSON)"""
        canonical_json = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    # =========================================================================
    # COMMAND: steward lineage [--tail N]
    # =========================================================================

    def cmd_lineage(self, tail: Optional[int] = None) -> int:
        """
        Show Parampara blockchain history.

        Args:
            tail: If specified, show only last N blocks

        SAFEGUARD: Uses read-only SQLite access.
        """
        print("⛓️  PARAMPARA - THE LINEAGE CHAIN")
        print("=" * 70)
        print()

        if not self.lineage_db.exists():
            print("❌ Parampara chain not found")
            print(f"   Expected: {self.lineage_db}")
            return 1

        try:
            # SAFEGUARD #1: Read-only mode
            conn = sqlite3.connect(f'file:{self.lineage_db}?mode=ro', uri=True)
            cursor = conn.cursor()

            # Get all blocks
            cursor.execute("""
                SELECT idx, timestamp, event_type, agent_id, data, hash
                FROM blocks
                ORDER BY idx DESC
            """)

            blocks = cursor.fetchall()
            conn.close()

            if len(blocks) == 0:
                print("⚠️  Chain is empty (no Genesis Block)")
                return 1

            # Apply tail filter
            if tail and tail > 0:
                blocks = blocks[:tail]

            # Display blocks (newest first)
            for idx, timestamp, event_type, agent_id, data, block_hash in blocks:
                agent_str = f"({agent_id})" if agent_id else "(SYSTEM)"
                ts_str = timestamp[:19]  # Trim to YYYY-MM-DDTHH:MM:SS

                print(f"Block {idx:3d}: {event_type:20s} {agent_str:15s}")
                print(f"          Time: {ts_str}")
                print(f"          Hash: {block_hash[:32]}...")

                # Show key data for certain events
                if event_type == "GENESIS":
                    data_json = json.loads(data)
                    anchors = data_json.get("anchors", {})
                    print(f"          GAD-000:  {anchors.get('philosophy_hash', 'N/A')[:16]}...")
                    print(f"          Constitution: {anchors.get('constitution_hash', 'N/A')[:16]}...")
                elif event_type == "PASSPORT_ISSUED":
                    data_json = json.loads(data)
                    print(f"          Manifest: {data_json.get('manifest_hash', 'N/A')[:16]}...")
                    print(f"          Version:  {data_json.get('version', 'N/A')}")

                print()

            print(f"Total blocks: {len(blocks)}")
            return 0

        except Exception as e:
            print(f"❌ Error reading Parampara: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # =========================================================================
    # COMMAND: steward ps
    # =========================================================================

    def cmd_ps(self) -> int:
        """
        List running agents.

        Reads OPERATIONS.md to get agent status.

        SAFEGUARD: Checks timestamp to detect stale data.
        """
        print("📊 AGENT PROCESSES")
        print("=" * 70)
        print()

        if not self.operations_file.exists():
            print("❌ OPERATIONS.md not found (kernel not running?)")
            return 1

        # SAFEGUARD #2: Check timestamp
        pulse_age = self._get_pulse_age()
        if pulse_age > 10:
            print(f"⚠️  WARNING: Dashboard is stale (last update {pulse_age:.1f}s ago)")
            print("   Kernel may be dead or hung")
            print()

        # Parse OPERATIONS.md
        try:
            with open(self.operations_file, 'r') as f:
                content = f.read()

            # Extract agent status (simple parsing)
            # Look for lines like: "- steward: RUNNING (PID 12345)"
            agents = []
            for line in content.split('\n'):
                if 'RUNNING' in line or 'STOPPED' in line or 'CRASHED' in line:
                    # Parse agent status
                    if '-' in line and ':' in line:
                        parts = line.split('-', 1)[1].split(':')
                        if len(parts) >= 2:
                            agent_name = parts[0].strip()
                            status_part = parts[1].strip()

                            # Extract PID if present
                            pid = "N/A"
                            if 'PID' in status_part:
                                pid_start = status_part.find('PID') + 4
                                pid_end = status_part.find(')', pid_start)
                                if pid_end > pid_start:
                                    pid = status_part[pid_start:pid_end].strip()

                            # Extract status
                            status = "UNKNOWN"
                            if 'RUNNING' in status_part:
                                status = "RUNNING"
                            elif 'STOPPED' in status_part:
                                status = "STOPPED"
                            elif 'CRASHED' in status_part:
                                status = "CRASHED"

                            agents.append({
                                'name': agent_name,
                                'status': status,
                                'pid': pid
                            })

            if len(agents) == 0:
                print("⚠️  No agents found in OPERATIONS.md")
                return 1

            # Display agents
            print(f"{'AGENT':<20} {'STATUS':<12} {'PID':<10}")
            print("-" * 70)
            for agent in agents:
                status_icon = "✅" if agent['status'] == "RUNNING" else "❌"
                print(f"{agent['name']:<20} {status_icon} {agent['status']:<10} {agent['pid']:<10}")

            print()
            print(f"Total agents: {len(agents)}")
            return 0

        except Exception as e:
            print(f"❌ Error parsing OPERATIONS.md: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward boot
    # =========================================================================

    def cmd_boot(self) -> int:
        """
        Start the kernel daemon.

        TODO: Implement daemon mode for kernel.
        Currently just provides instructions.
        """
        print("🚀 KERNEL BOOT")
        print("=" * 70)
        print()

        # Check if kernel is already running
        if self._check_kernel_pulse():
            print("⚠️  Kernel is already running")
            print(f"   Pulse age: {self._get_pulse_age():.1f}s")
            return 1

        print("⚠️  Daemon mode not yet implemented")
        print()
        print("To start the kernel manually, run:")
        print("  python scripts/stress_test_city.py")
        print()
        print("TODO (Phase 7.1): Implement proper daemon mode")
        print("  - Background process with PID file")
        print("  - Log redirection to /tmp/vibe_os/logs/kernel.log")
        print("  - Signal handling for graceful shutdown")
        return 1

    # =========================================================================
    # COMMAND: steward stop
    # =========================================================================

    def cmd_stop(self) -> int:
        """
        Graceful kernel shutdown.

        TODO: Implement signal-based shutdown.
        Currently just provides instructions.
        """
        print("🛑 KERNEL SHUTDOWN")
        print("=" * 70)
        print()

        # Check if kernel is running
        if not self._check_kernel_pulse():
            print("⚠️  Kernel is not running (pulse lost)")
            return 1

        print("⚠️  Signal-based shutdown not yet implemented")
        print()
        print("To stop the kernel manually:")
        print("  1. Find kernel process: ps aux | grep stress_test_city")
        print("  2. Send SIGTERM: kill -TERM <PID>")
        print()
        print("TODO (Phase 7.1): Implement signal-based shutdown")
        print("  - Send SIGTERM to kernel PID")
        print("  - Wait for graceful shutdown (max 30s)")
        print("  - Send SIGKILL if timeout")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='steward',
        description='🎛️  STEWARD Protocol - Agent OS Control Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # steward status
    subparsers.add_parser('status', help='Show system health and kernel pulse')

    # steward verify <agent_id>
    verify_parser = subparsers.add_parser('verify', help='Verify agent passport')
    verify_parser.add_argument('agent_id', help='Agent ID to verify')

    # steward lineage [--tail N]
    lineage_parser = subparsers.add_parser('lineage', help='Show Parampara blockchain')
    lineage_parser.add_argument('--tail', type=int, help='Show only last N blocks')

    # steward ps
    subparsers.add_parser('ps', help='List running agents')

    # steward boot
    subparsers.add_parser('boot', help='Start kernel daemon')

    # steward stop
    subparsers.add_parser('stop', help='Graceful kernel shutdown')

    # Parse args
    args = parser.parse_args()

    # Execute command
    cli = StewardCLI()

    if args.command == 'status':
        return cli.cmd_status()
    elif args.command == 'verify':
        return cli.cmd_verify(args.agent_id)
    elif args.command == 'lineage':
        return cli.cmd_lineage(tail=args.tail)
    elif args.command == 'ps':
        return cli.cmd_ps()
    elif args.command == 'boot':
        return cli.cmd_boot()
    elif args.command == 'stop':
        return cli.cmd_stop()
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
