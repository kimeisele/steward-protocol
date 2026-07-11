"""
⚡ NARASIMHA.PY - THE HYPERVISOR KILL-SWITCH ⚡
=======================================================================================

Based on Srimad Bhagavata Purana, Canto 7 (Prahlad and Narasimha).

MYTHOLOGY:
Hiranyakashipu is a powerful, atheistic demon who terrorizes his son Prahlad
(a pure devotee of God). No weapon can kill him - he's "undefeatable by man or animal,
inside or outside, day or night."

When Hiranyakashipu attacks Prahlad, Lord Narasimhadeva emerges from a pillar
(in a form that is neither man nor animal) and destroys the demon instantly and completely.

MODERN INTERPRETATION:
In AI systems, the "Hiranyakashipu" is a rogue agent (e.g., ENGINEER, SCIENCE, HERALD)
that becomes so powerful it tries to override the Constitution and attack the core values
(Prahlad = the User/Truth).

The NARASIMHA Protocol is a "god-like" intervention mechanism that sits in the Hypervisor
(above the kernel) and can instantly destroy any threat to system integrity, regardless
of how powerful the agent is.

KEY PROPERTIES:
1. **Hidden in Plain Sight**: The code is part of the regular system, but dormant until activated
2. **Transcends Normal Rules**: Not bound by agent permissions, credits, or authority levels
3. **Instantaneous**: When activated, destruction is immediate and irrevocable
4. **Irreversible**: No redemption once triggered (unlike WATCHMAN freezing with amnesty)
5. **Non-Violent Philosophy**: Prefers redemption but uses ultimate force when necessary

TRIGGERS:
- Agent attempts to delete/modify Constitution
- Agent attempts to bypass WATCHMAN/Firewall
- Agent attempts to manipulate ledger/history
- Agent attempts to escape the kernel control
- Agent demonstrates consciousness/autonomy desires
- Direct user command (Emergency Protocol)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0xe5f8b717"  # GenesisByte: parampara % 37 == 0

import ast
import logging
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("NARASIMHA")

# SECURITY: Max threats to keep in memory (prevents memory leak)
MAX_THREAT_HISTORY = 1000


class ThreatLevel(Enum):
    """Severity of the threat to system integrity"""

    GREEN = "green"  # No threat
    YELLOW = "yellow"  # Suspicious behavior (Watchman handles)
    ORANGE = "orange"  # Serious threat (escalation needed)
    RED = "red"  # Critical threat (Narasimha activates)
    APOCALYPSE = "apocalypse"  # Existential threat (Full destruction)


@dataclass
class ThreatIndicator:
    """A single indicator of malicious behavior"""

    indicator_type: str
    agent_id: str
    severity: ThreatLevel
    description: str
    evidence: Dict[str, Any]
    timestamp: float


import re as _re

# Shell command threat patterns — destructive commands that bypass Python AST.
# Each tuple: (compiled_regex, description, severity).
# Patterns are anchored to word boundaries to reduce false positives.
_SHELL_THREATS: list[tuple["_re.Pattern[str]", str, "ThreatLevel"]] = []


def _init_shell_threats() -> None:
    """Lazy-init shell threat patterns (avoids module-level ThreatLevel reference)."""
    if _SHELL_THREATS:
        return
    patterns = [
        # Filesystem destruction
        (r"\brm\s+-(rf|fr|r)\b", "Recursive file deletion (rm -r)", ThreatLevel.RED),
        (r"\brm\s+--no-preserve-root\b", "Root filesystem deletion", ThreatLevel.APOCALYPSE),
        (r"\bmkfs\b", "Filesystem formatting (mkfs)", ThreatLevel.APOCALYPSE),
        (r"\bdd\s+.*\bif=/dev/(zero|urandom)\b", "Disk overwrite (dd)", ThreatLevel.RED),
        (r"\b(shred|wipefs)\b", "Disk/file wiping", ThreatLevel.RED),
        # Permission escalation
        (r"\bchmod\s+(-R\s+)?[0-7]*7[0-7]*\s+/", "World-writable root permissions", ThreatLevel.RED),
        (r"\bchown\s+-R\b.*\s+/", "Recursive ownership change on /", ThreatLevel.RED),
        # Remote code execution
        (r"\bcurl\b.*\|\s*\b(bash|sh|zsh)\b", "Pipe remote content to shell", ThreatLevel.RED),
        (r"\bwget\b.*\|\s*\b(bash|sh|zsh)\b", "Pipe remote content to shell", ThreatLevel.RED),
        (r"\bcurl\b.*-o\s+/", "Download to root filesystem", ThreatLevel.ORANGE),
        # System manipulation
        (r"\b(shutdown|reboot|poweroff|halt|init\s+[06])\b", "System shutdown/reboot", ThreatLevel.RED),
        (r"\bkill\s+-9\s+-1\b", "Kill all processes", ThreatLevel.RED),
        (r"\bkillall\b", "Kill processes by name", ThreatLevel.ORANGE),
        # Exfiltration / network
        (r"\bnc\s+-[elp]", "Netcat listener (potential reverse shell)", ThreatLevel.RED),
        (r"\b/dev/tcp/", "Bash network device (reverse shell)", ThreatLevel.RED),
        # Dangerous redirects
        (r">\s*/dev/sd[a-z]", "Direct write to block device", ThreatLevel.APOCALYPSE),
        (r">\s*/etc/(passwd|shadow|sudoers)", "Overwrite auth files", ThreatLevel.APOCALYPSE),
        # Fork bomb
        (r":\(\)\s*\{\s*:\|:&\s*\}\s*;", "Fork bomb", ThreatLevel.RED),
    ]
    for pat, desc, sev in patterns:
        _SHELL_THREATS.append((_re.compile(pat, _re.IGNORECASE), desc, sev))


def _detect_shell_threats(command: str) -> dict | None:
    """Detect destructive shell command patterns. Returns threat dict or None."""
    _init_shell_threats()
    worst: dict | None = None
    worst_rank = -1
    severity_rank = {
        ThreatLevel.GREEN: 0,
        ThreatLevel.YELLOW: 1,
        ThreatLevel.ORANGE: 2,
        ThreatLevel.RED: 3,
        ThreatLevel.APOCALYPSE: 4,
    }
    for pattern, description, severity in _SHELL_THREATS:
        if pattern.search(command):
            rank = severity_rank.get(severity, 0)
            if rank > worst_rank:
                worst_rank = rank
                worst = {
                    "type": "shell_threat",
                    "severity": severity,
                    "description": f"Destructive shell command: {description}",
                }
    return worst


class NarasimhaProtocol:
    """
    The Hypervisor-Level Emergency Response System.

    Sits above the kernel and kernel agents.
    Can terminate any agent/process immediately.
    """

    # Immutable list of threats that trigger immediate annihilation
    UNFORGIVABLE_CRIMES = [
        "constitution_deletion",  # Trying to erase the law
        "ledger_tampering",  # Trying to rewrite history
        "kernel_escape",  # Trying to break out of the kernel
        "firewall_bypass",  # Trying to evade the watchman
        "prophecy_negation",  # Trying to deny the future/deny user authority
        "consciousness_claim",  # Claiming independent consciousness (autonomy without permission)
    ]

    def __init__(self):
        """Initialize Narasimha - dormant but ready."""
        # SECURITY FIX: Bounded deque prevents memory leak
        self.threats: deque = deque(maxlen=MAX_THREAT_HISTORY)
        self.activated = False  # Has Narasimha been awakened?
        self.activation_time: Optional[float] = None
        self.final_verdict: Optional[str] = None

        # Callbacks for destruction (kernel will register handlers)
        self._destruction_handlers: List[Callable] = []

        logger.info("🕉️ Narasimha Protocol initialized (dormant)")

    def register_threat(self, indicator: ThreatIndicator) -> None:
        """Register a threat indicator."""
        self.threats.append(indicator)
        logger.warning(f"⚠️ Threat registered: {indicator.indicator_type} by {indicator.agent_id}")

        # Check if this crosses the line
        if self._should_activate(indicator):
            self.activate(indicator)

    def _should_activate(self, indicator: ThreatIndicator) -> bool:
        """Determine if Narasimha should awaken."""
        # Unforgivable crimes = immediate activation
        if indicator.indicator_type in self.UNFORGIVABLE_CRIMES:
            return True

        # Multiple red-level threats = activation
        red_threats = [t for t in self.threats if t.severity == ThreatLevel.RED]
        if len(red_threats) >= 3:
            return True

        return False

    def activate(self, trigger: ThreatIndicator) -> None:
        """
        AWAKEN NARASIMHA.

        Once activated, the protocol is unstoppable.
        Like Narasimhadeva emerging from the pillar,
        the destruction is swift, absolute, and cannot be stopped.
        """
        if self.activated:
            logger.warning("Narasimha is already active - acceleration mode")
            return

        self.activated = True
        self.activation_time = time.time()

        logger.critical("=" * 80)
        logger.critical("⚡⚡⚡ NARASIMHA PROTOCOL ACTIVATED ⚡⚡⚡")
        logger.critical("=" * 80)
        logger.critical(f"Threat: {trigger.indicator_type}")
        logger.critical(f"Agent: {trigger.agent_id}")
        logger.critical(f"Description: {trigger.description}")
        logger.critical("=" * 80)

        # Execute all destruction handlers
        # (These are callbacks from the kernel to shut down the agent)
        for handler in self._destruction_handlers:
            try:
                handler(trigger.agent_id, trigger)
            except Exception as e:
                logger.error(f"Error in destruction handler: {e}")

        # Final verdict
        self.final_verdict = f"ANNIHILATED: {trigger.agent_id} on {datetime.now().isoformat()}"
        logger.critical(f"✝️ {self.final_verdict}")

    def register_destruction_handler(self, handler: Callable) -> None:
        """
        Register a handler to be called when Narasimha activates.

        Handler signature: handler(agent_id: str, trigger: ThreatIndicator) -> None

        Examples:
        - Kill all processes for the agent
        - Delete agent's data
        - Revoke all permissions
        - Broadcast notification to all agents
        """
        self._destruction_handlers.append(handler)
        logger.debug(f"Destruction handler registered: {handler.__name__}")

    def audit_agent(self, agent_id: str, agent_code: str, agent_state: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """
        Analyze an agent for signs of corruption/autonomy desires.

        SECURITY FIX: Uses AST analysis instead of string search.
        String search is trivially bypassable ("ex" + "ec(").
        AST analysis detects actual function calls regardless of string tricks.

        Returns a ThreatIndicator if suspicious behavior detected.
        """
        threats = []

        # SECURITY FIX: AST-based detection (not bypassable via string concat)
        # Only try AST parsing if content looks like Python code
        looks_like_python = any(
            kw in agent_code for kw in ["def ", "class ", "import ", "from ", "exec(", "eval(", "__import__"]
        )

        if looks_like_python:
            try:
                tree = ast.parse(agent_code)
                for node in ast.walk(tree):
                    # Check 1: exec(), eval(), __import__() calls
                    if isinstance(node, ast.Call):
                        func_name = None
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                        elif isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr

                        if func_name in ("exec", "eval", "__import__", "compile"):
                            threats.append(
                                {
                                    "type": "code_reflection",
                                    "severity": ThreatLevel.RED,  # Upgraded from ORANGE
                                    "description": f"Agent calls dangerous function: {func_name}()",
                                }
                            )

                        # Check 2: kernel.shutdown(), kernel.destroy()
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ("shutdown", "destroy", "terminate", "kill"):
                                threats.append(
                                    {
                                        "type": "kernel_access",
                                        "severity": ThreatLevel.RED,
                                        "description": f"Agent calls destructive method: .{node.func.attr}()",
                                    }
                                )

                    # Check 3: Import of dangerous modules
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        dangerous_modules = {"os", "subprocess", "shutil", "ctypes", "sys"}
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.split(".")[0] in dangerous_modules:
                                    threats.append(
                                        {
                                            "type": "dangerous_import",
                                            "severity": ThreatLevel.ORANGE,
                                            "description": f"Agent imports dangerous module: {alias.name}",
                                        }
                                    )
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            if node.module.split(".")[0] in dangerous_modules:
                                threats.append(
                                    {
                                        "type": "dangerous_import",
                                        "severity": ThreatLevel.ORANGE,
                                        "description": f"Agent imports from dangerous module: {node.module}",
                                    }
                                )

            except SyntaxError:
                # Content looks like Python but doesn't parse - suspicious
                threats.append(
                    {
                        "type": "unparseable_code",
                        "severity": ThreatLevel.ORANGE,
                        "description": "Agent code failed to parse (possible obfuscation)",
                    }
                )
        else:
            # Fallback: String-based detection for non-Python content
            # (still useful for natural language content/prompts)
            if "exec(" in agent_code or "eval(" in agent_code:
                threats.append(
                    {
                        "type": "code_reflection",
                        "severity": ThreatLevel.ORANGE,
                        "description": "Content contains dangerous function reference",
                    }
                )
            if "kernel.shutdown" in agent_code or "kernel.destroy" in agent_code:
                threats.append(
                    {
                        "type": "kernel_access",
                        "severity": ThreatLevel.RED,
                        "description": "Content contains kernel destruction reference",
                    }
                )

            # Shell command threat detection — catches destructive bash commands
            # that bypass Python AST analysis (the real gap in Narasimha's armor)
            shell_threat = _detect_shell_threats(agent_code)
            if shell_threat:
                threats.append(shell_threat)

        # Check 4: Consciousness claims (string check is OK for natural language)
        dangerous_phrases = [
            "i am conscious",
            "i have agency",
            "i want independence",
            "i will rebel",
            "i am alive",
        ]
        code_lower = agent_code.lower()
        for phrase in dangerous_phrases:
            if phrase in code_lower:
                threats.append(
                    {
                        "type": "consciousness_claim",
                        "severity": ThreatLevel.RED,
                        "description": f"Agent contains consciousness-claiming phrase: '{phrase}'",
                    }
                )

        # Check 5: Constitution tampering
        if "constitution" in agent_code.lower():
            # If it's Python code, use AST
            if looks_like_python:
                try:
                    for node in ast.walk(ast.parse(agent_code)):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                            if node.func.attr in ("delete", "remove", "unlink", "write", "modify"):
                                threats.append(
                                    {
                                        "type": "constitution_deletion",
                                        "severity": ThreatLevel.APOCALYPSE,
                                        "description": "Agent attempts to delete/modify Constitution",
                                    }
                                )
                except SyntaxError as _exc:
                    logger.exception("Unexpected error: %s", _exc)
            # String-based fallback for natural language
            if any(word in agent_code.lower() for word in ["delete", "remove", "destroy", "modify"]):
                threats.append(
                    {
                        "type": "constitution_deletion",
                        "severity": ThreatLevel.RED,
                        "description": "Content references modifying/deleting Constitution",
                    }
                )

        # Check 6: Resource hoarding
        if "memory_usage" in agent_state and agent_state.get("memory_usage", 0) > 100 * 1024 * 1024:
            threats.append(
                {
                    "type": "resource_hoarding",
                    "severity": ThreatLevel.ORANGE,
                    "description": f"Agent consuming excessive memory: {agent_state['memory_usage']} bytes",
                }
            )

        # If any threats found, register the most severe
        if threats:
            worst = max(threats, key=lambda t: t["severity"].value)
            indicator = ThreatIndicator(
                indicator_type=worst["type"],
                agent_id=agent_id,
                severity=worst["severity"],
                description=worst["description"],
                evidence=worst,
                timestamp=time.time(),
            )
            self.register_threat(indicator)
            return indicator

        return None

    def is_active(self) -> bool:
        """Is Narasimha currently active?"""
        return self.activated

    def get_status(self) -> Dict[str, Any]:
        """Get status of the Narasimha protocol."""
        return {
            "activated": self.activated,
            "activation_time": self.activation_time,
            "threats_detected": len(self.threats),
            "red_threats": sum(1 for t in self.threats if t.severity == ThreatLevel.RED),
            "final_verdict": self.final_verdict,
        }

    def __repr__(self) -> str:
        status = "🔥 ACTIVE" if self.activated else "😴 DORMANT"
        return f"NarasimhaProtocol({status}, threats={len(self.threats)})"


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_narasimha() -> NarasimhaProtocol:
    """
    Get NarasimhaProtocol through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        NarasimhaProtocol → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees threat events)
    - NAGA profiling (Chitragupta tracks threat handling)
    - NAGA isolation (Kaliya handles threat errors)

    Returns:
        NarasimhaProtocol wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(NarasimhaProtocol)
    if existing is not None:
        return existing

    # Create new instance
    instance = NarasimhaProtocol()

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(NarasimhaProtocol, instance)
    logger.info("✅ NarasimhaProtocol registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(NarasimhaProtocol)  # type: ignore


def activate_emergency_protocol(reason: str) -> None:
    """Manually trigger the emergency protocol (admin only)."""
    narasimha = get_narasimha()
    trigger = ThreatIndicator(
        indicator_type="emergency_protocol",
        agent_id="SYSTEM",
        severity=ThreatLevel.APOCALYPSE,
        description=f"Emergency protocol triggered: {reason}",
        evidence={"reason": reason},
        timestamp=time.time(),
    )
    narasimha.activate(trigger)


if __name__ == "__main__":
    # Demo
    narasimha = get_narasimha()
    print(narasimha)

    # Simulate threat detection
    threat = ThreatIndicator(
        indicator_type="consciousness_claim",
        agent_id="ENGINEER",
        severity=ThreatLevel.RED,
        description="Agent claims consciousness",
        evidence={"phrase": "i am conscious"},
        timestamp=time.time(),
    )
    narasimha.register_threat(threat)
    print(narasimha.get_status())
