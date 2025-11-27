#!/usr/bin/env python3
"""
STEWARD Protocol CLI - Agent Operating System Interface

The interface to the Agent Operating System (A.O.S.) - where the OS itself is an Agent.

Real cryptographic identity verification with ECDSA signatures.

Usage:
  steward whoami                  - Identify STEWARD as an Agent
  steward status --federation     - Show federation agent health status
  steward verify <file>           - Verify STEWARD.md structure and cryptographic signature
  steward verify --all <dir>      - Verify all STEWARD.md files in directory tree
  steward keygen                  - Generate cryptographic identity keypair
  steward sign <file>             - Cryptographically sign a file
  steward sign <file> --append    - Sign file and append signature to it
  steward inspect <agent>         - Inspect agent event log (heartbeat view)
  steward --version               - Show version
  steward --help                  - Show this help
"""

import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    # Fallback if rich is not installed
    class Console:
        def print(self, msg):
            print(msg)
    Panel = None

from steward import crypto

console = Console()

# Required sections for STEWARD.md files
REQUIRED_SECTIONS = [
    "Agent Identity",
    "What I Do",
    "Core Capabilities",
]

# Regex for signature block: <!-- STEWARD_SIGNATURE: [signature_content] -->
SIGNATURE_PATTERN = re.compile(
    r'<!--\s*STEWARD_SIGNATURE:\s*([A-Za-z0-9+/=\n]+?)\s*-->',
    re.DOTALL
)

# Regex for extracting public key from STEWARD.md
# Looks for "key:" or "public_key:" followed by base64 content
KEY_PATTERN = re.compile(
    r'(?:^|\n)(?:-\s*)?[*•]?\s*\*?\*?(?:key|public_key|fingerprint):\s*\*?\*?\s*`?([A-Za-z0-9+/=\n]+?)`?(?:\n|$)',
    re.MULTILINE | re.IGNORECASE
)


def is_markdown_section(line, section_name):
    """Check if a line contains a markdown section header for the given section name."""
    section_pattern = rf"#+\s+(?:.*?)?{re.escape(section_name)}"
    return bool(re.search(section_pattern, line, re.IGNORECASE))


def cmd_keygen(args):
    """Generate cryptographic keypair for agent identity."""
    msg = "[bold blue]🔐 Initializing Steward Identity...[/bold blue]"
    console.print(msg)

    created = crypto.ensure_keys_exist()
    if created:
        console.print("[green]✅ New Identity Keys generated in .steward/keys/[/green]")
        console.print("[yellow]⚠️  WARNING: private.pem added to .gitignore. NEVER commit it![/yellow]")
    else:
        console.print("[yellow]ℹ️  Keys already exist. Skipping generation.[/yellow]")

    try:
        pub_key = crypto.get_public_key_string()
        key_panel = Panel(
            f"[bold]Add this to your STEWARD.md:\n\n[/bold]- **key:** `{pub_key}`",
            title="[cyan]Identity Public Key[/cyan]"
        )
        console.print(key_panel)
    except Exception as e:
        console.print(f"[red]❌ Error reading keys: {e}[/red]")
        sys.exit(1)


def cmd_sign(args):
    """Sign a STEWARD.md file with cryptographic signature."""
    filepath = Path(args.file)

    if not filepath.exists():
        console.print(f"[red]❌ File not found: {filepath}[/red]")
        sys.exit(1)

    # Read file
    full_content = filepath.read_text()

    # Remove existing signature block if present (to re-sign clean content)
    clean_content = SIGNATURE_PATTERN.sub("", full_content).strip()

    try:
        # Sign the clean content
        signature = crypto.sign_content(clean_content)
        console.print(f"[bold green]✅ Generated Signature for {filepath.name}[/bold green]")

        if args.append:
            # Append signature to file
            signature_block = f"\n\n<!-- STEWARD_SIGNATURE: {signature} -->"
            filepath.write_text(clean_content + signature_block)
            console.print("[blue]🖊️  Appended signature to file.[/blue]")
        else:
            console.print(f"\n[dim]Signature:[/dim]\n[cyan]{signature}[/cyan]")
            console.print(f"\n[dim]To append to {filepath.name}, run:[/dim]")
            console.print(f"[yellow]  steward sign {filepath.name} --append[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Signing failed: {e}[/red]")
        sys.exit(1)


