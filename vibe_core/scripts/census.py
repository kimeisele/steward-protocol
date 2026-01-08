#!/usr/bin/env python3
"""
CENSUS: THE REALITY CHECK (92% REVEAL)
======================================
"Pratyaksha" - Direct Observation. No Bullshit.

This script scans the runtime memory to see what is ACTUALLY there.
It does NOT assume protocol inheritance.
It checks for method signatures (Shapes).

Output:
- The list of UNWRAPPED (Asuric) Services.
- The Structural Match Score (Can we force-wrap them?).
- The Status of the Arsenal (UnifiedRegistry).
"""

import inspect
import logging
from typing import Any, Dict, List, Set, Tuple

# Import the Registry directly (The Truth)
from vibe_core.di import ServiceRegistry
from vibe_core.unified_registry import ToolCapabilityAdapter, UnifiedRegistry

# Logging setup (Hard Console Output)
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger("CENSUS")


def analyze_shape(instance: Any) -> List[str]:
    """Returns a list of Protocol Candidates based on methods present."""
    try:
        methods = {m[0] for m in inspect.getmembers(instance, predicate=inspect.ismethod)}
    except Exception:
        # Some objects might fail inspection
        return []

    candidates = []

    # 1. READ/WRITE (Config, State)
    if {"read", "write"}.issubset(methods) or {"get", "set"}.issubset(methods):
        candidates.append("ReadWriteProtocol")

    # 2. SYNC (Ledger, Git)
    # also check for 'is_synced' or 'get_sync_status'
    if {"sync"}.intersection(methods) or {"pull", "push"}.intersection(methods) or {"commit"}.intersection(methods):
        candidates.append("SyncProtocol")

    # 3. ENFORCE (Security)
    if (
        {"check", "enforce"}.issubset(methods)
        or {"validate", "verify"}.intersection(methods)
        or {"has_capability"}.intersection(methods)
    ):
        candidates.append("EnforceProtocol")

    # 4. INFER (AI)
    if {"infer", "predict", "classify", "route"}.intersection(methods):
        candidates.append("InferProtocol")

    # 5. STORE (DB)
    if (
        {"store", "recall"}.issubset(methods)
        or {"save", "load"}.issubset(methods)
        or {"record_event"}.intersection(methods)
    ):
        candidates.append("StoreRecallProtocol")

    return candidates


def run_service_census():
    print("\n💀 VIBE CITY CENSUS - THE 92% REPORT (SERVICES) 💀")
    print("=====================================================")

    services = ServiceRegistry.list_services()
    total = len(services)

    if total == 0:
        print("❌ REGISTRY EMPTY. The system is dead or mocks are missing.")
        return

    wrapped_count = 0
    adaptable_count = 0
    hopeless_count = 0

    print(f"\nScanning {total} Services in Memory...\n")
    print(f"{'SERVICE ID':<40} | {'STATUS':<15} | {'SHAPE (Potenzial)'}")
    print("-" * 100)

    for name, type_name in services.items():
        with ServiceRegistry._lock:
            instance = ServiceRegistry._services.get(name)

        if not instance:
            continue

        # Check 1: Is it already Mantra-Wrapped? (Satya)
        is_wrapped = "Mantra" in type(instance).__name__

        # Check 2: Structural Analysis (Duck Typing)
        shapes = analyze_shape(instance)

        status = "✅ WRAPPED" if is_wrapped else "⚠️  NAKED"
        if not is_wrapped and not shapes:
            status = "❌ OPAQUE"
            hopeless_count += 1
        elif not is_wrapped:
            adaptable_count += 1
        else:
            wrapped_count += 1

        print(f"{name:<40} | {status:<15} | {', '.join(shapes) if shapes else 'Unknown Blob'}")

    print("\n==========================================")
    print(f"TOTAL SERVICES: {total}")
    print(f"SATYA (Wrapped): {wrapped_count} ({(wrapped_count / total) * 100:.1f}%)")
    print(f"RAJAS (Adaptable): {adaptable_count} ({(adaptable_count / total) * 100:.1f}%) <- TARGET FOR SUDARSHANA 2.0")
    print(f"TAMAS (Opaque):    {hopeless_count} ({(hopeless_count / total) * 100:.1f}%) <- THE DANGER ZONE")
    print("==========================================\n")


def run_arsenal_census():
    print("\n⚔️  ARSENAL CENSUS - THE WEAPONS REPORT (TOOLS) ⚔️")
    print("====================================================")

    registry = UnifiedRegistry.get_instance()
    try:
        total = registry.discover_all()
    except Exception as e:
        print(f"❌ DISCOVERY FAILED: {e}")
        return

    wrapped_count = 0
    naked_count = 0

    print(f"\nScanning {total} Capabilities...\n")
    print(f"{'CAPABILITY ID':<40} | {'STATUS':<15} | {'TYPE'}")
    print("-" * 100)

    # Access capabilities directly
    for cap_id, adapter in registry._capabilities.items():
        is_wrapped = False
        cap_type = "Unknown"

        if isinstance(adapter, ToolCapabilityAdapter):
            tool = adapter.tool
            cap_type = "Tool"
            if "Mantra" in type(tool).__name__:
                is_wrapped = True
        elif hasattr(adapter, "capability_type"):
            cap_type = str(adapter.capability_type)

        status = "✅ WRAPPED" if is_wrapped else "⚠️  NAKED"
        if is_wrapped:
            wrapped_count += 1
        else:
            naked_count += 1

        print(f"{cap_id:<40} | {status:<15} | {cap_type}")

    total_scanned = wrapped_count + naked_count
    if total_scanned > 0:
        print("\n==========================================")
        print(f"TOTAL WEAPONS: {total_scanned}")
        print(f"CONSECRATED: {wrapped_count} ({(wrapped_count / total_scanned) * 100:.1f}%)")
        print(f"MUNDANE:     {naked_count} ({(naked_count / total_scanned) * 100:.1f}%)")
        print("==========================================\n")


if __name__ == "__main__":
    run_service_census()
    run_arsenal_census()
