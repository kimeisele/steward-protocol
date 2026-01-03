"""
CI/CD CLI - Fractal Bridge for CI Hooks

PROMPT.md Compliance:
- Protocol: Implements CLIHandler
- Discoverable: @register_cli decorator
- Observable: Manifest-based discovery
- Hot-Swap: Add hooks to ci.yaml, no code changes

Pattern: Same as cartridge_bridge.py but for CI hooks.

Usage:
    steward ci run-all              # Run all hooks in phase order
    steward ci run <hook_id>        # Run specific hook
    steward ci list                 # List all hooks
    steward ci status               # Show last run status
"""

import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.protocols.cli import CLIMeta, CLIResult, register_cli

logger = logging.getLogger("CI")

# Manifest location (relative to repo root)
CI_MANIFEST_PATH = Path("scripts/ci/ci.yaml")
CI_SCRIPTS_DIR = Path("scripts/ci")


@dataclass
class CIHookMeta:
    """Metadata for a CI hook from manifest."""

    hook_id: str
    phase: str
    script: str
    description: str = ""
    fail_build: bool = False
    outputs: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class CIHookResult:
    """Result of CI hook execution."""

    hook_id: str
    success: bool
    exit_code: int
    duration_ms: float
    output: str = ""
    error: str = ""


class CIManifest:
    """
    Lazy manifest loader for CI hooks.

    Pattern: Same as LazyCartridgeRegistry.
    Loads YAML once, no Python imports until execution.
    """

    _instance: Optional["CIManifest"] = None
    _hooks: Dict[str, CIHookMeta] = {}
    _phases: List[str] = []
    _loaded: bool = False

    def __new__(cls) -> "CIManifest":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._hooks = {}
            cls._instance._phases = []
            cls._instance._loaded = False
        return cls._instance

    @classmethod
    def get_instance(cls) -> "CIManifest":
        return cls()

    def load(self) -> bool:
        """Load manifest from YAML."""
        if self._loaded:
            return True

        if not CI_MANIFEST_PATH.exists():
            logger.warning(f"[CI] Manifest not found: {CI_MANIFEST_PATH}")
            return False

        try:
            data = yaml.safe_load(CI_MANIFEST_PATH.read_text())

            # Load phases
            self._phases = data.get("phases", [])

            # Load hooks
            for hook_id, hook_data in data.get("hooks", {}).items():
                self._hooks[hook_id] = CIHookMeta(
                    hook_id=hook_id,
                    phase=hook_data.get("phase", "validate"),
                    script=hook_data.get("script", ""),
                    description=hook_data.get("description", ""),
                    fail_build=hook_data.get("fail_build", False),
                    outputs=hook_data.get("outputs", []),
                    depends_on=hook_data.get("depends_on", []),
                )

            self._loaded = True
            logger.info(f"[CI] Loaded {len(self._hooks)} hooks from manifest")
            return True

        except Exception as e:
            logger.error(f"[CI] Failed to load manifest: {e}")
            return False

    def get_hooks_by_phase(self, phase: str) -> List[CIHookMeta]:
        """Get hooks for a specific phase."""
        self.load()
        return [h for h in self._hooks.values() if h.phase == phase]

    def get_all_hooks_ordered(self) -> List[CIHookMeta]:
        """Get all hooks in phase order."""
        self.load()
        ordered = []
        for phase in self._phases:
            ordered.extend(self.get_hooks_by_phase(phase))
        return ordered

    def get_hook(self, hook_id: str) -> Optional[CIHookMeta]:
        """Get a specific hook by ID."""
        self.load()
        return self._hooks.get(hook_id)


@register_cli
class CICLI:
    """
    CI/CD CLI Handler.

    Implements CLIHandler protocol for discovery by UnifiedCLI.
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="ci",
            description="CI/CD hook management (Ouroboros integration)",
            domain="operations",
            subcommands=["run-all", "run", "list", "status"],
            tags=["ci", "cd", "ouroboros", "automation"],
        )

    def run(self, args: List[str]) -> int:
        """Execute CI command."""
        if not args or args[0] in ("--help", "-h"):
            return self._show_help()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "run-all":
            return self._run_all(sub_args)
        elif subcommand == "run":
            return self._run_hook(sub_args)
        elif subcommand == "list":
            return self._list_hooks(sub_args)
        elif subcommand == "status":
            return self._show_status(sub_args)
        else:
            print(f"Unknown subcommand: {subcommand}")
            return 1

    def _show_help(self) -> int:
        """Show help message."""
        print("""🔄 CI/CD Hook Management

