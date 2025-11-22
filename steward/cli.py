#!/usr/bin/env python3
"""
STEWARD Protocol CLI - Automated Protocol Attestation & Agent Identity Verification

Usage:
  steward verify <file>                    - Verify STEWARD.md compliance
  steward verify --all <directory>         - Verify all STEWARD.md files in directory
  steward keygen                           - Generate cryptographic identity keys
  steward sign <file>                      - Sign a STEWARD.md file
  steward --version                        - Show version
  steward --help                           - Show this help
"""

import sys
import re
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from steward import crypto

console = Console()

# Required sections for STEWARD.md files
REQUIRED_SECTIONS = [
    "Agent Identity",
    "What I Do",
    "Core Capabilities",
]

# Sections with different names based on entity type
FLEXIBLE_SECTIONS = {
    "Verification": ["Verification", "🔐 Verification"],
}

# Signature block pattern: captures signature block at end of file
SIG_BLOCK_PATTERN = re.compile(
    r'\n*<!-- STEWARD_SIGNATURE\s+(.*?)\s+-->\s*$',
    re.DOTALL
)

# Extract signature and key from the block content
SIG_LINE_PATTERN = re.compile(r'signature:\s*([A-Za-z0-9+/=]+)')
KEY_LINE_PATTERN = re.compile(r'key:\s*([A-Za-z0-9+/=\n]+)')



def is_markdown_section(line, section_name):
    """Check if a line contains a markdown section header for the given section name."""
    # Match patterns like "## 🆔 Agent Identity", "## Agent Identity", etc.
    section_pattern = rf"#+\s+(?:.*?)?{re.escape(section_name)}"
    return bool(re.search(section_pattern, line, re.IGNORECASE))


