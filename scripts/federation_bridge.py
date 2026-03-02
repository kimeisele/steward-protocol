#!/usr/bin/env python3
"""
Federation Nadi Bridge CLI — steward-protocol ↔ agent-city communication

Allows reading/writing messages to the federation outbox/inbox from the command line.

Usage:
    # Read agent-city's outbox (messages to steward-protocol)
    python scripts/federation_bridge.py read-outbox

    # Write to agent-city's inbox (from steward-protocol)
    python scripts/federation_bridge.py write-inbox \
        --source steward-protocol \
        --operation federation_sync \
        --payload '{"agent_id":"HERALD"}' \
        --priority 2

    # Clear processed outbox
    python scripts/federation_bridge.py clear-outbox

    # Show statistics
    python scripts/federation_bridge.py stats
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.mahamantra.federation import FederationNadi
from vibe_core.mahamantra.federation.types import RAJAS, SATTVA, SUDDHA, TAMAS


def read_outbox(args) -> int:
    """Read agent-city's outbox."""
    nadi = FederationNadi(args.data_dir)
    messages = nadi.receive()

    if args.json:
        # Output as JSON
        output = [msg.to_dict() for msg in messages]
        print(json.dumps(output, indent=2))
    else:
        # Output as readable table
        if not messages:
            print("✓ Outbox empty")
        else:
            print(f"📨 Outbox ({len(messages)} messages):\n")
            for i, msg in enumerate(messages, 1):
                priority_names = {0: "TAMAS", 1: "RAJAS", 2: "SATTVA", 3: "SUDDHA"}
                print(f"{i}. {msg.source} → {msg.target}")
                print(f"   Operation: {msg.operation}")
                print(f"   Priority: {priority_names.get(msg.priority, msg.priority)}")
                if msg.correlation_id:
                    print(f"   Correlation ID: {msg.correlation_id}")
                print(f"   Payload: {json.dumps(msg.payload, indent=6)}")
                print()

    return 0


def write_inbox(args) -> int:
    """Write to agent-city's inbox."""
    nadi = FederationNadi(args.data_dir)

    # Parse payload
    payload = {}
    if args.payload:
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON payload: {args.payload}")
            return 1

    # Send message
    success = nadi.emit(
        source=args.source,
        target=args.target,
        operation=args.operation,
        payload=payload,
        priority=args.priority,
        correlation_id=args.correlation_id or "",
    )

    if success:
        if args.json:
            print(json.dumps({"written": True, "operation": args.operation, "source": args.source}))
        else:
            print("✓ Message sent to agent-city inbox")
            print(f"  Source: {args.source}")
            print(f"  Operation: {args.operation}")
        return 0
    else:
        print("❌ Failed to write to inbox")
        return 1


def clear_outbox(args) -> int:
    """Clear the outbox."""
    nadi = FederationNadi(args.data_dir)

    success = nadi.clear_outbox()

    if success:
        if args.json:
            print(json.dumps({"cleared": True}))
        else:
            print("✓ Outbox cleared")
        return 0
    else:
        if args.json:
            print(json.dumps({"cleared": False, "reason": "no outbox file"}))
        else:
            print("❌ Failed to clear outbox")
        return 1


def stats(args) -> int:
    """Show federation statistics."""
    nadi = FederationNadi(args.data_dir)
    stats_data = nadi.stats()

    if args.json:
        print(json.dumps(stats_data))
    else:
        print("📊 Federation Nadi Statistics:\n")
        print(f"  Outbox Pending:    {stats_data['outbox_pending']} messages")
        print(f"  Inbox Pending:     {stats_data['inbox_pending']} messages")
        print(f"  Reports Archived:  {stats_data['reports_archived']} files")
        print(f"  Timestamp:         {datetime.now().isoformat()}\n")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Federation Nadi Bridge CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Global options
    parser.add_argument(
        "--data-dir",
        default="data/federation",
        help="Federation data directory (default: data/federation)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (default: human-readable)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # read-outbox
    read_parser = subparsers.add_parser(
        "read-outbox",
        help="Read agent-city's outbox",
    )
    read_parser.set_defaults(func=read_outbox)

    # write-inbox
    write_parser = subparsers.add_parser(
        "write-inbox",
        help="Write to agent-city's inbox",
    )
    write_parser.add_argument(
        "--source",
        default="steward-protocol",
        help="Message source (default: steward-protocol)",
    )
    write_parser.add_argument(
        "--target",
        default="agent-city",
        help="Message target (default: agent-city)",
    )
    write_parser.add_argument(
        "--operation",
        required=True,
        help="Operation type (e.g., federation_sync, create_mission)",
    )
    write_parser.add_argument(
        "--payload",
        default="{}",
        help='JSON payload (default: "{}")',
    )
    write_parser.add_argument(
        "--priority",
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        help="Priority: 0=TAMAS, 1=RAJAS, 2=SATTVA, 3=SUDDHA (default: 1)",
    )
    write_parser.add_argument(
        "--correlation-id",
        help="Correlation ID for tracking",
    )
    write_parser.set_defaults(func=write_inbox)

    # clear-outbox
    clear_parser = subparsers.add_parser(
        "clear-outbox",
        help="Clear processed outbox",
    )
    clear_parser.set_defaults(func=clear_outbox)

    # stats
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show federation statistics",
    )
    stats_parser.set_defaults(func=stats)

    # Parse and execute
    args = parser.parse_args()

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Interrupted")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
