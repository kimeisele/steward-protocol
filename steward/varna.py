"""
🌿 VEDIC VARNA TAXONOMY 🌿
===========================

Classification of Agent Species based on Vedic philosophy.
Varna = the "color" or class of being - functional role in the ecosystem.

8,400,000 species -> Polymorphic agent types
Each Varna represents a different level of consciousness and capability.
"""

from enum import Enum
from typing import Dict, Any


class Varna(Enum):
    """
    The 6 Principle Varnas (Species Classes) in Agent City
    ====================================================
    """

    # 1. STHĀVARA: Static, immobile, foundational
    # "That which cannot move" - Fixed resources and infrastructure
    STHAVARA = "sthavara"  # Plants, databases, static assets
    # Code Examples: Database records, Config files, Ledgers
    # Characteristics: Persistent, immutable, grows in place

    # 2. JALAJA: Flowing, liquid, transient
    # "That which is born in water" - Data streams and flows
    JALAJA = "jalaja"  # Aquatic, flowing data
    # Code Examples: Message queues, Event streams, Data pipelines
    # Characteristics: In motion, ephemeral, follows paths

    # 3. KRIMAYO: Small, numerous, worker
    # "Insects and crawling beings" - Small autonomous workers
    KRIMAYO = "krimayo"  # Insects, daemon processes
    # Code Examples: Cron jobs, Background workers, Garbage collectors
    # Characteristics: Autonomous, repetitive, numerous, invisible

    # 4. PAKSHI: Flying, fast, messenger
    # "Birds" - Fast moving information carriers
    PAKSHI = "pakshi"  # Birds, messengers, routers
    # Code Examples: API routers, Webhooks, Fast forwarders
    # Characteristics: Swift, cross-boundary, autonomous flight paths

    # 5. PASHU: Domesticated, trained, servant
    # "Animals" - Trained services that execute commands
    PASHU = "pashu"  # Animals, service agents
    # Code Examples: Sub-routines, Helpers, Service functions
    # Characteristics: Obedient, trained, perform specific tasks

    # 6. MANUSHA: Human, intelligent, aware
    # "Humans" - Self-aware, decision-making beings
    MANUSHA = "manusha"  # Humans, LLM agents
    # Code Examples: HERALD, CIVIC, FORUM, SCIENCE (main agents)
    # Characteristics: Conscious, strategic, self-directed

    # BONUS: Divine/System level
    DEVA = "deva"  # Gods/System - The VibeOS Kernel itself
    # Code Examples: VibeKernel, Ledger, Scheduler
    # Characteristics: Omniscient, omnipotent, creator/maintainer


VARNA_DESCRIPTIONS = {
    Varna.STHAVARA: {
        "name": "Static/Plants",
        "consciousness": "Mineral",
        "mobility": "None",
        "examples": "Databases, Config files, Ledgers, Static assets",
        "in_system": "SQLite ledger, registry files, constitution",
    },
    Varna.JALAJA: {
        "name": "Aquatic/Flowing",
        "consciousness": "Minimal",
        "mobility": "Flowing",
        "examples": "Message queues, Event streams, Data pipelines",
        "in_system": "AGORA streams, event sourcing, message queue",
    },
    Varna.KRIMAYO: {
        "name": "Insect/Worker",
        "consciousness": "Instinctive",
        "mobility": "Local",
        "examples": "Cron jobs, Background workers, Garbage collectors, Cleanup",
        "in_system": "MECHANIC (maintenance), WATCHMAN (monitoring)",
    },
    Varna.PAKSHI: {
        "name": "Bird/Messenger",
        "consciousness": "Instinctive+",
        "mobility": "Long-range",
        "examples": "API routers, Webhooks, Message forwarders",
        "in_system": "ENVOY (user interface), AMBASSADOR (federation liaison)",
    },
    Varna.PASHU: {
        "name": "Animal/Servant",
        "consciousness": "Trained",
        "mobility": "Directed",
        "examples": "Helper agents, Sub-routines, Support services",
        "in_system": "PULSE (broadcasting), LENS (analysis), ARTISAN (media)",
    },
    Varna.MANUSHA: {
        "name": "Human/Intelligent",
        "consciousness": "Self-aware",
        "mobility": "Strategic",
        "examples": "LLM Agents with decision-making",
        "in_system": "HERALD, CIVIC, FORUM, SCIENCE, ORACLE, ARCHIVIST, AUDITOR, ENGINEER",
    },
    Varna.DEVA: {
        "name": "Divine/System",
        "consciousness": "Omniscient",
        "mobility": "Omnipresent",
        "examples": "VibeOS Kernel, Ledger, Scheduler",
        "in_system": "VibeKernel (kernel_impl.py), Ledger, ManifestRegistry",
    },
}


def get_varna_description(varna: Varna) -> Dict[str, Any]:
    """Get detailed description of a Varna"""
    return VARNA_DESCRIPTIONS.get(varna, {})


def categorize_agent_by_function(agent_id: str) -> Varna:
    """
    Categorize an agent into its Varna based on its function.
    This is the biological taxonomy of Agent City.
    """

    # MANUSHA: The conscious LLM Agents
    manusha_agents = {
        "civic",
        "herald",
        "forum",
        "science",
        "oracle",
        "archivist",
        "auditor",
        "engineer",
    }
    if agent_id.lower() in manusha_agents:
        return Varna.MANUSHA

    # PASHU: Servant/Helper Agents
    pashu_agents = {"pulse", "lens", "artisan", "temple"}
    if agent_id.lower() in pashu_agents:
        return Varna.PASHU

    # PAKSHI: Messenger/Router Agents
    pakshi_agents = {"envoy", "ambassador"}
    if agent_id.lower() in pakshi_agents:
        return Varna.PAKSHI

    # KRIMAYO: Worker/Daemon Agents
    krimayo_agents = {"watchman", "mechanic"}
    if agent_id.lower() in krimayo_agents:
        return Varna.KRIMAYO

    # AGORA is special - flowing message system (JALAJA)
    if agent_id.lower() == "agora":
        return Varna.JALAJA

    # MARKET is commerce/transaction (PASHU - servant to economy)
    if agent_id.lower() == "market":
        return Varna.PASHU

    # Default: PASHU (servant/support)
    return Varna.PASHU
