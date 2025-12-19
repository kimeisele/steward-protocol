"""
OPUS-116: The Silent Observer - Proactive Disharmony Detection.

"यत्र योगेश्वरः कृष्णो यत्र पार्थो धनुर्धरः।
तत्र श्रीर्विजयो भूतिर्ध्रुवा नीतिर्मतिर्मम॥"
"Where there is harmony, there is victory, prosperity, and righteousness."

The Silent Observer watches for code that has wandered from its dharmic path:
- Files in the wrong layer (OUTPUT code doing KERNEL work)
- Import patterns that cross too many Varga boundaries
- Content that doesn't match its location

This is the SELF-HEALING aspect of VEDA-4.
The system can identify when code is "out of place" and suggest corrections.

Usage:
    from vibe_core.plugins.opus_assistant.manas.disharmony_detector import (
        DisharmonyDetector,
        scan_for_disharmony,
    )

    detector = DisharmonyDetector(workspace)
    report = detector.scan()

    for finding in report.findings:
        print(f"{finding.path}: {finding.description}")
        print(f"  Location Varga: {finding.location_varga}")
        print(f"  Content Varga: {finding.content_varga}")
        print(f"  Recommendation: {finding.recommendation}")
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .akshara import (
    PATH_VARGA_PATTERNS,
    VARGA_LAYERS,
    Varga,
    get_path_layer,
    map_path_to_varga,
)

logger = logging.getLogger("MANAS.Disharmony")


# =============================================================================
# IMPORT PATTERN → VARGA MAPPING
# =============================================================================

# What imports indicate about code's TRUE nature (what it DOES, not where it IS)
IMPORT_VARGA_INDICATORS: Dict[str, Varga] = {
    # KERNEL indicators - core system operations
    "vibe_core.runtime": Varga.KANTHYA,
    "vibe_core.governance": Varga.KANTHYA,
    "vibe_core.protocols": Varga.KANTHYA,
    "vibe_core.store": Varga.KANTHYA,
    "vibe_core.state": Varga.KANTHYA,
    "vibe_core.scheduling": Varga.KANTHYA,
    "subprocess": Varga.KANTHYA,
    "threading": Varga.KANTHYA,
    "multiprocessing": Varga.KANTHYA,
    "os.": Varga.KANTHYA,
    "sys.": Varga.KANTHYA,
    # COGNITION indicators - decision/reasoning
    "vibe_core.llm": Varga.TALAVYA,
    "vibe_core.cortex": Varga.TALAVYA,
    "vibe_core.agents": Varga.TALAVYA,
    "vibe_core.knowledge": Varga.TALAVYA,
    "anthropic": Varga.TALAVYA,
    "openai": Varga.TALAVYA,
    "langchain": Varga.TALAVYA,
    "transformers": Varga.TALAVYA,
    # REPAIR indicators - testing/fixing
    "pytest": Varga.MURDHANYA,
    "unittest": Varga.MURDHANYA,
    "vibe_core.plugins.doctor": Varga.MURDHANYA,
    "vibe_core.specialists": Varga.MURDHANYA,
    "hypothesis": Varga.MURDHANYA,
    "mock": Varga.MURDHANYA,
    # INTERFACE indicators - connections/docs
    "vibe_core.gateway": Varga.DANTYA,
    "vibe_core.loaders": Varga.DANTYA,
    "vibe_core.cartridges": Varga.DANTYA,
    "fastapi": Varga.DANTYA,
    "flask": Varga.DANTYA,
    "requests": Varga.DANTYA,
    "httpx": Varga.DANTYA,
    "aiohttp": Varga.DANTYA,
    # OUTPUT indicators - user-facing
    "vibe_core.cli": Varga.OSHTHYA,
    "vibe_core.phoenix": Varga.OSHTHYA,
    "click": Varga.OSHTHYA,
    "typer": Varga.OSHTHYA,
    "rich": Varga.OSHTHYA,
    "argparse": Varga.OSHTHYA,
    "print": Varga.OSHTHYA,
}

# Function name patterns that indicate Varga
FUNCTION_VARGA_PATTERNS: Dict[str, Varga] = {
    # KERNEL patterns
    r"^_?init": Varga.KANTHYA,
    r"^_?setup": Varga.KANTHYA,
    r"^_?bootstrap": Varga.KANTHYA,
    r"^_?load_": Varga.KANTHYA,
    r"^_?save_": Varga.KANTHYA,
    # COGNITION patterns
    r"^_?analyze": Varga.TALAVYA,
    r"^_?decide": Varga.TALAVYA,
    r"^_?evaluate": Varga.TALAVYA,
    r"^_?infer": Varga.TALAVYA,
    r"^_?predict": Varga.TALAVYA,
    r"^_?think": Varga.TALAVYA,
    # REPAIR patterns
    r"^test_": Varga.MURDHANYA,
    r"^_?fix": Varga.MURDHANYA,
    r"^_?repair": Varga.MURDHANYA,
    r"^_?validate": Varga.MURDHANYA,
    r"^_?check": Varga.MURDHANYA,
    # INTERFACE patterns
    r"^_?connect": Varga.DANTYA,
    r"^_?fetch": Varga.DANTYA,
    r"^_?send": Varga.DANTYA,
    r"^_?receive": Varga.DANTYA,
    r"^_?handle_": Varga.DANTYA,
    # OUTPUT patterns
    r"^_?render": Varga.OSHTHYA,
    r"^_?display": Varga.OSHTHYA,
    r"^_?print": Varga.OSHTHYA,
    r"^_?show": Varga.OSHTHYA,
    r"^_?format_": Varga.OSHTHYA,
}


# =============================================================================
# DISHARMONY FINDING
# =============================================================================


@dataclass
class DisharmonyFinding:
    """A single instance of detected disharmony."""

    path: str  # File path
    location_varga: Varga  # Where the file IS
    content_varga: Varga  # What the file DOES
    varga_distance: int  # How far apart (0-4)
    severity: str  # "low", "medium", "high", "critical"
    description: str  # Human-readable description
    evidence: List[str]  # Import/pattern evidence
    recommendation: str  # Suggested fix

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical disharmony (OUTPUT doing KERNEL)."""
        return self.varga_distance >= 3

    @property
    def location_layer(self) -> str:
        """Get the layer name for location."""
        return VARGA_LAYERS[self.location_varga]

    @property
    def content_layer(self) -> str:
        """Get the layer name for content."""
        return VARGA_LAYERS[self.content_varga]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "location_varga": self.location_varga.name,
            "content_varga": self.content_varga.name,
            "location_layer": self.location_layer,
            "content_layer": self.content_layer,
            "varga_distance": self.varga_distance,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class DisharmonyReport:
    """A complete disharmony scan report."""

    workspace: str
    scanned_files: int
    findings: List[DisharmonyFinding] = field(default_factory=list)
    scan_duration_ms: float = 0.0

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def critical_findings(self) -> List[DisharmonyFinding]:
        return [f for f in self.findings if f.is_critical]

    @property
    def findings_by_severity(self) -> Dict[str, List[DisharmonyFinding]]:
        result: Dict[str, List[DisharmonyFinding]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }
        for finding in self.findings:
            result[finding.severity].append(finding)
        return result

    @property
    def is_harmonious(self) -> bool:
        """Check if the codebase is in harmony (no critical/high findings)."""
        return all(f.severity in ("low", "medium") for f in self.findings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace": self.workspace,
            "scanned_files": self.scanned_files,
            "total_findings": self.total_findings,
            "is_harmonious": self.is_harmonious,
            "findings_by_severity": {k: len(v) for k, v in self.findings_by_severity.items()},
            "findings": [f.to_dict() for f in self.findings],
            "scan_duration_ms": self.scan_duration_ms,
        }

    def summary(self) -> str:
        """Get a human-readable summary."""
        if self.is_harmonious:
            return f"✅ Codebase is harmonious ({self.scanned_files} files scanned)"

        by_sev = self.findings_by_severity
        parts = []
        if by_sev["critical"]:
            parts.append(f"{len(by_sev['critical'])} critical")
        if by_sev["high"]:
            parts.append(f"{len(by_sev['high'])} high")
        if by_sev["medium"]:
            parts.append(f"{len(by_sev['medium'])} medium")
        if by_sev["low"]:
            parts.append(f"{len(by_sev['low'])} low")

        return f"⚠️ Disharmony detected: {', '.join(parts)} ({self.scanned_files} files)"


