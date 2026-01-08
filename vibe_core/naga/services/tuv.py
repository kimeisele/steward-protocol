"""
TÜV Service - NAGA Type Audit Intelligence Implementation.

"Das System wird organisch rot."

This service implements TÜVProtocol and UnionProtocol:
- Scans files for type leaks (Any, Dict[str, Any], etc.)
- Audits protocol/implementation alignment
- Persists leak registry to JSON
- Tracks churning (value creation)
- Provides 'State of the Union' report (heritage tracing)

SCALABILITY: Patterns and critical gaps are loaded from Phoenix config.
"""

import ast
import inspect
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from vibe_core.loaders.manifest_registry import ManifestRegistry
from vibe_core.naga.kulika import NagaCapability, NagaLord, get_kulika, naga_service
from vibe_core.naga.services.base import NagaBaseService
from vibe_core.protocols.naga import NagaStatus, NagaType
from vibe_core.protocols.naga.tuv import (
    ChurnEntry,
    FindingRegistry,
    Leak,
    LeakPattern,
    LeakSeverity,
    LeakStatus,
    ProtocolAudit,
    ProtocolCoverageReport,
    ProtocolGap,
    ProtocolGapSeverity,
    ProtocolGapStatus,
    TuvBadge,
    TÜVProtocol,
    TÜVReport,
)
from vibe_core.protocols.universal import EntityStatus, UnionProtocol

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.phoenix.sections.naga.section_main import TÜVConfig

logger = logging.getLogger("NAGA.TÜV")

# Registry file location
TÜV_REGISTRY_PATH = Path(".vibe/state/tuv_registry.json")


