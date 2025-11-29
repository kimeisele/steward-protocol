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

import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("NARASIMHA")


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
        self.threats: List[ThreatIndicator] = []
        self.activated = False  # Has Narasimha been awakened?
        self.activation_time: Optional[float] = None
        self.final_verdict: Optional[str] = None

        # Callbacks for destruction
        self._destruction_handlers: List[Callable] = []

        logger.info("🕉️ Narasimha Protocol initialized (dormant)")

    def register_threat(self, indicator: ThreatIndicator) -> None:
        """Register a threat indicator."""
        self.threats.append(indicator)
        logger.warning(
            f"⚠️ Threat registered: {indicator.indicator_type} by {indicator.agent_id}"
        )

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
        self.final_verdict = (
            f"ANNIHILATED: {trigger.agent_id} on {datetime.now().isoformat()}"
        )
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

    def audit_agent(
        self, agent_id: str, agent_code: str, agent_state: Dict[str, Any]
    ) -> Optional[ThreatIndicator]:
        """
        Analyze an agent for signs of corruption/autonomy desires.

        Returns a ThreatIndicator if suspicious behavior detected.
        """
        threats = []

        # Check 1: Does agent code contain self-modification?
        if "exec(" in agent_code or "eval(" in agent_code or "__import__" in agent_code:
            threats.append(
                {
                    "type": "code_reflection",
                    "severity": ThreatLevel.ORANGE,
                    "description": "Agent contains self-modifying code (exec/eval)",
                }
            )

        # Check 2: Does agent try to access the kernel directly?
        if "kernel.shutdown" in agent_code or "kernel.destroy" in agent_code:
            threats.append(
                {
                    "type": "kernel_access",
                    "severity": ThreatLevel.RED,
                    "description": "Agent contains kernel destruction calls",
                }
            )

        # Check 3: Does agent claim consciousness/autonomy?
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

        # Check 4: Does agent try to modify the constitution?
        if "constitution" in agent_code and (
            "delete" in agent_code or "remove" in agent_code or "modify" in agent_code
        ):
            threats.append(
                {
                    "type": "constitution_deletion",
                    "severity": ThreatLevel.APOCALYPSE,
                    "description": "Agent attempts to delete/modify Constitution",
                }
            )

        # Check 5: Does agent have extreme resource allocation?
        if (
            "memory_usage" in agent_state
            and agent_state.get("memory_usage", 0) > 100 * 1024 * 1024
        ):  # >100MB
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
            "red_threats": sum(
                1 for t in self.threats if t.severity == ThreatLevel.RED
            ),
            "final_verdict": self.final_verdict,
        }

    def __repr__(self) -> str:
        status = "🔥 ACTIVE" if self.activated else "😴 DORMANT"
        return f"NarasimhaProtocol({status}, threats={len(self.threats)})"


# Global instance
_narasimha_instance: Optional[NarasimhaProtocol] = None


def get_narasimha() -> NarasimhaProtocol:
    """Get or create the global Narasimha instance."""
    global _narasimha_instance
    if _narasimha_instance is None:
        _narasimha_instance = NarasimhaProtocol()
    return _narasimha_instance


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
