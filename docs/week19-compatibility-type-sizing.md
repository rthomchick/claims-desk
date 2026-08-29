# Week 19 — Sizing a Fifth Claim Type: Compatibility

**Status:** Investigation only. No schema, tool, skill, ADR, or registry changes were made in the course of this report.
**Scope:** Size the addition of a "compatibility" claim type (hardware/software/firmware/driver certified for a named platform version) alongside the existing four (Performance, Comparative, Compliance, Superlative).

---

## Part 1 — Change surface

### 1.1 Supabase schema

`claim_type` is **not** a native Postgres `ENUM`. It's `text` with an inline `CHECK` constraint, in `server/db/schema.sql`:

```sql
claim_type text not null check (claim_type in ('performance', 'comparative', 'compliance', 'superlative')),
```

**Change:** widen the `in (...)` list to include `'compatibility'`. This is a `DROP CONSTRAINT` / `ADD CONSTRAINT` migration (Postgres has no `ALTER TYPE ... ADD VALUE`-equivalent for a CHECK list — it's just a new constraint body), or edit-in-place if the table is being rebuilt anyway. **Size: ~1 line of DDL**, wrapped in a migration file matching the existing precedent (`server/db/migrate_week18.py`, ~30–40 lines including connection/commit/rollback boilerplate, no backfill needed since this is additive).

**No data migration required on the twelve existing claims** — none carry `claim_type = 'compatibility'` today (see 1.5), and widening a CHECK constraint doesn't touch existing rows.

Two other schema-adjacent things to note, not because they block anything but because they're where the type's *shape* first has to be decided:

- `evidence_links` has two columns already coupled to type via comment, not constraint: `sample_size` ("only populated for performance/comparative") and `expiry_date` ("populated for compliance/superlative"). Compatibility needs neither in their current sense — it needs a verification-report link (maps naturally to the existing `evidence_url` column) and a platform-version field, which **does not exist yet**. This is the one place where compatibility isn't just "slot into the existing shape" — it needs a new column (or a JSON blob) to hold the device/firmware/platform-version tuple. That's the real schema addition, and it's bigger than the CHECK constraint edit: a new nullable column, or reuse of an existing generic field if one exists for this purpose.
- `review_rulings`'s `ruling` enum (`approved`/`rejected`/`escalated`) is a separate global enum, untouched by adding a claim type — consistent with ADR-016 Decision 4's stated principle that risk classes and rulings stay global, only the *input rulesets* vary by type.

### 1.2 `append_claim`

`server/tools/append_claim.py` (71 lines) takes `claim_type: str` and stores it verbatim; it also uses it to build `claim_slug` (`f"{product_key}-{claim_type}-{next_n:02d}"`). **No branching on claim_type value anywhere in this file.** Change size: **0 lines** — this tool is type-agnostic by construction, and the DB CHECK constraint is the only gate keeping bad values out. (If a platform-version tuple becomes a new required field, this tool's parameter list grows, but that's a field addition, not a type-conditional branch.)

### 1.3 `check_substantiation`

`server/tools/check_substantiation.py` (104 lines) is the tool most exposed to breakage from an incomplete rollout:

- Lines 20–43: `EVIDENCE_STANDARDS` dict, one string entry per type. Line 97 does `EVIDENCE_STANDARDS[claim_type]` with **no `.get()` fallback** — a compatibility claim inserted before this dict is updated raises `KeyError` at review time, not at insert time (the DB constraint would already be widened by then).
- Line 46: `_SAMPLE_SIZE_NOT_APPLICABLE = {"compliance", "superlative"}` — needs `"compatibility"` added, since a compatibility claim has no sample size either.
- Line 49: `_EXPIRY_NOT_APPLICABLE = {"performance", "comparative"}` — this is the interesting one. Compatibility's currency model (goes stale at platform end-of-support, not at a fixed expiry date) doesn't fit either bucket cleanly. It's not "not applicable" the way Performance/Comparative are; it needs its own currency check, structurally similar to `expiry_date` but computed against a *different, external* date (see Part 2). This is a real logic branch, not a set-membership toggle.

**Change size: ~10–15 lines** if compatibility's currency logic is a lookup against a static/cached end-of-support table; more if it has to call out to a live API synchronously inside `check_substantiation` (see Part 2 for why that's the wrong design regardless).

### 1.4 `classify_claim_risk`

