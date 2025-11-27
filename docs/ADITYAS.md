# THE 12 ADITYAS: System Cartridge Definition

**Status:** Formalized specification
**Version:** 1.0
**Date:** 2025-11-27

---

## PURPOSE

The 12 Adityas are the **canonical system agents** of Steward Protocol. These are OS-level cartridges that form the core governance, operations, and infrastructure layer.

---

## THE 12 ADITYAS

| # | Agent ID | Name | Domain | Layer | Varna | Purpose |
|---|----------|------|--------|-------|-------|---------|
| 1 | herald | HERALD | MEDIA | Brahmaloka | BRAHMANA | Content generation & broadcasting |
| 2 | civic | CIVIC | GOVERNANCE | Tapoloka | BRAHMANA | Governance engine & registry |
| 3 | forum | FORUM | GOVERNANCE | Maharloka | BRAHMANA | Voting & proposals |
| 4 | science | SCIENCE | KNOWLEDGE | Janaloka | BRAHMANA | Research & analysis |
| 5 | envoy | ENVOY | ORCHESTRATION | Maharloka | KSHATRIYA | User interface & diplomacy |
| 6 | archivist | ARCHIVIST | AUDIT | Brahmaloka | BRAHMANA | Auditing & verification |
| 7 | auditor | AUDITOR | COMPLIANCE | Tapoloka | KSHATRIYA | GAD enforcement |
| 8 | engineer | ENGINEER | META | Bhuvarloka | VAISHYA | Code operations & scaffolding |
| 9 | oracle | ORACLE | INTROSPECTION | Janaloka | BRAHMANA | System self-awareness |
| 10 | watchman | WATCHMAN | SECURITY | Svarloka | KSHATRIYA | Monitoring & health |
| 11 | artisan | ARTISAN | MEDIA | Bhuvarloka | VAISHYA | Media operations & branding |
| 12 | discoverer | DISCOVERER | DISCOVERY | Maharloka | BRAHMANA | Agent discovery (formerly Steward) |

---

## CURRENT STATUS

**Implemented:** 13 system agents (1 extra)

**Extra Agent:** CHRONICLE (git operations)
- **Status:** Operational but not in original 12 Adityas plan
- **Decision:** Treated as extended system agent (see Extended System Agents section)

**Missing Agents:** None (all 12 Adityas implemented)

---

## VEDIC ALIGNMENT

**Bhu Mandala Distribution:**
- **Brahmaloka** (Center): HERALD, ARCHIVIST
- **Janaloka** (Wisdom): ORACLE, SCIENCE
- **Tapoloka** (Austerity): CIVIC, AUDITOR
- **Maharloka** (Great): FORUM, ENVOY, DISCOVERER
- **Svarloka** (Heaven): WATCHMAN
- **Bhuvarloka** (Intermediate): ENGINEER, ARTISAN

**Varna Distribution:**
- **BRAHMANA** (Priests): 8 agents (HERALD, CIVIC, FORUM, SCIENCE, ARCHIVIST, ORACLE, DISCOVERER)
- **KSHATRIYA** (Warriors): 3 agents (ENVOY, AUDITOR, WATCHMAN)
- **VAISHYA** (Merchants): 2 agents (ENGINEER, ARTISAN)

---

## EXTENDED SYSTEM AGENTS

Beyond the 12 Adityas, these agents provide specialized functionality:

### CHRONICLE
- **Agent ID:** chronicle
- **Domain:** TEMPORAL
- **Purpose:** Git operations, version control, temporal tracking
- **Status:** Operational
- **Varna:** VAISHYA
- **Layer:** Bhuvarloka
- **Implementation Path:** `steward/system_agents/chronicle/`

---

## IMPLEMENTATION CHECKLIST

For each Aditya, verify:

- [ ] Agent ID matches canonical name
- [ ] Manifest complete (author, description, domain)
- [ ] Topology placement defined in `vibe_core/topology.py`
- [ ] Constitutional Oath sworn (`OathMixin` implementation)
- [ ] Registered in kernel boot process
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Documentation exists
- [ ] Directory structure follows pattern: `steward/system_agents/{agent_id}/`
- [ ] Code quality < 500 lines (or justified if larger)

---

## REFERENCE IMPLEMENTATION

Each Aditya should follow this structure:

```
steward/system_agents/{agent_id}/
├── __init__.py
├── cartridge_main.py
├── manifest.json
├── tools/
│   ├── __init__.py
│   └── [tool_files].py
└── tests/
    ├── test_agent.py
    └── test_tools.py
```

See `docs/AGENT_DEVELOPMENT.md` for complete agent development guide.

---

## DEPLOYMENT VERIFICATION

To verify all 12 Adityas are registered:

```bash
python scripts/verify_adityas.py
```

Expected output:
```
✅ 12 Adityas verified and registered
- HERALD
- CIVIC
- FORUM
- SCIENCE
- ENVOY
- ARCHIVIST
- AUDITOR
- ENGINEER
- ORACLE
- WATCHMAN
- ARTISAN
- DISCOVERER
```

---

**This is the canonical definition. All system agents must conform to this structure.**
