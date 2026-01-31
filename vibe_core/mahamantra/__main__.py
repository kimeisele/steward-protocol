"""
MAHAMANTRA CLI ENTRY POINT
==========================

"The Conchshell Blows."

Enables `python -m vibe_core.mahamantra <command>` execution.
"""

import sys
import argparse
from vibe_core.mahamantra.commands import cli_chant, cli_listen, cli_resolve, cli_serve, cli_veda

def main():
    parser = argparse.ArgumentParser(description="Mahamantra CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # CHANT
    chant_parser = subparsers.add_parser("chant", help="Perform Kirtan (Chanting)")
    chant_parser.add_argument("--rounds", type=int, default=1, help="Number of rounds (16 ticks)")
    chant_parser.add_argument("--verbose", action="store_true", help="Verbose output")
    chant_parser.add_argument("--audio", action="store_true", help="Stream raw PCM audio to stdout")

    # LISTEN
    listen_parser = subparsers.add_parser("listen", help="Sravanam (Hearing)")
    listen_parser.add_argument("--source", type=str, default="all", help="Event source")
    listen_parser.add_argument("--tail", type=int, default=10, help="Number of entries")
    listen_parser.add_argument("--json", action="store_true", help="JSON output")

    # RESOLVE
    resolve_parser = subparsers.add_parser("resolve", help="Vandanam (Praying/Lookup)")
    resolve_parser.add_argument("name", type=str, help="Mahajana name or position")
    resolve_parser.add_argument("--json", action="store_true", help="JSON output")

    # SERVE
    serve_parser = subparsers.add_parser("serve", help="Pada Sevanam (Service)")
    serve_parser.add_argument("task", type=str, help="Task description")
    serve_parser.add_argument("--execute", action="store_true", help="Execute immediately")
    serve_parser.add_argument("--priority", type=str, default="normal", help="Task priority")
    serve_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # VEDA
    veda_parser = subparsers.add_parser("veda", help="Atma Nivedanam (Self-Surrender / Explorer)")
    veda_parser.add_argument("message", type=str, nargs="?", help="Message to explorer")
    veda_parser.add_argument("--mode", type=str, default="enhanced", help="Explorer mode")
    veda_parser.add_argument("--interactive", action="store_true", help="REPL mode")
    veda_parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if args.command == "chant":
        cli_chant(rounds=args.rounds, verbose=args.verbose, audio=args.audio)

    elif args.command == "listen":
        cli_listen(source=args.source, tail=args.tail, json=args.json)
    
    elif args.command == "resolve":
        cli_resolve(name=args.name, json=args.json)

    elif args.command == "serve":
        cli_serve(task=args.task, execute=args.execute, priority=args.priority, json=args.json)
        
    elif args.command == "veda":
        cli_veda(message=args.message, mode=args.mode, interactive=args.interactive, json=args.json)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
