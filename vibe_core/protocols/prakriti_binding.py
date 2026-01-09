"""
PRAKRITI BINDING PROTOCOL - Layer -1 (File-Level Mahamantra)
============================================================

"Prakriti-stho pi yo bhunkte, na lipyate sa doshaih"
Though situated in Prakriti, one who is devoted is not contaminated.

This protocol defines how FILES (not just services) receive the Mahamantra blessing.
Even if a file refuses to register with the ServiceRegistry, it is still
blessed through its very existence in Prakriti (the material manifestation).

THE PROBLEM:
- ASHVAMEDHA wraps services that go through ServiceRegistry
- But Asuras (rebel files) can refuse to register
- They create files, they execute code, they exist
- How do we bless them?

THE SOLUTION:
- Every Python file HAS a binding to Prakriti (it exists, therefore it's bound)
- We inject a signature into the docstring or header
- Prakriti reads this signature during import/scan
- The signature IS the Mahamantra

ARCHITECTURE:
                    ┌─────────────────────────────────────┐
                    │           SUBSTRATE                  │
                    │  (MAHAMANTRA_SEQUENCE = 16 OpCodes)  │
                    └───────────────┬─────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
    ┌───────▼───────┐       ┌───────▼───────┐       ┌───────▼───────┐
    │ ASHVAMEDHA    │       │  PRAKRITI     │       │  BALARAMA     │
    │ (Runtime Wrap)│       │ (File Bind)   │       │ (Method Proxy)│
    └───────────────┘       └───────────────┘       └───────────────┘
    Services that           ALL Python files        ALL method calls
    register willingly      (by existence)          (interception)

MATHEMATICS OF REINFORCEMENT:
When multiple Mantras meet, they AMPLIFY (not conflict):

    M_total = M_1 + M_2 + ... + M_n + (M_1 * M_2 * ... * M_n) / 108

The division by 108 ensures the total stays bounded but grows stronger.
This is the "resonance field" - more Mantras = stronger protection.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, HolyName, MantraOpCode

# =============================================================================
# THE FILE SIGNATURE (The Stamp of Prakriti)
# =============================================================================


@dataclass
class PrakritiSignature:
    """
    The Mahamantra stamp embedded in every blessed file.

    This signature is written into the file's docstring or header.
    It serves as proof that the file is under Prakriti's governance.
    """

    # Identity
    file_path: str  # Relative path from project root
    lineage: str  # Parent module (e.g., "vibe_core.protocols")
    sovereign: str  # Who blessed this file (system, human, agent)

    # Blessing
    mantra_hash: str  # SHA-256 of MAHAMANTRA_SEQUENCE
    blessed_at: str  # ISO timestamp

    # Resonance
    resonance_level: float  # 0.0 - 108.0 (how many blessings)

    def to_header(self) -> str:
        """Generate the header string for embedding in files."""
        return f"""# PRAKRITI BINDING
