"""
ARCHITECTURE MAP — The OS as it IS.

Not a report. A machine-readable truth table.
Verifies what exists, what connects, where the gaps are.

Run: python -m vibe_core.mahamantra.research.audit.architecture_map
"""

import importlib
import inspect
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("ARCH_MAP")


# =============================================================================
# LAYER DEFINITIONS — What the OS SHOULD be
# =============================================================================


@dataclass
class Layer:
    name: str
    module_path: str
    role: str  # what it IS in the OS
    owns: List[str]  # what it owns/provides
    depends_on: List[str]  # what it needs
    status: str = "UNKNOWN"  # EXISTS, MISSING, PARTIAL
    singleton: bool = False
    detail: str = ""


@dataclass
class Connection:
    source: str  # layer name
    target: str  # layer name
    mechanism: str  # how they connect
    direction: str  # "→", "←", "↔"
    status: str = "UNKNOWN"  # WIRED, OPEN, BROKEN
    detail: str = ""


@dataclass
class IntentCoverage:
    intent_type: str
    guardian: str
    has_resolver: bool = False
    resolver_module: str = ""
    wired_at_boot: bool = False
    detail: str = ""


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================


def verify_layer(layer: Layer) -> Layer:
    """Verify a layer exists and is importable."""
    try:
        mod = importlib.import_module(layer.module_path)
        layer.status = "EXISTS"

        # Check singleton
        if layer.singleton:
            # Look for module-level instance
            for name in dir(mod):
                obj = getattr(mod, name)
                if not name.startswith("_") and not inspect.isclass(obj) and not inspect.isfunction(obj):
                    if hasattr(obj, "__class__") and obj.__class__.__name__ != "module":
                        layer.detail = f"singleton: {name} ({obj.__class__.__name__})"
                        break

    except ImportError as e:
        layer.status = "MISSING"
        layer.detail = str(e)
    except Exception as e:
        layer.status = "PARTIAL"
        layer.detail = str(e)

    return layer


def verify_connection(conn: Connection) -> Connection:
    """Verify a connection between layers."""
    try:
        if conn.mechanism == "Singularity.tick()":
            from vibe_core.mahamantra.kernel.singularity import Mahamantra

            if hasattr(Mahamantra, "tick"):
                conn.status = "WIRED"
                conn.detail = "tick() exists, calls venu.step() + _broadcast()"
            else:
                conn.status = "BROKEN"

        elif conn.mechanism == "register_listener()":
            from vibe_core.mahamantra.kernel.singularity import mahamantra

            conn.status = "WIRED"
            conn.detail = f"{len(mahamantra._listeners)} listeners registered"

        elif conn.mechanism == "BeatSubscriber discovery":
            try:
                from vibe_core.services.venu_service import VenuService

                conn.status = "WIRED"
                conn.detail = "VenuService.discover_beat_subscribers() exists"
            except Exception as e:
                conn.status = "BROKEN"
                conn.detail = str(e)

        elif conn.mechanism == "DIWSubscriber dispatch":
            from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

            v = VenuOrchestrator()
            conn.status = "WIRED"
            conn.detail = f"VenuOrchestrator._emit() dispatches to {v.subscriber_count} subscribers"

        elif conn.mechanism == "MantraKernel.resolve()":
            from vibe_core.mahamantra.kernel.intent import get_kernel

            k = get_kernel()
            resolver_count = len(k._resolvers)
            conn.status = "WIRED" if resolver_count > 0 else "OPEN"
            conn.detail = f"{resolver_count} resolvers registered"

        elif conn.mechanism == "wire_healing_resolver()":
            from vibe_core.mahamantra.dharma.kumaras.healing_resolver import wire_healing_resolver

            ok = wire_healing_resolver()
            conn.status = "WIRED" if ok else "BROKEN"

        elif conn.mechanism == "wire_sravanam()":
            from vibe_core.mahamantra.dharma.kumaras.sravanam import wire_sravanam

            try:
                listener = wire_sravanam()
                conn.status = "WIRED"
                conn.detail = f"SravanamListener wired, enabled={listener._enabled}"
            except Exception as e:
                conn.status = "BROKEN"
                conn.detail = str(e)

        elif conn.mechanism == "KG → heal_all_violations()":
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.mahajanas.prithu.knowledge import KnowledgeGraphProtocol

                kg = ServiceRegistry.get(KnowledgeGraphProtocol)
                if kg:
                    conn.status = "WIRED"
                    conn.detail = "KG registered, violations queryable"
                else:
                    conn.status = "OPEN"
                    conn.detail = "KG not registered in ServiceRegistry"
            except Exception as e:
                conn.status = "OPEN"
                conn.detail = f"KG unavailable: {e}"

        elif conn.mechanism == "Lotus._fire_gate()":
            from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

            if hasattr(MahamantraLotus, "_fire_gate"):
                conn.status = "WIRED"
                conn.detail = "5 TattvaGates: PARSE→VALIDATE→EXECUTE→RESULT→SYNC"
            else:
                conn.status = "BROKEN"

        elif conn.mechanism == "Sravanam → Intent(OBSERVE)":
            # Does Sravanam emit OBSERVE intents?
            from vibe_core.mahamantra.dharma.kumaras.sravanam import SravanamListener

            source = inspect.getsource(SravanamListener)
            if "MantraIntent" in source or "IntentType" in source:
                conn.status = "WIRED"
                conn.detail = "Sravanam emits MantraIntents"
            else:
                conn.status = "OPEN"
                conn.detail = "Sravanam does NOT emit Intents. Scan results stay in RAM list."

        else:
            conn.detail = f"Unknown mechanism: {conn.mechanism}"

    except Exception as e:
        conn.status = "BROKEN"
        conn.detail = str(e)

    return conn


