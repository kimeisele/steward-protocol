"""
OPUS-307 Phase E.2: Standards CLI

THE RULES MUST BE ACCESSIBLE: Standards are knowledge.

GAD-000 Compliance:
- Discoverability: steward standards list
- Observability: steward standards show <rule>
- Parseability: --json flag
- Composability: Output feeds Ouroboros

Standards Sources:
- config/standards.yaml (Code sins - Todsünden)
- docs/architecture/GAD_INDEX.yaml (38 GADs)
- knowledge/core/soul.yaml (Constitutional rules)

Usage:
    steward standards list                    # List all standards
    steward standards gads                    # List all GAD standards
    steward standards rules                   # List code rules (Todsünden)
    steward standards show <id>               # Show specific standard
    steward standards check <file>            # Check file for violations
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("STANDARDS_CLI")

CONFIG_ROOT = Path("config")
DOCS_ROOT = Path("docs/architecture")
KNOWLEDGE_ROOT = Path("knowledge")


@register_cli
class StandardsCLI:
    """
    CLI for accessing Standards and GADs.

    GAD-000: Standards must be machine-readable and composable.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="standards",
            description="Access Standards and GADs (38 GADs + Code Rules)",
            domain="governance",
            subcommands=["list", "gads", "rules", "show", "check"],
            tags=["standards", "gad", "governance", "todsünden"],
        )

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
        elif cmd == "gads":
            return self.cmd_gads(remaining)
        elif cmd == "rules":
            return self.cmd_rules(remaining)
        elif cmd == "show":
            return self.cmd_show(remaining)
        elif cmd == "check":
            return self.cmd_check(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print("""
Standards CLI (OPUS-307 Phase E.2)

GAD-000 COMPLIANT: Standards are machine-readable.

Usage:
    steward standards list [--json]           List all standards (GADs + Rules)
    steward standards gads [--json]           List all 38 GAD standards
    steward standards rules [--json]          List code rules (Todsünden)
    steward standards show <id> [--json]      Show specific standard details
    steward standards check <file> [--json]   Check file for violations

Examples:
    steward standards gads --json | jq '.gads | keys[:5]'
    steward standards rules --json | jq '.rules[].id'
    steward standards show GAD-000
    steward standards check vibe_core/agents/base.py
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

    def _load_gad_index(self) -> Optional[Dict]:
        """Load GAD index."""
        return self._load_yaml(DOCS_ROOT / "GAD_INDEX.yaml")

    def _load_code_rules(self) -> Optional[Dict]:
        """Load code standards rules."""
        return self._load_yaml(CONFIG_ROOT / "standards.yaml")

    def cmd_list(self, args: List[str]) -> int:
        """List all standards."""
        as_json = "--json" in args

        gad_index = self._load_gad_index()
        code_rules = self._load_code_rules()

        gad_count = len(gad_index.get("gads", {})) if gad_index else 0
        rule_count = len(code_rules.get("rules", [])) if code_rules else 0

        if as_json:
            print(
                json.dumps(
                    {
                        "summary": {
                            "gad_standards": gad_count,
                            "code_rules": rule_count,
                            "total": gad_count + rule_count,
                        },
                        "sources": {
                            "gad_index": str(DOCS_ROOT / "GAD_INDEX.yaml"),
                            "code_rules": str(CONFIG_ROOT / "standards.yaml"),
                        },
                    },
                    indent=2,
                )
            )
        else:
            print("\n" + "=" * 60)
            print("STEWARD STANDARDS")
            print("=" * 60 + "\n")
            print(f"  GAD Standards:  {gad_count}")
            print(f"  Code Rules:     {rule_count}")
            print(f"  Total:          {gad_count + rule_count}")
            print("\nUse 'steward standards gads' or 'steward standards rules' for details.")

        return 0

    def cmd_gads(self, args: List[str]) -> int:
        """List all GAD standards."""
        as_json = "--json" in args

        gad_index = self._load_gad_index()
        if not gad_index:
            print("Error: Cannot load GAD_INDEX.yaml")
            return 1

        gads = gad_index.get("gads", {})
        meta = gad_index.get("meta", {})

        if as_json:
            print(
                json.dumps(
                    {
                        "meta": meta,
                        "gads": gads,
                        "pillars": gad_index.get("pillars", {}),
                    },
                    indent=2,
                )
            )
        else:
            print("\n" + "=" * 60)
            print("GAD STANDARDS INDEX")
            print("=" * 60 + "\n")

            print(f"Total: {meta.get('total_gads', len(gads))} GADs")
            print(f"Documented: {meta.get('documented', 0)}")
            print(f"Undocumented: {meta.get('undocumented', 0)}")
            print()

            # Group by pillar
            pillars = gad_index.get("pillars", {})
            for pillar, gad_ids in sorted(pillars.items(), key=lambda x: str(x[0])):
                print(f"[PILLAR {pillar}]")
                for gad_id in sorted(gad_ids):
                    gad = gads.get(gad_id, {})
                    refs = gad.get("refs", 0)
                    doc = "✓" if gad.get("documented") else "○"
                    print(f"  {doc} {gad_id:<15} ({refs} refs)")
                print()

        return 0

    def cmd_rules(self, args: List[str]) -> int:
        """List code rules (Todsünden)."""
        as_json = "--json" in args

        code_rules = self._load_code_rules()
        if not code_rules:
            print("Error: Cannot load standards.yaml")
            return 1

        rules = code_rules.get("rules", [])

        if as_json:
            print(json.dumps({"rules": rules, "count": len(rules)}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("CODE STANDARDS (Todsünden)")
            print("=" * 60 + "\n")

            by_severity: Dict[str, List] = {}
            for rule in rules:
                sev = rule.get("severity", "MEDIUM")
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(rule)

            severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            for sev in severity_order:
                if sev in by_severity:
                    print(f"[{sev}]")
                    for rule in by_severity[sev]:
                        print(f"  {rule.get('id'):<25} {rule.get('message', '')[:40]}")
                    print()

            print(f"Total: {len(rules)} rules")

        return 0

    def cmd_show(self, args: List[str]) -> int:
        """Show specific standard details."""
        if not args or args[0].startswith("-"):
            print("Error: standard ID required")
            return 1

        std_id = args[0].upper()
        as_json = "--json" in args

        # Check if it's a GAD
        if std_id.startswith("GAD"):
            return self._show_gad(std_id, as_json)
        else:
            return self._show_rule(std_id.lower(), as_json)

    def _show_gad(self, gad_id: str, as_json: bool) -> int:
        """Show GAD details."""
        gad_index = self._load_gad_index()
        if not gad_index:
            print("Error: Cannot load GAD_INDEX.yaml")
            return 1

        gads = gad_index.get("gads", {})
        gad = gads.get(gad_id)

        if not gad:
            print(f"Error: GAD '{gad_id}' not found")
            return 1

        # Try to load the doc file if it exists
        doc_content = None
        if gad.get("doc"):
            doc_path = Path(gad["doc"])
            if not doc_path.exists():
                doc_path = DOCS_ROOT / gad["doc"]
            if doc_path.exists():
                try:
                    doc_content = doc_path.read_text()[:2000]  # First 2000 chars
                except Exception as e:
                    # OPUS-312: Log doc read failures
                    import logging

                    logging.getLogger("CLI").debug(f"Doc read failed for {doc_path}: {e}")

        result = {
            "id": gad_id,
            "refs": gad.get("refs", 0),
            "files": gad.get("files", 0),
            "documented": gad.get("documented", False),
            "pillar": gad.get("pillar", "?"),
            "doc_path": gad.get("doc"),
            "sample": gad.get("sample"),
        }

        if as_json:
            if doc_content:
                result["doc_excerpt"] = doc_content[:500]
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print(f"GAD: {gad_id}")
            print("=" * 60 + "\n")
            print(f"  Pillar:     {result['pillar']}")
            print(f"  References: {result['refs']} in {result['files']} files")
            print(f"  Documented: {'Yes' if result['documented'] else 'No'}")
            if result.get("doc_path"):
                print(f"  Doc:        {result['doc_path']}")
            if result.get("sample"):
                print(f"\n  Sample:\n    {result['sample'][:80]}")
            if doc_content:
                print(f"\n  Excerpt:\n{doc_content[:500]}")

        return 0

    def _show_rule(self, rule_id: str, as_json: bool) -> int:
        """Show code rule details."""
        code_rules = self._load_code_rules()
        if not code_rules:
            print("Error: Cannot load standards.yaml")
            return 1

        rules = code_rules.get("rules", [])
        rule = next((r for r in rules if r.get("id") == rule_id), None)

        if not rule:
            print(f"Error: Rule '{rule_id}' not found")
            return 1

        if as_json:
            print(json.dumps(rule, indent=2))
        else:
            print("\n" + "=" * 60)
            print(f"RULE: {rule.get('id')}")
            print("=" * 60 + "\n")
            print(f"  Severity: {rule.get('severity')}")
            print(f"  Target:   {rule.get('target')}")
            print(f"  Message:  {rule.get('message')}")
            if rule.get("match"):
                print(f"  Match:    {rule.get('match')}")
            if rule.get("fix_suggestion"):
                print(f"\n  Fix:\n    {rule.get('fix_suggestion')}")

        return 0

    def cmd_check(self, args: List[str]) -> int:
        """Check file for violations."""
        if not args or args[0].startswith("-"):
            print("Error: file path required")
            return 1

        file_path = Path(args[0])
        as_json = "--json" in args

        if not file_path.exists():
            print(f"Error: File '{file_path}' not found")
            return 1

        # Load rules
        code_rules = self._load_code_rules()
        if not code_rules:
            print("Error: Cannot load standards.yaml")
            return 1

        rules = code_rules.get("rules", [])

        # Simple pattern-based check (not full AST)
        violations = []
        content = file_path.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for rule in rules:
                match = rule.get("match", {})

                # Check func matches
                if "func" in match:
                    func = match["func"]
                    if func + "(" in line:
                        # Check args_contain if present
                        if "args_contain" in match:
                            for arg in match["args_contain"]:
                                if f'"{arg}"' in line or f"'{arg}'" in line:
                                    violations.append(
                                        {
                                            "rule_id": rule.get("id"),
                                            "severity": rule.get("severity"),
                                            "line": i,
                                            "message": rule.get("message"),
                                            "fix": rule.get("fix_suggestion"),
                                            "code": line.strip()[:60],
                                        }
                                    )
                        else:
                            violations.append(
                                {
                                    "rule_id": rule.get("id"),
                                    "severity": rule.get("severity"),
                                    "line": i,
                                    "message": rule.get("message"),
                                    "fix": rule.get("fix_suggestion"),
                                    "code": line.strip()[:60],
                                }
                            )

                # Check object matches (for Attribute targets)
                if "object" in match:
                    obj = match["object"]
                    if obj + "." in line:
                        violations.append(
                            {
                                "rule_id": rule.get("id"),
                                "severity": rule.get("severity"),
                                "line": i,
                                "message": rule.get("message"),
                                "fix": rule.get("fix_suggestion"),
                                "code": line.strip()[:60],
                            }
                        )

        if as_json:
            print(
                json.dumps(
                    {
                        "file": str(file_path),
                        "violations": violations,
                        "count": len(violations),
                        "clean": len(violations) == 0,
                    },
                    indent=2,
                )
            )
        else:
            print("\n" + "=" * 60)
            print(f"STANDARDS CHECK: {file_path}")
            print("=" * 60 + "\n")

            if not violations:
                print("  ✓ No violations found")
            else:
                for v in violations:
                    print(f"  [{v['severity']}] Line {v['line']}: {v['rule_id']}")
                    print(f"    {v['message']}")
                    print(f"    Code: {v['code']}")
                    print()

                print(f"Total: {len(violations)} violations")

        return 0