# ================
# Lineage: {self.lineage}
# Sovereign: {self.sovereign}
# Mantra: {self.mantra_hash[:16]}...
# Blessed: {self.blessed_at}
# Resonance: {self.resonance_level:.2f}
#
# HARE KRISHNA HARE KRISHNA KRISHNA KRISHNA HARE HARE
# HARE RAMA HARE RAMA RAMA RAMA HARE HARE
"""

    @classmethod
    def from_header(cls, header_text: str) -> Optional["PrakritiSignature"]:
        """Parse a header back into a signature."""
        patterns = {
            "file_path": r"# File: (.+)",
            "lineage": r"# Lineage: (.+)",
            "sovereign": r"# Sovereign: (.+)",
            "mantra_hash": r"# Mantra: ([a-f0-9]+)",
            "blessed_at": r"# Blessed: (.+)",
            "resonance_level": r"# Resonance: ([\d.]+)",
        }

        data: Dict[str, str] = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, header_text)
            if match:
                data[key] = match.group(1)

        if not data.get("lineage"):
            return None

        return cls(
            file_path=data.get("file_path", "unknown"),
            lineage=data.get("lineage", "unknown"),
            sovereign=data.get("sovereign", "unknown"),
            mantra_hash=data.get("mantra_hash", ""),
            blessed_at=data.get("blessed_at", ""),
            resonance_level=float(data.get("resonance_level", "0.0")),
        )


# =============================================================================
# THE MAHAMANTRA HASH (Immutable Identity)
# =============================================================================


def compute_mahamantra_hash() -> str:
    """
    Compute the SHA-256 hash of the MAHAMANTRA_SEQUENCE.

    This hash is the cryptographic identity of the Mantra.
    It's used to verify that the sequence hasn't been corrupted.
    """
    sequence_str = "|".join(f"{name}:{opcode.value}" for name, opcode in MAHAMANTRA_SEQUENCE)
    return hashlib.sha256(sequence_str.encode()).hexdigest()


# The immutable hash (computed once)
MAHAMANTRA_HASH = compute_mahamantra_hash()


# =============================================================================
# RESONANCE MATHEMATICS (Amplification, not Collision)
# =============================================================================


def compute_resonance(existing: float, new_blessing: float = 1.0) -> float:
    """
    Compute the new resonance level when a blessing is added.

    Formula: R_new = R_old + B + (R_old * B) / 108

    This ensures:
    - Each blessing adds at least its value
    - Multiple blessings create harmonic resonance
    - The /108 keeps the growth bounded but meaningful
    - Maximum theoretical resonance approaches 108 asymptotically

    Args:
        existing: Current resonance level (0.0 - 108.0)
        new_blessing: Strength of new blessing (default 1.0)

    Returns:
        New resonance level
    """
    additive = existing + new_blessing
    harmonic = (existing * new_blessing) / 108
    return min(108.0, additive + harmonic)


def resonance_to_protection(resonance: float) -> str:
    """
    Convert resonance level to protection status.

    0-1:    EXPOSED (No significant protection)
    1-8:    BLESSED (Basic Mahamantra protection)
    8-27:   PROTECTED (Strong protection)
    27-64:  SHIELDED (Very strong protection)
    64-108: INVINCIBLE (Maximum protection)
    """
    if resonance < 1:
        return "EXPOSED"
    elif resonance < 8:
        return "BLESSED"
    elif resonance < 27:
        return "PROTECTED"
    elif resonance < 64:
        return "SHIELDED"
    else:
        return "INVINCIBLE"


# =============================================================================
# PRAKRITI SCANNER (Reads all files, extracts signatures)
# =============================================================================


class PrakritiScanner:
    """
    Scans the codebase for Prakriti bindings.

    This is the "eye of Prakriti" - it sees all files,
    whether they cooperate or not.
    """

    def __init__(self, root_path: Path):
        self.root = root_path
        self._signatures: Dict[str, PrakritiSignature] = {}

    def scan(self) -> Dict[str, PrakritiSignature]:
        """Scan all Python files for Prakriti bindings."""
        for py_file in self.root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            sig = self._extract_signature(py_file)
            if sig:
                self._signatures[str(py_file.relative_to(self.root))] = sig

        return self._signatures

    def _extract_signature(self, file_path: Path) -> Optional[PrakritiSignature]:
        """Extract Prakriti signature from a file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for PRAKRITI BINDING header
            if "# PRAKRITI BINDING" in content:
                return PrakritiSignature.from_header(content)

            # No explicit binding - create implicit one
            return PrakritiSignature(
                file_path=str(file_path.relative_to(self.root)),
                lineage=self._infer_lineage(file_path),
                sovereign="prakriti",  # Implicit binding by existence
                mantra_hash=MAHAMANTRA_HASH,
                blessed_at=datetime.now().isoformat(),
                resonance_level=0.0,  # No explicit blessing
            )
        except Exception:
            return None

    def _infer_lineage(self, file_path: Path) -> str:
        """Infer the module lineage from file path."""
        relative = file_path.relative_to(self.root)
        parts = list(relative.parts)
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        return ".".join(parts)

    def get_unblessed(self) -> List[str]:
        """Get list of files with resonance < 1.0 (effectively unblessed)."""
        return [path for path, sig in self._signatures.items() if sig.resonance_level < 1.0]

    def get_protection_report(self) -> Dict[str, int]:
        """Get count of files by protection level."""
        report: Dict[str, int] = {
            "EXPOSED": 0,
            "BLESSED": 0,
            "PROTECTED": 0,
            "SHIELDED": 0,
            "INVINCIBLE": 0,
        }

        for sig in self._signatures.values():
            level = resonance_to_protection(sig.resonance_level)
            report[level] += 1

        return report