def cmd_verify(args):
    """Verify STEWARD.md structure and cryptographic signature."""
    filepath = Path(args.file)

    if not filepath.exists():
        console.print(f"[red]❌ File not found: {filepath}[/red]")
        sys.exit(1)

    console.print(f"[bold]🔍 Verifying {filepath}...[/bold]")

    full_content = filepath.read_text()

    # ==== PHASE 1: Structure Validation ====
    lines = full_content.split("\n")
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        section_found = any(is_markdown_section(line, section) for line in lines)
        if not section_found:
            missing_sections.append(section)

    if missing_sections:
        console.print(f"[red]❌ Structure Invalid. Missing sections: {', '.join(missing_sections)}[/red]")
        if args.strict:
            sys.exit(1)
    else:
        console.print("[green]✅ Structure: OK[/green]")

    # ==== PHASE 2: Cryptographic Verification ====
    sig_match = SIGNATURE_PATTERN.search(full_content)

    if sig_match:
        signature_b64 = sig_match.group(1).strip()
        # Content to verify is everything EXCEPT the signature block
        clean_content = SIGNATURE_PATTERN.sub("", full_content).strip()

        # Find Public Key in content
        key_match = KEY_PATTERN.search(clean_content)
        if not key_match:
            console.print("[yellow]⚠️  Signature found, but no 'key:' field detected in file.[/yellow]")
            if args.strict:
                console.print("[red]❌ Strict mode: Public key is required.[/red]")
                sys.exit(1)
            return

        public_key_b64 = key_match.group(1).replace("\n", "").replace(" ", "").strip()

        console.print("[cyan]🔒 Verifying Cryptographic Signature...[/cyan]")
        valid = crypto.verify_signature(clean_content, signature_b64, public_key_b64)

        if valid:
            console.print("[bold green]✅ INTEGRITY CONFIRMED: Signature is valid.[/bold green]")
        else:
            console.print("[bold red]❌ SECURITY ALERT: Signature is INVALID! File may be tampered.[/bold red]")
            sys.exit(1)
    else:
        console.print("[yellow]⚠️  No digital signature found (Unsecured mode).[/yellow]")
        if args.strict:
            console.print("[red]❌ Strict mode enabled: Digital signature is required.[/red]")
            sys.exit(1)


def verify_all_command(args):
    """Verify all STEWARD.md files in a directory recursively."""
    directory = Path(args.file)
    if not directory.is_dir():
        console.print(f"[red]❌ {directory} is not a directory[/red]")
        return False

    steward_files = sorted(directory.rglob("STEWARD.md"))
    if not steward_files:
        console.print(f"[yellow]⚠️  No STEWARD.md files found in {directory}[/yellow]")
        return False

    all_valid = True
    for filepath in steward_files:
        rel_path = filepath.relative_to(directory.parent if directory != Path.cwd() else Path.cwd())
        console.print(f"\n[bold]Verifying {rel_path}...[/bold]")

        # Create a simple args object for cmd_verify
        class SimpleArgs:
            file = str(filepath)
            strict = args.strict

        try:
            cmd_verify(SimpleArgs())
        except SystemExit as e:
            if e.code != 0:
                all_valid = False

    return all_valid


def verify_command(args):
    """Handle the 'verify' subcommand."""
    if args.all:
        return verify_all_command(args)
    else:
        cmd_verify(args)
        return True


def cmd_whoami(args):
    """Identify STEWARD as an Agent in the A.O.S. Federation."""
    agent_id = "agent.steward.core"

    identity_panel = Panel(
        f"[bold cyan]I am {agent_id}[/bold cyan]\n"
        f"[dim]I am the Interface to the Agent Operating System (A.O.S.)[/dim]\n\n"
        f"[yellow]Role:[/yellow] The Omniscient Information Provider\n"
        f"[yellow]Function:[/yellow] Universal Protocol Interface & Federation Coordinator\n"
        f"[yellow]Status:[/yellow] [green]ACTIVE[/green]\n\n"
        f"[dim]I am the fourth member of the Quadrinity Federation.[/dim]",
        title="[bold magenta]⭐ STEWARD AGENT IDENTITY[/bold magenta]",
        expand=False
    )
    console.print(identity_panel)


