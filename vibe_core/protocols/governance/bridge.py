"""
PROTOCOL BRIDGE - The Material-Spiritual Interface
===================================================
Sanskrit: Setu = Bridge (like Rama-Setu to Lanka)

"The bridge connects the material to the spiritual without polluting either."

This module provides the GOVERNANCE layer that connects ALL protocols
to their owning Mahajanas WITHOUT polluting the mahajanas/ folder.

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  protocols/*.py (Wild/Ungoverned)                                       │
    │       ↓                                                                 │
    │  governance/bridge.py (THIS FILE - Prakriti/Material Interface)         │
    │       ↓                                                                 │
    │  mahajanas/* (Purusha/Clean Spiritual Zone)                            │
    └─────────────────────────────────────────────────────────────────────────┘

DESIGN PRINCIPLES:
1. CLEAN BORDERS: mahajanas/ stays pure - no imports from wild protocols
2. OWNERSHIP: Every protocol has exactly ONE owning Mahajana
3. SECURITY LEVEL: Every protocol has a SecurityLevel (-1 to 4)
4. DISCOVERABLE: CLI can query any protocol's governance
5. WATERTIGHT: No Dict[str, Any] - all typed

USAGE:
    from vibe_core.protocols.governance.bridge import ProtocolBridge

    # Get owner of a protocol
    owner = ProtocolBridge.get_owner("defense.py")  # → Mahajana.YAMARAJA

    # List all protocols owned by a Mahajana
    protocols = ProtocolBridge.list_by_owner(Mahajana.BRAHMA)

    # Validate governance
    report = ProtocolBridge.audit()  # → GovernanceAudit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Dict,
    Final,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
)

from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.yamaraja.security import SecurityLevel


# =============================================================================
# WATERTIGHT TYPEDDICTS - Governance Data Contracts
# =============================================================================


class ProtocolEntry(TypedDict):
    """A single protocol's governance entry. WATERTIGHT."""

    name: str  # File name (e.g., "defense.py")
    path: str  # Relative path from protocols/ (e.g., "defense.py" or "universal/krishna.py")
    owner: str  # Mahajana name
    level: int  # SecurityLevel value
    category: str  # "core", "universal", "service", "utility"
    description: str  # Short description
    has_tests: bool  # Whether tests exist


class GovernanceAudit(TypedDict):
    """Result of governance audit. WATERTIGHT."""

    total_protocols: int
    governed_count: int
    ungoverned_count: int
    ungoverned_list: List[str]
    owner_distribution: Dict[str, int]  # Mahajana → count
    level_distribution: Dict[str, int]  # Level name → count
    health_score: float  # 0.0 to 1.0


class MahajanaPortfolio(TypedDict):
    """All protocols owned by a Mahajana. WATERTIGHT."""

    mahajana: str
    protocol_count: int
    protocols: List[ProtocolEntry]
    security_levels: List[int]


# =============================================================================
# PROTOCOL CATEGORY
# =============================================================================


class ProtocolCategory(str, Enum):
    """Categories of protocols based on their nature."""

    CORE = "core"  # Essential system protocols (kernel, ledger)
    UNIVERSAL = "universal"  # Transcendental (Vishnu-level)
    SUBSTRATE = "substrate"  # Foundation layer (Mahamantra)
    SERVICE = "service"  # Service protocols (agents, manifestation)
    UTILITY = "utility"  # Helper protocols (types, circuit)
    GOVERNANCE = "governance"  # Governance protocols (this folder)
    NAGA = "naga"  # Threat detection protocols
    AVATARA = "avatara"  # Avatara protocols


# =============================================================================
# THE GRAND MAPPING - Protocol → Mahajana
# =============================================================================
# This is the CONSTITUTION. Every protocol must be assigned.
# Format: "relative/path.py": (Mahajana, SecurityLevel, Category, Description)

