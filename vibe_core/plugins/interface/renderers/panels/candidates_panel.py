"""
Candidates Panel - Auto-detected extraction candidates.

Analyzes source files for functions that could be extracted.
Config-driven thresholds from config/opus.yaml.
"""

from pathlib import Path
from typing import Any, Dict, List

from .base_panel import OpusPanel


class CandidatesPanel(OpusPanel):
    """
    Extraction Candidates Panel.

    Auto-analyzes configured files for extractable functions.
    Uses config-driven thresholds for complexity detection.
    """

    @property
    def panel_id(self) -> str:
        return "candidates"

    @property
    def section_id(self) -> str:
        return "extraction_detection"

    @property
    def priority(self) -> int:
        return 10  # After status panels

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render extraction candidates section."""
        display = config.get("display", {})
        if not display.get("show_extraction_candidates", True):
            return ""  # Panel disabled

        detection = config.get("extraction_detection", {})
        tracked = config.get("tracked_files", {})

        # Get primary file to analyze
        primary_path = tracked.get("primary", {}).get("path", "vibe_core/kernel_impl.py")

        # Analyze candidates
        candidates = self._analyze_candidates(Path(primary_path), detection)

        # Format table
        max_candidates = display.get("max_candidates", 8)
        table = self._format_candidates_table(candidates, detection, max_candidates)

        return f"""## Extraction Candidates

{table}

---
"""

    def _analyze_candidates(self, file_path: Path, detection_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze file for extraction candidates."""
        candidates = []
        min_loc = detection_config.get("min_loc_for_candidate", 15)
        keywords = detection_config.get("complexity_keywords", ["if ", "for ", "while ", "try:", "except", "with "])

        try:
            if not file_path.exists():
                return candidates

            content = file_path.read_text()
            lines = content.splitlines()

            current_func = None
            func_start = 0

            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if stripped.startswith("def ") or stripped.startswith("async def "):
                    # Save previous function
                    if current_func and (i - func_start) >= min_loc:
                        func_lines = lines[func_start:i]
                        complexity = self._estimate_complexity(func_lines, keywords)
                        candidates.append(
                            {
                                "name": current_func,
                                "start_line": func_start + 1,
                                "end_line": i,
                                "loc": i - func_start,
                                "complexity": complexity,
                            }
                        )

                    # Start tracking new function
                    func_name = stripped.split("(")[0].replace("def ", "").replace("async ", "")
                    current_func = func_name
                    func_start = i

            # Sort by LOC (largest first)
            candidates.sort(key=lambda x: x["loc"], reverse=True)
            return candidates

        except Exception:
            return []

    def _estimate_complexity(self, lines: List[str], keywords: List[str]) -> str:
        """Estimate function complexity."""
        control_flow = sum(1 for line in lines if any(kw in line for kw in keywords))
        if control_flow > 10:
            return "HIGH"
        elif control_flow > 5:
            return "MEDIUM"
        return "LOW"

    def _format_candidates_table(self, candidates: List[Dict], detection: Dict[str, Any], max_count: int) -> str:
        """Format candidates as markdown table."""
        if not candidates:
            return "_No significant extraction candidates found._"

        recommend_loc = detection.get("min_loc_for_recommendation", 30)

        lines = [
            "| Function | LOC | Lines | Complexity | Extractable? |",
            "|----------|-----|-------|------------|--------------|",
        ]

        for c in candidates[:max_count]:
            extractable = (
                "Yes"
                if c["complexity"] != "HIGH" and c["loc"] >= recommend_loc
                else "Maybe"
                if c["loc"] > recommend_loc
                else "No"
            )
            lines.append(
                f"| `{c['name']}` | {c['loc']} | "
                f"{c['start_line']}-{c['end_line']} | "
                f"{c['complexity']} | {extractable} |"
            )

        return "\n".join(lines)