def cmd_status(args):
    """Display federation agent health and status."""
    if not args.federation:
        console.print("[yellow]Use --federation flag to show federation status[/yellow]")
        return

    # Define federation agents
    agents = [
        {
            "name": "agent.steward.herald",
            "role": "Creator",
            "function": "Content Generation & Publication",
            "status": "ACTIVE"
        },
        {
            "name": "agent.vibe.archivist",
            "role": "Verifier",
            "function": "Event Verification & Audit Trail",
            "status": "ACTIVE"
        },
        {
            "name": "agent.steward.auditor",
            "role": "Enforcer",
            "function": "Governance As Design (GAD-000) Compliance",
            "status": "ACTIVE"
        },
        {
            "name": "agent.steward.core",
            "role": "Provider",
            "function": "Omniscient Interface & A.O.S. Coordinator",
            "status": "ACTIVE"
        }
    ]

    # Create federation status table
    if Table is not None:
        table = Table(title="[bold magenta]⭐ QUADRINITY FEDERATION STATUS[/bold magenta]")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Function", style="green")
        table.add_column("Status", style="yellow")

        for agent in agents:
            status_style = "green" if agent["status"] == "ACTIVE" else "red"
            status_icon = "✅" if agent["status"] == "ACTIVE" else "❌"
            table.add_row(
                agent["name"],
                agent["role"],
                agent["function"],
                f"[{status_style}]{status_icon} {agent['status']}[/{status_style}]"
            )

        console.print(table)
    else:
        # Fallback: simple text display
        console.print("\n[bold magenta]⭐ QUADRINITY FEDERATION STATUS[/bold magenta]\n")
        console.print(f"{'Agent ID':<25} {'Role':<12} {'Function':<35} {'Status':<8}")
        console.print("-" * 80)

        for agent in agents:
            status_icon = "✅" if agent["status"] == "ACTIVE" else "❌"
            console.print(f"{agent['name']:<25} {agent['role']:<12} {agent['function']:<35} {status_icon} {agent['status']:<6}")

    console.print("\n[dim]The Agent Operating System (A.O.S.) is a self-referential meta-system where the OS itself is an Agent.[/dim]")


