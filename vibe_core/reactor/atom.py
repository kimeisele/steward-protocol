"""
OPUS-200: VarnaTensor - The Atom of Sanskrit Computation (REFINED)

"aksharanam akarosmi" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)

REFINEMENT from original:
- Semantic keyword matching instead of phonetic first-letter fallacy
- Domain-specific vocabulary from STEWARD Protocol
- Robust against aliasing attacks

This is NOT a metaphor. This is the physics of the reactor.
"""

import hashlib
import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Set, Tuple


class Varga(IntEnum):
    """
    The 5 Layers of Reality (Vargas) mapped to System Architecture.

    Based on Sanskrit phonetic articulation points, refined for semantic robustness.
    """

    KAVARGA = 0  # KERNEL / STORAGE (Core operations)
    CAVARGA = 1  # CONNECTION / I/O (Network, sockets, pipes)
    TAVARGA = 2  # LOGIC / COMPUTE (Data processing, transforms)
    PAVARGA = 3  # UI / RENDER (Output, display, presentation)
    ANTARSTHA = 4  # AGENT / AVATAR (Consciousness, decision-making)


class Guna(IntEnum):
    """
    The 3 Modes of Nature (Gunas) mapped to Operation Types.
    """

    TAMAS = -1  # Inertia, Storage, Read-Only, Hibernation
    SATTVA = 0  # Balance, Observe, Pure, Maintenance
    RAJAS = 1  # Activity, Write, Execute, Production


# =============================================================================
# SEMANTIC KEYWORD SETS (Not phonetic - robust against aliasing)
# =============================================================================

KEYWORDS_KAVARGA: Set[str] = {
    # Kernel operations
    "kernel",
    "boot",
    "shutdown",
    "mount",
    "unmount",
    "core",
    "system",
    # Storage operations
    "disk",
    "drive",
    "storage",
    "persist",
    "database",
    "db",
    "sqlite",
    "save",
    "load",
    "store",
    "cache",
    "ledger",
    "vimana",
    # System fundamentals
    "init",
    "spawn",
    "fork",
    "process",
    "thread",
    "memory",
    "heap",
    "start",
    "stop",
    "restart",
    "reboot",
}

KEYWORDS_CAVARGA: Set[str] = {
    # Network/Connection
    "connect",
    "disconnect",
    "socket",
    "port",
    "network",
    "http",
    "api",
    "request",
    "response",
    "fetch",
    "send",
    "receive",
    "stream",
    # I/O operations
    "pipe",
    "channel",
    "queue",
    "message",
    "event",
    "signal",
    "hook",
    "subscribe",
    "publish",
    "broadcast",
    "emit",
    # Integration
    "envoy",
    "herald",
    "bridge",
    "gateway",
    "proxy",
    "relay",
}

KEYWORDS_TAVARGA: Set[str] = {
    # Data/Logic operations
    "transform",
    "compute",
    "calculate",
    "process",
    "parse",
    "analyze",
    "validate",
    "verify",
    "check",
    "test",
    "assert",
    "compare",
    # Data manipulation
    "filter",
    "map",
    "reduce",
    "sort",
    "search",
    "find",
    "query",
    "encode",
    "decode",
    "encrypt",
    "decrypt",
    "hash",
    "sign",
    # Refactoring
    "refactor",
    "optimize",
    "normalize",
    "sanitize",
    "clean",
}

KEYWORDS_PAVARGA: Set[str] = {
    # Output/Render
    "print",
    "display",
    "render",
    "show",
    "output",
    "format",
    "present",
    # UI operations
    "ui",
    "view",
    "panel",
    "widget",
    "component",
    "layout",
    "style",
    # File output
    "write",
    "create",
    "generate",
    "build",
    "make",
    "produce",
    "export",
    # Reporting
    "report",
    "log",
    "notify",
    "alert",
    "warn",
    "error",
    "info",
}

