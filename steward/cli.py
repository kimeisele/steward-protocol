#!/usr/bin/env python3
"""
STEWARD Protocol CLI - Automated Protocol Attestation & Agent Identity Verification

Real cryptographic identity verification with ECDSA signatures.

Usage:
  steward verify <file>           - Verify STEWARD.md structure and cryptographic signature
  steward verify --all <dir>      - Verify all STEWARD.md files in directory tree
  steward keygen                  - Generate cryptographic identity keypair
  steward sign <file>             - Cryptographically sign a file
  steward sign <file> --append    - Sign file and append signature to it
  steward --version               - Show version
  steward --help                  - Show this help
"""

import sys
import re
import argparse
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
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
"""
    )

    parser.add_argument(
        "--version",
        action="version",
        version="steward 0.2.0 (Real Cryptography)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

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

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "keygen":
            args.func(args)
            return 0
        elif args.command == "sign":
            args.func(args)
            return 0
        elif args.command == "verify":
            success = args.func(args)
            return 0 if success else 1
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