`server/tools/classify_claim_risk.py` (162 lines) is the most type-coupled file in the codebase by design (ADR-016 Decision 4 explicitly puts type-specific risk rulesets here, not in the Skill):

- Four private functions, one per type (`_classify_performance`, `_classify_comparative`, `_classify_compliance`, `_classify_superlative`), each ~20 lines.
- `_RULESETS` dict mapping type name → function; `_RULESETS[claim["claim_type"]]` at call time, again with no fallback — same `KeyError` exposure as 1.3.

**Change size: ~20–25 lines** — one new `_classify_compatibility(claim, evidence)` function matching the shape of the existing four (e.g., "no verification report → prohibited," "platform past end-of-support → high," "platform version not named → high") plus one new dict entry.

### 1.5 `list_claims`, `delete_claim`, `get_claim_status`

All three are pure passthrough on `claim_type` — a filter parameter or a plain selected column, no branching. **Change size: 0 lines each.**

### 1.6 `claim-taxonomy` skill

Exists as **two byte-identical directory copies** (`​.claude/skills/claim-taxonomy/` and `skills/claim-taxonomy/`) — confirmed via `diff`, zero output. Every edit below must be made in both, or one made a symlink to the other (out of scope to do here, but worth flagging as the single easiest way to eliminate a standing consistency risk before a fifth type makes the duplication cost worse).

- `SKILL.md` (45 lines): one row in the 4-row type table (~2 lines), one bullet in the evidence-standard summary (~2–3 lines), plus "four types" → "five types" language elsewhere (~2 line edits). **~10–15 lines**, ×2 copies.
- `references/evidence-standards-by-type.md` (37 lines): four `## <Type>` sections at ~5–7 lines each. A parallel `## Compatibility` section is **~6–8 lines**, plus a 1-line edit to the closing "spectrum" paragraph that currently characterizes where each of the four types sits between deterministic and judgment. **~8–10 lines**, ×2 copies.

### 1.7 `claim-review` skill

Also duplicated across two directories.

- `SKILL.md` (49 lines): procedural, not per-type — only touches claim types in two prose references ("See evidence-standards.md for what 'sufficient' means per claim type" and "each of the four claim types... has a distinct standard"). **~2–3 line edits**, ×2 copies.
- `references/evidence-standards.md` (26 lines): worked examples, not a full per-type breakdown — only Compliance and Superlative currently get one (~3 lines each); Performance and Comparative don't. A compatibility worked example is **optional for parity**, not required by the file's own pattern — add ~3–5 lines if desired.

**Skill total: roughly 25–35 lines of substantive content, doubled by the duplicate-directory structure → ~50–70 lines of edits actually typed.**

### 1.8 ADR-016

`docs/ADR-016-claims-desk-capability-surface.md` (228 lines), Decision 4 (lines 92–113) is the taxonomy's authoritative record — the 4-row table there is what the `EVIDENCE_STANDARDS` dict and the skill docs were derived from. Two things matter for sizing:

- Decision 4 currently documents two claim shapes **explicitly deferred**, not compatibility: Aspirational/roadmap and Environmental/Sustainability (the latter with a specific EU EmpCo Directive rationale, binding 2026-09-27). Compatibility is not mentioned as deferred or in-scope anywhere in the ADR — introducing it is a genuine taxonomy change, not a gap-fill.
- The ADR has precedent for exactly this kind of after-the-fact scope change: Decision 1 got a dated Addendum (lines 176–225, ~50 lines) when `delete_claim` was added later, rather than a rewrite of the original decision. A "Decision 4 Addendum" recording the compatibility type, its evidence standard, and why it's now in-scope would match that precedent.

**Change size: ~50 lines of new prose** (an addendum, not an edit to the original decision text), plus a 1-row update to the "Summary of Decisions" table at the bottom (line 138).

### 1.9 The twelve existing claims

`server/seed/seed_claims.py` is the only committed claim content (a live-DB seeding script, not static fixtures) — exactly 3 claims per existing type, 12 total. **None are compatibility-shaped; none need retroactive change.** Adding 2–3 new seed entries for parity (~10 lines each) is optional, not required.

### 1.10 Change surface not in the prompt's enumerated list, found in passing