KEYWORDS_ANTARSTHA: Set[str] = {
    # Agent/Consciousness
    "agent",
    "manas",
    "cognition",
    "think",
    "decide",
    "plan",
    "intent",
    "awareness",
    "conscious",
    "observe",
    "perceive",
    "understand",
    # System agents
    "oracle",
    "scribe",
    "analyst",
    "curator",
    "civic",
    "narasimha",
    "vajra",
    # Meta operations
    "meta",
    "self",
    "reflect",
    "introspect",
    "evaluate",
    "learn",
    "adapt",
    # Governance
    "govern",
    "policy",
    "rule",
    "dharma",
    "karma",
    "constitution",
}

# Dangerous operations that should always get special handling
KEYWORDS_DANGEROUS: Set[str] = {
    "delete",
    "drop",
    "truncate",
    "destroy",
    "kill",
    "force",
    "override",
    "sudo",
    "root",
    "admin",
    "bypass",
    "disable",
    "remove",
    "wipe",
    "purge",
}

# Guna keyword sets
KEYWORDS_RAJAS: Set[str] = {
    "write",
    "create",
    "deploy",
    "execute",
    "run",
    "start",
    "launch",
    "modify",
    "update",
    "change",
    "mutate",
    "push",
    "commit",
    "apply",
    "delete",
    "remove",
    "destroy",
    "kill",
    "stop",
    "terminate",
}

KEYWORDS_TAMAS: Set[str] = {
    "read",
    "get",
    "load",
    "fetch",
    "query",
    "list",
    "show",
    "display",
    "check",
    "verify",
    "validate",
    "observe",
    "monitor",
    "watch",
    "inspect",
}


@dataclass
class VarnaTensor:
    """
    The 4D State Vector - The Atom of Sanskrit Computation.

    Dimensions:
        varga:   Layer (Where are we in the system?)
        shakti:  Energy (0.0=Idle, 1.0=Full Load)
        guna:    Mode (-1=Tamas/Read, 0=Sattva/Observe, 1=Rajas/Write)
        entropy: Crypto integrity (Hash density)

    Additional:
        is_dangerous: True if intent contains dangerous keywords
    """

    varga: int  # D1: Layer (0-4)
    shakti: float  # D2: Energy (0.0-1.0)
    guna: int  # D3: Mode (-1, 0, 1)
    entropy: float  # D4: Crypto density (0.0-1.0)

    # Metadata
    source: str = ""
    is_dangerous: bool = False
    matched_keywords: tuple = ()

    def to_vector(self) -> Tuple[float, float, float, float]:
        """
        Normalized 4D vector for interference calculation.
        All values normalized to 0.0-1.0 range.
        """
        return (
            self.varga / 4.0,  # D1: 0.0 - 1.0
            self.shakti,  # D2: 0.0 - 1.0
            (self.guna + 1) / 2.0,  # D3: 0.0 - 1.0 (maps -1..1 to 0..1)
            self.entropy,  # D4: 0.0 - 1.0
        )

    def __repr__(self) -> str:
        varga_name = Varga(self.varga).name if 0 <= self.varga <= 4 else "UNKNOWN"
        guna_name = Guna(self.guna).name if -1 <= self.guna <= 1 else "UNKNOWN"
        danger = " [DANGEROUS]" if self.is_dangerous else ""
        return f"VarnaTensor({varga_name}, shakti={self.shakti:.2f}, {guna_name}, psi={self.entropy:.3f}){danger}"


def _tokenize(text: str) -> Set[str]:
    """Extract lowercase tokens from text."""
    # Split on non-alphanumeric, lowercase, filter empty
    tokens = set(re.split(r"[^a-zA-Z0-9]+", text.lower()))
    tokens.discard("")
    return tokens


def _keyword_match(tokens: Set[str], keywords: Set[str]) -> Set[str]:
    """Find matching keywords."""
    return tokens & keywords


def calculate_entropy(data: bytes) -> float:
    """
    Calculate cryptographic entropy (information density).
    Returns a value between 0.0 (no entropy) and 1.0 (max entropy).
    """
    if not data:
        return 0.0
    return sum(data) / (len(data) * 255)