USAGE:
    steward ci run-all              Run all hooks in phase order
    steward ci run <hook_id>        Run specific hook
    steward ci list                 List all registered hooks
    steward ci status               Show last run status

PHASES (in order):
    validate  → Fast checks, fail early
    analyze   → Deep analysis (AST, linting)
    test      → Run tests
    report    → Generate reports
    ingest    → Feed back to system (Ouroboros)

Add hooks to scripts/ci/ci.yaml - no workflow changes needed.
""")
        return 0

    def _run_all(self, args: List[str]) -> int:
        """Run all hooks in phase order."""
        manifest = CIManifest.get_instance()
        hooks = manifest.get_all_hooks_ordered()

        if not hooks:
            print("⚠️  No CI hooks found in manifest")
            return 0

        print(f"🔄 Running {len(hooks)} CI hooks...")
        print("=" * 60)

        results: List[CIHookResult] = []
        failed = False

        for hook in hooks:
            result = self._execute_hook(hook)
            results.append(result)

            status = "✅" if result.success else "❌"
            print(f"{status} [{hook.phase}] {hook.hook_id} ({result.duration_ms:.0f}ms)")

            if not result.success and hook.fail_build:
                failed = True
                print(f"   ⛔ Build failure: {hook.hook_id}")
                if "--continue-on-error" not in args:
                    break

        print("=" * 60)
        passed = sum(1 for r in results if r.success)
        print(f"Results: {passed}/{len(results)} passed")

        if failed:
            print("❌ CI FAILED")
            return 1

        print("✅ CI PASSED")
        return 0

    def _run_hook(self, args: List[str]) -> int:
        """Run a specific hook."""
        if not args:
            print("Usage: steward ci run <hook_id>")
            return 1

        hook_id = args[0]
        manifest = CIManifest.get_instance()
        hook = manifest.get_hook(hook_id)

        if not hook:
            print(f"❌ Hook not found: {hook_id}")
            return 1

        print(f"🔄 Running: {hook_id}")
        result = self._execute_hook(hook)

        if result.success:
            print(f"✅ {hook_id} passed ({result.duration_ms:.0f}ms)")
            return 0
        else:
            print(f"❌ {hook_id} failed ({result.duration_ms:.0f}ms)")
            if result.error:
                print(f"   Error: {result.error}")
            return 1

    def _execute_hook(self, hook: CIHookMeta) -> CIHookResult:
        """Execute a single hook script."""
        script_path = CI_SCRIPTS_DIR / hook.script

        if not script_path.exists():
            return CIHookResult(
                hook_id=hook.hook_id,
                success=False,
                exit_code=1,
                duration_ms=0,
                error=f"Script not found: {script_path}",
            )

        start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
            )
            duration_ms = (time.time() - start) * 1000

            return CIHookResult(
                hook_id=hook.hook_id,
                success=result.returncode == 0,
                exit_code=result.returncode,
                duration_ms=duration_ms,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else "",
            )

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start) * 1000
            return CIHookResult(
                hook_id=hook.hook_id,
                success=False,
                exit_code=124,
                duration_ms=duration_ms,
                error="Timeout after 5 minutes",
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return CIHookResult(
                hook_id=hook.hook_id,
                success=False,
                exit_code=1,
                duration_ms=duration_ms,
                error=str(e),
            )

    def _list_hooks(self, args: List[str]) -> int:
        """List all registered hooks."""
        manifest = CIManifest.get_instance()
        hooks = manifest.get_all_hooks_ordered()

        as_json = "--json" in args

        if as_json:
            data = [
                {
                    "id": h.hook_id,
                    "phase": h.phase,
                    "script": h.script,
                    "description": h.description,
                    "fail_build": h.fail_build,
                }
                for h in hooks
            ]
            print(json.dumps(data, indent=2))
        else:
            print("🔄 Registered CI Hooks")
            print("=" * 60)
            current_phase = None
            for hook in hooks:
                if hook.phase != current_phase:
                    current_phase = hook.phase
                    print(f"\n[{current_phase.upper()}]")
                fail_icon = "⛔" if hook.fail_build else "  "
                print(f"  {fail_icon} {hook.hook_id}: {hook.description}")

        return 0

    def _show_status(self, args: List[str]) -> int:
        """Show status of last CI run."""
        # TODO: Read from .prakriti/ci_status.json
        print("⚠️  CI Status: Not implemented yet")
        print("   Last run results will be stored in Prakriti")
        return 1  # HONEST: Return failure for unimplemented command
