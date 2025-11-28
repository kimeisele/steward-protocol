# RESEARCH REQUEST 1: FAE Constraints Database

## CONTEXT
We are building a "Feasibility Analysis Engine (FAE)" - a knowledge base of technical constraints for software project planning. This FAE will be used by an AI system (VIBE_ALIGNER) to automatically validate whether user requirements are technically feasible for a v1.0 scope.

## OBJECTIVE
Create a comprehensive YAML database (`FAE_constraints.yaml`) containing 50-100 constraint rules that define:
1. **Feature incompatibilities** (Feature X cannot coexist with Constraint Y)
2. **NFR conflicts** (Non-Functional Requirement A contradicts NFR B)
3. **Scope violations** (Feature Z is too complex for v1.0)

## REQUIRED RESEARCH

### Research Topic 1: Common v1.0 Scope Violations
**Questions to answer:**
- What features are commonly requested but unrealistic for MVP/v1.0?
- What are the top 20 "impossible for v1.0" feature categories?
- What technical complexity makes a feature "not v1.0-ready"?

**Search for:**
- "MVP scope common mistakes"
- "features too complex for v1.0"
- "v1.0 vs v2.0 feature prioritization"
- "technical debt v1.0 scope"
- "startup MVP anti-patterns"

**Extract:**
- List of features that are consistently flagged as "v2.0+" by professional architects
- Reasons WHY each feature is incompatible with v1.0 (infrastructure, complexity, time)

---

### Research Topic 2: Non-Functional Requirements (NFR) Conflicts
**Questions to answer:**
- What are the most common NFR conflicts in software projects?
- Which performance requirements conflict with budget/time constraints?
- What security requirements conflict with ease-of-use requirements?

**Search for:**
- "non-functional requirements conflicts"
- "performance vs cost tradeoffs software"
- "security vs usability conflicts"
- "scalability vs simplicity architecture"
- "high availability infrastructure requirements"

**Extract:**
- Pairs of conflicting NFRs (e.g., "real-time performance" vs "serverless architecture")
- Technical explanations of WHY these NFRs conflict

---

### Research Topic 3: Technology Stack Constraints
**Questions to answer:**
- What technology combinations are incompatible?
- What infrastructure requirements does each major feature type require?
- What are the minimum infrastructure needs for common features?

**Search for:**
- "technology stack compatibility matrix"
- "real-time features infrastructure requirements"
- "video streaming minimum requirements"
- "authentication infrastructure needs"
- "payment processing technical requirements"

**Extract:**
- Technology incompatibilities (e.g., "WebSockets don't work well with serverless")
- Infrastructure requirements per feature type (e.g., "Video streaming needs CDN, dedicated servers, WebRTC")

---

### Research Topic 4: Time & Complexity Estimation
**Questions to answer:**
- How long does each common feature type take to build?
- What are the dependency chains that increase complexity?
- What features require specialized expertise?

**Search for:**
- "software feature development time estimates"
- "complexity estimation software features"
- "authentication implementation time"
- "payment integration complexity"
- "real-time features development effort"

**Extract:**
- Rough time estimates for 20-30 common feature types
- Complexity multipliers (e.g., "OAuth adds 2x complexity to auth")

---

## DELIVERABLE FORMAT

Create a YAML file with this structure:

