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
  init <agent_id>     Initialize new agent manifest (steward.json)
  discover            Discover all registered agents
  introspect          Show detailed kernel state and statistics
  delegate            Submit task to agent (TODO)

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
import signal
import subprocess
import uuid
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

        print(
            f"   Parampara:  {'✅ VERIFIED' if chain_verified else '⚠️  NOT VERIFIED'} ({chain_blocks} blocks)"
        )
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
            return float("inf")
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
            conn = sqlite3.connect(f"file:{self.lineage_db}?mode=ro", uri=True)
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
            cursor.execute(
                """
                SELECT idx, timestamp, event_type, agent_id, data, previous_hash, hash
                FROM blocks
                ORDER BY idx
            """
            )

            blocks = cursor.fetchall()
            if len(blocks) == 0:
                return False

            # Verify each block
            for i, (
                idx,
                timestamp,
                event_type,
                agent_id,
                data,
                previous_hash,
                block_hash,
            ) in enumerate(blocks):
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
                    prev_block_hash = blocks[i - 1][6]  # hash from previous block
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
            with open(manifest_path, "r") as f:
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
            conn = sqlite3.connect(f"file:{self.lineage_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT idx, data, hash FROM blocks
                WHERE event_type = 'PASSPORT_ISSUED' AND agent_id = ?
            """,
                (agent_id,),
            )

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
                print(
                    f"   Constitution hash: {manifest.get('governance', {}).get('constitution_hash', 'N/A')[:16]}..."
                )
                print(
                    f"   Compliance level: {manifest.get('governance', {}).get('compliance_level', 'N/A')}"
                )
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
        canonical_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

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
            conn = sqlite3.connect(f"file:{self.lineage_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Get all blocks
            cursor.execute(
                """
                SELECT idx, timestamp, event_type, agent_id, data, hash
                FROM blocks
                ORDER BY idx DESC
            """
            )

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
                    print(
                        f"          GAD-000:  {anchors.get('philosophy_hash', 'N/A')[:16]}..."
                    )
                    print(
                        f"          Constitution: {anchors.get('constitution_hash', 'N/A')[:16]}..."
                    )
                elif event_type == "PASSPORT_ISSUED":
                    data_json = json.loads(data)
                    print(
                        f"          Manifest: {data_json.get('manifest_hash', 'N/A')[:16]}..."
                    )
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
            with open(self.operations_file, "r") as f:
                content = f.read()

            # Extract agent status (simple parsing)
            # Look for lines like: "- steward: RUNNING (PID 12345)"
            agents = []
            for line in content.split("\n"):
                if "RUNNING" in line or "STOPPED" in line or "CRASHED" in line:
                    # Parse agent status
                    if "-" in line and ":" in line:
                        parts = line.split("-", 1)[1].split(":")
                        if len(parts) >= 2:
                            agent_name = parts[0].strip()
                            status_part = parts[1].strip()

                            # Extract PID if present
                            pid = "N/A"
                            if "PID" in status_part:
                                pid_start = status_part.find("PID") + 4
                                pid_end = status_part.find(")", pid_start)
                                if pid_end > pid_start:
                                    pid = status_part[pid_start:pid_end].strip()

                            # Extract status
                            status = "UNKNOWN"
                            if "RUNNING" in status_part:
                                status = "RUNNING"
                            elif "STOPPED" in status_part:
                                status = "STOPPED"
                            elif "CRASHED" in status_part:
                                status = "CRASHED"

                            agents.append(
                                {"name": agent_name, "status": status, "pid": pid}
                            )

            if len(agents) == 0:
                print("⚠️  No agents found in OPERATIONS.md")
                return 1

            # Display agents
            print(f"{'AGENT':<20} {'STATUS':<12} {'PID':<10}")
            print("-" * 70)
            for agent in agents:
                status_icon = "✅" if agent["status"] == "RUNNING" else "❌"
                print(
                    f"{agent['name']:<20} {status_icon} {agent['status']:<10} {agent['pid']:<10}"
                )

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

        Spawns kernel in background process, writes PID file, redirects logs.
        """
        print("🚀 KERNEL BOOT")
        print("=" * 70)
        print()

        # Check if kernel is already running
        if self._check_kernel_pulse():
            print("⚠️  Kernel is already running")
            print(f"   Pulse age: {self._get_pulse_age():.1f}s")
            return 1

        # Ensure log directory exists
        log_dir = Path("/tmp/vibe_os/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        kernel_log = log_dir / "kernel.log"
        kernel_pidfile = Path("/tmp/vibe_os/kernel/kernel.pid")
        kernel_pidfile.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Start kernel in background
            with open(kernel_log, "w") as log_file:
                kernel_process = subprocess.Popen(
                    [
                        sys.executable,
                        str(PROJECT_ROOT / "scripts" / "stress_test_city.py"),
                    ],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,  # Daemonize
                )

            # Write PID file
            with open(kernel_pidfile, "w") as f:
                f.write(str(kernel_process.pid))

            # Give kernel time to boot
            time.sleep(1)

            # Verify kernel is running
            try:
                os.kill(kernel_process.pid, 0)  # Signal 0 = check if process exists
                print(f"✅ Kernel started (PID: {kernel_process.pid})")
                print(f"   Logs: {kernel_log}")
                print()
                print("To monitor logs:")
                print(f"  tail -f {kernel_log}")
                return 0
            except ProcessLookupError:
                print(f"❌ Kernel process exited unexpectedly")
                print(f"   Check logs: {kernel_log}")
                return 1

        except Exception as e:
            print(f"❌ Failed to start kernel: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward stop
    # =========================================================================

    def cmd_stop(self) -> int:
        """
        Graceful kernel shutdown.

        Sends SIGTERM to kernel process, waits for graceful shutdown.
        Falls back to SIGKILL if timeout.
        """
        print("🛑 KERNEL SHUTDOWN")
        print("=" * 70)
        print()

        # Check if kernel is running
        if not self._check_kernel_pulse():
            print("⚠️  Kernel is not running (pulse lost)")
            return 1

        # Get PID from file
        pidfile = Path("/tmp/vibe_os/kernel/kernel.pid")
        if not pidfile.exists():
            print("⚠️  PID file not found")
            print("   Try: kill -TERM <pid> manually")
            return 1

        try:
            with open(pidfile, "r") as f:
                pid = int(f.read().strip())

            print(f"Shutting down kernel (PID: {pid})...")
            print()

            # Send SIGTERM (graceful shutdown)
            os.kill(pid, signal.SIGTERM)

            # Wait for graceful shutdown (max 30s)
            for i in range(30):
                time.sleep(1)
                try:
                    os.kill(pid, 0)  # Check if still alive
                except ProcessLookupError:
                    print("✅ Kernel shut down gracefully")
                    pidfile.unlink()
                    return 0

            # Timeout - force kill
            print("⚠️  Graceful shutdown timeout, sending SIGKILL...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)

            try:
                os.kill(pid, 0)
                print("❌ SIGKILL failed")
                return 1
            except ProcessLookupError:
                print("✅ Kernel force-killed")
                pidfile.unlink()
                return 0

        except (ValueError, FileNotFoundError) as e:
            print(f"❌ Error reading PID file: {e}")
            return 1
        except ProcessLookupError:
            print("✅ Kernel already dead")
            pidfile.unlink()
            return 0
        except Exception as e:
            print(f"❌ Error stopping kernel: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward init
    # =========================================================================

    def cmd_init(self, agent_id: str) -> int:
        """
        Initialize a new agent with steward.json manifest.

        Creates a minimal steward.json in current directory.
        """
        print(f"📝 Initializing agent: {agent_id}")
        print()

        manifest_path = Path(f"steward.json")
        if manifest_path.exists():
            print(f"❌ Manifest already exists: {manifest_path}")
            return 1

        # Create minimal manifest
        manifest = {
            "identity": {"agent_id": agent_id, "name": agent_id.upper()},
            "specs": {"version": "1.0.0", "domain": "CUSTOM", "description": ""},
            "capabilities": {"operations": []},
            "governance": {
                "constitution_hash": "",
                "compliance_level": 1,
                "issued_at": datetime.utcnow().isoformat() + "Z",
                "issuer": "manual",
            },
        }

        try:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"✅ Created: {manifest_path}")
            print()
            print("Next steps:")
            print("  1. Edit steward.json (fill in domain, description, capabilities)")
            print("  2. Run: steward verify <agent_id>")
            return 0
        except Exception as e:
            print(f"❌ Error creating manifest: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward discover
    # =========================================================================

    def cmd_discover(self) -> int:
        """
        Discover all registered agents in the system.

        Reads Parampara chain for AGENT_REGISTERED events.
        """
        print("🔍 AGENT DISCOVERY")
        print("=" * 70)
        print()

        if not self.lineage_db.exists():
            print("❌ Parampara chain not found")
            return 1

        try:
            # Read-only mode
            conn = sqlite3.connect(f"file:{self.lineage_db}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Find all AGENT_REGISTERED events
            cursor.execute(
                """
                SELECT agent_id, timestamp, data FROM blocks
                WHERE event_type = 'AGENT_REGISTERED'
                ORDER BY idx
            """
            )

            agents = cursor.fetchall()
            conn.close()

            if len(agents) == 0:
                print("⚠️  No agents registered")
                return 1

            print(f"{'AGENT ID':<20} {'REGISTERED AT':<25} {'STATUS':<10}")
            print("-" * 70)

            for agent_id, timestamp, data in agents:
                ts_str = timestamp[:19].replace("T", " ")

                # Check if agent has passport
                manifest_path = MANIFESTS_DIR / agent_id / "steward.json"
                status = "✅ CERTIFIED" if manifest_path.exists() else "⚠️  NO PASSPORT"

                print(f"{agent_id:<20} {ts_str:<25} {status:<10}")

            print()
            print(f"Total agents: {len(agents)}")
            return 0

        except Exception as e:
            print(f"❌ Error discovering agents: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward introspect
    # =========================================================================

    def cmd_introspect(self) -> int:
        """
        Show detailed kernel state and statistics.

        Combines status, agent count, chain stats, and resource info.
        """
        print("🔬 KERNEL INTROSPECTION")
        print("=" * 70)
        print()

        # Kernel pulse
        kernel_running = self._check_kernel_pulse()
        print(f"Kernel Status:    {'✅ RUNNING' if kernel_running else '❌ OFFLINE'}")

        if kernel_running:
            pulse_age = self._get_pulse_age()
            print(f"Last Heartbeat:   {pulse_age:.1f}s ago")

        # Parampara stats
        if self.lineage_db.exists():
            try:
                conn = sqlite3.connect(f"file:{self.lineage_db}?mode=ro", uri=True)
                cursor = conn.cursor()

                # Total blocks
                cursor.execute("SELECT COUNT(*) FROM blocks")
                total_blocks = cursor.fetchone()[0]

                # Event type counts
                cursor.execute(
                    """
                    SELECT event_type, COUNT(*) FROM blocks
                    GROUP BY event_type
                    ORDER BY COUNT(*) DESC
                """
                )
                event_counts = cursor.fetchall()

                conn.close()

                print(f"Chain Blocks:     {total_blocks}")
                print()
                print("Event Breakdown:")
                for event_type, count in event_counts:
                    print(f"  {event_type:<25} {count:>3}")

            except Exception as e:
                print(f"Chain Error:      {e}")
        else:
            print("Chain Status:     ❌ NOT INITIALIZED")

        print()

        # Agent stats
        certified_count = self._count_certified_agents()
        print(f"Certified Agents: {certified_count}")

        return 0

    # =========================================================================
    # COMMAND: steward delegate
    # =========================================================================

    def cmd_logs(self, tail: int = 50) -> int:
        """
        View kernel logs (last N lines by default).

        Args:
            tail: Number of lines to show from end of log file (default: 50)
        """
        print("📋 KERNEL LOGS")
        print("=" * 70)
        print()

        kernel_log = Path("/tmp/vibe_os/logs/kernel.log")
        if not kernel_log.exists():
            print("❌ Kernel log not found")
            print(f"   Expected: {kernel_log}")
            print()
            print("Kernel may not be running. Try: steward boot")
            return 1

        try:
            with open(kernel_log, "r") as f:
                lines = f.readlines()

            # Show last N lines
            start_idx = max(0, len(lines) - tail)
            shown_lines = lines[start_idx:]

            if start_idx > 0:
                print(f"(showing last {tail} of {len(lines)} lines)\n")

            for line in shown_lines:
                print(line, end="")

            return 0

        except Exception as e:
            print(f"❌ Error reading logs: {e}")
            return 1

    # =========================================================================
    # COMMAND: steward delegate
    # =========================================================================

    def cmd_delegate(self, agent_id: str, task_description: str) -> int:
        """
        Submit a task to an agent via the kernel.

        Creates a task file in /tmp/vibe_os/tasks/ that the kernel can discover
        and execute. Task is assigned a unique ID for tracking.
        """
        print("📤 TASK DELEGATION")
        print("=" * 70)
        print()

        # Ensure task queue directory exists
        task_dir = Path("/tmp/vibe_os/tasks")
        task_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Create task manifest
        task_manifest = {
            "task_id": task_id,
            "agent_id": agent_id,
            "description": task_description,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "PENDING",
        }

        # Write task file
        task_file = task_dir / f"{task_id}.json"

        try:
            with open(task_file, "w") as f:
                json.dump(task_manifest, f, indent=2)

            print(f"Agent:       {agent_id}")
            print(f"Task:        {task_description}")
            print()
            print(f"✅ Task submitted successfully")
            print(f"   Task ID: {task_id}")
            print(f"   Queue:   {task_file}")
            print()
            print("Kernel will discover and execute this task when running.")
            print(f"To check status: steward status | grep {task_id}")
            return 0

        except Exception as e:
            print(f"❌ Failed to submit task: {e}")
            return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="steward",
        description="🎛️  STEWARD Protocol - Agent OS Control Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # steward status
    subparsers.add_parser("status", help="Show system health and kernel pulse")

    # steward verify <agent_id>
    verify_parser = subparsers.add_parser("verify", help="Verify agent passport")
    verify_parser.add_argument("agent_id", help="Agent ID to verify")

    # steward lineage [--tail N]
    lineage_parser = subparsers.add_parser("lineage", help="Show Parampara blockchain")
    lineage_parser.add_argument("--tail", type=int, help="Show only last N blocks")

    # steward ps
    subparsers.add_parser("ps", help="List running agents")

    # steward boot
    subparsers.add_parser("boot", help="Start kernel daemon")

    # steward stop
    subparsers.add_parser("stop", help="Graceful kernel shutdown")

    # steward logs [--tail N]
    logs_parser = subparsers.add_parser("logs", help="View kernel logs")
    logs_parser.add_argument(
        "--tail", type=int, default=50, help="Show last N lines (default: 50)"
    )

    # steward init <agent_id>
    init_parser = subparsers.add_parser("init", help="Initialize new agent manifest")
    init_parser.add_argument("agent_id", help="Agent ID to initialize")

    # steward discover
    subparsers.add_parser("discover", help="Discover all registered agents")

    # steward introspect
    subparsers.add_parser("introspect", help="Show detailed kernel state")

    # steward delegate <agent_id> <task>
    delegate_parser = subparsers.add_parser("delegate", help="Submit task to agent")
    delegate_parser.add_argument("agent_id", help="Agent ID to delegate to")
    delegate_parser.add_argument("task", help="Task description")

    # Parse args
    args = parser.parse_args()

    # Execute command
    cli = StewardCLI()

    if args.command == "status":
        return cli.cmd_status()
    elif args.command == "verify":
        return cli.cmd_verify(args.agent_id)
    elif args.command == "lineage":
        return cli.cmd_lineage(tail=args.tail)
    elif args.command == "ps":
        return cli.cmd_ps()
    elif args.command == "boot":
        return cli.cmd_boot()
    elif args.command == "stop":
        return cli.cmd_stop()
    elif args.command == "logs":
        return cli.cmd_logs(tail=args.tail)
    elif args.command == "init":
        return cli.cmd_init(args.agent_id)
    elif args.command == "discover":
        return cli.cmd_discover()
    elif args.command == "introspect":
        return cli.cmd_introspect()
    elif args.command == "delegate":
        return cli.cmd_delegate(args.agent_id, args.task)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