_PROTOCOL_GOVERNANCE: Dict[str, Tuple[Mahajana, SecurityLevel, ProtocolCategory, str]] = {
    # =========================================================================
    # YAMARAJA (Judgment/Security) - Level -1 to 0
    # =========================================================================
    "defense.py": (Mahajana.YAMARAJA, SecurityLevel.SUBSTRATE, ProtocolCategory.CORE,
                   "4 Regulating Principles (DAYA, SATYAM, TAPAS, SAUCAM)"),
    "testable.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                    "Testing framework and assertions"),
    "testable_registry.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                             "Test discovery and registration"),
    "integrity.py": (Mahajana.YAMARAJA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                     "Data integrity verification"),
    "shuddhi.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                   "Purification protocols"),

    # =========================================================================
    # BHISHMA (Commitment/Vow) - Level 0
    # =========================================================================
    "ledger.py": (Mahajana.BHISHMA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                  "Immutable ledger protocol"),
    "lineage.py": (Mahajana.BHISHMA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                   "Parampara/lineage tracking"),
    "crypto.py": (Mahajana.BHISHMA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                  "Cryptographic operations"),

    # =========================================================================
    # JANAKA (State/Duty) - Level 0-1
    # =========================================================================
    "kernel_protocol.py": (Mahajana.JANAKA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                           "Kernel interface protocol"),
    "kernel_types.py": (Mahajana.JANAKA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                        "Kernel type definitions"),
    "state.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                 "State management"),
    "scheduler.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.SERVICE,
                     "Task scheduling"),
    "process.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.SERVICE,
                   "Process management"),

    # =========================================================================
    # BRAHMA (Creation) - Level 1-4
    # =========================================================================
    "agent.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                 "Agent manifest and lifecycle"),
    "manifestation.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                         "Entity manifestation"),
    "boot_protocol.py": (Mahajana.BRAHMA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                         "System boot sequence"),
    "registry.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                    "Manifest registry"),
    "capability.py": (Mahajana.BRAHMA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                      "Capability definitions"),
    "plugin.py": (Mahajana.BRAHMA, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                  "Plugin interface"),

    # =========================================================================
    # NARADA (Communication) - Level 2-4
    # =========================================================================
    "synapse.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                   "Inter-component messaging"),
    "event.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                 "Event protocol"),
    "feedback.py": (Mahajana.NARADA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                    "Feedback loops"),
    "network.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.SERVICE,
                   "Network protocol"),
    "chat.py": (Mahajana.NARADA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                "Chat protocol"),
    "language.py": (Mahajana.NARADA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                    "Language processing"),
    "translation.py": (Mahajana.NARADA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                       "Translation protocol"),

    # =========================================================================
    # SHAMBHU (Destruction/Cleanup) - Level 1-2
    # =========================================================================
    "circuit.py": (Mahajana.SHAMBHU, SecurityLevel.DEFENSE, ProtocolCategory.UTILITY,
                   "Circuit breaker pattern"),
    "correction.py": (Mahajana.SHAMBHU, SecurityLevel.DEFENSE, ProtocolCategory.SERVICE,
                      "Error correction"),

    # =========================================================================
    # KUMARAS (Knowledge/Purity) - Level 2-4
    # =========================================================================
    "cognition.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                     "Cognitive processing"),
    "memory.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                  "Memory protocol"),
    "reflection.py": (Mahajana.KUMARAS, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                      "Self-reflection"),
    "akashic.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                   "Akashic records"),

    # =========================================================================
    # KAPILA (Analysis/Sankhya) - Level 2-4
    # =========================================================================
    "primal.py": (Mahajana.KAPILA, SecurityLevel.NAGA, ProtocolCategory.CORE,
                  "Primal/fundamental analysis"),
    "reactor.py": (Mahajana.KAPILA, SecurityLevel.NAGA, ProtocolCategory.SERVICE,
                   "Reactive processing"),

    # =========================================================================
    # MANU (Law/Governance) - Level 0-2
    # =========================================================================
    "dharma.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                  "Dharma protocol"),
    "gad.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
               "Governance Architecture Document"),
    "governance_gate.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                           "Governance gates"),
    "governance/fractal_cli.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                                  "16-command fractal CLI protocol"),

    # =========================================================================
    # PRAHLADA (Devotion/Resilience) - Level 1-4
    # =========================================================================
    "om.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
              "OM - The primordial sound"),
    "vedic.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                 "Vedic protocols"),
    "prakriti_binding.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                            "Prakriti (nature) binding"),

    # =========================================================================
    # BALI (Surrender/Resources) - Level 2-4
    # =========================================================================
    "resource.py": (Mahajana.BALI, SecurityLevel.NAGA, ProtocolCategory.SERVICE,
                    "Resource management"),
    "economy.py": (Mahajana.BALI, SecurityLevel.PLUGIN, ProtocolCategory.SERVICE,
                   "Economic protocols"),

    # =========================================================================
    # SHUKA (Vision/Narration) - Level 2-4
    # =========================================================================
    "cli.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
               "CLI protocol"),
    "cli_execution.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                         "CLI execution"),
    "command.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                   "Command protocol"),
    "llm.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
               "LLM interface"),
    "opus.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                "Opus assistant protocol"),

    # =========================================================================
    # UTILITY PROTOCOLS (Various owners) - Level 3-4
    # =========================================================================
    "types.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.UTILITY,
                 "Common type definitions"),
    "intent.py": (Mahajana.KUMARAS, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                  "Intent protocol"),
    "task.py": (Mahajana.JANAKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                "Task protocol"),
    "cartridge.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                     "Cartridge protocol"),
    "section.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.UTILITY,
                   "Section protocol"),
    "steward.py": (Mahajana.JANAKA, SecurityLevel.APPLICATION, ProtocolCategory.SERVICE,
                   "Steward protocol"),
    "external.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.SERVICE,
                    "External integrations"),
    "identity.py": (Mahajana.BHISHMA, SecurityLevel.KERNEL, ProtocolCategory.CORE,
                    "Identity protocol"),
    "auditor.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                   "Audit protocol"),
    "operator_protocol.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.SERVICE,
                             "Operator protocol"),
    "system_shell.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.SERVICE,
                        "System shell"),

    # =========================================================================
    # SUBDIRECTORY PROTOCOLS
    # =========================================================================

    # --- governance/ ---
    "governance/dwarapala.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                                 "Gatekeepers (Jaya & Vijaya)"),
    "governance/yamaraja.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                                "Yamaraja gate"),
    "governance/bridge.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                              "Protocol governance bridge (this file)"),

    # --- universal/ (Vishnu-level - transcends Mahajanas) ---
    "universal/krishna.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                              "Krishna - The Supreme (Vishnu)"),
    "universal/bhagavan.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                               "Bhagavan - 6 Opulences"),
    "universal/purusha.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                              "Purusha - The Person"),
    "universal/gita.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                           "Bhagavad Gita wisdom"),
    "universal/dharma.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                             "Universal dharma"),
    "universal/guna.py": (Mahajana.KAPILA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                           "Three gunas (modes)"),
    "universal/kurukshetra.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                                  "Battle testing"),
    "universal/mantra.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                             "Mantra protocol"),
    "universal/ramanujan.py": (Mahajana.KAPILA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                                "Mathematical proof"),
    "universal/types.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                            "Universal types"),
    "universal/enforce.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                              "Enforcement"),
    "universal/bridge.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                             "Universal bridge"),
    "universal/sudarshana.py": (Mahajana.YAMARAJA, SecurityLevel.KERNEL, ProtocolCategory.UNIVERSAL,
                                 "Sudarshana chakra (protection)"),
    "universal/read_write.py": (Mahajana.JANAKA, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                                 "Read/write operations"),
    "universal/sync.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                           "Synchronization"),
    "universal/autobahn.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                               "Fast message highway"),
    "universal/semantic_router.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                                      "Semantic routing"),

    # --- substrate/ (Foundation - Mahamantra engine) ---
    "substrate/byte.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                           "MantraByte - packed ternary"),
    "substrate/engine.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                             "Mahamantra engine"),
    "substrate/cpu.py": (Mahajana.JANAKA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                          "MantraCPU - execution"),
    "substrate/gpu.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                          "MantraGPU - sankirtan"),
    "substrate/resonance.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                "Phonetic resonance"),

    # --- naga/ (Threat detection - Shuka's vision) ---
    "naga/takshaka.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                          "Input validation (Takshaka)"),
    "naga/kaliya.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Output sanitization (Kaliya)"),
    "naga/vasuki.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Threat coordination (Vasuki)"),
    "naga/ananta.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Ananta Shesha (infinite support)"),
    "naga/balarama.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                          "Balarama (strength)"),
    "naga/base.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                      "Base NAGA protocol"),
    "naga/chitragupta.py": (Mahajana.YAMARAJA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                             "Chitragupta (karma records)"),
    "naga/cli_command.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                             "NAGA CLI commands"),
    "naga/cortex.py": (Mahajana.KUMARAS, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "NAGA cortex (cognition)"),
    "naga/federation.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                            "NAGA federation"),
    "naga/flood.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                       "Flood detection"),
    "naga/garuda.py": (Mahajana.PRAHLADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Garuda (NAGA controller)"),
    "naga/groups.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "NAGA groups"),
    "naga/intel_bridge.py": (Mahajana.KUMARAS, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                              "Intelligence bridge"),
    "naga/kala.py": (Mahajana.YAMARAJA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                      "Kala (time/death)"),
    "naga/karkotaka.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                           "Karkotaka NAGA"),
    "naga/kulika.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Kulika NAGA"),
    "naga/narada.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                        "Narada integration"),
    "naga/nrisimha.py": (Mahajana.PRAHLADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                          "Nrisimha protection"),
    "naga/padma.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                       "Padma NAGA"),
    "naga/prahlad.py": (Mahajana.PRAHLADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                         "Prahlad resilience"),
    "naga/proxy.py": (Mahajana.NARADA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                       "NAGA proxy"),
    "naga/sesha.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                       "Sesha NAGA"),
    "naga/shankha.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                         "Shankha NAGA"),
    "naga/tuv.py": (Mahajana.YAMARAJA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                     "TÜV certification"),
    "naga/types.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                       "NAGA type definitions"),

    # --- avataras/ (Vishnu's incarnations) ---
    "avataras/nrisimha.py": (Mahajana.PRAHLADA, SecurityLevel.KERNEL, ProtocolCategory.AVATARA,
                              "Nrisimha - Protection"),
    "avataras/parashurama.py": (Mahajana.BHISHMA, SecurityLevel.DEFENSE, ProtocolCategory.AVATARA,
                                 "Parashurama - Warrior"),
    "avataras/prithu.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.AVATARA,
                            "Prithu - First King"),
    "avataras/vyasa.py": (Mahajana.SHUKA, SecurityLevel.DEFENSE, ProtocolCategory.AVATARA,
                           "Vyasa - Compiler"),

    # --- lila/ (Divine play) ---
    "lila/jagannath.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.SERVICE,
                           "Jagannath Puri lila"),

    # --- mahajanas/ (Pure zone - governance metadata only) ---
    "mahajanas/owned_protocol.py": (Mahajana.BRAHMA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                                     "Owned protocol base"),
    "mahajanas/protocol.py": (Mahajana.BRAHMA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                               "Mahajana protocol base"),
    "mahajanas/router.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                             "OpCode → Mahajana router"),
    "mahajanas/sabha.py": (Mahajana.MANU, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                            "Mahajana assembly"),
    "mahajanas/vyuha.py": (Mahajana.JANAKA, SecurityLevel.DEFENSE, ProtocolCategory.GOVERNANCE,
                            "Chatur-Vyuha architecture"),
    "mahajanas/shuka/naga.py": (Mahajana.SHUKA, SecurityLevel.NAGA, ProtocolCategory.NAGA,
                                 "Shuka's NAGA vision"),
    "mahajanas/yamaraja/security.py": (Mahajana.YAMARAJA, SecurityLevel.SUBSTRATE, ProtocolCategory.CORE,
                                        "SecurityProtocol"),

    # --- science/ (Analysis) ---
    "science/caitanya_kernel.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                                    "Caitanya consciousness kernel"),
    "science/entropy.py": (Mahajana.KAPILA, SecurityLevel.DEFENSE, ProtocolCategory.CORE,
                            "Entropy analysis"),

    # --- substrate/mantra/ (Sacred foundation) ---
    "substrate/bhava.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                            "Bhava (emotional states)"),
    "substrate/gene.py": (Mahajana.BRAHMA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                           "iGene protocol"),
    "substrate/nama.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                           "Holy Name"),
    "substrate/shakti.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                             "Shakti (energy)"),
    "substrate/tattva.py": (Mahajana.KAPILA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                             "Tattva (truth/elements)"),
    "substrate/mantra/acintya.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                     "Acintya (inconceivable)"),
    "substrate/mantra/aksara.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                    "Aksara (syllables)"),
    "substrate/mantra/diksha.py": (Mahajana.NARADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                    "Diksha (initiation)"),
    "substrate/mantra/mala.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                  "Mala (rosary/rounds)"),
    "substrate/mantra/pada.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                  "Pada (word)"),
    "substrate/mantra/prabhupada.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                        "Prabhupada (spiritual master)"),
    "substrate/mantra/routing.py": (Mahajana.MANU, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                     "Mantra routing"),
    "substrate/mantra/sadhana.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                     "Sadhana (practice)"),
    "substrate/mantra/vakya.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                   "Vakya (sentence)"),
    "substrate/mantra/varna.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.SUBSTRATE,
                                   "Varna (letters)"),

    # --- universal/ (remaining) ---
    "universal/cli.py": (Mahajana.SHUKA, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                          "Universal CLI"),
    "universal/infer.py": (Mahajana.KUMARAS, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                            "Inference engine"),
    "universal/intent_bridge.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                                    "Intent bridge"),
    "universal/jagannath.py": (Mahajana.PRAHLADA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                                "Jagannath protocol"),
    "universal/om.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                         "OM - primordial sound"),
    "universal/rama.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                           "Rama protocol"),
    "universal/resonance.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                                "Resonance protocol"),
    "universal/samsara.py": (Mahajana.SHAMBHU, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                              "Samsara (cycle of birth/death)"),
    "universal/steward.py": (Mahajana.JANAKA, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                              "Steward protocol"),
    "universal/store_recall.py": (Mahajana.KUMARAS, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                                   "Store/recall memory"),
    "universal/synapse.py": (Mahajana.NARADA, SecurityLevel.PLUGIN, ProtocolCategory.UNIVERSAL,
                              "Universal synapse"),
    "universal/the_37th.py": (Mahajana.PRAHLADA, SecurityLevel.SUBSTRATE, ProtocolCategory.UNIVERSAL,
                               "The 37th Principle (Divine Override)"),
    "universal/union.py": (Mahajana.BRAHMA, SecurityLevel.APPLICATION, ProtocolCategory.UNIVERSAL,
                            "Union types"),
    "universal/watertight.py": (Mahajana.YAMARAJA, SecurityLevel.DEFENSE, ProtocolCategory.UNIVERSAL,
                                 "Watertight type checking"),
}


