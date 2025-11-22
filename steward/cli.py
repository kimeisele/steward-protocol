#!/usr/bin/env python3
"""
STEWARD Protocol CLI - Automated Protocol Attestation & Agent Identity Verification

Usage:
  steward verify <file>                    - Verify STEWARD.md compliance
  steward verify --all <directory>         - Verify all STEWARD.md files in directory
  steward --version                        - Show version
  steward --help                           - Show this help
"""

import sys
import re
import argparse
from pathlib import Path


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
        help="Path to STEWARD.md file or directory (when using --all)"
    )
    verify_parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all STEWARD.md files in directory tree"
    )
    verify_parser.set_defaults(func=verify_command)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        success = args.func(args)
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
