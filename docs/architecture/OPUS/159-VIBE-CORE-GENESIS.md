# OPUS-159: Vibe Core Genesis - The Central Stadtamt

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Pattern**: Layered Lasagna (not Spaghetti)
> **Depends**: OPUS-158 (MANAS Genesis PoC), GAD-000

---

## Preamble: From PoC to Production

OPUS-158 created a proof-of-concept "Bauamt" in MANAS.
OPUS-159 elevates this to vibe_core level - the proper Stadtamt.

**The Lasagna Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: MANAS (Consumer)                                       │
│  - Detects gaps via ShrutaSense                                  │
│  - Calls vibe_core genesis service                               │
│  - Does NOT own infrastructure generation                        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: ENGINEER (Builder)                                     │
│  - BuilderTool extended with GAD-000 templates                   │
│  - Spawns agents, plugins, modules                               │
│  - Uses vibe_core/genesis for compliance                         │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: VIBE_CORE/GENESIS (Foundation)                         │
│  - GAD-000 compliance checking                                   │
│  - Template registry for all module types                        │
│  - Infrastructure generation API                                 │
│  - Integration with LoaderRegistry                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Stadtamt Offices

### Office 1: Compliance Bureau (GAD-000 Turing Test)

```python
# vibe_core/genesis/compliance.py

class ComplianceBureau:
    """
    GAD-000 Turing Test: Can an AI operate this module?

    Checks:
    1. Discoverability - manifest.json exists and valid
    2. Observability - status/state queryable
    3. Parseability - errors are structured
    4. Composability - follows interface contracts
    5. Idempotency - safe to retry
    6. Documentation - AI-readable
    """

    def audit(self, path: Path) -> ComplianceReport:
        """Run full GAD-000 compliance audit."""
        pass

    def quick_check(self, path: Path) -> bool:
        """Fast check: Does minimum infrastructure exist?"""
        pass

    def get_missing(self, path: Path, module_type: ModuleType) -> List[str]:
        """What infrastructure is missing?"""
        pass
```

### Office 2: Template Registry

```python
# vibe_core/genesis/templates.py

class TemplateRegistry:
    """
    Central registry for all module type templates.

    Templates are versioned and validated.
    Each module type has required + optional templates.
    """

    def get_templates(self, module_type: ModuleType) -> Dict[str, Template]:
        """Get all templates for a module type."""
        pass

    def register_template(self, module_type: ModuleType,
                          name: str, template: Template) -> None:
        """Register a custom template."""
        pass
```

### Office 3: Infrastructure Builder

```python
# vibe_core/genesis/builder.py

class InfrastructureBuilder:
    """
    The actual construction worker.

    Uses templates to generate infrastructure.
    Reports what was created/skipped.
    """

    def build(self, path: Path, module_type: ModuleType,
              context: Dict = None) -> BuildResult:
        """Build infrastructure for a module."""
        pass

    def repair(self, path: Path, module_type: ModuleType) -> RepairResult:
        """Repair missing infrastructure (self-healing)."""
        pass
```

### Office 4: Genesis Service (The Front Desk)

```python
# vibe_core/genesis/service.py

class GenesisService:
    """
    The unified API for infrastructure genesis.

    This is what MANAS and Engineer call.
    Coordinates: Compliance → Templates → Builder
    """

    def __init__(self):
        self.compliance = ComplianceBureau()
        self.templates = TemplateRegistry()
        self.builder = InfrastructureBuilder()

    def ensure_compliance(self, path: Path,
                          module_type: ModuleType) -> GenesisResult:
        """
        Ensure a module is GAD-000 compliant.

        1. Check current compliance
        2. Build missing infrastructure
        3. Verify result
        """
        pass

    def scaffold_new(self, path: Path,
                     module_type: ModuleType,
                     context: Dict = None) -> GenesisResult:
        """Scaffold a completely new module."""
        pass
```

---

## Directory Structure

```
vibe_core/genesis/
├── __init__.py              # Exports GenesisService
├── service.py               # GenesisService (front desk)
├── compliance.py            # ComplianceBureau (GAD-000 audit)
├── builder.py               # InfrastructureBuilder
├── templates.py             # TemplateRegistry
├── types.py                 # ModuleType, BuildResult, etc.
└── templates/               # Default templates
    ├── plugin/
    │   ├── __init__.py.j2
    │   ├── manifest.json.j2
    │   └── plugin_main.py.j2
    ├── cartridge/
    │   ├── cartridge_main.py.j2
    │   ├── cartridge.yaml.j2
    │   └── steward.json.j2
    ├── analyzer/
    │   └── analyzer.py.j2
    ├── sense/
    │   └── sense.py.j2
    ├── action/
    │   └── action.py.j2
    └── section/
        └── manifest.json.j2
```

