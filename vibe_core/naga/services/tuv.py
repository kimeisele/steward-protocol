"""
TÜV Service - NAGA Type Audit Intelligence Implementation.

"Das System wird organisch rot."

This service implements TÜVProtocol:
- Scans files for type leaks (Any, Dict[str, Any], etc.)
- Audits protocol/implementation alignment
- Persists leak registry to JSON
- Tracks churning (value creation)

SCALABILITY: Patterns and critical gaps are loaded from Phoenix config.
To add a new pattern: edit naga.yaml or NagaConfig.tuv.implementation_patterns
"""

import ast
import inspect
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.loaders.manifest_registry import ManifestRegistry
from vibe_core.naga.kulika import NagaCapability, NagaLord, get_kulika, naga_service
from vibe_core.naga.mixins.tuv import TuvBadge
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
    priority=65,  # Below Chitragupta (60), tool for the auditor
    capabilities=[NagaCapability.TYPE_AUDIT, NagaCapability.AUDIT],
    protocol_class="vibe_core.protocols.naga.TÜVProtocol",
)
class TÜVService(NagaBaseService, UnionProtocol):
    """

    TÜV Audit Intelligence Service.



    Implements TÜVProtocol - not documentation, CODE.

    Auto-discovered by Narada via @naga_service decorator.



    HIERARCHY: Prahlad → Chitragupta → TÜV

    TÜV is an INSTITUTION (tool), not a PERSON (lord).

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

        self._config = config  # Will be loaded from Phoenix if None

        # In-memory state - GENERIC REGISTRIES (protocol-first!)

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
                entities.append(
                    EntityStatus(
                        id=manifest.name,
                        type="naga",
                        status="ACTIVE",
                        protocol=manifest.protocol_class,
                        is_living=True,  # Nagas are persistent in memory
                        tuv_score=1.0,  # TODO: actual check
                        last_heartbeat=datetime.now(),
                    )
                )

        # 2. Get Agents from ManifestRegistry

        for entry in ManifestRegistry.all():
            entities.append(
                EntityStatus(
                    id=entry.id,
                    type=entry.type,
                    status="ACTIVE" if entry.enabled else "DORMANT",
                    protocol=entry.manifest.get("protocol_class"),
                    is_living=entry.enabled,
                    tuv_score=0.8,  # TODO: actual check
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

    def _get_config(self) -> "TÜVConfig":
        """Get TÜV config, loading from Phoenix if needed."""
        if self._config is not None:
            return self._config

        # Lazy load from Phoenix to avoid circular imports
        try:
            from vibe_core.phoenix.sections.naga.section_main import TÜVConfig

            # Try to get from Phoenix loader
            try:
                from vibe_core.phoenix import get_config

                phoenix_config = get_config()
                if hasattr(phoenix_config, "naga") and hasattr(phoenix_config.naga, "tuv"):
                    self._config = phoenix_config.naga.tuv
                    return self._config
            except Exception:
                pass

            # Fall back to defaults
            self._config = TÜVConfig()
            return self._config

        except ImportError:
            # Phoenix not available, create minimal config
            from vibe_core.phoenix.sections.naga.section_main import TÜVConfig

            self._config = TÜVConfig()
            return self._config

    def get_status(self) -> NagaStatus:
        """Get current status - required for NAGA discovery."""
        # Using TÜVRegistry.count() - generic filtering!
        open_leaks = self._leaks.count(status=LeakStatus.OPEN)
        open_gaps = len(self._gaps.all()) - self._gaps.count(status=ProtocolGapStatus.CLOSED)

        return NagaStatus(
            naga_type=NagaType.CHITRAGUPTA,  # Closest type (auditor)
            healthy=True,
            events_processed=self._scans_performed,
            errors=open_leaks + open_gaps,
            last_heartbeat=self._last_heartbeat,
            details={
                "leaks_total": len(self._leaks.all()),
                "leaks_open": open_leaks,
                "leaks_healed": self._leaks.count(status=LeakStatus.HEALED),
                "gaps_total": len(self._gaps.all()),
                "gaps_open": open_gaps,
                "churns": len(self._churns),
            },
        )

    # =========================================================================
    # Persistence
    # =========================================================================

    def _load_registry(self) -> None:
        """Load registry from disk - uses TÜVRegistry.load_list()."""
        if not self._registry_path.exists():
            return

        try:
            with open(self._registry_path) as f:
                data = json.load(f)

            # Generic loading via TÜVRegistry - NO manual wiring!
            self._leaks.load_list(data.get("leaks", []))
            self._gaps.load_list(data.get("gaps", []))

            # Churns are simple, keep manual
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

            logger.debug(f"TÜV: Loaded {len(self._leaks.all())} leaks, {len(self._gaps.all())} gaps")

        except Exception as e:
            logger.warning(f"TÜV: Could not load registry: {e}")

    def _save_registry(self) -> None:
        """Save registry to disk - uses TÜVRegistry.to_list()."""
        try:
            self._registry_path.parent.mkdir(parents=True, exist_ok=True)

            # Generic serialization via TÜVRegistry - NO manual wiring!
            data = {
                "leaks": self._leaks.to_list(),
                "gaps": self._gaps.to_list(),
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
        leak_id = self._leaks.register(leak)
        self._save_registry()
        logger.info(f"TÜV: Registered {leak_id} at {leak.location}")
        return leak_id

    def get_leak(self, leak_id: str) -> Optional[Leak]:
        """Get leak by ID."""
        return self._leaks.get(leak_id)

    def get_leaks(
        self,
        status: Optional[LeakStatus] = None,
        severity: Optional[LeakSeverity] = None,
        pattern: Optional[LeakPattern] = None,
    ) -> List[Leak]:
        """Query leaks with optional filters - uses generic TÜVRegistry.filter()."""
        return self._leaks.filter(status=status, severity=severity, pattern=pattern)

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
    # Protocol Coverage (REPRODUCIBLE INTELLIGENCE)
    # =========================================================================

    def scan_protocol_coverage(self, base_path: str = "vibe_core") -> ProtocolCoverageReport:
        """
        Scan codebase for protocol gaps.

        REPRODUCIBLE intelligence:
        1. Find all Protocol classes
        2. Find all services/implementations
        3. Identify implementations WITHOUT protocols
        4. Detect scattered implementations (same name pattern, no unified protocol)
        """
        path = Path(base_path)
        if not path.exists():
            return ProtocolCoverageReport(
                timestamp=datetime.now(),
                protocols_found=0,
                gaps_total=0,
                gaps_critical=0,
                gaps_high=0,
                coverage_percent=0.0,
                gaps=[],
            )

        protocols_found: List[str] = []
        implementations: Dict[str, List[str]] = {}  # pattern -> [locations]

        # Scan for Protocol classes
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a Protocol
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == "Protocol":
                                protocols_found.append(node.name)
                            elif isinstance(base, ast.Attribute) and base.attr == "Protocol":
                                protocols_found.append(node.name)

                        # Track implementations by pattern
                        name = node.name
                        for pattern in self._implementation_patterns():
                            if name.endswith(pattern):
                                base_name = name[: -len(pattern)] if pattern else name
                                if base_name not in implementations:
                                    implementations[base_name] = []
                                implementations[base_name].append(f"{py_file}:{name}")

            except Exception:
                continue

        # Detect gaps
        gaps: List[ProtocolGap] = []

        # Check for scattered implementations (same base name, multiple classes)
        for base_name, locations in implementations.items():
            if len(locations) > 2:  # Multiple implementations
                protocol_name = f"{base_name}Protocol"
                if protocol_name not in protocols_found:
                    gaps.append(
                        ProtocolGap(
                            id="",
                            name=protocol_name,
                            severity=ProtocolGapSeverity.HIGH,
                            status=ProtocolGapStatus.IDENTIFIED,
                            description=f"{len(locations)} scattered implementations without protocol",
                            existing_implementations=locations[:5],  # First 5
                            suggested_location=f"protocols/{base_name.lower()}.py",
                        )
                    )

        # Check for known critical gaps (loaded from Phoenix config)
        config = self._get_config()
        for critical_gap in config.critical_gaps:
            if critical_gap.name not in protocols_found:
                gaps.append(
                    ProtocolGap(
                        id="",
                        name=critical_gap.name,
                        severity=ProtocolGapSeverity.CRITICAL,
                        status=ProtocolGapStatus.IDENTIFIED,
                        description=critical_gap.description,
                        existing_implementations=[],
                        suggested_location=critical_gap.suggested_location,
                    )
                )

        # Calculate coverage
        total = len(protocols_found) + len(gaps)
        coverage = (len(protocols_found) / total * 100) if total > 0 else 0.0

        return ProtocolCoverageReport(
            timestamp=datetime.now(),
            protocols_found=len(protocols_found),
            gaps_total=len(gaps),
            gaps_critical=len([g for g in gaps if g.severity == ProtocolGapSeverity.CRITICAL]),
            gaps_high=len([g for g in gaps if g.severity == ProtocolGapSeverity.HIGH]),
            coverage_percent=coverage,
            gaps=gaps,
        )

    def _implementation_patterns(self) -> List[str]:
        """Patterns that indicate an implementation (not a protocol).

        SCALABILITY: Loaded from Phoenix config. Add new patterns via:
        - naga.yaml: tuv.implementation_patterns: [...]
        - NagaConfig.tuv.implementation_patterns
        """
        return self._get_config().implementation_patterns

    def register_gap(self, gap: ProtocolGap) -> str:
        """Register a protocol gap. Returns gap ID."""
        gap_id = self._gaps.register(gap)
        self._save_registry()
        logger.info(f"TÜV: Registered {gap_id} - {gap.name}")
        return gap_id

    def get_gap(self, gap_id: str) -> Optional[ProtocolGap]:
        """Get gap by ID."""
        return self._gaps.get(gap_id)

    def get_gaps(
        self,
        status: Optional[ProtocolGapStatus] = None,
        severity: Optional[ProtocolGapSeverity] = None,
    ) -> List[ProtocolGap]:
        """Query gaps with optional filters - uses generic TÜVRegistry.filter()."""
        return self._gaps.filter(status=status, severity=severity)

    def close_gap(self, gap_id: str, protocol_location: str = "") -> bool:
        """Mark a gap as closed (protocol created)."""
        gap = self._gaps.get(gap_id)
        if not gap:
            return False

        gap.status = ProtocolGapStatus.CLOSED
        gap.closed_at = datetime.now()

        self._save_registry()
        logger.info(f"TÜV: Closed {gap_id} - protocol at {protocol_location}")
        return True

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_report(self) -> TÜVReport:
        """Get full TÜV report - uses TÜVRegistry."""
        all_leaks = self._leaks.all()
        return TÜVReport(
            timestamp=datetime.now(),
            protocols_checked=0,  # Updated when audits run
            protocols_passed=0,
            leaks_total=len(all_leaks),
            leaks_open=self._leaks.count(status=LeakStatus.OPEN),
            leaks_healed=self._leaks.count(status=LeakStatus.HEALED),
            leaks=all_leaks,
            audits=[],
            churns=self._churns,
        )

    def record_churn(self, entry: ChurnEntry) -> None:
        """Record a churning (value creation)."""
        self._churns.append(entry)
        self._save_registry()

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts - uses TÜVRegistry.count() - NO manual filtering!"""
        return {
            "leaks_total": len(self._leaks.all()),
            "leaks_open": self._leaks.count(status=LeakStatus.OPEN),
            "leaks_workaround": self._leaks.count(status=LeakStatus.WORKAROUND),
            "leaks_healed": self._leaks.count(status=LeakStatus.HEALED),
            "gaps_total": len(self._gaps.all()),
            "gaps_open": len(self._gaps.all()) - self._gaps.count(status=ProtocolGapStatus.CLOSED),
            "gaps_critical": self._gaps.count(severity=ProtocolGapSeverity.CRITICAL),
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
        existing_locations = {l.location for l in self._leaks.all()}
        new_count = 0

        for leak in leaks:
            if leak.location not in existing_locations:
                self.register_leak(leak)
                new_count += 1

        logger.info(f"TÜV: Scan complete. {new_count} new leaks registered.")

        return self.get_report()

    # =========================================================================
    # Badging (Runtime Certification)
    # =========================================================================

    def issue_badge(self, target: str) -> TuvBadge:
        """Issue a runtime badge for a component."""
        now = datetime.now()
        expires = now + timedelta(hours=24)  # Default 24h validity

        # Calculate score (Mock logic for now, could use audit results)
        score = 1.0

        return TuvBadge(
            entity_id=target,
            issued_at=now,
            expires_at=expires,
            score=score,
            signature="signed_by_tuv_service",  # TODO: Use Karkotaka
        )

    def verify_badge(self, badge: TuvBadge) -> bool:
        """Verify a badge is valid and authentic."""
        if datetime.now() > badge.expires_at:
            return False
        # TODO: verify signature
        return True