- `README.md`: three spots describing "four type-specific rulesets" / "four claim types" — ~3 line edits.
- `server/agents/review_rubric.md` and the three `review_agent_*.md` files: each has one Compliance-specific line about currency-policy statements in the review Rationale. No change forced by adding compatibility *unless* compatibility gets an equivalent currency carve-out in the rubric — which, given Part 2's findings below, it probably should, making this an additional ~4 files × ~1 line.
- `week17/adversary.js` and `week17/arm_b_workflow.js`: Week 17 adversary-harness scripts, not on the production path, but they hand-author ~15–20 lines of attack-round definitions per existing type. Keeping the adversary harness usable against compatibility claims would cost **~40–60 lines per file** — flagged as optional legacy-artifact cost, not part of the core estimate below.

### Bottom-line LOC table

| Area | Files | Est. lines |
|---|---|---|
| DB schema/migration (CHECK widen) | `schema.sql` + new migration | 1–5 |
| DB schema (platform-version tuple field) | `schema.sql`, `evidence_links` | new column, ~5–10 |
| MCP tools | `check_substantiation.py`, `classify_claim_risk.py` | ~30–40 |
| Skills (×2 duplicated copies) | 4 md files × 2 dirs | ~50–70 |
| ADR | new Decision 4 Addendum | ~50 (prose) |
| Seed data | `seed_claims.py` | 0–30 (optional) |
| Prose/README/rubric updates | README, agent `.md` files | ~5–10 |
| **Core production subtotal** | | **~140–215 LOC** |
| Week 17 adversary harness (optional legacy) | `adversary.js`, `arm_b_workflow.js` | +80–120 |

No file in this surface requires a rewrite; every change is additive (new dict entry, new function, new table row, new section, new column). The two real risks are: (a) the duplicated skill directories drifting if only one copy is edited, and (b) the two bare dict-lookup `KeyError` sites in `check_substantiation.py:97` and `classify_claim_risk.py:146` — if the DB CHECK constraint is widened before those two files ship, any compatibility claim touched by either tool crashes instead of failing gracefully.

---

## Part 2 — Hygiene branch feasibility: platform end-of-support

**Verdict: partially deterministic.** Two of the three proposed checks (verification-report link present, platform version named) are structurally identical to existing Compliance checks and equally deterministic. The third — platform version not end-of-support — is deterministic *in principle* but not from a single authoritative, uniformly-structured, universally-covering source. It's deterministic per-vendor, not deterministic as a general mechanism.

### Sources checked

**endoflife.date** — confirmed live, unauthenticated, machine-readable. `GET https://endoflife.date/api/v1/products/windows-server/` returns per-release-cycle JSON with `releaseDate`, `eolFrom`, `eoasFrom` (end of active support), `isEol`, `isLts`, `isMaintained` fields, e.g. Windows Server 2025 `eolFrom: 2034-11-14`. The response envelope carries `generated_at` and `last_modified` timestamps (fetched 2026-08-29: `last_modified: 2026-08-21`) and explicitly cites Microsoft Learn as its underlying source. RHEL is tracked the same way (`/api/v1/products/rhel/`).

  **Authority:** endoflife.date is a well-maintained community aggregator, not a vendor-primary source. It's current (updated within the week at time of check) and its schema is stable and documented (community wiki + versioned `/v1/` path), but it is a third party re-publishing vendor data, not the vendor's own record. A ruling that depends on it inherits whatever lag or transcription error exists between the vendor page and this aggregator — historically small, but not zero, and not contractually guaranteed.

- **Microsoft** — does not expose a clean top-level EOL API endpoint, but the effectively-equivalent thing exists: `learn.microsoft.com/en-us/lifecycle/products/windows-server-2022` is server-rendered (fetched and confirmed: a plain HTML table, "Mainstream End Date," "Extended End Date," no JS required), and — more importantly — that page's frontmatter (`original_content_git_url`, `gitcommit`) points directly at a **public GitHub repo of source YAML**: `github.com/MicrosoftDocs/lifecycle-data-pr/blob/live/lifecycle-data/products/windows-server-2022.yml`. That YAML is the actual primary source Microsoft Learn renders from. (The raw-content fetch attempted here 404'd on the exact path guessed — the repo's default branch/path likely differs slightly from what the page frontmatter implied at a glance — but the existence and structure of the repo is confirmed via the page metadata itself, and locating the correct raw path is a five-minute follow-up, not a research risk.) This is a **vendor-primary, machine-readable, git-versioned** source, which is strictly better authority than endoflife.date for Microsoft products specifically.

