"""
TÜV Service - NAGA Type Audit Intelligence Implementation.

"Das System wird organisch rot."

This service implements TÜVProtocol:
- Scans files for type leaks (Any, Dict[str, Any], etc.)
- Audits protocol/implementation alignment
- Persists leak registry to JSON
- Tracks churning (value creation)
"""

import ast
import inspect
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from vibe_core.naga.kulika import NagaCapability, NagaLord, naga_service
from vibe_core.naga.services.base import NagaBaseService
from vibe_core.protocols.naga.tuv import (
    ChurnEntry,
    Leak,
    LeakPattern,
    LeakSeverity,
    LeakStatus,
    ProtocolAudit,
    TÜVProtocol,
    TÜVReport,
)

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex

logger = logging.getLogger("NAGA.TÜV")

# Registry file location
TÜV_REGISTRY_PATH = Path(".vibe/state/tuv_registry.json")


@naga_service(
    name="TÜV",
    lord=NagaLord.TÜV,
    drift_source=None,  # Pure audit, no drift handling
    priority=70,  # After infrastructure, before governance actions
    capabilities=[NagaCapability.TYPE_AUDIT, NagaCapability.AUDIT],
    protocol_class="vibe_core.protocols.naga.TÜVProtocol",
)
class TÜVService(NagaBaseService):
    """
    TÜV Audit Intelligence Service.

    Implements TÜVProtocol - not documentation, CODE.
    Auto-discovered by Narada via @naga_service decorator.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        registry_path: Optional[Path] = None,
    ):
        """Initialize TÜV service."""
        super().__init__(service_name="TÜV")
        self._cortex = cortex
        self._registry_path = registry_path or TÜV_REGISTRY_PATH

        # In-memory state (loaded from disk)
        self._leaks: Dict[str, Leak] = {}
        self._churns: List[ChurnEntry] = []
        self._next_id = 1

        # Load existing registry
        self._load_registry()

        logger.info("🔍 TÜV initialized - Type Audit Intelligence active")

    # =========================================================================
    # Persistence
    # =========================================================================

    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self._registry_path.exists():
            return

        try:
            with open(self._registry_path) as f:
                data = json.load(f)

            for leak_data in data.get("leaks", []):
                leak = Leak(
                    id=leak_data["id"],
                    location=leak_data["location"],
                    pattern=LeakPattern(leak_data["pattern"]),
                    severity=LeakSeverity(leak_data["severity"]),
                    status=LeakStatus(leak_data["status"]),
                    description=leak_data["description"],
                    antidote=leak_data["antidote"],
                    detected_at=datetime.fromisoformat(leak_data["detected_at"]),
                    healed_at=(datetime.fromisoformat(leak_data["healed_at"]) if leak_data.get("healed_at") else None),
                )
                self._leaks[leak.id] = leak

            for churn_data in data.get("churns", []):
                self._churns.append(
                    ChurnEntry(
                        date=churn_data["date"],
                        target=churn_data["target"],
                        gift=churn_data["gift"],
                        nektar=churn_data["nektar"],
                        churn_type=churn_data["churn_type"],
                    )
                )

            self._next_id = data.get("next_id", len(self._leaks) + 1)

            logger.debug(f"TÜV: Loaded {len(self._leaks)} leaks from registry")

        except Exception as e:
            logger.warning(f"TÜV: Could not load registry: {e}")

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            self._registry_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "leaks": [leak.to_dict() for leak in self._leaks.values()],
                "churns": [
                    {
                        "date": c.date,
                        "target": c.target,
                        "gift": c.gift,
                        "nektar": c.nektar,
                        "churn_type": c.churn_type,
                    }
                    for c in self._churns
                ],
                "next_id": self._next_id,
                "updated_at": datetime.now().isoformat(),
            }

            with open(self._registry_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.warning(f"TÜV: Could not save registry: {e}")

    # =========================================================================
    # Leak Registry (TÜVProtocol)
    # =========================================================================

    def register_leak(self, leak: Leak) -> str:
        """Register a new leak. Returns leak ID."""
        if not leak.id:
            leak.id = f"LEAK-{self._next_id:03d}"
            self._next_id += 1

        self._leaks[leak.id] = leak
        self._save_registry()

        logger.info(f"TÜV: Registered {leak.id} at {leak.location}")
        return leak.id

    def get_leak(self, leak_id: str) -> Optional[Leak]:
        """Get leak by ID."""
        return self._leaks.get(leak_id)

    def get_leaks(
        self,
        status: Optional[LeakStatus] = None,
        severity: Optional[LeakSeverity] = None,
        pattern: Optional[LeakPattern] = None,
    ) -> List[Leak]:
        """Query leaks with optional filters."""
        result = list(self._leaks.values())

        if status:
            result = [l for l in result if l.status == status]
        if severity:
            result = [l for l in result if l.severity == severity]
        if pattern:
            result = [l for l in result if l.pattern == pattern]

        return result

    def heal_leak(self, leak_id: str, commit_hash: str = "") -> bool:
        """Mark a leak as healed."""
        leak = self._leaks.get(leak_id)
        if not leak:
            return False

        leak.status = LeakStatus.HEALED
        leak.healed_at = datetime.now()

        self._save_registry()
        logger.info(f"TÜV: Healed {leak_id}")
        return True

    # =========================================================================
    # Scanning
    # =========================================================================

    def scan_file(self, filepath: str) -> List[Leak]:
        """Scan a file for type leaks."""
        leaks: List[Leak] = []
        path = Path(filepath)

        if not path.exists() or not path.suffix == ".py":
            return leaks

        try:
            content = path.read_text()
            lines = content.split("\n")

            # Pattern: ": Any" (parameter or return type)
            any_pattern = re.compile(r":\s*Any(?:\s*[,\)\]=]|$)")
            # Pattern: "Dict[str, Any]"
            dict_any_pattern = re.compile(r"Dict\[str,\s*Any\]")
            # Pattern: "-> Any"
            return_any_pattern = re.compile(r"->\s*Any(?:\s*:|$)")

            for i, line in enumerate(lines, 1):
                # Skip TYPE_CHECKING blocks and comments
                if "TYPE_CHECKING" in line or line.strip().startswith("#"):
                    continue
                # Skip intentional decorator patterns
                if "*args: Any" in line or "**kwargs: Any" in line:
                    continue

                location = f"{filepath}:{i}"

                # Check for : Any
                if any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.ANY_PARAM,
                            severity=LeakSeverity.MEDIUM,
                            status=LeakStatus.OPEN,
                            description=f"Any type annotation: {line.strip()[:60]}",
                            antidote="Replace with specific type or Protocol",
                        )
                    )

                # Check for Dict[str, Any]
                if dict_any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.DICT_STR_ANY,
                            severity=LeakSeverity.MEDIUM,
                            status=LeakStatus.OPEN,
                            description=f"Dict[str, Any]: {line.strip()[:60]}",
                            antidote="Replace with TypedDict",
                        )
                    )

                # Check for -> Any return
                if return_any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.ANY_RETURN,
                            severity=LeakSeverity.HIGH,
                            status=LeakStatus.OPEN,
                            description=f"Any return type: {line.strip()[:60]}",
                            antidote="Replace with specific return type",
                        )
                    )

        except Exception as e:
            logger.warning(f"TÜV: Error scanning {filepath}: {e}")

        return leaks

    def scan_module(self, module_path: str) -> List[Leak]:
        """Scan a module (directory) for type leaks."""
        leaks: List[Leak] = []
        path = Path(module_path)

        if not path.exists():
            return leaks

        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            leaks.extend(self.scan_file(str(py_file)))

        return leaks

    def audit_protocol(self, protocol_name: str, service_name: str) -> ProtocolAudit:
        """Audit a protocol against its implementation."""
        audit = ProtocolAudit(
            protocol_name=protocol_name,
            service_name=service_name,
            passed=True,
        )

        try:
            # Dynamic import
            proto_module = __import__(
                "vibe_core.protocols.naga",
                fromlist=[protocol_name],
            )
            proto_cls = getattr(proto_module, protocol_name, None)

            # Try to find service
            svc_cls = None
            for svc_path in [
                f"vibe_core.naga.services.{service_name.lower().replace('service', '')}",
                f"vibe_core.naga.services.{service_name.lower()}",
            ]:
                try:
                    svc_module = __import__(svc_path, fromlist=[service_name])
                    svc_cls = getattr(svc_module, service_name, None)
                    if svc_cls:
                        break
                except ImportError:
                    continue

            if not proto_cls or not svc_cls:
                audit.passed = False
                audit.mismatches.append(f"Could not load {protocol_name} or {service_name}")
                return audit

            # Get protocol methods
            proto_methods = [
                m for m in dir(proto_cls) if not m.startswith("_") and callable(getattr(proto_cls, m, None))
            ]

            for method_name in proto_methods:
                proto_method = getattr(proto_cls, method_name, None)
                svc_method = getattr(svc_cls, method_name, None)

                if svc_method is None:
                    audit.passed = False
                    audit.missing_methods.append(method_name)
                    continue

                try:
                    proto_sig = inspect.signature(proto_method)
                    svc_sig = inspect.signature(svc_method)

                    proto_params = list(proto_sig.parameters.keys())
                    svc_params = list(svc_sig.parameters.keys())

                    if proto_params != svc_params:
                        audit.passed = False
                        audit.mismatches.append(f"{method_name}: {proto_params} != {svc_params}")
                except Exception:
                    pass

        except Exception as e:
            audit.passed = False
            audit.mismatches.append(f"Audit error: {e}")

        return audit

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_report(self) -> TÜVReport:
        """Get full TÜV report."""
        leaks = list(self._leaks.values())
        open_leaks = [l for l in leaks if l.status == LeakStatus.OPEN]
        healed_leaks = [l for l in leaks if l.status == LeakStatus.HEALED]

        return TÜVReport(
            timestamp=datetime.now(),
            protocols_checked=0,  # Updated when audits run
            protocols_passed=0,
            leaks_total=len(leaks),
            leaks_open=len(open_leaks),
            leaks_healed=len(healed_leaks),
            leaks=leaks,
            audits=[],
            churns=self._churns,
        )

    def record_churn(self, entry: ChurnEntry) -> None:
        """Record a churning (value creation)."""
        self._churns.append(entry)
        self._save_registry()

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts."""
        leaks = list(self._leaks.values())
        return {
            "leaks_total": len(leaks),
            "leaks_open": len([l for l in leaks if l.status == LeakStatus.OPEN]),
            "leaks_workaround": len([l for l in leaks if l.status == LeakStatus.WORKAROUND]),
            "leaks_healed": len([l for l in leaks if l.status == LeakStatus.HEALED]),
            "churns": len(self._churns),
        }

    # =========================================================================
    # Convenience: Full Scan
    # =========================================================================

    def full_scan(self, base_path: str = "vibe_core") -> TÜVReport:
        """Run full TÜV scan and register all leaks."""
        logger.info(f"TÜV: Starting full scan of {base_path}")

        # Scan for leaks
        leaks = self.scan_module(base_path)

        # Register new leaks (avoid duplicates by location)
        existing_locations = {l.location for l in self._leaks.values()}
        new_count = 0

        for leak in leaks:
            if leak.location not in existing_locations:
                self.register_leak(leak)
                new_count += 1

        logger.info(f"TÜV: Scan complete. {new_count} new leaks registered.")

        return self.get_report()
