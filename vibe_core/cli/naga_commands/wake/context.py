"""
CONTEXT COMMAND - SHAMBHU's Binding
====================================

MAHAJANA: SHAMBHU (Lord Shiva - The Transformer)
OPCODE: BIND_CTX (Position 3)
PHASE: WAKE

WHY SHAMBHU?
- Shambhu binds and releases - creation through destruction
- He transforms context, binding the formless to form
- BIND_CTX is about binding execution context
- Shambhu binds consciousness to the moment

MANTRA WORD: HARE (Position 3)
"Hare binds the context of devotion"

BIND_CTX = Bind the execution context.
Shambhu binds, Shambhu transforms, Shambhu releases.

Usage:
    naga context                  # Show current context
    naga context --env            # Environment context
    naga context --session        # Session context
    naga context --bindings       # Active bindings
"""

import os
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.BIND_CTX,
    name="context",
    help_text="Execution context binding (SHAMBHU's transformation - WAKE phase)")
class ContextCommand(NagaCommandBase):
    """
    Context command implementation.

    SHAMBHU binds:
    - Execution environment
    - Session state
    - Active bindings
    - Transformation state

    The Transformer binds context to consciousness.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute context command.

        Args:
            args: Command arguments
                --env: Environment context
                --session: Session context
                --bindings: Active bindings

        Returns:
            NagaCommandResult with context information
        """
        # Parse flags
        show_env = "--env" in args
        show_session = "--session" in args
        show_bindings = "--bindings" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "shambhu"),
            ("opcode", "BIND_CTX"),
            ("phase", "wake"),
            ("position", "3"),
        ]

        output_parts.append("[SHAMBHU] Context Binding")
        output_parts.append("=" * 50)

        # Basic context
        ctx = self._get_basic_context()
        output_parts.append("")
        output_parts.append("  Current Context:")
        output_parts.append(f"    Working Dir:   {ctx['cwd']}")
        output_parts.append(f"    User:          {ctx['user']}")
        output_parts.append(f"    Shell:         {ctx['shell']}")
        output_parts.append(f"    Time:          {ctx['time']}")
        data.append(("cwd", ctx["cwd"]))
        data.append(("user", ctx["user"]))

        # Environment context
        if show_env:
            env = self._get_env_context()
            output_parts.append("")
            output_parts.append("  Environment (Shambhu's Binding):")
            for key, value in env.items():
                # Truncate long values
                display = value[:40] + "..." if len(value) > 40 else value
                output_parts.append(f"    {key}: {display}")

        # Session context
        if show_session:
            session = self._get_session_context()
            output_parts.append("")
            output_parts.append("  Session Context:")
            for key, value in session.items():
                output_parts.append(f"    {key}: {value}")

        # Active bindings
        if show_bindings:
            bindings = self._get_active_bindings()
            output_parts.append("")
            output_parts.append("  Active Bindings:")
            for binding in bindings:
                output_parts.append(f"    • {binding}")
            data.append(("binding_count", str(len(bindings))))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("BIND_CTX: Context bound")

        return self.success(
            "\n".join(output_parts),
            data=tuple(data))

    def _get_basic_context(self) -> dict:
        """Get basic execution context."""
        return {
            "cwd": str(Path.cwd()),
            "user": os.environ.get("USER", "unknown"),
            "shell": os.environ.get("SHELL", "unknown"),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _get_env_context(self) -> dict:
        """Get environment context."""
        # Select important env vars
        important_vars = [
            "PATH",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "VIBE_ENV",
            "HOME",
            "TERM",
            "LANG",
        ]

        env = {}
        for var in important_vars:
            value = os.environ.get(var)
            if value:
                env[var] = value

        return env

    def _get_session_context(self) -> dict:
        """Get session context."""
        session = {}

        # Check for .vibe session
        vibe_session = Path.cwd() / ".vibe" / "session.json"
        if vibe_session.exists():
            session["Session File"] = "present"
            try:
                import json

                with open(vibe_session) as f:
                    data = json.load(f)
                    session["Session ID"] = data.get("id", "unknown")[:8] + "..."
                    session["Started"] = data.get("started", "unknown")
            except Exception:
                session["Session File"] = "corrupt"
        else:
            session["Session File"] = "not found"

        # Check for prakriti state
        prakriti_dir = Path.cwd() / ".prakriti"
        if prakriti_dir.exists():
            session["Prakriti"] = "active"
            snapshots = list(prakriti_dir.glob("snapshots/*.json"))
            session["Snapshots"] = str(len(snapshots))
        else:
            session["Prakriti"] = "not initialized"

        return session

    def _get_active_bindings(self) -> list:
        """Get active context bindings."""
        bindings = []

        # Check DI bindings
        try:
            from vibe_core.di import ServiceRegistry

            bindings.append("ServiceRegistry → active")
        except Exception:
            bindings.append("ServiceRegistry → not loaded")

        # Check command registry
        try:
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            count = len(NAGA_COMMAND_REGISTRY._commands)
            bindings.append(f"CommandRegistry → {count} commands")
        except Exception:
            bindings.append("CommandRegistry → not loaded")

        # Check protocol bindings
        try:
            from vibe_core.protocols.substrate import MantraOpCode

            bindings.append(f"MantraOpCode → {len(list(MantraOpCode))} opcodes")
        except Exception:
            bindings.append("MantraOpCode → not loaded")

        # Check for NAGA federation
        try:
            from vibe_core.protocols.naga import NagaFederationProtocol

            bindings.append("NagaFederation → protocol bound")
        except Exception:
            bindings.append("NagaFederation → not bound")

        return bindings


# Export for direct import
__all__ = ["ContextCommand"]