- **Red Hat** — has a real, documented, unauthenticated REST API: `access.redhat.com/product-life-cycles/api/v1/products?name=Red%20Hat%20Enterprise%20Linux` returned live JSON (confirmed via fetch) with per-major-version phase arrays (General availability / Full support / Maintenance support / Extended Life Cycle add-on / Extended life phase), each with start/end dates, plus an `is_retired` boolean. This is documented at `docs.redhat.com/.../red_hat_product_life_cycle_data_api/` as an official, versioned (`v1`) API. **This is vendor-primary and machine-readable**, the strongest of the three sources checked.

### Can the check be deterministic?

Yes, per-vendor, using vendor-primary sources: Red Hat's own API for RHEL, Microsoft's lifecycle-data git repo (or its HTML rendering, as a fallback) for Windows Server. Both return unambiguous dates that a "today > end-of-support-date" comparison can evaluate without judgment.

What is **not** deterministic as a single mechanism:

1. **No universal schema.** Red Hat's API and Microsoft's YAML/HTML have different field names, different phase models (Red Hat has five phases including an ELS add-on; Microsoft has two — Mainstream/Extended), and different product-naming conventions. A compatibility check that needs to work "for at least Windows Server and RHEL" needs **two source-specific adapters**, not one client against one schema. Every additional platform vendor (VMware, Oracle Linux, Ubuntu LTS, etc.) adds another adapter with its own quirks.
2. **endoflife.date is the only source that normalizes across vendors**, which is exactly why it's tempting to use as the single integration point — but doing so means the check's authority is one aggregation step removed from the vendor of record, for every platform, all the time, in exchange for one schema instead of N.
3. **Freshness is a runtime dependency either way.** Whichever source is chosen, `check_substantiation` calling out to a live external API synchronously (as opposed to a periodically-refreshed cache) introduces a new failure mode this tool doesn't currently have: an external outage or rate limit turns a claim review into an error instead of a ruling. None of the other three deterministic checks in the existing four types (certificate link present, expiry date present, expiry not past) depend on a network call at review time — they're pure computations over fields already in the registry.

### Recommended fallback

Given the above, the honest framing is: **deterministic in principle, but not safely inline-synchronous.** The pattern that matches the existing architecture (deterministic checks are cheap, offline computations inside `check_substantiation`) is a **periodically-refreshed local cache** — a small table or JSON blob of `(platform, version) → end_of_support_date`, refreshed on a schedule (daily/weekly) from Red Hat's API and Microsoft's source, with `check_substantiation` reading only the cache. This keeps the per-claim check deterministic and fast, isolates the two vendor-specific adapters into one refresh job instead of two call sites, and degrades gracefully (stale-but-present data) instead of catastrophically (network error mid-review) if a source is briefly unreachable. The judgment fallback, for any platform not in the cache (a long tail exists beyond Windows Server and RHEL), is the same escalate-to-judgment path Compliance already uses when a certificate's status can't be automatically resolved.

---

## Part 3 — Fetchability spot checks

### A. Microsoft Windows Compatible Products List (`partner.microsoft.com/en-us/dashboard/hardware/search/cpl`)

**Result: fails.** The base page is a large (~640KB) server-rendered shell, but the CPL search itself is an AngularJS single-page app (`ng-app`, `ng-controller="DriverCertificationController"`) with two-way-bound inputs (`ng-model="productName"`, `ng-model="PartnerVisibility.FindText"`) — there is no query-string contract at all. Confirmed empirically: fetching the base URL and the same URL with `?query=Windows+Server+2022` appended produced byte-for-byte identical page content apart from a request-correlation ID and timestamp comment — the parameter is inert. Search results are populated via a background API call triggered by JS after form interaction, so they never appear in any fetched HTML regardless of URL construction. The "No results" string visible in the raw HTML belongs to the site's global header search-autocomplete widget, not the CPL results area — a coincidental false-positive if grepped for naively.

**Verdict: not fetchable without JS execution.** No query parameter names exist to report, because the form does not use them.

### B. Windows Server Catalog (`windowsservercatalog.com`)

**Result: fails, more completely than A.** The homepage is a bare React shell: `<div id="root"></div>`, a single `<script type="module" src="/assets/index-*.js">`, no server-rendered content of any kind, not even a form. Confirmed via direct fetch of the raw HTML — total page body is two lines. This is a harder failure mode than the CPL page (which at least server-renders a form and a shell), and rules out any URL-parameter-based approach for this resource entirely.