---

## Integration Points

### 1. MANAS Integration (Simplified)

```python
# In cognitive_kernel.py (OPUS-158 refactored)

def _process_genesis_vibrations(self, perception):
    """MANAS detects, vibe_core builds."""
    from vibe_core.genesis import GenesisService, ModuleType

    genesis = GenesisService.get_instance()

    for vibration in perception.vibrations:
        if vibration.event_type == "created" and vibration.is_directory:
            # Just call the central service
            result = genesis.ensure_compliance(
                vibration.path,
                self._classify_path(vibration.path)
            )
            if result.files_created:
                logger.info(f"🏛️ Genesis: {result.summary}")
```

### 2. Engineer Integration

```python
# In engineer/tools/builder_tool.py (extended)

def scaffold_agent(self, name: str, domain: str) -> Dict:
    """Use GenesisService for consistent scaffolding."""
    from vibe_core.genesis import GenesisService, ModuleType

    genesis = GenesisService.get_instance()
    target = self.workspace / "vibe_core/cartridges" / domain / name

    return genesis.scaffold_new(
        path=target,
        module_type=ModuleType.CARTRIDGE,
        context={"name": name, "domain": domain}
    )
```

### 3. LoaderRegistry Integration

```python
# In loaders/base_loader.py (extended)

class UnifiedLoader:
    def discover_and_load(self, ...):
        # Before loading, ensure compliance
        from vibe_core.genesis import GenesisService
        genesis = GenesisService.get_instance()

        for path in self._scan_paths():
            if not genesis.compliance.quick_check(path):
                logger.warning(f"Non-compliant module: {path}")
                # Optionally auto-repair
                genesis.ensure_compliance(path, self.item_type)
```

---

## Migration Plan

### Phase 1: Create vibe_core/genesis (This PR)
- [ ] Create directory structure
- [ ] Implement types.py (ModuleType, Results)
- [ ] Implement templates.py (TemplateRegistry)
- [ ] Implement compliance.py (ComplianceBureau)
- [ ] Implement builder.py (InfrastructureBuilder)
- [ ] Implement service.py (GenesisService)
- [ ] Copy templates from OPUS-158

### Phase 2: Integration
- [ ] Refactor MANAS to use GenesisService
- [ ] Extend Engineer BuilderTool
- [ ] Add LoaderRegistry hooks

### Phase 3: Self-Healing
- [ ] Add watch mode to GenesisService
- [ ] Integrate with Lifecycle for auto-repair
- [ ] Add metrics/observability

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/genesis/__init__.py
    required: true
  - path: vibe_core/genesis/service.py
    required: true
  - path: vibe_core/genesis/compliance.py
    required: true
  - path: vibe_core/genesis/builder.py
    required: true
  - path: vibe_core/genesis/templates.py
    required: true
  - path: vibe_core/genesis/types.py
    required: true
tests:
  - tests/unit/genesis/test_genesis_service.py
  - tests/unit/genesis/test_compliance.py
wiring:
  - pattern: "class GenesisService"
    in: vibe_core/genesis/service.py
  - pattern: "class ComplianceBureau"
    in: vibe_core/genesis/compliance.py
  - pattern: "class TemplateRegistry"
    in: vibe_core/genesis/templates.py
  - pattern: "class InfrastructureBuilder"
    in: vibe_core/genesis/builder.py
-->

---

## Related Documents

- [OPUS-158: MANAS Genesis PoC](158-INFRASTRUCTURE-GENESIS.md)
- [GAD-000: Operator Inversion Principle](../../GAD-0XX/GAD-000.md)
- [OPUS-098: Analyzer Loader](098-ANALYZER-LOADER.md)

---

## Summary

**OPUS-158**: MANAS has its own Bauamt (PoC, useful for MANAS-specific needs)
**OPUS-159**: vibe_core has the central Stadtamt (production, all services use it)

The Lasagna:
- **Top Layer**: Consumers (MANAS, Engineer, etc.) - detect & request
- **Middle Layer**: GenesisService - coordinate & build
- **Bottom Layer**: Templates + Compliance - the foundation

*"Feinste Lasagne, vegetarisch, ohne Zwiebeln, beste Bio-Zutaten."*