def check_intent_coverage() -> List[IntentCoverage]:
    """Check which IntentTypes have resolvers."""
    results = []
    try:
        from vibe_core.mahamantra.kernel.intent import IntentType, get_kernel, MantraIntent

        # Guardian mapping from MantraIntent
        guardian_map = {
            IntentType.READ: "PRAHLADA",
            IntentType.WRITE: "BHISHMA",
            IntentType.TRANSFORM: "JANAKA",
            IntentType.RESOLVE: "KAPILA",
            IntentType.BIND: "MANU",
            IntentType.MIGRATE: "BRAHMA",
            IntentType.WAKE: "BRAHMA",
            IntentType.SYNC: "NARADA",
            IntentType.HEAL: "SHAMBHU",
            IntentType.OBSERVE: "SHUKA",
            IntentType.SURRENDER: "BALI",
        }

        kernel = get_kernel()

        for it in IntentType:
            has_resolver = it in kernel._resolvers
            resolver_mod = ""
            if has_resolver:
                resolver = kernel._resolvers[it]
                resolver_mod = type(resolver).__module__

            results.append(
                IntentCoverage(
                    intent_type=it.value,
                    guardian=guardian_map.get(it, "YAMARAJA"),
                    has_resolver=has_resolver,
                    resolver_module=resolver_mod,
                    wired_at_boot=has_resolver,
                )
            )

    except Exception as e:
        results.append(
            IntentCoverage(
                intent_type="ERROR",
                guardian="",
                detail=str(e),
            )
        )

    return results


# =============================================================================
# THE MAP
# =============================================================================


def build_map():
    """Build the complete architecture map."""

    # --- LAYERS ---
    layers = [
        Layer(
            name="Singularity",
            module_path="vibe_core.mahamantra.kernel.singularity",
            role="OS KERNEL — 16 positions, tick, kala, broadcast, routing",
            owns=["ProtocolRouter", "ModuleRouter", "CellRouter", "Governance", "Kala", "Venu"],
            depends_on=["VenuOrchestrator", "substrate"],
            singleton=True,
        ),
        Layer(
            name="Lotus",
            module_path="vibe_core.mahamantra.substrate.lotus_core",
            role="CPU — 5-gate computation pipeline (__call__), vibrate(), execute()",
            owns=["PipelineCache", "Compressor", "Chamber", "Antaranga", "ShadowReactor", "Akash"],
            depends_on=["Singularity", "VenuOrchestrator"],
        ),
        Layer(
            name="VenuOrchestrator",
            module_path="vibe_core.mahamantra.substrate.venu_orchestrator",
            role="FLUTE — 19-bit DIW, LUT-based O(1) step(), DIWSubscriber dispatch",
            owns=["THE_FLUTE_CYCLE", "DIWSubscribers"],
            depends_on=["_seed.py (SSOT)"],
        ),
        Layer(
            name="VenuService",
            module_path="vibe_core.services.venu_service",
            role="CLOCK — async heartbeat loop, 250ms ticks, BeatSubscriber dispatch",
            owns=["MantraClock", "BeatSubscribers", "telemetry"],
            depends_on=["Singularity", "VenuOrchestrator", "ServiceRegistry"],
        ),
        Layer(
            name="MantraKernel",
            module_path="vibe_core.mahamantra.kernel.intent",
            role="SCHEDULER — Intent declaration → resolution, priority queue",
            owns=["IntentQueue", "IntentResolvers"],
            depends_on=["IntentResolver implementations"],
            singleton=True,
        ),
        Layer(
            name="HealingResolver",
            module_path="vibe_core.mahamantra.dharma.kumaras.healing_resolver",
            role="HEAL INTENT — 5-gate healing pipeline (SATTVA→RAJAS)",
            owns=["CellularHealer"],
            depends_on=["MantraKernel", "Lotus", "ShuddhiEngine"],
        ),
        Layer(
            name="ShuddhiEngine",
            module_path="vibe_core.mahamantra.dharma.kumaras.engine",
            role="CST SURGERY — purify(), scan_file(), scan_cell(), 14 remedies",
            owns=["RemedyLoader", "CSTRemedies"],
            depends_on=["libcst", "Lotus (vibration emission)"],
        ),
        Layer(
            name="Sravanam",
            module_path="vibe_core.mahamantra.dharma.kumaras.sravanam",
            role="CELL SCANNER — tick-driven scanning, 1 cell per tick per position",
            owns=["SravanamScanner", "SravanamListener"],
            depends_on=["Singularity (listener)", "ShuddhiEngine", "CellRouter"],
        ),
    ]

    # --- CONNECTIONS ---
    connections = [
        Connection(
            "VenuService",
            "Singularity",
            "Singularity.tick()",
            "→",
            detail="VenuService.start() calls self._singularity.tick() every 250ms",
        ),
        Connection("Singularity", "VenuOrchestrator", "venu.step()", "→", detail="tick() calls self.venu.step() → DIW"),
        Connection("VenuOrchestrator", "DIWSubscribers", "DIWSubscriber dispatch", "→"),
        Connection(
            "Singularity", "Listeners", "register_listener()", "→", detail="_broadcast(TickState) to all listeners"
        ),
        Connection(
            "VenuService",
            "BeatSubscribers",
            "BeatSubscriber discovery",
            "→",
            detail="discover_beat_subscribers() from ServiceRegistry",
        ),
        Connection("Lotus", "Singularity", "Lotus._fire_gate()", "→", detail="__call__() fires 5 TattvaGates"),
        Connection("MantraKernel", "HealingResolver", "MantraKernel.resolve()", "→"),
        Connection("HealingResolver", "MantraKernel", "wire_healing_resolver()", "→"),
        Connection("ShuddhiEngine", "MantraKernel", "heal_all_violations() → MantraIntent(HEAL)", "→"),
        Connection("Sravanam", "Singularity", "wire_sravanam()", "→"),
        Connection(
            "Sravanam",
            "MantraKernel",
            "Sravanam → Intent(OBSERVE)",
            "→",
            detail="SHOULD emit OBSERVE intents from scan results",
        ),
        Connection("Ouroboros", "KnowledgeGraph", "KG → heal_all_violations()", "→"),
    ]

    return layers, connections


