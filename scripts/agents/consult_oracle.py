#!/usr/bin/env python3
"""
CONSULT THE ORACLE

User interface for querying the system's self-awareness.

Usage:
    python3 scripts/consult_oracle.py --ask "Why is Herald frozen?"
    python3 scripts/consult_oracle.py --status science
    python3 scripts/consult_oracle.py --timeline --limit 10
    python3 scripts/consult_oracle.py --health
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from civic.tools.economy import CivicBank
from oracle.cartridge_main import Oracle


def print_response(response: dict, format_type: str = "narrative"):
    """Pretty-print Oracle response."""
    if format_type == "json":
        print(json.dumps(response, indent=2))
    else:
        # Narrative format
        print("\n" + "=" * 70)
        if "narrative" in response:
            print(response["narrative"])
        elif "error" in response:
            print(f"❌ Error: {response['error']}")
        else:
            print(json.dumps(response, indent=2))
        print("=" * 70)

        # Show alerts if present
        if "alerts" in response and response["alerts"]:
            print("\n⚠️  SYSTEM ALERTS:")
            for alert in response["alerts"]:
                print(f"  [{alert.get('severity', 'INFO')}] {alert.get('message')}")

        # Show evidence/data if present (for trust)
        if "evidence" in response and format_type == "narrative":
            print("\n📋 RAW EVIDENCE (for verification):")
            print(json.dumps(response["evidence"], indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Consult the Oracle - Query system self-awareness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ask "Why is Herald frozen?"
  %(prog)s --status science
  %(prog)s --timeline --limit 10
  %(prog)s --health
  %(prog)s --tx TX-abc123
        """,
    )

    # Query types
    parser.add_argument(
        "--ask",
        type=str,
        help="Ask a free-form question (e.g., 'Why is Herald frozen?')",
    )
    parser.add_argument(
        "--status", type=str, metavar="AGENT_ID", help="Get status of specific agent"
    )
    parser.add_argument(
        "--timeline", action="store_true", help="Show transaction timeline"
    )
    parser.add_argument(
        "--health", action="store_true", help="Show system health status"
    )
    parser.add_argument(
        "--tx", type=str, metavar="TX_ID", help="Trace specific transaction"
    )

    # Options
    parser.add_argument(
        "--limit", type=int, default=20, help="Limit results (default: 20)"
    )
    parser.add_argument(
        "--format",
        choices=["narrative", "json"],
        default="narrative",
        help="Output format (default: narrative)",
    )

    args = parser.parse_args()

    # Initialize Oracle
    try:
        bank = CivicBank()
        oracle = Oracle(bank=bank)
    except Exception as e:
        print(f"❌ Failed to initialize Oracle: {e}")
        return 1

    # Parse query
    if args.ask:
        # Free-form question - try to parse intent
        question = args.ask.lower()

        if "frozen" in question or "freeze" in question:
            # Extract agent name
            agent_id = _extract_agent_from_question(args.ask)
            if agent_id:
                response = oracle.explain_freeze(agent_id)
            else:
                print("❓ Could not determine which agent you're asking about")
                print("   Usage: --ask 'Why is [AGENT_NAME] frozen?'")
                return 1

        elif "status" in question:
            agent_id = _extract_agent_from_question(args.ask)
            if agent_id:
                response = oracle.explain_agent(agent_id)
            else:
                print("❓ Could not determine which agent you're asking about")
                return 1

        else:
            print(f"❓ Question not understood: {args.ask}")
            print("   Try: --ask 'Why is [AGENT] frozen?'")
            return 1

    elif args.status:
        response = oracle.explain_agent(args.status)

    elif args.timeline:
        response = oracle.audit_timeline(limit=args.limit)

    elif args.health:
        response = oracle.system_health()

    elif args.tx:
        response = oracle.get_raw_transaction(args.tx)

    else:
        parser.print_help()
        return 0

    # Print response
    print_response(response, format_type=args.format)

    return 0


def _extract_agent_from_question(question: str) -> str:
    """
    Extract agent name from a natural language question.

    Examples:
    - "Why is Herald frozen?" -> "herald"
    - "What's wrong with Science?" -> "science"
    - "Is Watchman running?" -> "watchman"
    """
    question_lower = question.lower()

    # Common agent names
    agents = [
        "herald",
        "science",
        "watchman",
        "archivist",
        "auditor",
        "envoy",
        "steward",
    ]

    for agent in agents:
        if agent in question_lower:
            return agent

    return ""


if __name__ == "__main__":
    sys.exit(main())