@naga_service(
    name="TÜV",
    lord=NagaLord.CHITRAGUPTA,  # Tool under Chitragupta (the Auditor)
    drift_source=None,  # Pure audit, no drift handling
    priority=65,
    capabilities=[NagaCapability.TYPE_AUDIT, NagaCapability.AUDIT],
    protocol_class="vibe_core.protocols.naga.TÜVProtocol",
)
class TÜVService(NagaBaseService, TÜVProtocol, UnionProtocol):
    """
    TÜV Audit Intelligence Service.

    Implements TÜVProtocol and UnionProtocol.
    Auto-discovered by Narada via @naga_service decorator.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        registry_path: Optional[Path] = None,
        config: Optional["TÜVConfig"] = None,
    ):
        """Initialize TÜV service."""
        super().__init__(service_name="TÜV")
        self._cortex = cortex
        self._registry_path = registry_path or TÜV_REGISTRY_PATH
        self._config = config

        # In-memory state - GENERIC REGISTRIES
        self._leaks: FindingRegistry[Leak] = FindingRegistry(Leak, "LEAK")
        self._gaps: FindingRegistry[ProtocolGap] = FindingRegistry(ProtocolGap, "GAP")
        self._churns: List[ChurnEntry] = []
        self._last_heartbeat = datetime.now()
        self._scans_performed = 0

        # Load existing registry
        self._load_registry()

        logger.info("🔍 TÜV initialized - Type Audit Intelligence active")

    # =========================================================================
    # UnionProtocol Implementation (The State of the Union)
    # =========================================================================

    def get_living_entities(self) -> List[EntityStatus]:
        """
        List all active entities and their protocol heritage.
        """
        entities: List[EntityStatus] = []

        # 1. Get Nagas from Kulika
        kulika = get_kulika()
        for name in kulika.all_names():
            manifest = kulika.get(name)
            if manifest:
                proto = manifest.protocol_class or "MAYAVAD (Missing Protocol)"
                entities.append(
                    EntityStatus(
                        id=manifest.name,
                        type="naga",
                        status="ACTIVE",
                        protocol=proto,
                        is_living=True,
                        tuv_score=1.0 if manifest.protocol_class else 0.0,
                        last_heartbeat=datetime.now(),
                    )
                )

        # 2. Get Agents/Plugins from ManifestRegistry
        for entry in ManifestRegistry.all():
            proto = entry.manifest.get("protocol_class") or "MAYAVAD (Missing Protocol)"
            entities.append(
                EntityStatus(
                    id=entry.id,
                    type=entry.type,
                    status="ACTIVE" if entry.enabled else "DORMANT",
                    protocol=proto,
                    is_living=entry.enabled,
                    tuv_score=0.8 if entry.manifest.get("protocol_class") else 0.1,
                    last_heartbeat=datetime.now(),
                )
            )

        return entities

    def get_union_summary(self) -> Dict[str, object]:
        """
        Get high-level summary of the Union.
        """
        entities = self.get_living_entities()
        types: Dict[str, int] = {}
        for e in entities:
            types[e.type] = types.get(e.type, 0) + 1

        return {
            "timestamp": datetime.now().isoformat(),
            "population": len(entities),
            "by_type": types,
            "compliance": {
                "leaks_open": self._leaks.count(status=LeakStatus.OPEN),
                "gaps_open": self._gaps.count(status=ProtocolGapStatus.IDENTIFIED),
            },
        }

    # =========================================================================
    # Badging (Runtime Certification)
    # =========================================================================

    def issue_badge(self, target: str) -> TuvBadge:
        """Issue a runtime badge for a component."""
        now = datetime.now()
        expires = now + timedelta(hours=24)
        score = 1.0  # TODO: calculate based on audit
        return TuvBadge(
            entity_id=target,
            issued_at=now,
            expires_at=expires,
            score=score,
            signature="signed_by_tuv",
        )

    def verify_badge(self, badge: TuvBadge) -> bool:
        """Verify a badge is valid."""
        return datetime.now() <= badge.expires_at

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
            self._leaks.load_list(data.get("leaks", []))
            self._gaps.load_list(data.get("gaps", []))
            for c in data.get("churns", []):
                self._churns.append(ChurnEntry(**c))
        except Exception as e:
            logger.warning(f"TÜV: Could not load registry: {e}")

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            self._registry_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "leaks": self._leaks.to_list(),
                "gaps": self._gaps.to_list(),
                "churns": [inspect.getmembers(c) for c in self._churns],  # Simplified
                "updated_at": datetime.now().isoformat(),
            }
            # Fix churn serialization
            data["churns"] = [
                {"date": c.date, "target": c.target, "gift": c.gift, "nektar": c.nektar, "churn_type": c.churn_type}
                for c in self._churns
            ]
            with open(self._registry_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"TÜV: Could not save registry: {e}")

    # =========================================================================
    # Leak Registry
    # =========================================================================

    def register_leak(self, leak: Leak) -> str:
        leak_id = self._leaks.register(leak)
        self._save_registry()
        return leak_id

    def get_leak(self, leak_id: str) -> Optional[Leak]:
        return self._leaks.get(leak_id)

    def get_leaks(self, **kwargs) -> List[Leak]:
        return self._leaks.filter(**kwargs)

    def heal_leak(self, leak_id: str, commit_hash: str = "") -> bool:
        leak = self._leaks.get(leak_id)
        if not leak:
            return False
        leak.status = LeakStatus.HEALED
        leak.healed_at = datetime.now()
        self._save_registry()
        return True

    # =========================================================================
    # Scanning
    # =========================================================================

    def scan_file(self, filepath: str) -> List[Leak]:
        leaks: List[Leak] = []
        path = Path(filepath)
        if not path.exists() or path.suffix != ".py":
            return leaks
        try:
            content = path.read_text()
            lines = content.splitlines()
            any_pattern = re.compile(r":\s*Any(?:\s*[,\)\]=]|$)")
            dict_any_pattern = re.compile(r"Dict\[str,\s*Any\]")
            return_any_pattern = re.compile(r"->\s*Any(?:\s*:|$)")
            for i, line in enumerate(lines, 1):
                if "TYPE_CHECKING" in line or line.strip().startswith("#"):
                    continue
                if "*args: Any" in line or "**kwargs: Any" in line:
                    continue
                location = f"{filepath}:{i}"
                if any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.ANY_PARAM,
                            severity=LeakSeverity.MEDIUM,
                            status=LeakStatus.OPEN,
                            description=f"Any annotation: {line.strip()}",
                            antidote="Use specific type",
                        )
                    )
                if dict_any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.DICT_STR_ANY,
                            severity=LeakSeverity.MEDIUM,
                            status=LeakStatus.OPEN,
                            description=f"Dict[str, Any]: {line.strip()}",
                            antidote="Use TypedDict",
                        )
                    )
                if return_any_pattern.search(line):
                    leaks.append(
                        Leak(
                            id="",
                            location=location,
                            pattern=LeakPattern.ANY_RETURN,
                            severity=LeakSeverity.HIGH,
                            status=LeakStatus.OPEN,
                            description=f"Any return: {line.strip()}",
                            antidote="Use specific return type",
                        )
                    )
        except Exception as e:
            logger.warning(f"TÜV: Error scanning {filepath}: {e}")
        return leaks

    def scan_module(self, module_path: str) -> List[Leak]:
        leaks: List[Leak] = []
        path = Path(module_path)
        if not path.exists():
            return leaks
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            leaks.extend(self.scan_file(str(py_file)))
        return leaks

    def full_scan(self, base_path: str = "vibe_core") -> TÜVReport:
        leaks = self.scan_module(base_path)
        existing = {l.location for l in self._leaks.all()}
        for leak in leaks:
            if leak.location not in existing:
                self.register_leak(leak)
        self._scans_performed += 1
        return self.get_report()

    def get_report(self) -> TÜVReport:
        all_leaks = self._leaks.all()
        return TÜVReport(
            timestamp=datetime.now(),
            protocols_checked=0,
            protocols_passed=0,
            leaks_total=len(all_leaks),
            leaks_open=self._leaks.count(status=LeakStatus.OPEN),
            leaks_healed=self._leaks.count(status=LeakStatus.HEALED),
            leaks=all_leaks,
            audits=[],
            churns=self._churns,
        )

    # =========================================================================
    # Protocol Alignment
    # =========================================================================

    def audit_protocol(self, protocol_name: str, service_name: str) -> ProtocolAudit:
        return ProtocolAudit(
            protocol_name=protocol_name, service_name=service_name, passed=False, mismatches=["Not implemented"]
        )

    def scan_protocol_coverage(self, base_path: str = "vibe_core") -> ProtocolCoverageReport:
        return ProtocolCoverageReport(
            timestamp=datetime.now(),
            protocols_found=0,
            gaps_total=0,
            gaps_critical=0,
            gaps_high=0,
            coverage_percent=0.0,
            gaps=[],
        )

    def register_gap(self, gap: ProtocolGap) -> str:
        return self._gaps.register(gap)

    def get_gap(self, gap_id: str) -> Optional[ProtocolGap]:
        return self._gaps.get(gap_id)

    def get_gaps(self, **kwargs) -> List[ProtocolGap]:
        return self._gaps.filter(**kwargs)

    def close_gap(self, gap_id: str, protocol_location: str = "") -> bool:
        gap = self._gaps.get(gap_id)
        if not gap:
            return False
        gap.status = ProtocolGapStatus.CLOSED
        gap.closed_at = datetime.now()
        self._save_registry()
        return True

    def record_churn(self, entry: ChurnEntry) -> None:
        self._churns.append(entry)
        self._save_registry()

    def get_summary(self) -> Dict[str, int]:
        return {
            "leaks_total": len(self._leaks.all()),
            "leaks_open": self._leaks.count(status=LeakStatus.OPEN),
            "gaps_open": self._gaps.count(status=ProtocolGapStatus.IDENTIFIED),
            "churns": len(self._churns),
        }

    def get_status(self) -> NagaStatus:
        summary = self.get_summary()
        return NagaStatus(
            naga_type=NagaType.CHITRAGUPTA,
            healthy=True,
            events_processed=self._scans_performed,
            errors=summary["leaks_open"],
            last_heartbeat=self._last_heartbeat,
            details=summary,
        )

    def _implementation_patterns(self) -> List[str]:
        return ["Service", "Manager", "Registry", "Engine"]

    def _get_config(self) -> Optional[Any]:
        return None
