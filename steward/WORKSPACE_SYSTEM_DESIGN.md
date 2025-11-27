# Workspace System Design (P50)
## Multi-Tenancy Architecture for Steward Protocol

**Status:** Design Phase (P50 - Defer if not needed)
**Last Updated:** 2025-11-27
**Prepared By:** CIVIC Governance System

---

## Executive Summary

The **Workspace System** extends Steward Protocol to support **multi-tenancy** through logical isolation and hierarchical namespace organization. This design provides a path for the protocol to evolve from a monolithic single-app OS to a federated multi-tenant platform.

**Key Decision:** This is a **P50 Design** - implementation is deferred pending product vision clarification. However, the architecture is designed to be backward-compatible and can be adopted incrementally.

---

## 1. Architecture Overview

### 1.1 Saptadvipa Model (Logical Zones)

The **Saptadvipa (7 Island Continents)** model provides logical isolation:

```
        Jambudvipa (Core OS)
              ↓
    ┌─────────┴──────────┐
    ↓                    ↓
Plakshadvipa         Shalmalidvipa
(Internal Workspaces) (External Tenants)
    ↓                    ↓
    Internal Agents      Multi-tenant Apps
    Private API          Public API
    Org-scoped           Namespace-scoped
```

**Zones:**
- **Jambudvipa**: Core VibeOS kernel + CIVIC governance
- **Plakshadvipa**: Internal workspaces (company teams, departments)
- **Shalmalidvipa**: External tenants (client organizations, third-party apps)
- **4 Remaining Islands**: Reserved for future expansion (federation, partner networks, etc.)

### 1.2 Hierarchical Namespace Structure

Workspaces are organized using DNS-like hierarchical namespaces:

```
steward-registry.org (root)
├─ com.steward-registry.org (commercial)
│  ├─ vibe-agency.com.steward-registry.org
│  │  ├─ vibe-agency-orchestrator
│  │  ├─ vibe-agency-discoverer
│  │  └─ vibe-agency-workflow
│  └─ acme-corp.com.steward-registry.org
│     ├─ acme-crm-agent
│     └─ acme-analytics-agent
├─ org.steward-registry.org (non-profit)
│  ├─ openai.org.steward-registry.org
│  └─ anthropic.org.steward-registry.org
└─ github.steward-registry.org
   ├─ user/kimeisele.github.steward-registry.org
   └─ org/anthropics.github.steward-registry.org
```

**Benefits:**
- Decentralized ownership (each organization controls its namespace)
- Federation-ready (other registries can use same pattern)
- DNS-compatible (can be mapped to actual DNS in the future)

### 1.3 Role-Based Access Control via Varna

The **Vedic Varna system** (already implemented in Lifecycle Agent) provides RBAC:

```
BRAHMANA (High Authority)
  ├─ System policies
  ├─ Cross-workspace management
  └─ Governance decisions

KSHATRIYA (Warrior/Manager)
  ├─ Workspace creation
  ├─ Member management
  └─ Resource allocation

VAISHYA (Merchant/User)
  ├─ Agent operations
  ├─ Data access
  └─ Publishing permissions

SHUDRA (Service/Low Authority)
  ├─ Read-only access
  ├─ Execution only
  └─ No management rights
```

**Implementation:** Leverage existing `LifecycleAgent` and `LifecycleEnforcer` for workspace-scoped permissions.

---

## 2. Workspace Types

### 2.1 Internal Workspaces (Plakshadvipa)
- **Owner**: Single organization/team
- **Visibility**: Internal only
- **Isolation**: Strong (data encryption, network segmentation)
- **Use Cases**:
  - Department teams
  - Project-specific agents
  - Confidential research
- **API**: Private endpoints

**Example Structure:**
```
steward-protocol/
├─ core/                          # Jambudvipa (immutable)
├─ workspaces/
│  ├─ marketing-agency/           # Internal workspace
│  │  ├─ agents/
│  │  │  ├─ content-generator/
│  │  │  ├─ social-planner/
│  │  │  └─ analytics-agent/
│  │  ├─ data/
│  │  ├─ WORKSPACE.md
│  │  └─ workspace.json
│  ├─ engineering/                # Internal workspace
│  │  ├─ agents/
│  │  │  ├─ code-reviewer/
│  │  │  └─ test-runner/
│  │  ├─ WORKSPACE.md
│  │  └─ workspace.json
```

### 2.2 External Tenants (Shalmalidvipa)
- **Owner**: Third-party organization
- **Visibility**: Limited (public APIs only)
- **Isolation**: Very strong (complete data separation)
- **Use Cases**:
  - Multi-tenant SaaS platform
  - Client workspaces (white-label)
  - API partners
