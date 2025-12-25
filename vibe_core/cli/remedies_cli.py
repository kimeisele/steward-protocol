"""
OPUS-307 Phase E.3: Remedies CLI

HEALING KNOWLEDGE MUST BE ACCESSIBLE: The Sattva remedy layer.

GAD-000 Compliance:
- Discoverability: steward remedies list
- Observability: steward remedies show <id>
- Parseability: --json flag
- Composability: Ouroboros uses this to heal

Remedy Sources:
- config/standards.yaml (fix_suggestion per rule)
- error_recovery.yaml (error patterns + strategies)
- heal_codebase.yaml (violation → action mapping)
- auto_heal.yaml (drift patterns)

The SATTVA layer: Pure knowledge for healing.

Usage:
    steward remedies list                     # List all remedies
    steward remedies fixes                    # List code violation fixes
    steward remedies patterns                 # List error patterns
    steward remedies circuits                 # List healing circuits
    steward remedies get <rule_id>            # Get remedy for specific rule
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("REMEDIES_CLI")

CONFIG_ROOT = Path("config")
CIRCUITS_ROOT = Path("vibe_core/playbook/circuits")
GENESIS_CIRCUITS = Path("knowledge/genesis/circuits")
PLUGIN_CIRCUITS = Path("vibe_core/plugins/opus_assistant/circuits")


class RemediesCLI:
    """
    CLI for accessing Healing/Remedy Knowledge.

    GAD-000: Remedies must be machine-readable and composable.
    SATTVA: Pure knowledge for healing.
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def run(self, args: List[str]) -> int:
        """Main entry point."""
        if not args:
            self._print_usage()
            return 1

        cmd = args[0]
        remaining = args[1:]

        if cmd in ("--help", "-h", "help"):
            self._print_usage()
            return 0
        elif cmd == "list":
            return self.cmd_list(remaining)
        elif cmd == "fixes":
            return self.cmd_fixes(remaining)
        elif cmd == "patterns":
            return self.cmd_patterns(remaining)
        elif cmd == "circuits":
            return self.cmd_circuits(remaining)
        elif cmd == "get":
            return self.cmd_get(remaining)
        elif cmd == "for":
            return self.cmd_for(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print("""
Remedies CLI (OPUS-307 Phase E.3) - SATTVA Layer

GAD-000 COMPLIANT: Healing knowledge is machine-readable.

Usage:
    steward remedies list [--json]            List all remedies (summary)
    steward remedies fixes [--json]           List code violation fixes
    steward remedies patterns [--json]        List error patterns & strategies
    steward remedies circuits [--json]        List healing circuits
    steward remedies get <rule_id> [--json]   Get remedy for specific rule
    steward remedies for <violation> [--json] Get remedy for violation type

Examples:
    steward remedies fixes --json | jq '.[].id'
    steward remedies get unsafe_io_write
    steward remedies for silent_failure --json
    steward remedies patterns --json | jq '.transient'
""")

    def _load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file with caching."""
        key = str(path)
        if key not in self._cache:
            if path.exists():
                try:
                    self._cache[key] = yaml.safe_load(path.read_text())
                except Exception as e:
                    logger.error(f"Failed to load {path}: {e}")
                    return None
            else:
                return None
        return self._cache[key]

    def _load_standards(self) -> Optional[Dict]:
        """Load code standards rules."""
        return self._load_yaml(CONFIG_ROOT / "standards.yaml")

    def _load_error_recovery(self) -> Optional[Dict]:
        """Load error recovery circuit."""
        # Try genesis first, then playbook
        data = self._load_yaml(GENESIS_CIRCUITS / "error_recovery.yaml")
        if not data:
            data = self._load_yaml(CIRCUITS_ROOT / "error_recovery.yaml")
        return data

    def _load_heal_codebase(self) -> Optional[Dict]:
        """Load heal codebase circuit."""
        return self._load_yaml(CIRCUITS_ROOT / "heal_codebase.yaml")

    def _load_auto_heal(self) -> Optional[Dict]:
        """Load auto heal circuit."""
        return self._load_yaml(PLUGIN_CIRCUITS / "auto_heal.yaml")

    def cmd_list(self, args: List[str]) -> int:
        """List all remedies (summary)."""
        as_json = "--json" in args

        # Count fixes
        standards = self._load_standards()
        fixes = []
        if standards:
            for rule in standards.get("rules", []):
                if rule.get("fix_suggestion"):
                    fixes.append(
                        {
                            "rule_id": rule.get("id"),
                            "severity": rule.get("severity"),
                            "fix": rule.get("fix_suggestion"),
                        }
                    )

        # Count error patterns (inside circuit object)
        error_recovery = self._load_error_recovery()
        error_patterns = {}
        if error_recovery:
            circuit = error_recovery.get("circuit", {})
            error_patterns = circuit.get("error_patterns", error_recovery.get("error_patterns", {}))

        # Count drift patterns
        auto_heal = self._load_auto_heal()
        drift_patterns = {}
        if auto_heal:
            drift_patterns = auto_heal.get("patterns", {})

        # Count healing circuits
        healing_circuits = []
        for circuit_dir in [CIRCUITS_ROOT, GENESIS_CIRCUITS, PLUGIN_CIRCUITS]:
            if circuit_dir.exists():
                for f in circuit_dir.glob("*.yaml"):
                    name = f.stem.lower()
                    if any(kw in name for kw in ["heal", "recovery", "fix", "purge"]):
                        healing_circuits.append(str(f))

        summary = {
            "code_fixes": len(fixes),
            "error_pattern_categories": len(error_patterns),
            "drift_patterns": len(drift_patterns),
            "healing_circuits": len(healing_circuits),
            "total_remedies": len(fixes) + len(error_patterns) + len(drift_patterns),
        }

        if as_json:
            print(
                json.dumps(
                    {
                        "summary": summary,
                        "sources": {
                            "standards": str(CONFIG_ROOT / "standards.yaml"),
                            "error_recovery": str(GENESIS_CIRCUITS / "error_recovery.yaml"),
                            "auto_heal": str(PLUGIN_CIRCUITS / "auto_heal.yaml"),
                        },
                    },
                    indent=2,
                )
            )
        else:
            print("\n" + "=" * 60)
            print("SATTVA REMEDY LAYER")
            print("=" * 60 + "\n")
            print(f"  Code Fixes:          {summary['code_fixes']}")
            print(f"  Error Patterns:      {summary['error_pattern_categories']} categories")
            print(f"  Drift Patterns:      {summary['drift_patterns']}")
            print(f"  Healing Circuits:    {summary['healing_circuits']}")
            print(f"\n  Total Remedies:      {summary['total_remedies']}")
            print("\nUse 'steward remedies fixes' or 'steward remedies patterns' for details.")

        return 0

    def cmd_fixes(self, args: List[str]) -> int:
        """List code violation fixes."""
        as_json = "--json" in args

        standards = self._load_standards()
        if not standards:
            print("Error: Cannot load standards.yaml")
            return 1

        fixes = []
        for rule in standards.get("rules", []):
            if rule.get("fix_suggestion"):
                fixes.append(
                    {
                        "rule_id": rule.get("id"),
                        "severity": rule.get("severity"),
                        "violation": rule.get("message"),
                        "fix": rule.get("fix_suggestion"),
                        "target": rule.get("target"),
                        "match": rule.get("match"),
                    }
                )

        if as_json:
            print(json.dumps(fixes, indent=2))
        else:
            print("\n" + "=" * 60)
            print("CODE VIOLATION FIXES (Todsünden Remedies)")
            print("=" * 60 + "\n")

            for fix in fixes:
                print(f"  [{fix['severity']}] {fix['rule_id']}")
                print(f"    Violation: {fix['violation'][:50]}...")
                print(f"    Fix:       {fix['fix']}")
                print()

            print(f"Total: {len(fixes)} fixes available")

        return 0

    def cmd_patterns(self, args: List[str]) -> int:
        """List error patterns and strategies."""
        as_json = "--json" in args

        error_recovery = self._load_error_recovery()
        if not error_recovery:
            print("Error: Cannot load error_recovery.yaml")
            return 1

        # Error patterns are inside circuit object
        circuit = error_recovery.get("circuit", {})
        error_patterns = circuit.get("error_patterns", error_recovery.get("error_patterns", {}))

        # Also get recovery strategies from states
        states = circuit.get("states", {})
        replan_state = states.get("REPLAN", {})

        strategies = {}
        for action in replan_state.get("entry_actions", []):
            if action.get("action") == "select_strategy":
                strategies = action.get("params", {}).get("strategies", {})

        if as_json:
            print(
                json.dumps(
                    {
                        "error_patterns": error_patterns,
                        "recovery_strategies": strategies,
                    },
                    indent=2,
                )
            )
        else:
            print("\n" + "=" * 60)
            print("ERROR PATTERNS & RECOVERY STRATEGIES")
            print("=" * 60 + "\n")

            print("[ERROR PATTERNS]")
            for category, patterns in error_patterns.items():
                print(f"\n  {category.upper()}:")
                for p in patterns[:5]:
                    print(f"    - {p}")
                if len(patterns) > 5:
                    print(f"    ... and {len(patterns) - 5} more")

            print("\n[RECOVERY STRATEGIES]")
            for name, strategy in strategies.items():
                when = strategy.get("when", "?")
                print(f"\n  {name}:")
                print(f"    When: {when}")

            print()

        return 0

    def cmd_circuits(self, args: List[str]) -> int:
        """List healing circuits."""
        as_json = "--json" in args

        circuits = []

        for circuit_dir in [CIRCUITS_ROOT, GENESIS_CIRCUITS, PLUGIN_CIRCUITS]:
            if circuit_dir.exists():
                for f in circuit_dir.glob("*.yaml"):
                    name = f.stem.lower()
                    if any(kw in name for kw in ["heal", "recovery", "fix", "purge", "ouroboros"]):
                        try:
                            data = yaml.safe_load(f.read_text())
                            circuit_data = data.get("circuit", {})
                            circuits.append(
                                {
                                    "id": circuit_data.get("id", f.stem.upper()),
                                    "domain": circuit_data.get("domain", "unknown"),
                                    "description": circuit_data.get("description", "")[:60],
                                    "path": str(f),
                                    "entry_state": circuit_data.get("entry_state", "?"),
                                }
                            )
                        except Exception:
                            pass

        if as_json:
            print(json.dumps({"healing_circuits": circuits, "count": len(circuits)}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("HEALING CIRCUITS")
            print("=" * 60 + "\n")

            for c in circuits:
                print(f"  {c['id']}")
                print(f"    Domain:      {c['domain']}")
                print(f"    Entry:       {c['entry_state']}")
                print(f"    Description: {c['description'][:50]}")
                print()

            print(f"Total: {len(circuits)} healing circuits")

        return 0

    def cmd_get(self, args: List[str]) -> int:
        """Get remedy for specific rule."""
        if not args or args[0].startswith("-"):
            print("Error: rule_id required")
            return 1

        rule_id = args[0].lower()
        as_json = "--json" in args

        standards = self._load_standards()
        if not standards:
            print("Error: Cannot load standards.yaml")
            return 1

        rule = next((r for r in standards.get("rules", []) if r.get("id") == rule_id), None)

        if not rule:
            print(f"Error: Rule '{rule_id}' not found")
            return 1

        remedy = {
            "rule_id": rule.get("id"),
            "severity": rule.get("severity"),
            "violation": rule.get("message"),
            "fix_suggestion": rule.get("fix_suggestion"),
            "target": rule.get("target"),
            "match": rule.get("match"),
            "healing_circuit": "HEAL_CODEBASE_V1",
            "invocation": f"steward run HEAL_CODEBASE_V1 --violation_type {rule_id}",
        }

        if as_json:
            print(json.dumps(remedy, indent=2))
        else:
            print("\n" + "=" * 60)
            print(f"REMEDY: {remedy['rule_id']}")
            print("=" * 60 + "\n")
            print(f"  Severity:   {remedy['severity']}")
            print(f"  Violation:  {remedy['violation']}")
            print(f"  Target:     {remedy['target']}")
            print("\n  FIX:")
            print(f"    {remedy['fix_suggestion']}")
            print("\n  HEALING CIRCUIT:")
            print(f"    {remedy['healing_circuit']}")
            print("\n  INVOCATION:")
            print(f"    {remedy['invocation']}")

        return 0

    def cmd_for(self, args: List[str]) -> int:
        """Get remedy for violation type (alias for get)."""
        return self.cmd_get(args)
