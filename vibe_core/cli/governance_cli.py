"""
GOVERNANCE CLI - INTELLIGENT Protocol Interface
================================================
GAD-000 Compliant: Connected to NAGA IntelBridge.

"CLI = ANANTA SHESHA + SHUKA's VISION"

PATTERN: Protocol Call + Intelligence Query = Enriched Response
- Protocol: governance/bridge.py (data)
- Intel: IntelBridgeProtocol (gaps, threats, recommendations)

Owner: YAMARAJA (Judgment) + SHUKA (Vision)
OpCode: FETCH_RES via Mahamantra routing
"""

import json
from typing import List, Optional

from vibe_core.protocols.cli import CLIMeta, register_cli

# Protocol functions - THE DATA
from vibe_core.protocols.governance.bridge import (
    ProtocolBridge,
    ProtocolCategory,
    audit,
    get_owner,
    list_by_owner,
)
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.yamaraja.security import SecurityLevel

# For file writing
from pathlib import Path
from datetime import datetime
import re

# Intelligence - THE INSIGHT
from vibe_core.protocols.naga.intel_bridge import (
    IntelBridgeProtocol,
    IntelCategory,
    IntelQuery,
    NullIntelBridge,
)

import logging
logger = logging.getLogger(__name__)


@register_cli
class GovernanceCLI:
    """
    Protocol Governance CLI with NAGA Intelligence.

    PATTERN: DATA + INTEL = INSIGHT
    - Data from governance/bridge.py (audit, list, inspect)
    - Intel from IntelBridgeProtocol (threats, gaps, suggestions)

    Like CIA: See what exists, see what's MISSING, see what's WRONG.
    """

    def __init__(self):
        self._intel_bridge: Optional[IntelBridgeProtocol] = None

    def _get_intel(self) -> IntelBridgeProtocol:
        """Get IntelBridge - lazy loaded from ServiceRegistry."""
        if self._intel_bridge is None:
            try:
                from vibe_core.di import ServiceRegistry

                bridge = ServiceRegistry.get(IntelBridgeProtocol)
                if bridge is not None:
                    self._intel_bridge = bridge
                else:
                    self._intel_bridge = NullIntelBridge()
            except Exception:
                self._intel_bridge = NullIntelBridge()
        return self._intel_bridge

    def _query_governance_intel(self) -> List[str]:
        """Query NAGA for governance-related intelligence."""
        intel = self._get_intel()
        insights = []

        # Query for governance-related intel
        query = IntelQuery(
            context="governance protocol audit",
            categories=(IntelCategory.SECURITY, IntelCategory.HEALTH, IntelCategory.SUGGESTION),
            max_results=5,
        )
        response = intel.query(query)

        for item in response.items:
            insights.append(item.to_chat_message())

        # Check for critical/threats
        critical = intel.get_critical()
        for item in critical:
            if "governance" in item.summary.lower() or "protocol" in item.summary.lower():
                insights.append(f"🚨 CRITICAL: {item.summary}")

        return insights

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="governance",
            description="Protocol Governance + NAGA Intel (12 Mahajanas)",
            domain="governance",
            subcommands=["audit", "inspect", "list", "owners", "intel", "gaps", "scan", "terrain", "assign", "fix-all"],
            tags=["protocol", "governance", "mahajana", "yamaraja", "intel", "shuka", "scan", "assign", "fix"],
        )

    def run(self, args: List[str]) -> int:
        """Main entry - dispatch to protocol functions + intel."""
        if not args:
            self._print_usage()
            return 0

        cmd = args[0]
        remaining = args[1:]

        if cmd in ("--help", "-h", "help"):
            self._print_usage()
            return 0
        elif cmd == "audit":
            return self.cmd_audit(remaining)
        elif cmd == "inspect":
            return self.cmd_inspect(remaining)
        elif cmd == "list":
            return self.cmd_list(remaining)
        elif cmd == "owners":
            return self.cmd_owners(remaining)
        elif cmd == "intel":
            return self.cmd_intel(remaining)
        elif cmd == "gaps":
            return self.cmd_gaps(remaining)
        elif cmd == "scan":
            return self.cmd_scan(remaining)
        elif cmd == "terrain":
            return self.cmd_terrain(remaining)
        elif cmd == "assign":
            return self.cmd_assign(remaining)
        elif cmd == "fix-all":
            return self.cmd_fix_all(remaining)
        else:
            print(f"Unknown command: {cmd}")
            self._print_usage()
            return 1

    def _print_usage(self):
        """Print usage - shows data + intel status."""
        report = audit()  # DELEGATE to protocol
        intel_insights = self._query_governance_intel()

        print(f"""
GOVERNANCE CLI (NAGA Intelligence Connected)

DATA COMMANDS:
    steward governance audit              Audit report + NAGA intel
    steward governance inspect <path>     Protocol details
    steward governance list --owner X     List by Mahajana
    steward governance owners             12 Mahajana distribution

INTEL COMMANDS:
    steward governance intel              NAGA intelligence feed
    steward governance gaps               Identify gaps & anomalies

DISCOVERY COMMANDS:
    steward governance scan               Scan ENTIRE repo (unknown terrain)
    steward governance terrain            Show ungoverned directories

WRITE COMMANDS:
    steward governance assign <path> <mahajana>   Assign ownership to file
    steward governance fix-all [--dry-run]        Auto-fix all ungoverned files

Status: {report["governed_count"]}/{report["total_protocols"]} governed | {len(intel_insights)} intel items
""")

    def cmd_audit(self, args: List[str]) -> int:
        """DELEGATE to audit() + NAGA intel."""
        as_json = "--json" in args
        no_intel = "--no-intel" in args

        report = audit()  # PROTOCOL CALL
        intel_insights = [] if no_intel else self._query_governance_intel()

        if as_json:
            result = {**report, "intel": intel_insights}
            print(json.dumps(result, indent=2))
        else:
            # DATA section
            print(f"\n{'=' * 60}")
            print(f"  GOVERNANCE AUDIT (DATA)")
            print(f"{'=' * 60}")
            print(f"  Health: {report['health_score'] * 100:.0f}%")
            print(f"  Governed: {report['governed_count']}")
            print(f"  Ungoverned: {report['ungoverned_count']}")
            if report["ungoverned_list"]:
                print(f"  Issues: {report['ungoverned_list'][:5]}")

            # INTEL section
            if intel_insights:
                print(f"\n{'=' * 60}")
                print(f"  NAGA INTELLIGENCE (SHUKA)")
                print(f"{'=' * 60}")
                for insight in intel_insights:
                    print(f"  {insight}")
            else:
                print(f"\n  [No NAGA intel available]")

        return 0

    def cmd_inspect(self, args: List[str]) -> int:
        """DELEGATE to ProtocolBridge.get_entry()."""
        if not args or args[0].startswith("-"):
            print("Error: path required")
            return 1

        path = args[0]
        as_json = "--json" in args
        entry = ProtocolBridge.get_entry(path)  # PROTOCOL CALL

        if entry is None:
            print(f"Not found: {path}")
            return 1

        if as_json:
            print(json.dumps(entry, indent=2))
        else:
            print(f"\n{entry['name']}")
            print(f"  Owner: {entry['owner'].upper()}")
            print(f"  Level: {SecurityLevel(entry['level']).name}")
            print(f"  Category: {entry['category']}")
        return 0

    def cmd_list(self, args: List[str]) -> int:
        """DELEGATE to list_by_owner() or ProtocolBridge methods."""
        as_json = "--json" in args

        # Parse --owner flag
        owner = None
        for i, arg in enumerate(args):
            if arg == "--owner" and i + 1 < len(args):
                owner = args[i + 1]
                break

        if owner:
            try:
                mahajana = Mahajana(owner.lower())
                protocols = list_by_owner(mahajana)  # PROTOCOL CALL
            except ValueError:
                print(f"Unknown owner: {owner}")
                print(f"Valid: {', '.join(m.value for m in Mahajana)}")
                return 1
        else:
            # No filter - show summary
            report = audit()  # PROTOCOL CALL
            print(f"\nTotal: {report['total_protocols']} protocols")
            print("Use --owner <mahajana> to filter")
            return 0

        if as_json:
            print(json.dumps(protocols, indent=2))
        else:
            print(f"\n{owner.upper()} owns {len(protocols)} protocols:")
            for p in protocols[:20]:
                print(f"  {p['name']}")
            if len(protocols) > 20:
                print(f"  ... and {len(protocols) - 20} more")
        return 0

    def cmd_owners(self, args: List[str]) -> int:
        """DELEGATE to audit() for owner distribution."""
        as_json = "--json" in args
        report = audit()  # PROTOCOL CALL
        dist = report["owner_distribution"]

        if as_json:
            print(json.dumps(dist, indent=2))
        else:
            print("\n12 Mahajana Distribution:")
            for m in Mahajana:
                count = dist.get(m.value, 0)
                bar = "#" * min(count, 30)
                print(f"  {m.value:12} {bar} {count}")
        return 0

    # =========================================================================
    # INTELLIGENCE COMMANDS (SHUKA's Vision)
    # =========================================================================

    def cmd_intel(self, args: List[str]) -> int:
        """Query NAGA intelligence for governance insights."""
        as_json = "--json" in args
        intel = self._get_intel()

        # Get all intel categories
        recent = intel.get_recent(limit=10)
        critical = intel.get_critical()
        threats = intel.get_threats()

        if as_json:
            result = {
                "recent": [
                    {"summary": i.summary, "category": i.category.value, "priority": i.priority.value} for i in recent
                ],
                "critical": [i.summary for i in critical],
                "threats": [i.summary for i in threats],
                "active_nagas": intel.get_active_nagas(),
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"  NAGA INTELLIGENCE FEED (SHUKA)")
            print(f"{'=' * 60}")

            if critical:
                print(f"\n  🚨 CRITICAL ({len(critical)}):")
                for item in critical:
                    print(f"    - {item.summary}")

            if threats:
                print(f"\n  ⚠️  THREATS ({len(threats)}):")
                for item in threats:
                    print(f"    - {item.summary}")

            if recent:
                print(f"\n  📊 RECENT ({len(recent)}):")
                for item in recent:
                    print(f"    {item.to_chat_message()}")

            active = intel.get_active_nagas()
            if active:
                print(f"\n  🐍 Active NAGAs: {', '.join(active)}")
            else:
                print(f"\n  [No active NAGAs - running in NullIntelBridge mode]")

        return 0

    def cmd_gaps(self, args: List[str]) -> int:
        """Identify governance gaps and anomalies."""
        as_json = "--json" in args

        # Get protocol data
        report = audit()

        # Identify gaps
        gaps = []

        # 1. Ungoverned protocols = GAPS
        for p in report["ungoverned_list"]:
            gaps.append(
                {
                    "type": "ungoverned",
                    "severity": "high",
                    "item": p,
                    "suggestion": f"Assign {p} to a Mahajana",
                }
            )

        # 2. Underrepresented Mahajanas = IMBALANCE
        dist = report["owner_distribution"]
        avg = sum(dist.values()) / len(dist) if dist else 0
        for m in Mahajana:
            count = dist.get(m.value, 0)
            if count < avg * 0.3:  # Less than 30% of average
                gaps.append(
                    {
                        "type": "imbalance",
                        "severity": "medium",
                        "item": m.value,
                        "suggestion": f"{m.value.upper()} only owns {count} protocols (avg: {avg:.0f})",
                    }
                )

        # 3. Security level distribution gaps
        level_dist = report.get("level_distribution", {})
        if level_dist.get("SUBSTRATE", 0) < 5:
            gaps.append(
                {
                    "type": "security",
                    "severity": "high",
                    "item": "SUBSTRATE",
                    "suggestion": "Need more SUBSTRATE level protocols for foundation",
                }
            )

        # 4. Query NAGA for additional gaps
        intel = self._get_intel()
        query = IntelQuery(
            context="governance gaps anomalies missing",
            categories=(IntelCategory.SUGGESTION,),
            max_results=5,
        )
        intel_response = intel.query(query)
        for item in intel_response.items:
            gaps.append(
                {
                    "type": "intel",
                    "severity": item.priority.value,
                    "item": item.source_naga,
                    "suggestion": item.summary,
                }
            )

        if as_json:
            print(json.dumps({"gaps": gaps, "total": len(gaps)}, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"  GOVERNANCE GAPS & ANOMALIES")
            print(f"{'=' * 60}")

            if not gaps:
                print(f"\n  ✅ No gaps detected - governance is watertight!")
            else:
                high = [g for g in gaps if g["severity"] == "high"]
                medium = [g for g in gaps if g["severity"] == "medium"]
                low = [g for g in gaps if g["severity"] not in ("high", "medium")]

                if high:
                    print(f"\n  🔴 HIGH SEVERITY ({len(high)}):")
                    for g in high:
                        print(f"    [{g['type']}] {g['suggestion']}")

                if medium:
                    print(f"\n  🟡 MEDIUM ({len(medium)}):")
                    for g in medium:
                        print(f"    [{g['type']}] {g['suggestion']}")

                if low:
                    print(f"\n  🟢 LOW ({len(low)}):")
                    for g in low:
                        print(f"    [{g['type']}] {g['suggestion']}")

            print(f"\n  Total: {len(gaps)} gaps identified")

        return 0

    # =========================================================================
    # DISCOVERY COMMANDS (Full Repo Scan)
    # =========================================================================

    def cmd_scan(self, args: List[str]) -> int:
        """Scan ENTIRE repo using mahamantra scanner - find __mahajana__ declarations."""
        as_json = "--json" in args

        # Use mahamantra ONE IMPORT pattern
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.scan()

        if as_json:
            output = {
                "files_scanned": result.files_scanned,
                "declarations_found": result.declarations_found,
                "simple_declarations": result.simple_declarations,
                "by_mahajana": dict(result.by_mahajana),
                "by_position": {str(k): v for k, v in result.by_position.items()},
                "errors": result.errors,
                "coverage_pct": (result.declarations_found / max(result.files_scanned, 1)) * 100,
            }
            print(json.dumps(output, indent=2))
        else:
            # Use mahamantra's built-in print_scan()
            mahamantra.print_scan()

            # Add governance context
            coverage = (result.declarations_found / max(result.files_scanned, 1)) * 100
            ungoverned = result.files_scanned - result.declarations_found

            print(f"\n  {'=' * 50}")
            print(f"  GOVERNANCE STATUS")
            print(f"  {'=' * 50}")
            print(f"  Coverage:    {coverage:.1f}%")
            print(f"  Ungoverned:  {ungoverned} files")
            print(f"\n  ACTION: Add __mahajana__ = 'name' to ungoverned files")
            print(f"  DOCS:   from vibe_core.mahamantra import mahamantra")

        return 0

    def cmd_terrain(self, args: List[str]) -> int:
        """Show detailed terrain of ungoverned directories with Mahajana suggestions."""
        from pathlib import Path
        from collections import defaultdict

        as_json = "--json" in args

        vibe_core = Path(__file__).parent.parent

        # Directory → Suggested Mahajana mapping
        # Based on domain/purpose
        DIR_MAHAJANA_MAP = {
            "protocols": ("yamaraja", "Law/Governance - already governed"),
            "naga": ("yamaraja", "Security/Judgment - NAGA federation"),
            "cli": ("narada", "Communication - user interface"),
            "plugins": ("prahlada", "Devotion - extensions serving the core"),
            "cartridges": ("prahlada", "Devotion - modular capabilities"),
            "state": ("bhishma", "Commitment - immutable state"),
            "runtime": ("brahma", "Creation - system bootstrap"),
            "phoenix": ("brahma", "Creation - resurrection/rebirth"),
            "shuddhi": ("kapila", "Analysis - purification/healing"),
            "services": ("janaka", "Duty - service layer"),
            "loaders": ("brahma", "Creation - initialization"),
            "tools": ("narada", "Communication - tool interfaces"),
            "llm": ("shuka", "Vision - AI/LLM integration"),
            "agents": ("brahma", "Creation - agent factories"),
            "knowledge": ("kumaras", "Knowledge - wisdom storage"),
            "governance": ("manu", "Law - rules and policies"),
            "cortex": ("shuka", "Vision - intelligence center"),
            "vajra": ("yamaraja", "Judgment - security enforcement"),
            "genesis": ("brahma", "Creation - system genesis"),
            "steward": ("janaka", "Duty - core steward"),
            "ouroboros": ("shambhu", "Destruction - cycle management"),
            "gateway": ("narada", "Communication - API gateway"),
            "scheduling": ("manu", "Law - time management"),
            "config": ("bhishma", "Commitment - configuration"),
            "ROOT": ("brahma", "Creation - core modules"),
        }

        by_dir = defaultdict(list)
        for f in vibe_core.rglob("*.py"):
            try:
                rel = f.relative_to(vibe_core)
                parts = rel.parts
                top_dir = parts[0] if len(parts) > 1 else "ROOT"
                by_dir[top_dir].append(str(rel))
            except ValueError as _exc:
                logger.exception("Unexpected error: %s", _exc)

        if as_json:
            result = {
                d: {
                    "files": len(files),
                    "suggested_mahajana": DIR_MAHAJANA_MAP.get(d, ("prahlada", "Default"))[0],
                    "reason": DIR_MAHAJANA_MAP.get(d, ("prahlada", "Default"))[1],
                }
                for d, files in by_dir.items()
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"  TERRAIN MAP - Mahajana Assignments")
            print(f"{'=' * 60}")
            print(f"\n  {'DIRECTORY':<15} {'FILES':>5} {'MAHAJANA':<12} {'REASON':<25}")
            print(f"  {'-' * 60}")

            for d, files in sorted(by_dir.items(), key=lambda x: -len(x[1])):
                mahajana, reason = DIR_MAHAJANA_MAP.get(d, ("prahlada", "Default assignment"))
                emoji = "" if d == "protocols" else "📍"
                print(f"  {emoji} {d:<13} {len(files):>5} {mahajana.upper():<12} {reason[:25]}")

            print(f"\n  Legend: ✅ = Governed, 📍 = Needs governance")
            print(f"\n  ACTION: Use governance bridge to add these directories")

        return 0

    # =========================================================================
    # WRITE COMMANDS (Modify Governance)
    # =========================================================================

    def cmd_assign(self, args: List[str]) -> int:
        """
        Assign ownership to a file.

        Usage: governance assign <path> <mahajana>

        Writes OWNER declaration to file + logs to ledger.
        """
        if len(args) < 2:
            print("Usage: governance assign <path> <mahajana>")
            print("Example: governance assign substrate/balarama.py bali")
            print(f"\nValid Mahajanas: {', '.join(m.value for m in Mahajana)}")
            return 1

        file_path = args[0]
        mahajana_name = args[1].lower()
        dry_run = "--dry-run" in args

        # Validate Mahajana
        try:
            mahajana = Mahajana(mahajana_name)
        except ValueError:
            print(f"❌ Unknown Mahajana: {mahajana_name}")
            print(f"Valid: {', '.join(m.value for m in Mahajana)}")
            return 1

        # Find the file
        vibe_core = Path(__file__).parent.parent

        # Try different path resolutions
        candidates = [
            vibe_core / "protocols" / file_path,
            vibe_core / file_path,
            Path(file_path),
        ]

        target_file = None
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                target_file = candidate
                break

        if target_file is None:
            print(f"❌ File not found: {file_path}")
            print(f"Tried: {[str(c) for c in candidates]}")
            return 1

        # Check if already has OWNER
        content = target_file.read_text()
        has_owner = "OWNER: Final" in content or "OWNER =" in content

        if has_owner and "--force" not in args:
            print(f"⚠️  {file_path} already has OWNER declaration")
            print("Use --force to overwrite")
            return 1

        if dry_run:
            print(f"[DRY-RUN] Would assign {file_path} → {mahajana.value.upper()}")
            return 0

        # Write OWNER to file
        success = self._write_owner_to_file(target_file, mahajana, content, has_owner)

        if success:
            print(f"✅ Assigned {file_path} → {mahajana.value.upper()}")

            # Log to ledger (if available)
            self._log_assignment(file_path, mahajana)

            return 0
        else:
            print(f"❌ Failed to write to {file_path}")
            return 1

    def _write_owner_to_file(self, file_path: Path, mahajana: Mahajana, content: str, has_owner: bool) -> bool:
        """
        Write OWNER declaration to a Python file.

        Inserts after imports, before first class/function.
        """
        try:
            # Build the OWNER block
            owner_block = f"""
# =============================================================================
# PROTOCOL OWNERSHIP (Governed by CLI)
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.{mahajana.name}
"""

            if has_owner:
                # Replace existing OWNER line
                content = re.sub(
                    r"OWNER:\s*Final\[Mahajana\]\s*=\s*Mahajana\.\w+",
                    f"OWNER: Final[Mahajana] = Mahajana.{mahajana.name}",
                    content,
                )
            else:
                # Find insertion point (after imports, before first class/def)
                lines = content.split("\n")
                insert_idx = 0

                # Skip docstring
                in_docstring = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        if in_docstring:
                            in_docstring = False
                            insert_idx = i + 1
                        else:
                            in_docstring = True
                    elif not in_docstring:
                        if line.startswith("from ") or line.startswith("import "):
                            insert_idx = i + 1
                        elif line.startswith("class ") or line.startswith("def "):
                            break

                # Check if we need to add the import
                needs_import = "from vibe_core.protocols.mahajanas.router import" not in content
                needs_final = "from typing import" not in content or "Final" not in content

                import_additions = []
                if needs_import:
                    import_additions.append("from vibe_core.protocols.mahajanas.router import Mahajana")
                if needs_final:
                    if "from typing import" in content:
                        # Add Final to existing typing import
                        content = re.sub(r"from typing import \(", "from typing import (\n    Final,", content)
                        content = re.sub(r"from typing import ([^(])", r"from typing import Final, \1", content)
                    else:
                        import_additions.append("from typing import Final")

                # Insert imports if needed
                if import_additions:
                    import_block = "\n".join(import_additions) + "\n"
                    lines.insert(insert_idx, import_block)
                    insert_idx += 1

                # Insert OWNER block
                lines.insert(insert_idx, owner_block)
                content = "\n".join(lines)

            # Write back
            file_path.write_text(content)
            return True

        except Exception as e:
            print(f"Error writing to file: {e}")
            return False

    def _log_assignment(self, file_path: str, mahajana: Mahajana) -> None:
        """Log assignment to Bhishma ledger (if available)."""
        try:
            from vibe_core.protocols.mahajanas.bhishma.ledger import Ledger

            ledger = Ledger()
            ledger.record(
                event_type="governance.assign",
                data={
                    "path": str(file_path),
                    "owner": mahajana.value,
                    "timestamp": datetime.now().isoformat(),
                    "by": "governance-cli",
                },
            )
        except Exception as _exc:
            logger.exception("Unexpected error: %s", _exc)

    def cmd_fix_all(self, args: List[str]) -> int:
        """
        Auto-fix all ungoverned files.

        Usage: governance fix-all [--dry-run]

        Uses heuristics to determine Mahajana based on:
        1. File location (mahajanas/bali/*.py → BALI)
        2. Directory patterns (substrate/ → based on purpose)
        3. File name patterns
        """
        dry_run = "--dry-run" in args
        as_json = "--json" in args

        # Get ungoverned files
        report = audit()
        ungoverned = report["ungoverned_list"]

        if not ungoverned:
            print("✅ No ungoverned files - governance is watertight!")
            return 0

        print(f"\n{'=' * 60}")
        print(f"  FIX-ALL: {len(ungoverned)} ungoverned files")
        print(f"{'=' * 60}")

        if dry_run:
            print("  [DRY-RUN MODE - No changes will be made]\n")

        # Heuristic mapping
        fixed = []
        failed = []

        for file_path in ungoverned:
            mahajana = self._determine_mahajana(file_path)

            if dry_run:
                print(f"  {file_path} → {mahajana.value.upper()}")
                fixed.append({"path": file_path, "owner": mahajana.value})
            else:
                # Actually assign
                result = self.cmd_assign([file_path, mahajana.value])
                if result == 0:
                    fixed.append({"path": file_path, "owner": mahajana.value})
                else:
                    failed.append(file_path)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"  SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Fixed: {len(fixed)}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print(f"\n  Failed files:")
            for f in failed:
                print(f"    - {f}")

        if as_json:
            print(json.dumps({"fixed": fixed, "failed": failed}, indent=2))

        return 0 if not failed else 1

    def _determine_mahajana(self, file_path: str) -> Mahajana:
        """
        Determine which Mahajana should own a file based on heuristics.

        Priority:
        1. Explicit folder (mahajanas/bali/*.py → BALI)
        2. Substrate patterns
        3. Name patterns
        4. Default
        """
        path_lower = file_path.lower()

        # 1. Explicit Mahajana folder
        for m in Mahajana:
            if f"mahajanas/{m.value}/" in path_lower or f"mahajanas/{m.value}\\" in path_lower:
                return m

        # 2. Substrate patterns
        substrate_map = {
            "balarama": Mahajana.BALI,  # Balarama = Bali's service
            "cli_substrate": Mahajana.NARADA,  # CLI = communication
            "graph": Mahajana.KAPILA,  # Graph = analysis
            "lotus": Mahajana.BRAHMA,  # Lotus = creation
            "acintya": Mahajana.SHUKA,  # Acintya = vision/knowledge
            "mantra": Mahajana.NARADA,  # Mantra = sacred sound/communication
            "gpu": Mahajana.JANAKA,  # GPU = execution
            "cpu": Mahajana.JANAKA,  # CPU = execution
            "resonance": Mahajana.NARADA,  # Resonance = vibration/communication
        }

        for pattern, mahajana in substrate_map.items():
            if pattern in path_lower:
                return mahajana

        # 3. Root mahajanas files
        root_map = {
            "router": Mahajana.NARADA,
            "parampara": Mahajana.BHISHMA,
            "vishnu": Mahajana.BRAHMA,  # Vishnu protocol
            "adoption": Mahajana.BRAHMA,
            "discovery": Mahajana.SHUKA,
            "vyuha": Mahajana.BRAHMA,
            "protocol": Mahajana.YAMARAJA,
            "sabha": Mahajana.MANU,
        }

        for pattern, mahajana in root_map.items():
            if pattern in path_lower:
                return mahajana

        # 4. Security/validation → YAMARAJA
        if "security" in path_lower or "validation" in path_lower:
            return Mahajana.YAMARAJA

        # 5. Cognition/samkhya → KAPILA
        if "cognition" in path_lower or "samkhya" in path_lower:
            return Mahajana.KAPILA

        # 6. Default based on current distribution (pick least loaded)
        report = audit()
        dist = report["owner_distribution"]
        min_count = min(dist.values()) if dist else 0
        for m in Mahajana:
            if dist.get(m.value, 0) == min_count:
                return m

        return Mahajana.PRAHLADA  # Ultimate fallback