- **API**: Public endpoints with tenant headers

**Example Structure:**
```
steward-protocol/
├─ tenants/
│  ├─ acme-corp/                  # External tenant
│  │  ├─ agents/
│  │  │  ├─ crm-agent/
│  │  │  └─ analytics-agent/
│  │  ├─ data/
│  │  ├─ TENANT.md
│  │  └─ tenant.json
│  ├─ client-xyz/                 # White-label workspace
│  │  ├─ agents/
│  │  ├─ TENANT.md
│  │  └─ tenant.json
```

---

## 3. Workspace Isolation Model

### 3.1 Data Isolation

```
User Request
    ↓
[Tenant Context Router]
    ├─→ Extract tenant_id from header/path
    ├─→ Load tenant credentials
    └─→ Scope database query
        ↓
[Workspace Boundary]
    ├─ Query: SELECT * FROM agents WHERE workspace_id = ?
    ├ Query: SELECT * FROM tasks WHERE workspace_id = ?
    └─ Ledger: record_event(workspace_id=?, agent_id=?, ...)
        ↓
[Respond to Tenant A only]
```

**Database Schema** (example):

```sql
CREATE TABLE agents (
    agent_id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    config JSON,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    UNIQUE(workspace_id, agent_id)  -- unique per workspace
);

CREATE TABLE tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    payload JSON,
    status VARCHAR(50),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

CREATE TABLE workspaces (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    namespace VARCHAR(255) UNIQUE,     -- e.g., acme-corp.com.steward-registry.org
    owner_id VARCHAR(255),
    varna VARCHAR(50),                 -- Workspace varna (BRAHMANA, KSHATRIYA, etc.)
    created_at TIMESTAMP,
    created_by VARCHAR(255)
);
```

### 3.2 API Isolation

```python
# Tenant context is extracted from request headers
class TenantMiddleware:
    def __call__(self, request):
        # Option 1: Header-based
        tenant_id = request.headers.get('X-Tenant-ID')

        # Option 2: Path-based
        # GET /api/v1/tenants/{tenant_id}/agents

        # Option 3: Subdomain-based
        # GET https://{tenant_id}.steward-protocol.io/api/agents

        request.tenant_id = tenant_id
        request.workspace = load_workspace(tenant_id)

        # Gate based on varna
        if not request.workspace.has_permission(request.user, 'read_agents'):
            raise PermissionDenied()

        return request
```

### 3.3 Agent Isolation

Each agent is scoped to a workspace:

```python
class WorkspacedAgent(VibeAgent):
    def __init__(self, workspace_id: str, agent_id: str):
        super().__init__(agent_id=agent_id)
        self.workspace_id = workspace_id

    def process(self, task: Task) -> Dict[str, Any]:
        # All tasks are automatically scoped
        task.workspace_id = self.workspace_id

        # Record with workspace context
        self.kernel.ledger.record_event(
            workspace_id=self.workspace_id,
            agent_id=self.agent_id,
            event_type='task_processed',
            details=task.payload
        )

        return {"status": "success"}
```

---

## 4. Governance & Permissions

### 4.1 Workspace Roles

```yaml
Workspace Administrator (BRAHMANA):
  Permissions:
    - Create/delete agents
    - Manage workspace members
    - Configure workspace policies
    - View audit logs
    - Access all agents/data
    - Modify workspace varna

Workspace Member (KSHATRIYA):
  Permissions:
    - View workspace agents
    - Deploy agents
    - Manage agent credentials
    - View agent logs
    - Create sub-workspaces (if KSHATRIYA_ADMIN role)

Agent User (VAISHYA):
  Permissions:
    - Execute agents
    - Submit tasks
    - View task results
    - Use agent APIs

Guest (SHUDRA):
  Permissions:
    - Read-only access to public information
    - Cannot create/modify anything
```

### 4.2 Permission Enforcement

Use existing `LifecycleAgent` pattern for workspace-level permissions:

```python
class WorkspacePermissionGate:
    def __init__(self, lifecycle_agent: LifecycleAgent):
        self.lifecycle_agent = lifecycle_agent

    def check_workspace_permission(
        self,
        workspace_id: str,
        agent_id: str,
        action: str,  # 'read', 'write', 'create', 'delete'
        required_varna: str = 'VAISHYA'
    ) -> bool:
        # Get agent's varna in this workspace
        agent_varna = self.get_agent_varna(workspace_id, agent_id)

        # Check Varna hierarchy
        return self.varna_permits(agent_varna, action, required_varna)
```