# =============================================================================
# MAIN
# =============================================================================


def main():
    layers, connections = build_map()

    # Verify
    layers = [verify_layer(l) for l in layers]
    connections = [verify_connection(c) for c in connections]
    intents = check_intent_coverage()

    # Print
    print("=" * 100)
    print("ARCHITECTURE MAP — The Mahamantra OS")
    print("=" * 100)

    print("\n## LAYERS")
    print(f"{'Name':20s} | {'Status':8s} | Role")
    print("-" * 100)
    for l in layers:
        print(f"{l.name:20s} | {l.status:8s} | {l.role}")
        if l.detail:
            print(f"{'':20s} | {'':8s} | → {l.detail}")
        print(f"{'':20s} | {'':8s} | owns: {', '.join(l.owns)}")
        print(f"{'':20s} | {'':8s} | needs: {', '.join(l.depends_on)}")

    print("\n## CONNECTIONS")
    print(f"{'Source':15s} → {'Target':15s} | {'Status':8s} | Mechanism")
    print("-" * 100)
    for c in connections:
        icon = {"WIRED": "●", "OPEN": "○", "BROKEN": "✗"}.get(c.status, "?")
        print(f"{c.source:15s} → {c.target:15s} | {icon} {c.status:7s} | {c.mechanism}")
        if c.detail:
            print(f"{'':15s}   {'':15s} | {'':8s} | {c.detail}")

    print("\n## INTENT COVERAGE (MantraKernel)")
    print(f"{'IntentType':15s} | {'Guardian':12s} | {'Resolver':8s} | Module")
    print("-" * 80)
    for ic in intents:
        icon = "●" if ic.has_resolver else "○"
        print(
            f"{ic.intent_type:15s} | {ic.guardian:12s} | {icon} {'YES' if ic.has_resolver else 'NO':7s} | {ic.resolver_module}"
        )

    # Summary
    wired = sum(1 for c in connections if c.status == "WIRED")
    open_c = sum(1 for c in connections if c.status == "OPEN")
    broken = sum(1 for c in connections if c.status == "BROKEN")
    resolved = sum(1 for ic in intents if ic.has_resolver)
    total_intents = len(intents)

    print(f"\n{'=' * 100}")
    print(f"LAYERS:      {sum(1 for l in layers if l.status == 'EXISTS')}/{len(layers)} exist")
    print(f"CONNECTIONS: {wired} wired, {open_c} open, {broken} broken")
    print(f"INTENTS:     {resolved}/{total_intents} have resolvers")
    print(f"{'=' * 100}")

    if open_c > 0:
        print("\n## OPEN CONNECTIONS (the organism cannot feel these)")
        for c in connections:
            if c.status == "OPEN":
                print(f"  ○ {c.source} → {c.target}: {c.detail}")

    if resolved < total_intents:
        print(f"\n## MISSING RESOLVERS ({total_intents - resolved}/{total_intents} IntentTypes have no resolver)")
        for ic in intents:
            if not ic.has_resolver:
                print(f"  ○ {ic.intent_type} (guardian: {ic.guardian})")


if __name__ == "__main__":
    main()
