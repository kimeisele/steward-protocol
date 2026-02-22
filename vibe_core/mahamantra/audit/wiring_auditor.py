"""
WIRING AUDITOR - Architectural Integrity Enforcement
=====================================================

Verifies that the system's wiring contracts are intact:
- bootstrap() calls the right functions
- boot_orchestrator does NOT duplicate bootstrap work
- Kernel internals use raw services, not proxies
- ReactorLoop reads state, does not drive ticks
- No split-brain (shared singletons, shared event bus)

Each check uses inspect.getsource() to verify source-level contracts.
This is static analysis, not runtime testing.

Implements AuditorProtocol: class Auditor + run_audit() → List[AuditFinding].
Auto-discovered by AuditDispatcher via __position__ + Auditor class.
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 4  # Fifth auditor to run (after hygiene at 3)
__genesis__ = "0x8fd1e5e1"  # GenesisByte: parampara % 37 == 0

import inspect
import logging
from typing import List

from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity

logger = logging.getLogger("AUDIT.WIRING")


def _source_of(cls_or_fn, method_name: str = "") -> str:
    """Get source code of a class method or function."""
    target = getattr(cls_or_fn, method_name) if method_name else cls_or_fn
    return inspect.getsource(target)


def _finding(description: str, severity: FindingSeverity = FindingSeverity.CRITICAL) -> AuditFinding:
    return AuditFinding(
        source="wiring_auditor",
        position=__position__,
        mahajana=__mahajana__,
        description=description,
        severity=severity,
    )


class Auditor:
    """Wiring Auditor — verifies architectural contracts via source inspection."""

    def run_audit(self) -> List[AuditFinding]:
        findings: List[AuditFinding] = []
        findings.extend(self._check_bootstrap_wiring())
        findings.extend(self._check_boot_orchestrator_no_duplication())
        findings.extend(self._check_reactor_loop())
        findings.extend(self._check_kernel_raw_services())
        findings.extend(self._check_shared_eventbus())
        findings.extend(self._check_input_routing())
        findings.extend(self._check_boot_inversion())
        return findings

    # =========================================================================
    # BOOTSTRAP WIRING
    # =========================================================================

    def _check_bootstrap_wiring(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        source = _source_of(MahamantraLotus, "bootstrap")

        required = {
            "wire_gate_providers": "Gate providers must be wired at boot",
            "wire_healing_resolver": "HealingIntentResolver must be wired at boot",
            "auto_wrap_services": "Balarama Pattern must be wired at boot",
            "adopt_services": "Orbital reactor mounting must happen at boot",
            "wire_sravanam": "Sravanam listener must be wired at boot",
            "register_governance_hook": "Sudarshana governance must be registered at boot",
        }
        for token, msg in required.items():
            if token not in source:
                findings.append(_finding(f"bootstrap() missing {token}: {msg}"))

        return findings

    # =========================================================================
    # BOOT ORCHESTRATOR — must NOT duplicate bootstrap work
    # =========================================================================

    def _check_boot_orchestrator_no_duplication(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.boot_orchestrator import BootOrchestrator

        # _act_wire_gate_providers must NOT re-import wire_gate_providers
        try:
            src = _source_of(BootOrchestrator, "_act_wire_gate_providers")
            if "from vibe_core.mahamantra.substrate.gate_providers import wire_gate_providers" in src:
                findings.append(_finding(
                    "_act_wire_gate_providers() re-imports wire_gate_providers — should only verify"
                ))
        except AttributeError:
            pass

        # _act_wire_sravanam must NOT call wire_sravanam()
        try:
            src = _source_of(BootOrchestrator, "_act_wire_sravanam")
            if "wire_sravanam()" in src:
                findings.append(_finding(
                    "_act_wire_sravanam() still calls wire_sravanam() — should only verify"
                ))
        except AttributeError:
            pass

        # _act_register_governance_hook must NOT re-import register_governance_hook
        try:
            src = _source_of(BootOrchestrator, "_act_register_governance_hook")
            if "from vibe_core.protocols.substrate.mantra_protocol import register_governance_hook" in src:
                findings.append(_finding(
                    "_act_register_governance_hook() re-imports — should only verify"
                ))
        except AttributeError:
            pass

        # Ingestion must stay in boot_orchestrator (too expensive for bootstrap)
        try:
            src = _source_of(BootOrchestrator, "_act_ingest_codebase")
            if "parse_file_to_fragments" not in src:
                findings.append(_finding(
                    "_act_ingest_codebase() no longer does ingestion — must stay in boot_orchestrator"
                ))
        except AttributeError:
            pass

        return findings

    # =========================================================================
    # REACTOR LOOP — consumer, not driver
    # =========================================================================

    def _check_reactor_loop(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.mahamantra.reactor.loop import ReactorLoop

        # _meditate must use get_tick() (read), not tick() (advance)
        src = _source_of(ReactorLoop, "_meditate")
        if "get_tick()" not in src:
            findings.append(_finding("_meditate() does not call get_tick() — must READ, not advance"))
        if "_singularity.tick()" in src:
            findings.append(_finding("_meditate() calls _singularity.tick() — would DOUBLE-TICK"))

        # _process_request must use Clock, not hardcoded 'unknown'
        src = _source_of(ReactorLoop, "_process_request")
        if "get_tick_info" not in src:
            findings.append(_finding("_process_request() does not use get_tick_info()"))
        if '"unknown"' in src:
            findings.append(_finding('_process_request() has hardcoded "unknown" values'))

        # _init_bus must use get_event_bus(), not EventBus()
        src = _source_of(ReactorLoop, "_init_bus")
        if "get_event_bus" not in src:
            findings.append(_finding("_init_bus() does not call get_event_bus()"))
        if "EventBus()" in src:
            findings.append(_finding("_init_bus() creates EventBus() directly — split-brain"))

        return findings

    # =========================================================================
    # KERNEL — raw services, not proxies
    # =========================================================================

    def _check_kernel_raw_services(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.kernel_impl import RealVibeKernel

        # _init_mahajana_services must set _raw_* attributes
        src = _source_of(RealVibeKernel, "_init_mahajana_services")
        for name in ("_raw_brahma", "_raw_bhishma", "_raw_janaka", "_raw_bali", "_raw_kapila"):
            if name not in src:
                findings.append(_finding(f"_init_mahajana_services() missing {name}"))

        # Key methods must use _raw_*, not self.brahma (proxy)
        for method_name in ("get_agent_capabilities", "register_agent", "get_status", "boot_async"):
            try:
                src = _source_of(RealVibeKernel, method_name)
                if "self.brahma." in src or "self.bhishma." in src:
                    findings.append(_finding(
                        f"{method_name}() uses proxy (self.brahma/bhishma) — must use _raw_*"
                    ))
            except AttributeError:
                pass

        # factory.py must register _raw_* in PositionRegistry
        from vibe_core.factory import VibeFactory
        src = _source_of(VibeFactory, "get_kernel")
        if "_raw_brahma" not in src:
            findings.append(_finding("factory.py does not reference _raw_brahma"))

        # kernel_ops must use _raw_brahma
        from vibe_core.protocols.mahajanas.manu.types import kernel_ops
        src = inspect.getsource(kernel_ops)
        if "_raw_brahma" not in src:
            findings.append(_finding("kernel_ops.py does not reference _raw_brahma"))

        return findings

    # =========================================================================
    # SHARED EVENT BUS — no split-brain
    # =========================================================================

    def _check_shared_eventbus(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.boot_orchestrator import BootOrchestrator

        src = _source_of(BootOrchestrator, "__init__")
        if "get_event_bus" not in src:
            findings.append(_finding("BootOrchestrator.__init__ does not call get_event_bus()"))

        return findings

    # =========================================================================
    # INPUT ROUTING — all through lotus.execute()
    # =========================================================================

    def _check_input_routing(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.boot_orchestrator import BootOrchestrator

        src = _source_of(BootOrchestrator, "_execute_intent")
        if "_lotus.execute(" not in src:
            findings.append(_finding("_execute_intent() does not call lotus.execute()"))
        if "IntentType.QUERY" in src:
            findings.append(_finding("_execute_intent() has hardcoded QUERY handling"))
        if "IntentType.DELEGATION" in src:
            findings.append(_finding("_execute_intent() has hardcoded DELEGATION handling"))
        if "IntentType.CONTROL" not in src:
            findings.append(_finding("_execute_intent() lost CONTROL handling"))

        return findings

    # =========================================================================
    # BOOT INVERSION — mahamantra boots BEFORE legacy kernel
    # =========================================================================

    def _check_boot_inversion(self) -> List[AuditFinding]:
        findings = []
        from vibe_core.boot_orchestrator import BootOrchestrator

        # Must have _orient_mahamantra
        if not hasattr(BootOrchestrator, "_orient_mahamantra"):
            findings.append(_finding("BootOrchestrator missing _orient_mahamantra()"))
        else:
            src = _source_of(BootOrchestrator, "_orient_mahamantra")
            if "_lotus.bootstrap(" not in src:
                findings.append(_finding("_orient_mahamantra() does not call bootstrap()"))

        # _orient must call mahamantra BEFORE akasha
        try:
            src = _source_of(BootOrchestrator, "_orient")
            m_pos = src.index("_orient_mahamantra")
            a_pos = src.index("_orient_akasha")
            if m_pos > a_pos:
                findings.append(_finding("_orient() calls akasha before mahamantra — Boot Inversion broken"))
        except (AttributeError, ValueError):
            pass

        # _init_sharanagati must be idempotent
        from vibe_core.kernel_impl import RealVibeKernel
        src = _source_of(RealVibeKernel, "_init_sharanagati")
        if "_bootstrapped" not in src:
            findings.append(_finding("_init_sharanagati() does not check _bootstrapped — not idempotent"))

        return findings
