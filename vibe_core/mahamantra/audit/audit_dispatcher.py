"""
AUDIT DISPATCHER - The Conductor of Dharma
===========================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all varieties of religion and just surrender unto Me." (BG 18.66)

THE LAW:
========
    - The Dispatcher routes audit tasks to the correct Mahajana.
    - Routing is based on the __position__ declared in each audit module.
    - It aggregates findings from all auditors into the central AuditRegistry.
    - The filesystem IS the configuration. Adding a new audit file with a
      __position__ automatically wires it into the system.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x..."  # TODO: Add genesis byte

__all__ = ["AuditDispatcher", "get_dispatcher", "AuditorProtocol"]

import importlib
import logging
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol

from vibe_core.mahamantra.audit.audit_registry import AuditFinding, AuditRegistryProtocol, get_registry

logger = logging.getLogger("AUDIT.DISPATCHER")


class AuditorProtocol(Protocol):
    """A protocol defining the interface for a position-specific auditor."""

    def run_audit(self) -> List[AuditFinding]:
        """Execute the audit and return a list of findings."""
        ...


@dataclass
class RegisteredAuditor:
    """Metadata for a discovered auditor."""
    module_path: str
    position: int
    mahajana: str
    instance: AuditorProtocol


class AuditDispatcher:
    """
    Discovers and runs all position-specific auditors, aggregating findings
    into the central AuditRegistry.
    """

    def __init__(self, registry: Optional[AuditRegistryProtocol] = None) -> None:
        self._registry = registry or get_registry()
        self._auditors: Dict[int, RegisteredAuditor] = {}
        self._discovered = False

    def discover_auditors(self) -> None:
        """
        Scan the audit directory and register all valid auditors.
        An auditor is valid if it has a __position__ and an Auditor class.
        """
        if self._discovered:
            return

        import vibe_core.mahamantra.audit as audit_package

        package_path = Path(audit_package.__file__).parent

        for module_info in pkgutil.iter_modules([str(package_path)]):
            if module_info.name.startswith("_"):
                continue

            try:
                module_path = f"vibe_core.mahamantra.audit.{module_info.name}"
                module = importlib.import_module(module_path)

                if hasattr(module, "__position__") and hasattr(module, "Auditor"):
                    position = getattr(module, "__position__")
                    mahajana = getattr(module, "__mahajana__", "unknown")
                    auditor_class = getattr(module, "Auditor")

                    instance = auditor_class()

                    self._auditors[position] = RegisteredAuditor(
                        module_path=module_path,
                        position=position,
                        mahajana=mahajana,
                        instance=instance,
                    )
            except Exception as e:
                logger.warning("Failed to load auditor %s: %s", module_info.name, e)

        self._discovered = True

    def run_all(self) -> None:
        """Run all discovered auditors and register their findings."""
        self.discover_auditors()
        for position, auditor in self._auditors.items():
            try:
                findings = auditor.instance.run_audit()
                for finding in findings:
                    self._registry.register(finding)
            except Exception as e:
                logger.error("Auditor at position %d failed: %s", position, e)

    def run_by_position(self, position: int) -> None:
        """Run a specific auditor by its position."""
        self.discover_auditors()
        auditor = self._auditors.get(position)
        if not auditor:
            raise ValueError(f"No auditor found for position {position}")

        try:
            findings = auditor.instance.run_audit()
            for finding in findings:
                self._registry.register(finding)
        except Exception:
            # TODO: Add logging for failed audit run
            raise

    @property
    def auditors(self) -> Dict[int, RegisteredAuditor]:
        """Return the map of discovered auditors."""
        self.discover_auditors()
        return self._auditors


# Singleton instance
_dispatcher: Optional[AuditDispatcher] = None

def get_dispatcher() -> AuditDispatcher:
    """Get the singleton AuditDispatcher instance."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = AuditDispatcher()
    return _dispatcher