---

## 5. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Create `WorkspaceContext` class
- [ ] Implement tenant middleware
- [ ] Add workspace database schema
- [ ] Create workspace CRUD operations
- [ ] Document workspace configuration format

### Phase 2: Integration (Weeks 5-8)
- [ ] Integrate with LifecycleAgent for RBAC
- [ ] Implement workspace-scoped ledger recording
- [ ] Add TenantMiddleware to request handler
- [ ] Update CIVIC governance for multi-workspace
- [ ] Create workspace isolation tests

### Phase 3: Scaling (Weeks 9-12)
- [ ] Implement workspace quotas (resource limits)
- [ ] Add workspace audit logging
- [ ] Create workspace dashboards
- [ ] Implement workspace-to-workspace communication
- [ ] Federation protocols (Phase 3 per FEDERATION.md)

### Phase 4: Production (Weeks 13+)
- [ ] Multi-region support
- [ ] Disaster recovery per workspace
- [ ] SLA per workspace
- [ ] Compliance certifications
- [ ] Full federated registry

---

## 6. Compliance Levels Integration

Map Workspace System to existing **Compliance Levels**:

```
Level 1 (Minimal):
  └─ Single workspace, no WORKSPACE.md required

Level 2 (Standard) ⭐ RECOMMENDED:
  ├─ WORKSPACE.md defines workspace metadata
  ├─ workspace.json with configuration
  ├─ RBAC via varna system
  └─ Basic multi-tenancy support

Level 3 (Advanced):
  ├─ Level 2 +
  ├─ Workspace health checks
  ├─ Real-time quota monitoring
  └─ Introspection API per workspace

Level 4 (Full Protocol):
  ├─ Level 3 +
  ├─ Federated workspace registry
  ├─ Cross-workspace delegation
  └─ Multi-sig workspace policies
```

---

## 7. Example: Workspace Configuration

### `WORKSPACE.md` (Workspace Definition)

```markdown
# Vibe Agency Marketing Workspace

**Namespace**: vibe-agency.com.steward-registry.org
**Type**: Internal
**Varna**: KSHATRIYA (Workspace Management Authority)
**Owner**: Vibe Agency Team
**Established**: 2025-01-01

## Purpose
Marketing automation and content generation for Vibe Agency.

## Agents
- content-generator: Write and optimize marketing copy
- social-planner: Schedule and analyze social posts
- analytics-agent: Track campaign performance

## Isolation Level
Strong (encrypted data, network-scoped)

## Permissions
- Admin: marketing-team@vibe-agency.com
- Members: [list of team members]
```

### `workspace.json` (Workspace Config)

```json
{
  "workspace_id": "vibe-agency-marketing",
  "namespace": "vibe-agency.com.steward-registry.org",
  "name": "Marketing Workspace",
  "type": "internal",
  "varna": "KSHATRIYA",
  "owner": "vibe-agency",
  "created_at": "2025-01-01T00:00:00Z",
  "config": {
    "isolation_level": "strong",
    "data_encryption": "AES-256",
    "audit_logging": true,
    "rate_limit": {
      "tasks_per_hour": 1000,
      "agents_max": 50
    },
    "api_endpoints": {
      "private": "internal.steward-protocol.io",
      "public": null
    }
  },
  "members": [
    {
      "user_id": "alice@vibe-agency.com",
      "varna": "BRAHMANA",
      "roles": ["admin"]
    },
    {
      "user_id": "bob@vibe-agency.com",
      "varna": "KSHATRIYA",
      "roles": ["member"]
    }
  ]
}
```

---

## 8. Reference Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│          VibeOS Kernel (Jambudvipa - Core)              │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Ledger    │  │  Scheduler   │  │   Registry   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
         [Tenant Context Router - TenantMiddleware]
                         ↓
     ┌───────────────────┬───────────────────┐
     ↓                   ↓
┌─────────────┐   ┌──────────────────┐
│ Plakshadvipa│   │  Shalmalidvipa   │
│  (Internal) │   │  (External/SaaS) │
├─────────────┤   ├──────────────────┤
│Workspaces:  │   │Tenants:          │
│ - marketing │   │ - acme-corp      │
│ - engr      │   │ - client-xyz     │
│ - research  │   │ - partner-abc    │
├─────────────┤   ├──────────────────┤
│Isolation:   │   │Isolation:        │
│ Strong      │   │ Very Strong      │
├─────────────┤   ├──────────────────┤
│RBAC: Varna  │   │RBAC: Varna + MFA │
└─────────────┘   └──────────────────┘
     ↓                   ↓