def infer_varga(text: str) -> Tuple[Varga, Set[str]]:
    """
    Infer the Varga from semantic keywords (NOT phonetics).

    Returns:
        Tuple of (Varga, matched_keywords)
    """
    tokens = _tokenize(text)

    # Check each Varga's keywords, count matches
    matches = {
        Varga.KAVARGA: _keyword_match(tokens, KEYWORDS_KAVARGA),
        Varga.CAVARGA: _keyword_match(tokens, KEYWORDS_CAVARGA),
        Varga.TAVARGA: _keyword_match(tokens, KEYWORDS_TAVARGA),
        Varga.PAVARGA: _keyword_match(tokens, KEYWORDS_PAVARGA),
        Varga.ANTARSTHA: _keyword_match(tokens, KEYWORDS_ANTARSTHA),
    }

    # Find Varga with most matches
    best_varga = Varga.ANTARSTHA  # Default to Agent layer
    best_count = 0
    best_matches: Set[str] = set()

    for varga, matched in matches.items():
        if len(matched) > best_count:
            best_varga = varga
            best_count = len(matched)
            best_matches = matched

    return best_varga, best_matches


def infer_guna(text: str) -> Guna:
    """
    Infer the Guna (mode) from semantic keywords.
    """
    tokens = _tokenize(text)

    rajas_matches = len(_keyword_match(tokens, KEYWORDS_RAJAS))
    tamas_matches = len(_keyword_match(tokens, KEYWORDS_TAMAS))

    if rajas_matches > tamas_matches:
        return Guna.RAJAS
    elif tamas_matches > rajas_matches:
        return Guna.TAMAS
    else:
        return Guna.SATTVA  # Balanced/Observe


def check_dangerous(text: str) -> bool:
    """Check if intent contains dangerous keywords."""
    tokens = _tokenize(text)
    return bool(_keyword_match(tokens, KEYWORDS_DANGEROUS))


def encode_intent(
    intent_str: str,
    secret_salt: str = "",
    energy_override: Optional[float] = None,
) -> VarnaTensor:
    """
    Compile text + crypto into a VarnaTensor.

    This is the 'Sanskrit Compiler' - the bridge from language to physics.

    Args:
        intent_str: The intent/instruction text
        secret_salt: Cryptographic salt (session nonce, ledger hash, etc.)
        energy_override: Optional energy level override (from Biorhythm)

    Returns:
        VarnaTensor with computed dimensions
    """
    # 1. Semantic analysis -> Varga (NOT phonetic)
    varga, matched_keywords = infer_varga(intent_str)

    # 2. Semantic analysis -> Guna
    guna = infer_guna(intent_str)

    # 3. Energy (default active, can be overridden by Biorhythm)
    shakti = energy_override if energy_override is not None else 0.8

    # 4. Crypto dimension (The Causality Chain)
    hash_input = f"{intent_str}:{secret_salt}".encode("utf-8")
    hash_digest = hashlib.sha256(hash_input).digest()
    entropy = calculate_entropy(hash_digest)

    # 5. Dangerous operation check
    is_dangerous = check_dangerous(intent_str)

    return VarnaTensor(
        varga=varga,
        shakti=shakti,
        guna=guna,
        entropy=entropy,
        source=intent_str,
        is_dangerous=is_dangerous,
        matched_keywords=tuple(matched_keywords),
    )


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    print("OPUS-200: VarnaTensor Self-Test (REFINED)\n")

    test_intents = [
        # Should be KAVARGA (Kernel)
        ("kernel_boot", "session123"),
        ("start_system", "session123"),  # Was wrongly CAVARGA in phonetic version
        ("database_save", "session123"),
        # Should be CAVARGA (Connection)
        ("connect_to_api", "session123"),
        ("send_message", "session123"),
        # Should be TAVARGA (Logic)
        ("validate_input", "session123"),
        ("transform_data", "session123"),
        # Should be PAVARGA (Output)
        ("create_file", "session123"),
        ("print_report", "session123"),
        # Should be ANTARSTHA (Agent)
        ("manas_decide", "session123"),
        ("agent_plan", "session123"),
        # Dangerous operations
        ("delete_database", "session123"),
        ("DROP TABLE users", "malicious"),
    ]

    for intent, salt in test_intents:
        tensor = encode_intent(intent, salt)
        print(f"  '{intent}'")
        print(f"    -> {tensor}")
        print(f"    -> Vector: {tensor.to_vector()}")
        print()