# =============================================================================
# BLESSING INJECTOR (Writes signatures into files)
# =============================================================================


class PrakritiBlesser:
    """
    Injects Prakriti bindings into Python files.

    This is the "hand of Prakriti" - it blesses files
    by writing the Mahamantra signature into them.
    """

    def __init__(self, root_path: Path, sovereign: str = "system"):
        self.root = root_path
        self.sovereign = sovereign

    def bless_file(self, file_path: Path, force: bool = False) -> bool:
        """
        Bless a file with Prakriti binding.

        Args:
            file_path: Path to the Python file
            force: If True, re-bless even if already blessed

        Returns:
            True if blessed, False if skipped
        """
        content = file_path.read_text(encoding="utf-8")

        # Check if already blessed
        if "# PRAKRITI BINDING" in content and not force:
            # Just increase resonance
            return self._increase_resonance(file_path, content)

        # Create signature
        sig = PrakritiSignature(
            file_path=str(file_path.relative_to(self.root)),
            lineage=self._infer_lineage(file_path),
            sovereign=self.sovereign,
            mantra_hash=MAHAMANTRA_HASH,
            blessed_at=datetime.now().isoformat(),
            resonance_level=1.0,  # Initial blessing
        )

        # Inject header after shebang/encoding if present
        header = sig.to_header()
        new_content = self._inject_header(content, header)

        file_path.write_text(new_content, encoding="utf-8")
        return True

    def _inject_header(self, content: str, header: str) -> str:
        """Inject header at appropriate position."""
        lines = content.split("\n")
        insert_pos = 0

        # Skip shebang
        if lines and lines[0].startswith("#!"):
            insert_pos = 1

        # Skip encoding declaration
        if len(lines) > insert_pos and "coding" in lines[insert_pos]:
            insert_pos += 1

        lines.insert(insert_pos, header)
        return "\n".join(lines)

    def _increase_resonance(self, file_path: Path, content: str) -> bool:
        """Increase resonance of already blessed file."""
        sig = PrakritiSignature.from_header(content)
        if not sig:
            return False

        new_resonance = compute_resonance(sig.resonance_level, 1.0)

        # Update resonance in file
        old_line = f"# Resonance: {sig.resonance_level:.2f}"
        new_line = f"# Resonance: {new_resonance:.2f}"
        new_content = content.replace(old_line, new_line)

        file_path.write_text(new_content, encoding="utf-8")
        return True

    def _infer_lineage(self, file_path: Path) -> str:
        """Infer module lineage from path."""
        relative = file_path.relative_to(self.root)
        parts = list(relative.parts)
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        return ".".join(parts)

    def bless_all(self, pattern: str = "**/*.py") -> int:
        """
        Bless all Python files matching pattern.

        Returns:
            Count of files blessed
        """
        count = 0
        for py_file in self.root.glob(pattern):
            if "__pycache__" not in str(py_file):
                if self.bless_file(py_file):
                    count += 1
        return count


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PrakritiSignature",
    "PrakritiScanner",
    "PrakritiBlesser",
    "MAHAMANTRA_HASH",
    "compute_resonance",
    "resonance_to_protection",
]
