## Steward Protocol Authority Surface Model

### Purpose

`steward-protocol` should be the normative mothership of the federation: constitutional, governable, semantically stable, and explicit about provenance. The source repo should therefore export governed authority artifacts; public wiki/projection rendering belongs to `agent-internet`.

### Audit Summary

- The legacy local SUTRA wiki compiler has been removed.
- Authority export now lives in neutral top-level modules such as `vibe_core/authority_exports.py` and `vibe_core/source_authority_registry.py`.
- Public membrane rendering and publication belong to `agent-internet`, not `steward-protocol`.
- Rich authored source material already exists in the repo (`CONSTITUTION.md`, `README.md`, `AGI_MANIFESTO.md`, `PROTOCOLS.md`, `STEWARD.md`, `KERNEL.md`, `ARCHITECTURE.md`, `INDEX.md`, `docs/*`).
- The current public surface collapses this corpus into shallow projections instead of binding canonical documents directly.
- `Law.md` is the clearest failure mode: it flattens `CONSTITUTION.md` headings and mixes in noisy implementation stems like `__init__`, `keys`, `contracts`, and `invariants`.

### Core Design Principle

The authority surface must distinguish **binding canonical documents** from **derived public projections**.

- **Canonical pages** preserve authored doctrine with minimal transformation.
- **Derived pages** summarize, index, compare, or map canonical/code sources.
- **Hybrid pages** combine small authored framing with bounded generated sections.
- Navigation pages should be generated from a declared surface model, not handwritten templates hidden in Python.

### Page Classes

#### 1. Canonical bound pages

One authored source document binds to one canonical authority artifact.

Examples:
- `Constitution`
- `Start-Here` / `README`
- `AGI-Manifesto`
- `Protocols`
- `Stewardship`
- `Kernel`
- `Architecture`

#### 2. Hybrid hub pages

Curated landing pages with small authored framing and official generated sections.

Examples:
- `Home`
- topic landing pages added later

#### 3. Derived index pages

Indexes over canonical material.

Examples:
- `Governance-Index`
- `Protocol-Index`
- `Doc-Atlas`

#### 4. Derived map/report pages

Structural or graph-oriented views built from many sources.

Examples:
- `Map`
- `Pantheon` or a renamed constellation page
- later federation topology/report pages

#### 5. Navigation support pages

Examples:
- `_Sidebar`
- `_Footer`

### Navigation Model

#### Start Here
- `Home`
- `Start-Here` / `README`
- `Index`

#### Governance
- `Constitution`
- `Stewardship`
- `Governance-Index`

#### Protocol Stack
- `Protocols`
- `Kernel`
- `Architecture`

#### Federation Surface
- `Map`
- `Pantheon` / constellation
- future federation reports

#### Reference
- glossary / atlas / doc indexes

### Binding Rules

- Never compress a canonical authored document into a derivative if the authored document itself can be the page.
- Preserve headings and wording on canonical pages.
- Keep provenance explicit: every page should be identifiable as canonical, derived, hybrid, or navigation-only.
- Derived governance pages may summarize constitutional neighbors, but must never replace the constitution itself.

### First Required Correction

Replace the current governance surface:

- retire `Law.md` as the primary constitutional page
- bind `CONSTITUTION.md` directly to `Constitution.md`
- create a separate `Governance-Index.md` for cross-links, summaries, and related governance files

### Minimal Implementation Slice

1. Keep the source-authority registry declarative and manifest-like.
2. Bind canonical authored documents directly into neutral authority exports.
3. Let `agent-internet` render/project the public membrane from those exports.
4. Maintain direct bindings for:
   - `README.md`
   - `CONSTITUTION.md`
   - `AGI_MANIFESTO.md`
   - `PROTOCOLS.md`
   - `ARCHITECTURE.md` or `KERNEL.md`
5. Keep local publication entrypoints removed so the boundary stays explicit.

### Likely Initial File Changes

- modify `vibe_core/authority_exports.py`
- modify `vibe_core/source_authority_registry.py`
- modify `agent-internet` projection/rendering code for public membrane views
- add tests for canonical binding, authority export completeness, and projection consumption

### Success Criteria

- The authority exports cover the canonical doctrine corpus without a local wiki compiler.
- Canonical pages read like real source doctrine, not summaries.
- Public navigation mirrors the actual doctrine/governance/protocol structure once rendered by `agent-internet`.
- Derived pages remain clearly secondary to the canon instead of masquerading as the canon.