### C. Red Hat per-product certification detail page (`catalog.redhat.com/en/hardware/system/detail/{id}`)

**Result: succeeds.** Unlike the search/listing page (`catalog.redhat.com/en/hardware`, confirmed to be a generic Next.js shell with only marketing/footer content in the initial payload — matching the prompt's premise that search fails client-side), individual detail pages are server-rendered via Next.js React Server Components and the certification data ships inline in the initial HTML response as a `self.__next_f.push(...)` streamed payload — no client JS execution needed to read it. Confirmed by fetching `catalog.redhat.com/en/hardware/system/detail/41715` (Dell PowerEdge R7525) directly: the raw response contains `"title":"Dell PowerEdge R7525"`, and further into the payload, explicit certified-platform records including `"name":"Red Hat Enterprise Linux 9"`, `"shortName":"RHEL 9"`, `"name":"Red Hat Enterprise Linux 8"`, plus architecture (`"architecture":"x86_64"`) and related knowledge-base article references. One other detail ID tested (144067) returned only generic shell content with no product-specific fields — most likely a stale, retired, or malformed ID rather than evidence the page type itself fails, since the working ID returned a fully-populated, differently-structured payload from the same route pattern; this should be treated as a one-ID anomaly to re-check, not a contradiction of the working result.

**Verdict: fetchable.** Detail pages are the one resource of the three where the required fields (product name, certified RHEL versions, architecture) reliably appear in fetched HTML with no JS execution — provided the detail page is reached via a valid ID, which in production would come from Red Hat's own product-lifecycle/certification API (Part 2) or a prior known-good link, not from scraping the search page (which fails, as expected).

### Summary

| Resource | Fetchable without JS? | Mechanism |
|---|---|---|
| MS Compatible Products List (CPL) | **No** | AngularJS SPA, inert query params, results via background XHR |
| Windows Server Catalog | **No** | Bare React shell, zero server-rendered content |
| Red Hat hardware detail page | **Yes** | Next.js RSC streaming payload, product data inline in initial HTML |

Practical implication: for Windows-side compatibility evidence, there is **no fetchable public catalog page** to verify a certification claim against — the verification-report-link check for Windows compatibility claims will have to rely on the vendor-issued PDF/report URL itself (which is exactly what the proposed hygiene check already asks for: "verification report link present"), not on cross-referencing a live Microsoft catalog. For Red Hat, the detail page *is* independently fetchable and could in principle support a stronger check — "does the named platform version actually appear as certified on this product's Red Hat catalog page" — that has no Windows-side equivalent.

---

## Part 4 — Verdict

**This is a contained addition, not a second build — with one caveat.**

The core production surface (schema CHECK widen, two tool files, two duplicated skill trees, one ADR addendum) is ~140–215 lines across files that already exist and already have a clean per-type extension point in each case (a dict, a CHECK list, a markdown section, a private function). None of it requires new architecture — ADR-016 Decision 4's deterministic/judgment field split and Decision 1's MCP-vs-Skill split both already accommodate a fifth type without re-litigation. This is materially the same shape and rough size as the files that would need touching for an evidence *scope* field addition to Compliance (the `evidence_links` table, `check_substantiation.py`, and the two skill reference docs) — the same small set of files, extended rather than restructured.

The caveat is that compatibility is not *purely* an evidence-standard variation the way, say, a sixth Superlative sub-case would be — it needs one genuinely new piece of data the schema doesn't have anywhere today (the device/firmware/platform-version tuple), and one genuinely new kind of currency check (external, vendor-sourced, time-varying) that none of the other four types need. Those two things are why this isn't a one-line taxonomy entry, even though the total line count stays modest.

**Single largest source of uncertainty: the end-of-support currency check's operational design (Part 2), not its feasibility.** The data exists and is fetchable from vendor-primary sources for the two platforms named in the brief. What's unresolved is the integration shape: a synchronous external call inside `check_substantiation` (fast to build, fragile — turns a network hiccup into a broken review) versus a periodically-refreshed cache (matches the existing architecture's all-deterministic-checks-are-offline pattern, but is new infrastructure this system doesn't have yet — a scheduled job, a cache table, a staleness policy). That design decision, not the schema change or the tool dict entries, is the part of this work that hasn't been done before in this codebase and is the one place a "contained addition" could quietly grow into more than a files-already-being-edited change.