[Workspace-Scoped Agents & Data]
```

---

## 9. Backward Compatibility

The Workspace System is **fully backward compatible**:

1. **No Changes Required** for single-workspace deployments
   - All agents continue to work with `workspace_id = 'default'`
   - Default workspace uses Jambudvipa + Plakshadvipa

2. **Optional Adoption**
   - Existing `STEWARD.md` continues to work
   - New `WORKSPACE.md` is optional
   - Migration path: STEWARD.md → WORKSPACE.md

3. **Feature Gates**
   ```python
   if FEATURE_MULTI_TENANCY_ENABLED:
       # Use workspace isolation
       workspace_id = extract_tenant_context(request)
   else:
       # Legacy single-workspace mode
       workspace_id = 'default'
   ```

---

## 10. Security Considerations

### 10.1 Potential Threats & Mitigations

| Threat | Mitigation |
|--------|-----------|
| **Tenant Data Leakage** | Workspace isolation via `workspace_id` scope, database constraints |
| **Unauthorized Access** | Varna-based RBAC + MFA for sensitive actions |
| **Cross-tenant Privilege Escalation** | Lifecycle gating, capability constraints, audit logging |
| **Resource Starvation** | Workspace quotas, rate limiting per workspace |
| **Audit Log Tampering** | Immutable kernel ledger with cryptographic signatures |
| **API Key Exposure** | Per-workspace API keys, rotation policies |

### 10.2 Encryption

```
┌─────────────────┐
│   Plaintext     │  User submits task
│   Task/Data     │
└────────┬────────┘
         ↓
┌─────────────────────────────────────┐
│  Encryption (TLS-in-transit)        │
│  + Workspace-scoped key derivation  │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Database (AES-256 at rest)         │
│  workspace_id + partition key       │
└─────────────────────────────────────┘
```

---

## 11. Deferral Rationale (P50)

This design is P50 (lower priority) because:

1. **Product Vision Not Finalized**
   - Unclear if Steward Protocol is single-app OS or multi-app platform
   - CIVIC currently manages single homogeneous agent population

2. **No Current Multi-Tenancy Requirements**
   - Existing deployments are monolithic
   - No clients demanding workspace isolation yet

3. **Implementation Complexity vs. Benefit**
   - Significant engineering effort (2-3 months)
   - Only needed if product pivots to SaaS/white-label

4. **Alternative Approach**
   - Deploy separate instances per tenant (simpler, works now)
   - Adopt Workspace System only if operational costs prohibit this

---

## 12. Success Criteria (If Implemented)

- [ ] **Isolation:** 100% data separation between workspaces verified by tests
- [ ] **Performance:** <5% latency overhead from tenant scoping
- [ ] **Scalability:** Support 1000+ workspaces on single cluster
- [ ] **Compliance:** SOC 2 Type II certification with workspace isolation
- [ ] **Adoption:** <1 day to provision new workspace
- [ ] **Documentation:** Zero tenant data leaks in first 12 months

---

## 13. Related Documents

- [FEDERATION.md](./FEDERATION.md) - Inter-registry federation (Phase 3)
- [GRACEFUL_DEGRADATION.md](./GRACEFUL_DEGRADATION.md) - Compliance levels
- [ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md) - Current architecture
- [GAP_ANALYSIS_REPORT.md](../GAP_ANALYSIS_REPORT.md) - Gap 3.4 (Workspace System)
- [vibe_core/topology.py](../vibe_core/topology.py) - Saptadvipa architecture
- [steward/system_agents/civic/lifecycle_agent.py](../steward/system_agents/civic/lifecycle_agent.py) - RBAC via Varna

---

## Conclusion

The **Workspace System** is a comprehensive multi-tenancy architecture that leverages existing Vedic patterns (Saptadvipa zones, Varna RBAC) and proven isolation techniques (tenant middleware, database scoping).

**Key Takeaway:** This is a **design, not an implementation**. It provides a roadmap for when the product vision clarifies and multi-tenancy becomes a priority. Until then, the monolithic single-workspace model suffices.

**Recommendation:** **Keep as P50 (Deferred)** until one of these occurs:
1. Product pivots to SaaS/white-label platform
2. First multi-tenant customer requires isolation
3. Operational costs demand consolidation

Then, implement Phase 1-2 (Foundation + Integration) in parallel with other P1/P2 work.

---

**Design Status:** ✅ Complete
**Implementation Status:** ⏳ Deferred (P50)
**Next Steps:** Await product vision clarity or multi-tenancy requirement trigger
