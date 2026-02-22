"""
HEALING LOOP DIAGNOSIS — Why the organism doesn't heal itself.

This is a RUNNABLE diagnostic that traces the actual healing loop
and identifies where it breaks.

Run: python -m vibe_core.mahamantra.research.audit.healing_loop_diagnosis
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("DIAGNOSIS")


@dataclass
class LoopCheck:
    name: str
    status: str  # "CLOSED", "OPEN", "BROKEN"
    detail: str


def check_sravanam_output() -> LoopCheck:
    """Does Sravanam's scan output go anywhere?"""
    try:
        from vibe_core.mahamantra.dharma.kumaras.sravanam import SravanamListener
        import inspect

        source = inspect.getsource(SravanamListener)

        # Check if scan results are stored, emitted, or fed back
        feeds_kg = "knowledge" in source.lower() or "kg" in source.lower()
        feeds_ouroboros = "ouroboros" in source.lower() or "ingest" in source.lower()
        feeds_task = "task" in source.lower()
        emits_event = "event" in source.lower() or "emit" in source.lower()

        if feeds_kg or feeds_ouroboros:
            return LoopCheck("sravanam→KG", "CLOSED", "Scan results feed into Knowledge Graph")
        elif feeds_task:
            return LoopCheck("sravanam→tasks", "CLOSED", "Scan results create tasks")
        elif emits_event:
            return LoopCheck("sravanam→events", "CLOSED", "Scan results emitted as events")
        else:
            return LoopCheck(
                "sravanam→???",
                "OPEN",
                "Sravanam scans cells but results are NOT stored, NOT fed to KG, NOT emitted. "
                "Detection results vanish.",
            )
    except Exception as e:
        return LoopCheck("sravanam", "BROKEN", f"Cannot inspect: {e}")


def check_shuddhi_subscriber_dryrun() -> LoopCheck:
    """Is ShuddhiSubscriber actually healing or just dry-running?"""
    try:
        from vibe_core.services.healing_subscribers import ShuddhiSubscriber

        sub = ShuddhiSubscriber()
        if sub._dry_run:
            return LoopCheck(
                "shuddhi_subscriber.dry_run",
                "OPEN",
                f"ShuddhiSubscriber._dry_run={sub._dry_run} — it NEVER writes healed code. "
                "The healing loop produces diffs but discards them.",
            )
        return LoopCheck("shuddhi_subscriber.dry_run", "CLOSED", "dry_run=False, healing is live")
    except Exception as e:
        return LoopCheck("shuddhi_subscriber", "BROKEN", f"Cannot import: {e}")


def check_ouroboros_feeds_kg() -> LoopCheck:
    """Does OuroborosSubscriber actually feed violations into KG?"""
    try:
        from vibe_core.services.healing_subscribers import OuroborosSubscriber

        sub = OuroborosSubscriber()
        # Check if it can resolve workspace
        workspace = sub._resolve_workspace()
        if workspace is None:
            return LoopCheck(
                "ouroboros→KG",
                "OPEN",
                "OuroborosSubscriber cannot resolve workspace (no kernel in ServiceRegistry). "
                "Without workspace, it cannot find CI artifacts to ingest.",
            )
        return LoopCheck("ouroboros→KG", "CLOSED", f"Workspace resolved: {workspace}")
    except Exception as e:
        return LoopCheck("ouroboros→KG", "BROKEN", f"Cannot check: {e}")


def check_kg_has_violations() -> LoopCheck:
    """Does the Knowledge Graph actually contain violations?"""
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol

        kg = ServiceRegistry.get(KnowledgeGraphProtocol)
        if kg is None:
            return LoopCheck(
                "KG.violations",
                "OPEN",
                "KnowledgeGraphProtocol not registered in ServiceRegistry. "
                "heal_all_violations() will find 0 violations.",
            )
        violations = kg.get_violations(healed=False)
        return LoopCheck(
            "KG.violations", "CLOSED" if violations else "OPEN", f"{len(violations)} unhealed violations in KG"
        )
    except Exception as e:
        return LoopCheck("KG.violations", "BROKEN", f"Cannot query: {e}")


def check_engine_remedies() -> LoopCheck:
    """How many remedies does the engine actually discover?"""
    try:
        from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine

        engine = ShuddhiEngine()
        remedies = engine.list_remedies()
        healers = []
        detectors = []
        for rid in remedies:
            cls = engine._remedies[rid]
            instance = cls()
            # Check if remedy can actually apply fixes (not just detect)
            # by looking at whether it ever sets self.applied = True
            import inspect

            source = inspect.getsource(cls)
            if "self.applied = True" in source:
                healers.append(rid)
            else:
                detectors.append(rid)

        return LoopCheck(
            "engine.remedies",
            "CLOSED" if healers else "OPEN",
            f"{len(remedies)} total: {len(healers)} healers {healers}, {len(detectors)} detect-only {detectors}",
        )
    except Exception as e:
        return LoopCheck("engine.remedies", "BROKEN", f"Cannot load: {e}")


def check_venu_heartbeat() -> LoopCheck:
    """Is VenuService actually running and dispatching beats?"""
    try:
        from vibe_core.services.beat_discovery import discover_beat_subscribers

        subs = discover_beat_subscribers()
        names = [s.beat_name for s in subs if hasattr(s, "beat_name")]
        if not names:
            return LoopCheck(
                "venu.subscribers", "OPEN", "No BeatSubscribers discovered. The heartbeat has no listeners."
            )
        return LoopCheck("venu.subscribers", "CLOSED", f"{len(names)} subscribers: {names}")
    except Exception as e:
        return LoopCheck("venu.subscribers", "BROKEN", f"Cannot discover: {e}")


def main():
    logging.basicConfig(level=logging.WARNING)

    checks: List[LoopCheck] = [
        check_engine_remedies(),
        check_sravanam_output(),
        check_shuddhi_subscriber_dryrun(),
        check_ouroboros_feeds_kg(),
        check_kg_has_violations(),
        check_venu_heartbeat(),
    ]

    print("=" * 80)
    print("HEALING LOOP DIAGNOSIS — Where does the loop break?")
    print("=" * 80)

    open_count = 0
    broken_count = 0
    for c in checks:
        icon = {"CLOSED": "●", "OPEN": "○", "BROKEN": "✗"}[c.status]
        print(f"\n  {icon} [{c.status:7s}] {c.name}")
        print(f"    {c.detail}")
        if c.status == "OPEN":
            open_count += 1
        elif c.status == "BROKEN":
            broken_count += 1

    print(f"\n{'=' * 80}")
    total = len(checks)
    closed = total - open_count - broken_count
    print(f"Loop integrity: {closed}/{total} closed, {open_count} open, {broken_count} broken")

    if open_count > 0:
        print("\nOPEN LOOPS = healing energy escapes. The organism cannot self-heal.")
        print("Each open loop must be closed for the immune system to function.")

    print("=" * 80)


if __name__ == "__main__":
    main()
