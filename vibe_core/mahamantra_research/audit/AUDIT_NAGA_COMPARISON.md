# NAGA Audit Capabilities vs Mahamantra/Audit

**Date:** 2026-02-05  
**Status:** Comparative Analysis (Facts Only)

---

## 1. NAGA Audit Infrastructure (Prahlad Service)

### Methods Available
- `dharma_audit()` → DharmaScore
- `audit(target)` → AuditResult  
- `get_dharma_score()` → float

### DharmaScore Components
```
- total_score: float (0-100)
- unsigned_decisions: int
- signature_compliance: float
- ledger_intact: bool
- agents_without_identity: int
- identity_coverage: float
- timestamp: datetime
- auditor_id: str
- signature: Optional[bytes]
```

**What it checks:**
- Unsigned decisions in ledger
- Signature compliance across chain
- Ledger integrity verification
- Agent identity coverage
- All with cryptographic signing

---

## 2. Mahamantra/Audit Infrastructure (DriftAuditor)

### Methods Available
- `lineage()` → (valid_count, broken_count, violations)
- `ssot()` → (violations_count, violations_tuple)
- `protocols()` → (live_count, dead_count, violations)
- `audit()` → AuditReport
- `heal_lineage()` → List[str] (MODIFIES FILES)
- `start_listening()` → None (stub)

### What it checks
- **Genesis Lineage:** `__genesis__ % 37 == 0` for all .py files
- **SSOT (Single Source of Truth):** Hardcoded constants duplicated
- **Protocols:** 8 hardcoded protocol compliance rules

---

## 3. Capability Comparison

| Feature | NAGA | Mahamantra | Status |
|---------|------|-----------|--------|
| Boot audit trail | ✓ (Ananta) | ✗ | Missing |
| Ledger integrity | ✓ (Prahlad) | ✗ | Missing |
| Signature chain verification | ✓ (Prahlad) | ✗ | Missing |
| Agent identity tracking | ✓ (Prahlad) | ✗ | Missing |
| Genesis lineage check | ✗ | ✓ | Only here |
| SSOT constant tracking | ✗ | ✓ | Only here |
| Protocol compliance | ✓ (generic) | ✓ (8 hardcoded) | Different approach |
| Persistence/Registry | ✓ (Chitragupta) | ✗ | Missing |
| Auto-correction | ✗ (detection only) | ✓ (heal_lineage) | Only here |
| Quantified health score | ✓ (DharmaScore) | ✗ | Missing |

---

## 4. Key Findings

### Mahamantra/Audit Strengths
1. Checks genesis lineage (PARAMPARA principle)
2. Can auto-fix broken lineages
3. Detects constant duplication (SSOT violations)
4. Simple, focused (3 check functions)

### Mahamantra/Audit Gaps
1. No ledger state verification
2. No signature chain checking
3. No agent registry integrity
4. No boot sequence audit
5. Limited to 8 hardcoded protocols (not scalable to 16 Mahajanas)
6. No persistent finding registry

### NAGA Audit Strengths
1. Comprehensive signature verification
2. Ledger integrity checking
3. Agent identity coverage tracking
4. Boot sequence audit trail
5. Distributed registry (Chitragupta)
6. Quantified health metrics

### NAGA Audit Gaps
1. Doesn't check genesis lineage
2. Doesn't check constant duplication
3. Detection-only (no auto-correction)
4. Not integrated into Mahamantra

---

## 5. Integration Opportunities

### Phase 1: Registry (Low Risk)
Add finding storage to Mahamantra:
```python
# vibe_core/mahamantra/audit/registry.py
class AuditFinding:
    path: str
    violation_type: str  # "lineage", "ssot", "protocol", "boot", "identity"
    severity: str  # "critical", "high", "medium"
    timestamp: datetime
    status: str  # "identified", "investigating", "closed"

class AuditRegistry:
    def register_finding(finding: AuditFinding) → str
    def get_findings(violation_type: str, status: str) → List[AuditFinding]
    def close_finding(finding_id: str) → bool
```

### Phase 2: Position-based Routing (Medium)
Map audit handlers to positions (like Diamond Plan):
```python
# vibe_core/mahamantra/audit/position_router.py
AUDIT_HANDLERS = {
    0: "genesis_audit",      # Brahma - creation/lineage
    15: "yamaraja_audit",    # Yamaraja - judgment/verification
    # ... 14 more
}

def audit_at_position(position: int) → AuditReport:
    handler_name = AUDIT_HANDLERS.get(position)
    handler = route_to_position(position)
    return handler.audit()
```

### Phase 3: NAGA Integration (Higher Risk)
Connect back to NAGA services:
```python
# In DriftAuditor.audit()
def audit(self) -> AuditReport:
    # Keep existing checks
    lineage_report = self.lineage()
    ssot_report = self.ssot()
    protocol_report = self.protocols()
    
    # Add NAGA checks via callback
    # naga_dharma = prahlad.dharma_audit()
    # naga_boot = ananta.get_boot_audit()
    
    return AuditReport(...)
```

---

## 6. Recommendation

**DO NOT MERGE** NAGA and Mahamantra audit.

**INSTEAD:**
1. Keep DriftAuditor as-is (genesis/ssot/protocol checks work fine)
2. Add AuditRegistry for persistence (prevents losing findings)
3. Add position-based routing (future: delegate to position-specific auditors)
4. Document integration points for future NAGA callback

**Timeline:** Research in `vibe_core/mahamantra/research/audit/` first.

---

## 7. Files to Reference

### Read-Only
- `vibe_core/naga/services/prahlad/service.py` - DharmaScore implementation
- `vibe_core/naga/services/prahlad/types.py` - DharmaScore dataclass
- `vibe_core/mahamantra/audit/drift.py` - Current audit implementation

### To Create/Modify (Later)
- `vibe_core/mahamantra/audit/registry.py` - NEW: Finding storage
- `vibe_core/mahamantra/audit/position_router.py` - NEW: Position mapping
- `vibe_core/mahamantra/audit/drift.py` - MODIFY: Add registry calls

---

## 8. Next Steps

1. ✓ This analysis document
2. Research: How to add registry without breaking existing code
3. Research: How position routing should work in audit context
4. Prototype: Small registry implementation
5. Test: Ensure existing audits still pass

**NO code changes yet. Analysis phase.**