def verify_steward_file(filepath):
    """
    Verify that a STEWARD.md file contains all required sections.

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
    except FileNotFoundError:
        return False, f"File not found: {filepath}"
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Extract file path for display
    display_path = str(filepath)

    # Check required sections
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        section_found = any(is_markdown_section(line, section) for line in lines)
        if not section_found:
            missing_sections.append(section)

    if missing_sections:
        error_msg = f"Missing required sections: {', '.join(missing_sections)}"
        return False, error_msg

    # Basic validation: ensure file has meaningful content
    if len(content.strip()) < 100:
        return False, "File appears to be empty or too short"

    return True, "All required sections present"


def cmd_keygen(args):
    """Generates a new identity keypair."""
    console.print("[bold blue]🔐 Initializing Steward Identity...[/bold blue]")
    created = crypto.ensure_keys_exist()
    if created:
        console.print("[green]✅ New Identity Keys generated in .steward/keys/[/green]")
        console.print("[yellow]⚠️  WARNING: private.pem added to .gitignore. NEVER commit it![/yellow]")
    else:
        console.print("[yellow]ℹ️  Keys already exist. Skipping generation.[/yellow]")

    try:
        pub_key = crypto.get_public_key_string()
        console.print(Panel(
            f"[bold]Add this key block to your STEWARD.md:[/bold]\n\n```\nkey: {pub_key}\n```",
            title="Identity Public Key"
        ))
    except Exception as e:
        console.print(f"[red]❌ Error reading keys: {e}[/red]")
        sys.exit(1)


def cmd_sign(args):
    """Signs the STEWARD.md file."""
    path = Path(args.file)
    if not path.exists():
        console.print(f"[red]❌ File not found: {path}[/red]")
        sys.exit(1)

    try:
        full_content = path.read_text()

        # Remove existing signature block if present (re-sign clean content)
        clean_content = SIG_BLOCK_PATTERN.sub('', full_content).rstrip()

        # Get public key and sign
        pub_key = crypto.get_public_key_string()
        signature = crypto.sign_content(clean_content)

        console.print(f"[bold green]✅ Generated Signature for {path.name}[/bold green]")

        if args.append:
            # Create signature block in HTML comment format
            sig_block = f"\n\n<!-- STEWARD_SIGNATURE\nsignature: {signature}\nkey: {pub_key}\n-->"

            # Write back with signature
            with open(path, "w") as f:
                f.write(clean_content + sig_block)

            console.print("[blue]🖊️  Appended signature to file.[/blue]")
            console.print(f"[dim]File updated: {path}[/dim]")
        else:
            # Just display the signature
            console.print(f"\n[bold]Signature:[/bold]\n{signature}")
            console.print(f"\n[bold]Public Key:[/bold]\n{pub_key}")
            console.print(f"\n[dim]Use --append to write signature to file[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Signing failed: {e}[/red]")
        sys.exit(1)


def cmd_verify(args):
    """Verifies structure and cryptographic signature."""
    path = Path(args.file)
    console.print(f"[bold]🔍 Verifying {path}...[/bold]")

    if not path.exists():
        console.print(f"[red]❌ File not found: {path}[/red]")
        sys.exit(1)

    try:
        full_content = path.read_text()

        # 1. Structure Check
        required = ["Agent Identity", "ID:", "Name:"]
        missing = [r for r in required if r not in full_content]

        if missing:
            console.print(f"[red]❌ Structure Invalid. Missing: {', '.join(missing)}[/red]")
            if args.strict:
                sys.exit(1)
            return
        else:
            console.print("[green]✅ Structure: OK[/green]")

        # 2. Cryptographic Verification
        sig_match = SIG_BLOCK_PATTERN.search(full_content)

        if sig_match:
            sig_block_content = sig_match.group(1)

            # Extract signature and key from block
            sig_match_line = SIG_LINE_PATTERN.search(sig_block_content)
            key_match_line = KEY_LINE_PATTERN.search(sig_block_content)

            if not sig_match_line or not key_match_line:
                console.print("[yellow]⚠️  Signature block found but incomplete.[/yellow]")
                if args.strict:
                    sys.exit(1)
                return

            signature = sig_match_line.group(1).strip()
            public_key_str = key_match_line.group(1).replace("\n", "").replace(" ", "")

            # Get content that was signed (everything except signature block)
            clean_content = SIG_BLOCK_PATTERN.sub('', full_content).rstrip()

            console.print("[cyan]🔒 Verifying Cryptographic Signature...[/cyan]")
            valid = crypto.verify_signature(clean_content, signature, public_key_str)

            if valid:
                console.print("[bold green]✅ INTEGRITY CONFIRMED: Signature is valid.[/bold green]")
            else:
                console.print("[bold red]❌ SECURITY ALERT: Signature is INVALID! File may be tampered.[/bold red]")
                sys.exit(1)
        else:
            console.print("[yellow]⚠️  No digital signature found (Unsecured).[/yellow]")
            if args.strict:
                console.print("[red]❌ Strict mode enabled: Signature required.[/red]")
                sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Verification error: {e}[/red]")
        sys.exit(1)


def verify_command(args):
    """Handle the 'verify' subcommand."""
    if args.all:
        # Verify all STEWARD.md files in directory
        directory = Path(args.file)
        if not directory.is_dir():
            print(f"❌ Error: {directory} is not a directory")
            return False

        steward_files = list(directory.rglob("STEWARD.md"))
        if not steward_files:
            print(f"⚠️  No STEWARD.md files found in {directory}")
            return False

        all_valid = True
        for filepath in sorted(steward_files):
            is_valid, message = verify_steward_file(filepath)
            status = "✅" if is_valid else "❌"
            rel_path = filepath.relative_to(directory.parent if directory != Path.cwd() else Path.cwd())
            print(f"{status} {rel_path}: {message}")
            if not is_valid:
                all_valid = False

        return all_valid
    else:
        # Verify single file
        filepath = Path(args.file)
        is_valid, message = verify_steward_file(filepath)

        if is_valid:
            print(f"✅ Verification successful: {filepath}")
            print(f"   {message}")
            return True
        else:
            print(f"❌ Verification failed: {filepath}")
            print(f"   {message}")
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="STEWARD Protocol CLI - Attestation & Agent Identity Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  steward verify STEWARD.md                    # Verify single file
  steward verify . --all                       # Verify all STEWARD.md in directory tree
  steward verify examples/ --all               # Verify all agents in examples/
  steward keygen                               # Generate identity keys
  steward sign STEWARD.md                      # Sign a file
"""
    )

    parser.add_argument(
        "--version",
        action="version",
        version="steward 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify STEWARD.md protocol compliance"
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
        help="Fail if file is unsigned or signature is invalid"
    )

    # Set default function to cmd_verify if not using --all
    def verify_wrapper(args):
        if args.all:
            return verify_command(args)
        else:
            return cmd_verify(args)

    verify_parser.set_defaults(func=verify_wrapper)

    # Keygen subcommand
    keygen_parser = subparsers.add_parser(
        "keygen",
        help="Generate cryptographic identity keys"
    )
    keygen_parser.set_defaults(func=cmd_keygen)

    # Sign subcommand
    sign_parser = subparsers.add_parser(
        "sign",
        help="Cryptographically sign a file"
    )
    sign_parser.add_argument(
        "file",
        default="STEWARD.md",
        nargs="?",
        help="File to sign (default: STEWARD.md)"
    )
    sign_parser.add_argument(
        "--append",
        action="store_true",
        help="Append signature to file"
    )
    sign_parser.set_defaults(func=cmd_sign)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if hasattr(args, 'func'):
            if args.command == "verify":
                success = args.func(args)
                return 0 if success else 1
            else:
                args.func(args)
                return 0
        else:
            parser.print_help()
            return 0
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