# =============================================================================
# PROTOCOL BRIDGE CLASS
# =============================================================================


class ProtocolBridge:
    """
    The Bridge between wild protocols and Mahajana governance.

    This is the PRAKRITI layer - it touches the material (protocols)
    but connects to the spiritual (Mahajanas) without polluting either.

    DESIGN:
    - All queries go through this bridge
    - Mahajanas/ folder stays pure (no wild imports)
    - Wild protocols remain where they are (no forced migration)
    - Ownership is established through this registry
    """

    _instance: Optional["ProtocolBridge"] = None
    _protocols_root: Path = Path(__file__).parent.parent  # protocols/

    @classmethod
    def get_instance(cls) -> "ProtocolBridge":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_owner(cls, protocol_path: str) -> Optional[Mahajana]:
        """
        Get the owning Mahajana for a protocol.

        Args:
            protocol_path: Relative path from protocols/ (e.g., "defense.py")

        Returns:
            Mahajana owner or None if ungoverned
        """
        entry = _PROTOCOL_GOVERNANCE.get(protocol_path)
        if entry:
            return entry[0]
        return None

    @classmethod
    def get_level(cls, protocol_path: str) -> Optional[SecurityLevel]:
        """Get the security level for a protocol."""
        entry = _PROTOCOL_GOVERNANCE.get(protocol_path)
        if entry:
            return entry[1]
        return None

    @classmethod
    def get_category(cls, protocol_path: str) -> Optional[ProtocolCategory]:
        """Get the category for a protocol."""
        entry = _PROTOCOL_GOVERNANCE.get(protocol_path)
        if entry:
            return entry[2]
        return None

    @classmethod
    def get_entry(cls, protocol_path: str) -> Optional[ProtocolEntry]:
        """Get full governance entry for a protocol."""
        entry = _PROTOCOL_GOVERNANCE.get(protocol_path)
        if not entry:
            return None

        mahajana, level, category, description = entry
        return ProtocolEntry(
            name=Path(protocol_path).name,
            path=protocol_path,
            owner=mahajana.value,
            level=level.value,
            category=category.value,
            description=description,
            has_tests=cls._check_tests_exist(protocol_path),
        )

    @classmethod
    def list_by_owner(cls, mahajana: Mahajana) -> List[ProtocolEntry]:
        """List all protocols owned by a Mahajana."""
        result = []
        for path, (owner, level, category, desc) in _PROTOCOL_GOVERNANCE.items():
            if owner == mahajana:
                result.append(ProtocolEntry(
                    name=Path(path).name,
                    path=path,
                    owner=owner.value,
                    level=level.value,
                    category=category.value,
                    description=desc,
                    has_tests=cls._check_tests_exist(path),
                ))
        return result

    @classmethod
    def list_by_level(cls, level: SecurityLevel) -> List[ProtocolEntry]:
        """List all protocols at a security level."""
        result = []
        for path, (owner, proto_level, category, desc) in _PROTOCOL_GOVERNANCE.items():
            if proto_level == level:
                result.append(ProtocolEntry(
                    name=Path(path).name,
                    path=path,
                    owner=owner.value,
                    level=proto_level.value,
                    category=category.value,
                    description=desc,
                    has_tests=cls._check_tests_exist(path),
                ))
        return result

    @classmethod
    def list_by_category(cls, category: ProtocolCategory) -> List[ProtocolEntry]:
        """List all protocols in a category."""
        result = []
        for path, (owner, level, proto_cat, desc) in _PROTOCOL_GOVERNANCE.items():
            if proto_cat == category:
                result.append(ProtocolEntry(
                    name=Path(path).name,
                    path=path,
                    owner=owner.value,
                    level=level.value,
                    category=proto_cat.value,
                    description=desc,
                    has_tests=cls._check_tests_exist(path),
                ))
        return result

    @classmethod
    def get_portfolio(cls, mahajana: Mahajana) -> MahajanaPortfolio:
        """Get the full portfolio for a Mahajana."""
        protocols = cls.list_by_owner(mahajana)
        levels = sorted(set(p["level"] for p in protocols))
        return MahajanaPortfolio(
            mahajana=mahajana.value,
            protocol_count=len(protocols),
            protocols=protocols,
            security_levels=levels,
        )

    @classmethod
    def audit(cls) -> GovernanceAudit:
        """
        Audit the governance of all protocols.

        Scans the protocols/ directory and reports:
        - Total protocols found
        - How many are governed vs ungoverned
        - Distribution by owner and level
        """
        governed = set(_PROTOCOL_GOVERNANCE.keys())

        # Scan actual files
        actual_files: Set[str] = set()
        protocols_root = cls._protocols_root

        for py_file in protocols_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            if py_file.name.startswith("_"):
                continue  # Skip __init__.py etc.

            rel_path = str(py_file.relative_to(protocols_root))
            actual_files.add(rel_path)

        # Calculate ungoverned
        ungoverned = actual_files - governed
        ungoverned_list = sorted(ungoverned)

        # Owner distribution
        owner_dist: Dict[str, int] = {}
        for _, (owner, _, _, _) in _PROTOCOL_GOVERNANCE.items():
            owner_dist[owner.value] = owner_dist.get(owner.value, 0) + 1

        # Level distribution
        level_dist: Dict[str, int] = {}
        for _, (_, level, _, _) in _PROTOCOL_GOVERNANCE.items():
            level_dist[level.name] = level_dist.get(level.name, 0) + 1

        # Health score
        governed_count = len(governed & actual_files)
        total = len(actual_files)
        health = governed_count / total if total > 0 else 0.0

        return GovernanceAudit(
            total_protocols=total,
            governed_count=governed_count,
            ungoverned_count=len(ungoverned),
            ungoverned_list=ungoverned_list,
            owner_distribution=owner_dist,
            level_distribution=level_dist,
            health_score=round(health, 3),
        )

    @classmethod
    def _check_tests_exist(cls, protocol_path: str) -> bool:
        """Check if tests exist for a protocol."""
        # Simple heuristic - check tests/ folder
        name = Path(protocol_path).stem
        tests_root = cls._protocols_root.parent.parent / "tests"

        # Check common patterns
        patterns = [
            f"test_{name}.py",
            f"**/test_{name}.py",
            f"**/{name}/test_*.py",
        ]

        for pattern in patterns:
            if list(tests_root.glob(pattern)):
                return True
        return False


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_owner(protocol_path: str) -> Optional[Mahajana]:
    """Get owner of a protocol."""
    return ProtocolBridge.get_owner(protocol_path)


def list_by_owner(mahajana: Mahajana) -> List[ProtocolEntry]:
    """List protocols by owner."""
    return ProtocolBridge.list_by_owner(mahajana)


def audit() -> GovernanceAudit:
    """Run governance audit."""
    return ProtocolBridge.audit()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Bridge
    "ProtocolBridge",
    # Types
    "ProtocolEntry",
    "ProtocolCategory",
    "GovernanceAudit",
    "MahajanaPortfolio",
    # Convenience
    "get_owner",
    "list_by_owner",
    "audit",
]
