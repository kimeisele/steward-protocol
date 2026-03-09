## Steward Protocol Wiki Canonical Surface Model

### Purpose

`steward-protocol` should be the normative mothership of the federation: constitutional, governable, semantically stable, and explicit about provenance. The wiki should therefore be a governed document surface, not a thin generated brochure.

### Audit Summary

- The current SUTRA wiki compiler emits only 6 pages: `Home`, `Pantheon`, `Law`, `Map`, `_Sidebar`, `_Footer`.
- The generator is largely hardcoded inside `vibe_core/plugins/opus_assistant/manas/cortex/sutra.py`.
- Rich authored source material already exists in the repo (`CONSTITUTION.md`, `README.md`, `AGI_MANIFESTO.md`, `PROTOCOLS.md`, `STEWARD.md`, `KERNEL.md`, `ARCHITECTURE.md`, `INDEX.md`, `docs/*`).
- The current public surface collapses this corpus into shallow projections instead of binding canonical documents directly.
- `Law.md` is the clearest failure mode: it flattens `CONSTITUTION.md` headings and mixes in noisy implementation stems like `__init__`, `keys`, `contracts`, and `invariants`.

### Core Design Principle

The wiki must distinguish **binding canonical pages** from **derived pages**.

- **Canonical pages** preserve authored doctrine with minimal transformation.
- **Derived pages** summarize, index, compare, or map canonical/code sources.
- **Hybrid pages** combine small authored framing with bounded generated sections.
- Navigation pages should be generated from a declared surface model, not handwritten templates hidden in Python.

### Page Classes

#### 1. Canonical bound pages

One authored source document binds to one public wiki page.

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

1. Introduce a manifest-driven page registry for the wiki surface.
2. Move page declarations and nav order out of hardcoded SUTRA templates.
3. Add direct bindings for:
   - `README.md`
   - `CONSTITUTION.md`
   - `AGI_MANIFESTO.md`
   - `PROTOCOLS.md`
   - `ARCHITECTURE.md` or `KERNEL.md`
4. Generate `_Sidebar` and `_Footer` from the manifest.
5. Keep current build/publish entrypoints intact so rollout risk stays low.

### Likely Initial File Changes

- modify `vibe_core/plugins/opus_assistant/manas/cortex/sutra.py`
- modify `vibe_core/wiki_publisher.py`
- add a wiki surface manifest (for example `wiki-src/manifest.yaml`)
- add tests for canonical binding, derived page generation, and navigation output

### Success Criteria

- The wiki expands beyond the current 6-page bottleneck.
- Canonical pages read like real source doctrine, not summaries.
- Navigation mirrors the actual doctrine/governance/protocol structure of the repo.
- Derived pages become clearly secondary to the canon instead of masquerading as the canon.