```yaml
# FAE_constraints.yaml
# Feasibility Analysis Engine - Technical Constraints Database

version: "1.0"
last_updated: "2025-01-XX"

# SECTION 1: Feature-Scope Incompatibilities
incompatibilities:
  - id: "FAE-001"
    type: "feature_scope_conflict"
    feature: "real_time_video_streaming"
    incompatible_with: "scope_v1.0"
    reason: "Requires WebRTC implementation, CDN setup, STUN/TURN servers, bandwidth optimization. Typical implementation: 8-12 weeks for basic version."
    required_nfrs:
      - "low_latency_<100ms"
      - "high_bandwidth_support"
      - "99.9%_uptime"
    recommended_scope: "v2.0_or_later"
    alternatives_for_v1:
      - "pre_recorded_video_upload"
      - "scheduled_video_calls_via_3rd_party"
  
  - id: "FAE-002"
    type: "feature_scope_conflict"
    feature: "multi_language_localization"
    incompatible_with: "scope_v1.0"
    reason: "Requires i18n framework setup, translation management, RTL support, locale-specific formatting. Adds 40-60% complexity to all UI components."
    required_nfrs:
      - "translation_management_system"
      - "locale_specific_testing"
    recommended_scope: "v1.5_or_v2.0"
    alternatives_for_v1:
      - "english_only_with_i18n_architecture_ready"

  # ADD 48-98 MORE CONSTRAINTS...

# SECTION 2: NFR Conflicts
nfr_conflicts:
  - id: "FAE-NFR-001"
    type: "nfr_conflict"
    nfr_a: "real_time_performance_latency_<50ms"
    nfr_b: "serverless_architecture"
    reason: "Serverless has cold start latency (100-3000ms). Incompatible with real-time requirements."
    resolution_options:
      - "Use dedicated servers (increases cost 10x)"
      - "Relax latency requirement to <500ms"
      - "Hybrid: serverless for non-critical, dedicated for real-time"
  
  - id: "FAE-NFR-002"
    type: "nfr_conflict"
    nfr_a: "high_security_compliance_gdpr_hipaa"
    nfr_b: "rapid_v1.0_development_<3months"
    reason: "Compliance requires: data encryption, audit logs, access controls, legal review, penetration testing. Adds 6-12 weeks to timeline."
    resolution_options:
      - "Delay launch for compliance"
      - "Launch in non-regulated market first"
      - "Use compliant 3rd party services (increases cost)"

  # ADD 18-28 MORE NFR CONFLICTS...

# SECTION 3: Technology Stack Constraints
tech_constraints:
  - id: "FAE-TECH-001"
    technology: "websockets"
    incompatible_with:
      - "serverless_lambda_aws"
      - "static_hosting_netlify_vercel"
    reason: "WebSockets require persistent connections. Serverless/static hosts terminate connections."
    workarounds:
      - "Use AWS API Gateway WebSocket (complex setup)"
      - "Use dedicated server (EC2, DigitalOcean)"
      - "Use 3rd party service (Pusher, Ably)"
  
  # ADD 18-28 MORE TECH CONSTRAINTS...

# SECTION 4: Dependency Complexity Chains
dependency_chains:
  - feature: "user_authentication"
    basic_dependencies:
      - "user_database"
      - "password_hashing"
      - "session_management"
    complexity_multipliers:
      - trigger: "oauth_social_login"
        multiplier: 2.0
        adds_dependencies: ["oauth_provider_integration", "token_management"]
      - trigger: "multi_factor_auth"
        multiplier: 1.5
        adds_dependencies: ["sms_service", "totp_generation"]
      - trigger: "magic_link_passwordless"
        multiplier: 1.3
        adds_dependencies: ["email_service", "secure_token_generation"]

  # ADD 18-28 MORE DEPENDENCY CHAINS...

# SECTION 5: Time Estimates
feature_time_estimates:
  - feature_type: "user_authentication_basic"
    typical_time: "1-2 weeks"
    complexity: "medium"
    
  - feature_type: "user_authentication_oauth"
    typical_time: "2-3 weeks"
    complexity: "medium-high"
    
  - feature_type: "payment_processing_stripe"
    typical_time: "2-4 weeks"
    complexity: "high"
    reason: "Requires PCI compliance understanding, webhook handling, subscription logic, refund flows"
    
  - feature_type: "real_time_chat"
    typical_time: "3-6 weeks"
    complexity: "high"
    reason: "WebSocket infrastructure, message persistence, presence system, typing indicators"
    
  # ADD 16-26 MORE TIME ESTIMATES...
```

---

## VALIDATION CRITERIA

The delivered YAML must:
1. ✅ Contain at least 50 total constraint entries
2. ✅ Cover these categories:
   - 20-30 feature-scope incompatibilities
   - 10-15 NFR conflicts
   - 10-15 technology constraints
   - 10-15 dependency chains
   - 15-20 time estimates
3. ✅ Each constraint must have:
   - Clear ID
   - Concrete reason (not vague)
   - Actionable alternatives or workarounds
4. ✅ All information must be research-backed (cite sources if possible)
5. ✅ Focus on common software project types:
   - Web apps (SaaS, marketplaces, social platforms)
   - Mobile apps (iOS/Android)
   - APIs/Backend services
   - CLI tools

---

## SOURCES TO CONSULT

**Recommended resources:**
- Y Combinator Startup School materials
- Software architecture blogs (Martin Fowler, ThoughtWorks)
- AWS Well-Architected Framework
- Microsoft Azure Architecture Center
- Real-world post-mortems (HN, dev.to, medium)
- Project management case studies
- Technology radar reports (ThoughtWorks Technology Radar)

---

## DELIVERABLE

A single file: `FAE_constraints.yaml` (50-100 constraints, production-ready, research-backed)