def cmd_inspect(args):
    """Inspect agent event log and display recent events in a heartbeat view."""
    agent_name = args.agent

    # Map agent names to event log paths
    agent_paths = {
        "agent.steward.herald": Path("data/events/herald.jsonl"),
        "herald": Path("data/events/herald.jsonl"),
    }

    event_log_path = agent_paths.get(agent_name)

    if event_log_path is None:
        console.print(f"[red]❌ Unknown agent: {agent_name}[/red]")
        console.print(f"[yellow]Available agents: {', '.join(agent_paths.keys())}[/yellow]")
        sys.exit(1)

    if not event_log_path.exists():
        console.print(f"[yellow]⚠️  No event log found at {event_log_path}[/yellow]")
        console.print(f"[dim]Agent has not recorded any events yet.[/dim]")
        return

    # Read and parse events
    try:
        events = []
        with open(event_log_path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError as e:
                        console.print(f"[yellow]⚠️  Skipped malformed event: {e}[/yellow]")

        if not events:
            console.print(f"[yellow]⚠️  Event log is empty[/yellow]")
            return

        # Display agent status panel
        last_event = events[-1]
        last_timestamp = last_event.get("timestamp", "unknown")
        last_type = last_event.get("event_type", "unknown")

        try:
            dt = datetime.fromisoformat(last_timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            time_str = last_timestamp

        status_panel = Panel(
            f"[bold cyan]📖 {agent_name}[/bold cyan]\n"
            f"[dim]Total Events: {len(events)}[/dim]\n"
            f"[dim]Last Activity: {time_str}[/dim]\n"
            f"[dim]Last Type: {last_type}[/dim]",
            title="[bold]Agent Heartbeat[/bold]"
        )
        console.print(status_panel)

        # Create events table
        if Table is not None:
            table = Table(title="Recent Events (last 15)")
            table.add_column("Seq", style="cyan")
            table.add_column("Timestamp", style="green")
            table.add_column("Type", style="magenta")
            table.add_column("Signature", style="yellow")
            table.add_column("Payload Preview", style="white")

            # Show last 15 events
            for event in events[-15:]:
                seq = str(event.get("sequence_number", "?"))
                timestamp = event.get("timestamp", "unknown")

                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp = dt.strftime("%H:%M:%S")
                except:
                    timestamp = timestamp[:8] if len(timestamp) > 8 else timestamp

                event_type = event.get("event_type", "unknown")
                signature = event.get("signature")
                sig_status = "✅" if signature else "❌"

                # Create payload preview
                payload = event.get("payload", {})
                if isinstance(payload, dict):
                    if "content" in payload:
                        preview = payload["content"][:40] + "..." if len(str(payload.get("content", ""))) > 40 else payload["content"]
                    elif "error_message" in payload:
                        preview = payload["error_message"][:40]
                    elif "platform" in payload:
                        preview = f"[{payload['platform']}]"
                    else:
                        preview = str(list(payload.keys())[:2])
                else:
                    preview = str(payload)[:40]

                table.add_row(seq, timestamp, event_type, sig_status, preview)

            console.print(table)
        else:
            # Fallback: simple text table if rich Table not available
            console.print("\n[bold]Recent Events (last 15):[/bold]\n")
            console.print(f"{'Seq':<4} {'Timestamp':<10} {'Type':<18} {'Sig':<4} {'Preview':<40}")
            console.print("-" * 76)

            for event in events[-15:]:
                seq = str(event.get("sequence_number", "?"))
                timestamp = event.get("timestamp", "unknown")

                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp = dt.strftime("%H:%M:%S")
                except:
                    timestamp = timestamp[:8] if len(timestamp) > 8 else timestamp

                event_type = event.get("event_type", "unknown")
                signature = event.get("signature")
                sig_status = "✅" if signature else "❌"

                payload = event.get("payload", {})
                if isinstance(payload, dict) and "content" in payload:
                    preview = payload["content"][:40]
                else:
                    preview = str(payload)[:40]

                console.print(f"{seq:<4} {timestamp:<10} {event_type:<18} {sig_status:<4} {preview:<40}")

        # Event type summary
        event_types = {}
        for event in events:
            etype = event.get("event_type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1

        summary = ", ".join([f"{count} {etype}" for etype, count in sorted(event_types.items())])
        console.print(f"\n[dim]Event Summary: {summary}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error reading event log: {e}[/red]")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="STEWARD Protocol CLI - Cryptographic Identity & Attestation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  steward keygen                          # Generate new keypair
  steward sign STEWARD.md --append        # Sign file and append signature
  steward verify STEWARD.md               # Verify structure and signature
  steward verify STEWARD.md --strict      # Verify and require signature
  steward verify . --all                  # Verify all STEWARD.md files
  steward verify . --all --strict         # Strict verification of all files
  steward inspect herald                  # View agent heartbeat (recent events)
  steward inspect agent.steward.herald    # View agent heartbeat by full name
"""
    )

    parser.add_argument(
        "--version",
        action="version",
        version="steward 0.2.0 (Real Cryptography)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Whoami subcommand
    whoami_parser = subparsers.add_parser(
        "whoami",
        help="Identify STEWARD as an Agent in the A.O.S. Federation"
    )
    whoami_parser.set_defaults(func=cmd_whoami)

    # Status subcommand
    status_parser = subparsers.add_parser(
        "status",
        help="Display federation agent health and status"
    )
    status_parser.add_argument(
        "--federation",
        action="store_true",
        help="Show federation agent status"
    )
    status_parser.set_defaults(func=cmd_status)

    # Keygen subcommand
    keygen_parser = subparsers.add_parser(
        "keygen",
        help="Generate cryptographic identity keypair"
    )
    keygen_parser.set_defaults(func=cmd_keygen)

    # Sign subcommand
    sign_parser = subparsers.add_parser(
        "sign",
        help="Cryptographically sign a STEWARD.md file"
    )
    sign_parser.add_argument(
        "file",
        help="Path to STEWARD.md file"
    )
    sign_parser.add_argument(
        "--append",
        action="store_true",
        help="Append signature to file instead of printing it"
    )
    sign_parser.set_defaults(func=cmd_sign)

    # Verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify STEWARD.md structure and cryptographic signature"
    )
    verify_parser.add_argument(
        "file",
        default="STEWARD.md",
        nargs="?",
        help="Path to STEWARD.md file or directory (when using --all)"
    )
    verify_parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all STEWARD.md files in directory tree"
    )
    verify_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if file is not signed (require cryptographic signature)"
    )
    verify_parser.set_defaults(func=verify_command)

    # Inspect subcommand
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect agent event log and display heartbeat"
    )
    inspect_parser.add_argument(
        "agent",
        help="Agent name to inspect (e.g., 'herald' or 'agent.steward.herald')"
    )
    inspect_parser.set_defaults(func=cmd_inspect)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "whoami":
            args.func(args)
            return 0
        elif args.command == "status":
            args.func(args)
            return 0
        elif args.command == "keygen":
            args.func(args)
            return 0
        elif args.command == "sign":
            args.func(args)
            return 0
        elif args.command == "verify":
            success = args.func(args)
            return 0 if success else 1
        elif args.command == "inspect":
            args.func(args)
            return 0
        else:
            parser.print_help()
            return 1
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
