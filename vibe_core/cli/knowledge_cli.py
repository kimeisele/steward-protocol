"""
OPUS-307 Phase E: Knowledge CLI

THE MISSING PIECE: Knowledge must be CLI-accessible.

GAD-000 Compliance:
- Discoverability: steward knowledge list
- Observability: steward knowledge show <module>
- Parseability: --json flag
- Composability: Output can feed other commands

Knowledge Modules:
- SANKHYA (concepts): Semantic normalization
- DHARMA (intents): Agent routing rules
- VEDA-4 (circuits): Cognitive state machines
- CORE (soul): Constitutional rules

Usage:
    steward knowledge list                    # List all modules
    steward knowledge concepts                # Show SANKHYA map
    steward knowledge intents                 # Show DHARMA routing
    steward knowledge circuits                # List circuits
    steward knowledge soul                    # Show constitutional rules
    steward knowledge query <term>            # Search knowledge base
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("KNOWLEDGE_CLI")

KNOWLEDGE_ROOT = Path("knowledge")


@register_cli
class KnowledgeCLI:
    """
    CLI for accessing the Knowledge Graph.

    GAD-000: Knowledge must be machine-readable and composable.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="knowledge",
            description="Access Knowledge Graph (SANKHYA, DHARMA, VEDA-4, Soul)",
            domain="knowledge",
            subcommands=["list", "concepts", "intents", "circuits", "soul", "query", "show"],
            tags=["knowledge", "sankhya", "dharma", "veda"],
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
        elif cmd == "concepts":
            return self.cmd_concepts(remaining)
        elif cmd == "intents":
            return self.cmd_intents(remaining)
        elif cmd == "circuits":
            return self.cmd_circuits(remaining)
        elif cmd == "soul":
            return self.cmd_soul(remaining)
        elif cmd == "query":
            return self.cmd_query(remaining)
        elif cmd == "show":
            return self.cmd_show(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        print("""
Knowledge CLI (OPUS-307 Phase E)

GAD-000 COMPLIANT: Knowledge is machine-readable.

Usage:
    steward knowledge list                    List all knowledge modules
    steward knowledge concepts [--json]       Show SANKHYA concept map
    steward knowledge intents [--json]        Show DHARMA routing rules
    steward knowledge circuits [--json]       List VEDA-4 circuits
    steward knowledge soul [--json]           Show constitutional rules
    steward knowledge query <term> [--json]   Search knowledge base
    steward knowledge show <path> [--json]    Show specific knowledge file

Examples:
    steward knowledge concepts --json | jq '.actions'
    steward knowledge query "vote"
    steward knowledge soul --json | jq '.constraints[:5]'
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

    def cmd_list(self, args: List[str]) -> int:
        """List all knowledge modules."""
        as_json = "--json" in args

        modules = []

        # Check each knowledge subdirectory
        if KNOWLEDGE_ROOT.exists():
            for subdir in sorted(KNOWLEDGE_ROOT.iterdir()):
                if subdir.is_dir() and not subdir.name.startswith("."):
                    # Count files
                    yaml_count = len(list(subdir.glob("**/*.yaml")))
                    json_count = len(list(subdir.glob("**/*.json")))
                    md_count = len(list(subdir.glob("**/*.md")))

                    manifest = subdir / "manifest.json"
                    description = ""
                    if manifest.exists():
                        try:
                            m = json.loads(manifest.read_text())
                            description = m.get("description", "")
                        except Exception:
                            pass

                    modules.append(
                        {
                            "name": subdir.name,
                            "path": str(subdir),
                            "files": yaml_count + json_count + md_count,
                            "description": description[:60] if description else "",
                        }
                    )

        if as_json:
            print(json.dumps({"modules": modules, "total": len(modules)}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("KNOWLEDGE MODULES")
            print("=" * 60 + "\n")
            for m in modules:
                print(f"  {m['name']:<20} ({m['files']} files)")
                if m["description"]:
                    print(f"    {m['description']}")
            print(f"\nTotal: {len(modules)} modules")

        return 0

    def cmd_concepts(self, args: List[str]) -> int:
        """Show SANKHYA concept map."""
        as_json = "--json" in args

        path = KNOWLEDGE_ROOT / "concepts" / "general.yaml"
        data = self._load_yaml(path)

        if not data:
            print(f"Error: Cannot load {path}")
            return 1

        if as_json:
            print(json.dumps(data, indent=2))
        else:
            print("\n" + "=" * 60)
            print("SANKHYA CONCEPT MAP (Chaos -> Order)")
            print("=" * 60 + "\n")

            for category, items in data.items():
                print(f"[{category.upper()}]")
                if isinstance(items, dict):
                    for key, values in items.items():
                        print(f"  {key}: {', '.join(values[:5])}" + ("..." if len(values) > 5 else ""))
                print()

        return 0

    def cmd_intents(self, args: List[str]) -> int:
        """Show DHARMA routing rules."""
        as_json = "--json" in args

        path = KNOWLEDGE_ROOT / "intents" / "routing_rules.yaml"
        data = self._load_yaml(path)

        if not data:
            print(f"Error: Cannot load {path}")
            return 1

        if as_json:
            print(json.dumps(data, indent=2))
        else:
            print("\n" + "=" * 60)
            print("DHARMA ROUTING RULES (Concepts -> Agents)")
            print("=" * 60 + "\n")

            rules = data.get("rules", [])
            for rule in rules:
                name = rule.get("name", "?")
                agent = rule.get("agent", "?")
                response = rule.get("response_type", "?")
                triggers = rule.get("triggers", [])
                print(f"  {name}")
                print(f"    Agent: {agent} ({response})")
                print(f"    Triggers: {', '.join(triggers) if triggers else 'FALLBACK'}")
                print()

        return 0

    def cmd_circuits(self, args: List[str]) -> int:
        """List VEDA-4 circuits."""
        as_json = "--json" in args

        circuits = []

        # Check multiple circuit locations
        circuit_paths = [
            KNOWLEDGE_ROOT / "genesis" / "circuits",
            KNOWLEDGE_ROOT / "circuits",
            Path("vibe_core/playbook/circuits"),
        ]

        for circuit_dir in circuit_paths:
            if circuit_dir.exists():
                for f in circuit_dir.glob("*.yaml"):
                    try:
                        data = yaml.safe_load(f.read_text())
                        circuit = data.get("circuit", {})
                        circuits.append(
                            {
                                "id": circuit.get("id", f.stem.upper()),
                                "domain": circuit.get("domain", "unknown"),
                                "description": circuit.get("description", "")[:50],
                                "source": str(f),
                            }
                        )
                    except Exception:
                        pass

        if as_json:
            print(json.dumps({"circuits": circuits, "total": len(circuits)}, indent=2))
        else:
            print("\n" + "=" * 60)
            print("VEDA-4 COGNITIVE CIRCUITS")
            print("=" * 60 + "\n")

            by_domain: Dict[str, List] = {}
            for c in circuits:
                domain = c["domain"]
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(c)

            for domain, cs in sorted(by_domain.items()):
                print(f"[{domain.upper()}]")
                for c in sorted(cs, key=lambda x: x["id"]):
                    print(f"  {c['id']:<30} {c['description']}")
                print()

            print(f"Total: {len(circuits)} circuits")

        return 0

    def cmd_soul(self, args: List[str]) -> int:
        """Show constitutional rules (soul.yaml)."""
        as_json = "--json" in args

        path = KNOWLEDGE_ROOT / "core" / "soul.yaml"
        data = self._load_yaml(path)

        if not data:
            print(f"Error: Cannot load {path}")
            return 1

        if as_json:
            print(json.dumps(data, indent=2, default=str))
        else:
            print("\n" + "=" * 60)
            print("NARASIMHA KILL-SWITCH RULES (IMMUTABLE)")
            print("=" * 60 + "\n")

            # Safety rules
            safety = data.get("safety_rules", [])
            print(f"[SAFETY RULES] ({len(safety)})")
            for rule in safety[:10]:
                print(f"  {rule.get('id')}: {rule.get('message', '')[:50]}")
            if len(safety) > 10:
                print(f"  ... and {len(safety) - 10} more")
            print()

            # Constraints
            constraints = data.get("constraints", [])
            print(f"[CONSTRAINTS] ({len(constraints)})")
            for c in constraints[:10]:
                print(f"  {c.get('id')}: {c.get('message', '')[:50]}")
            if len(constraints) > 10:
                print(f"  ... and {len(constraints) - 10} more")

        return 0

    def cmd_query(self, args: List[str]) -> int:
        """Search knowledge base."""
        if not args or args[0].startswith("-"):
            print("Error: query term required")
            return 1

        term = args[0].lower()
        as_json = "--json" in args

        results = []

        # Search concepts
        concepts = self._load_yaml(KNOWLEDGE_ROOT / "concepts" / "general.yaml")
        if concepts:
            for category, items in concepts.items():
                if isinstance(items, dict):
                    for key, values in items.items():
                        if term in key.lower() or any(term in v.lower() for v in values):
                            results.append(
                                {
                                    "module": "concepts",
                                    "category": category,
                                    "key": key,
                                    "matches": [v for v in values if term in v.lower()][:5],
                                }
                            )

        # Search intents
        intents = self._load_yaml(KNOWLEDGE_ROOT / "intents" / "routing_rules.yaml")
        if intents:
            for rule in intents.get("rules", []):
                name = rule.get("name", "")
                desc = rule.get("description", "")
                if term in name.lower() or term in desc.lower():
                    results.append(
                        {
                            "module": "intents",
                            "name": name,
                            "agent": rule.get("agent"),
                            "description": desc,
                        }
                    )

        # Search soul
        soul = self._load_yaml(KNOWLEDGE_ROOT / "core" / "soul.yaml")
        if soul:
            for rule in soul.get("safety_rules", []):
                if term in rule.get("id", "").lower() or term in rule.get("message", "").lower():
                    results.append(
                        {
                            "module": "soul",
                            "type": "safety_rule",
                            "id": rule.get("id"),
                            "message": rule.get("message"),
                        }
                    )
            for c in soul.get("constraints", []):
                if term in c.get("id", "").lower() or term in c.get("message", "").lower():
                    results.append(
                        {
                            "module": "soul",
                            "type": "constraint",
                            "id": c.get("id"),
                            "message": c.get("message"),
                        }
                    )

        if as_json:
            print(json.dumps({"query": term, "results": results, "count": len(results)}, indent=2))
        else:
            print(f"\nSearch: '{term}'\n")
            print(f"Found {len(results)} results:\n")
            for r in results[:20]:
                module = r.get("module", "?")
                print(f"  [{module}] ", end="")
                if module == "concepts":
                    print(f"{r.get('key')}: {', '.join(r.get('matches', []))}")
                elif module == "intents":
                    print(f"{r.get('name')} -> {r.get('agent')}")
                elif module == "soul":
                    print(f"{r.get('id')}: {r.get('message', '')[:40]}")
            if len(results) > 20:
                print(f"\n  ... and {len(results) - 20} more")

        return 0

    def cmd_show(self, args: List[str]) -> int:
        """Show specific knowledge file."""
        if not args or args[0].startswith("-"):
            print("Error: file path required")
            return 1

        path = Path(args[0])
        as_json = "--json" in args

        # Try relative to knowledge/
        if not path.exists():
            path = KNOWLEDGE_ROOT / args[0]
        if not path.exists():
            print(f"Error: {args[0]} not found")
            return 1

        if path.suffix in (".yaml", ".yml"):
            data = self._load_yaml(path)
            if data:
                if as_json:
                    print(json.dumps(data, indent=2, default=str))
                else:
                    print(yaml.dump(data, default_flow_style=False))
        elif path.suffix == ".json":
            data = json.loads(path.read_text())
            print(json.dumps(data, indent=2))
        else:
            print(path.read_text())

        return 0
