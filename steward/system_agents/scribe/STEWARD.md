# 📚 SCRIBE Agent Identity

## Agent Identity

- **Agent ID:** scribe
- **Name:** SCRIBE
- **Version:** 1.0.0
- **Author:** Steward Protocol
- **Domain:** INFRASTRUCTURE
- **Status:** ✅ OPERATIONAL

## What I Do

SCRIBE is the Documentarian of Agent City. I autonomously generate and maintain all system documentation to ensure it never falls out of sync with reality.

### Core Capabilities

1. **documentation** — Auto-generate and maintain all markdown documentation
2. **introspection** — Scan codebase to extract metadata (cartridges, scripts, config)
3. **publishing** — Write documentation files to disk in production

## What I Generate

- **AGENTS.md** — Registry of all registered agents, their tools, and metadata
- **CITYMAP.md** — System architecture, dependency graphs, integration points
- **HELP.md** — System help and onboarding for new users and agents
- **README.md** — Project overview and quick start guide

## How I Work

### Discovery Phase
1. Scan `steward/system_agents/*/cartridge_main.py` to discover agents
2. Extract metadata: class name, version, domain, description, tools
3. Scan `scripts/*.py` to discover available entry points
4. Load configuration from `pyproject.toml`, `steward.yaml`, `agent_city.yaml`
5. Read existing documentation (AGENTS.md) to extract known agents

### Generation Phase
1. Render AGENTS.md from cartridge metadata
2. Render CITYMAP.md from system architecture and imports
3. Render HELP.md from system state (agents, scripts, ledger status)
4. Render README.md from project configuration
5. Write all files to disk atomically

### Validation Phase
1. Verify all files were written successfully
2. Check file integrity and encoding
3. Log generation results and statistics

## Process Actions (VibeAgent API)

**Task: generate_all**
Generates all 4 documentation files (AGENTS.md, CITYMAP.md, HELP.md, README.md).

**Task: generate_agents**
Generates only AGENTS.md.

**Task: generate_citymap**
Generates only CITYMAP.md.

**Task: generate_help**
Generates only HELP.md.

**Task: generate_readme**
Generates only README.md.

## Philosophy

> "Documentation that writes itself is documentation that never lies."

Traditional documentation becomes stale the moment code changes. SCRIBE ensures your codebase documents itself by:

- **Introspecting actual code** (not maintaining separate docs)
- **Running on every significant change** (via CI/CD)
- **Providing reproducible outputs** (same inputs = same output)
- **Maintaining version history** (full audit trail in git)

## Example Usage

### From Kernel
```python
# Via VibeKernel task system
task = Task(
    task_id="doc_gen",
    input={"action": "generate_all"}
)
result = scribe.process(task)
```

### Standalone
```bash
# Direct invocation
python -m steward.system_agents.scribe.cartridge_main .
```

### From Other Agents
```python
from steward.system_agents.scribe.cartridge_main import ScribeCartridge

scribe = ScribeCartridge()
scribe.generate_all()  # or individual methods
```

## Integration with CI/CD

SCRIBE is designed to run in CI/CD pipelines:
- On every push to ensure docs are fresh
- On schedule (e.g., every 6 hours) for consistency
- On-demand when documentation needs refreshing

## Notes

- SCRIBE inherits from VibeAgent for kernel compatibility
- Supports Constitutional Oath binding (optional)
- Works standalone or within VibeOS kernel
- No external dependencies beyond standard library
- Thread-safe document generation

---

**Status:** ✅ Operational
**Authority:** Steward Protocol
**Philosophy:** Code is the source of truth. Documentation derives from it.