# =============================================================================
# CONTENT ANALYZER
# =============================================================================


class ContentAnalyzer:
    """Analyzes file content to determine its TRUE Varga."""

    def __init__(self):
        self._import_cache: Dict[str, Set[str]] = {}

    def analyze_python_file(self, path: Path) -> Tuple[Optional[Varga], List[str]]:
        """
        Analyze a Python file to determine its content Varga.

        Returns:
            Tuple of (inferred Varga, evidence list)
            Returns None if content is ambiguous or neutral
        """
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None, []

        evidence = []
        varga_votes: Dict[Varga, int] = {v: 0 for v in Varga}

        # Analyze imports
        imports = self._extract_imports(content)
        for imp in imports:
            for pattern, varga in IMPORT_VARGA_INDICATORS.items():
                if pattern in imp:
                    varga_votes[varga] += 1
                    evidence.append(f"import: {imp}")
                    break

        # Analyze function names
        functions = self._extract_function_names(content)
        for func in functions:
            for pattern, varga in FUNCTION_VARGA_PATTERNS.items():
                if re.match(pattern, func):
                    varga_votes[varga] += 1
                    evidence.append(f"function: {func}")
                    break

        # Determine dominant Varga
        if not any(varga_votes.values()):
            return None, evidence

        max_votes = max(varga_votes.values())
        if max_votes < 2:  # Need at least 2 indicators
            return None, evidence

        # Get the Varga with max votes
        for varga, votes in varga_votes.items():
            if votes == max_votes:
                return varga, evidence

        return None, evidence

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code."""
        imports = []

        # Match 'import X' and 'from X import Y'
        import_pattern = re.compile(r"^(?:from\s+(\S+)\s+)?import\s+(\S+)", re.MULTILINE)
        for match in import_pattern.finditer(content):
            if match.group(1):
                imports.append(match.group(1))
            if match.group(2):
                imports.append(match.group(2).split(".")[0])

        return imports

    def _extract_function_names(self, content: str) -> List[str]:
        """Extract function names from Python code."""
        functions = []
        func_pattern = re.compile(r"^(?:async\s+)?def\s+(\w+)", re.MULTILINE)
        for match in func_pattern.finditer(content):
            functions.append(match.group(1))
        return functions


# =============================================================================
# DISHARMONY DETECTOR
# =============================================================================


class DisharmonyDetector:
    """
    OPUS-116: The Silent Observer.

    Scans the codebase for disharmony - files whose content doesn't match
    their location. This is the proactive self-healing component of VEDA-4.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._analyzer = ContentAnalyzer()

    def scan(
        self,
        paths: Optional[List[str]] = None,
        min_severity: str = "low",
    ) -> DisharmonyReport:
        """
        Scan the codebase for disharmony.

        Args:
            paths: Specific paths to scan (default: all Python files in vibe_core)
            min_severity: Minimum severity to report ("low", "medium", "high", "critical")

        Returns:
            DisharmonyReport with findings
        """
        import time

        start = time.time()

        # Determine files to scan
        if paths:
            files = [self._workspace / p for p in paths]
        else:
            files = list((self._workspace / "vibe_core").rglob("*.py"))

        findings = []
        scanned = 0

        for file_path in files:
            if not file_path.exists():
                continue
            if "__pycache__" in str(file_path):
                continue

            scanned += 1
            finding = self._analyze_file(file_path)
            if finding and self._meets_severity(finding.severity, min_severity):
                findings.append(finding)

        duration = (time.time() - start) * 1000

        report = DisharmonyReport(
            workspace=str(self._workspace),
            scanned_files=scanned,
            findings=findings,
            scan_duration_ms=duration,
        )

        logger.info(f"🔍 SILENT OBSERVER: {report.summary()}")
        return report

    def _analyze_file(self, path: Path) -> Optional[DisharmonyFinding]:
        """Analyze a single file for disharmony."""
        rel_path = str(path.relative_to(self._workspace))

        # Get location Varga (where the file IS)
        location_varga = map_path_to_varga(rel_path)

        # Get content Varga (what the file DOES)
        content_varga, evidence = self._analyzer.analyze_python_file(path)

        if content_varga is None:
            return None  # No clear content Varga

        # Calculate distance
        distance = abs(location_varga - content_varga)

        if distance == 0:
            return None  # Perfect harmony

        # Determine severity based on distance
        if distance >= 4:
            severity = "critical"
        elif distance >= 3:
            severity = "high"
        elif distance >= 2:
            severity = "medium"
        else:
            severity = "low"

        # Generate description and recommendation
        description = self._generate_description(rel_path, location_varga, content_varga, distance)
        recommendation = self._generate_recommendation(rel_path, location_varga, content_varga)

        return DisharmonyFinding(
            path=rel_path,
            location_varga=location_varga,
            content_varga=content_varga,
            varga_distance=distance,
            severity=severity,
            description=description,
            evidence=evidence[:5],  # Limit evidence
            recommendation=recommendation,
        )

    def _generate_description(
        self,
        path: str,
        location: Varga,
        content: Varga,
        distance: int,
    ) -> str:
        """Generate a human-readable description of the disharmony."""
        location_layer = VARGA_LAYERS[location]
        content_layer = VARGA_LAYERS[content]

        if distance >= 4:
            return (
                f"Critical disharmony: {location_layer} code performing {content_layer} operations. "
                f"Maximum Varga distance ({distance})."
            )
        elif distance >= 3:
            return (
                f"High disharmony: {location_layer} code with {content_layer} behavior. Large Varga gap ({distance})."
            )
        elif distance >= 2:
            return (
                f"Moderate disharmony: {location_layer} code leaning toward {content_layer}. "
                f"Varga distance: {distance}."
            )
        else:
            return f"Minor disharmony: {location_layer} code with some {content_layer} patterns. Adjacent Vargas."

    def _generate_recommendation(
        self,
        path: str,
        location: Varga,
        content: Varga,
    ) -> str:
        """Generate a recommendation for fixing the disharmony."""
        location_layer = VARGA_LAYERS[location]
        content_layer = VARGA_LAYERS[content]

        # Find the correct folder for the content Varga
        target_patterns = PATH_VARGA_PATTERNS.get(content, [])
        target_folder = None
        for pattern in target_patterns:
            if pattern.endswith("/") and not pattern.startswith("*"):
                target_folder = pattern.rstrip("/")
                break

        if target_folder:
            return (
                f"Consider moving to {target_folder}/ where {content_layer} code belongs, "
                f"or refactor to remove {content_layer} operations from this {location_layer} module."
            )
        else:
            return (
                f"Refactor to remove {content_layer} operations from this {location_layer} module, "
                f"or extract that logic into a dedicated {content_layer} component."
            )

    def _meets_severity(self, severity: str, min_severity: str) -> bool:
        """Check if severity meets minimum threshold."""
        levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        return levels.get(severity, 0) >= levels.get(min_severity, 0)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def scan_for_disharmony(
    workspace: Path,
    min_severity: str = "medium",
) -> DisharmonyReport:
    """
    Convenience function to scan for disharmony.

    Args:
        workspace: Workspace path
        min_severity: Minimum severity to report

    Returns:
        DisharmonyReport
    """
    detector = DisharmonyDetector(workspace)
    return detector.scan(min_severity=min_severity)


def check_file_harmony(workspace: Path, file_path: str) -> Optional[DisharmonyFinding]:
    """
    Check a single file for disharmony.

    Args:
        workspace: Workspace path
        file_path: Relative file path

    Returns:
        DisharmonyFinding if disharmony found, None if harmonious
    """
    detector = DisharmonyDetector(workspace)
    report = detector.scan(paths=[file_path], min_severity="low")
    return report.findings[0] if report.findings else None


def get_harmony_score(workspace: Path) -> float:
    """
    Get an overall harmony score for the codebase.

    Returns a score from 0.0 (total disharmony) to 1.0 (perfect harmony).
    """
    report = scan_for_disharmony(workspace, min_severity="low")

    if report.scanned_files == 0:
        return 1.0

    # Calculate weighted score
    weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    total_penalty = sum(weights[f.severity] * f.varga_distance for f in report.findings)

    max_penalty = report.scanned_files * 4 * 4  # All files, critical, max distance
    harmony = 1.0 - (total_penalty / max_penalty) if max_penalty > 0 else 1.0

    return max(0.0, min(1.0, harmony))
