# Decision 5 Addendum — Build A and Build B Scoping Resolved

**Date:** 2026-09-03
**Status:** Accepted
**Amends:** Decision 5 (Repo structure — per-build repos vs. Claims Desk monorepo)
**Precedent:** follows the Decision 1 and Decision 4 addendum pattern. The original decision text is left intact; this addendum records what changed and why.

---

## Context

The Decision 4 addendum (2026-08-30) flagged Decision 5 as no longer describing the plan, and declined to resolve it:

> Week 19's scope changed after Week 18's outcome: the Kalder manifest page and the false-premise eval harness moved outside the arc and their disposition is undecided. So `false-premise-eval` is not being created this week and Build A/Build B no longer name anything real.
>
> A Decision 5 addendum is warranted once that disposition is decided, and it should not be folded into this one, which is about the taxonomy.

That disposition is now decided. This addendum records it.

---

## What changed

Week 19 ran a cross-session Memory retest rather than either syllabus build, and ended in a kill. The two builds Decision 5 scopes were not started that week. Week 20 was reframed as completing them, split across two weeks after the work was sized:

- **Build A — the agent-readable Kalder product page and claims manifest.** Built and shipped in Week 20, inside the `claims-desk` monorepo for the registry-side work (schema migration, `append_ruling`, the read-only `GET /claims/{slug}.json` route) and inside the `ai-portfolio` repo for the page, manifest, and generator. Live at `https://www.richardthomchick.com/projects/claims-desk/demo`.
- **Build B — the standalone false-premise eval harness.** Scheduled for Week 21. The `false-premise-eval` repo is still not scaffolded, for the same reason Decision 5 gave originally: it gets created when the build starts.

Week 21 is a hard cap on the arc's builds. Publishing and documentation debt land in a wrap period after it, with no fixed date.

---

## Decision

**Decision 5's hybrid conclusion stands unchanged. Only its week labels and its repo assumption need correcting.**

The reasoning that produced the hybrid — shared claim types defined once, and a harness whose reusability premise requires it to stand apart — was never contingent on which week the builds landed in. Both halves held under a two-week slip.

Two corrections to the text as written:

**Week labels.** "Week 19 Build A" is Week 20. "Week 19 Build B" is Week 21. The same relabel applies to the Context section's downstream-consumers paragraph, which names "Week 19's claims-manifest product page and standalone false-premise eval harness."

**Build A is not wholly inside the monorepo.** Decision 5's hybrid assumed Build A would live in `claims-desk`. In practice it spans two repos, and the split is not arbitrary:

- Registry-side work is in `claims-desk`, because it is the registry: the append-only `review_rulings` migration, the `append_ruling` tool, the derived-read changes to `get_claim_status` and `check_substantiation`, and the read-only HTTP route the manifest links to.
- The page, the manifest, the `llms.txt`, and the generator script are in `ai-portfolio`, because they are website content. The page is an Astro route on an existing deployed site; importing it into the Claims Desk repo would have meant standing up separate hosting for four claims' worth of HTML.

This is a widening of the hybrid rather than a departure from it. The principle Decision 5 actually settled — that shared claim types are defined once and that a component whose purpose is standing apart gets its own repo — is unchanged. The manifest generator reads claim types over HTTP from the registry rather than redeclaring them, so no duplication was introduced.

---

## Consequences

**The manifest exists, and it is smaller than Week 19 assumed.** The Decision 4 addendum notes that "something downstream still assumes the manifest exists: the Broadcom backlog page and the demonstration-bucket claims (AMD SeaMicro 2012, Cisco 2009 UCS) were both scoped as manifest material."

The manifest now exists and carries four claims: `kalder_resolve-performance-01`, `kalder_resolve-comparative-01`, `kalder_vendor-compliance-01`, and `salesforce_govcloud-compliance-01`. None of the Broadcom or demonstration-bucket claims are in it, and none of the six `vendor_compat` compatibility claims are either.

That is a scoping decision, not an oversight, and the reason is category rather than quality. The published set was chosen to span verification states and evidence-retrievability rather than to exhaust the registry. The compatibility rows were investigated for inclusion during Week 20 and set aside because they are not claims in the sense the rest of the registry uses the word.

A claim is an assertion someone makes. What those six rows hold is an *extracted text span* — a capture of where an assertion appeared on a vendor page, with the surrounding context preserved. One carries a bulleted OS-support list with column whitespace and a "see Dell.com/OSsupport" trailer. Another carries a bracketed editorial note about the text's position relative to a call-to-action block and a duplicate hero render. Those are faithful capture records and they are useful as such; they are simply a different object from an authored claim, and a page that renders `claim_text` as the claim would have displayed a note about source-page layout to an agent.

**This is a schema observation, not just a scoping one.** `claims.claim_text` currently holds both authored assertions and extracted spans, and nothing distinguishes them — no field, no claim type, no flag. That is the same shape as the three-meanings-of-`status` collision Decision 6 resolves: two different objects sharing a column because the difference had not yet needed naming. Extraction is a legitimate and interesting use case; it is not the same scope as claim authoring, and the registry does not currently model the difference.

**What this leaves open:** whether the Broadcom backlog page and the demonstration-bucket claims still have a home. They were scoped as manifest material and the manifest shipped without them. Either the manifest grows later, or those claims need a different destination, or the scoping that produced them is retired. Not resolved here.

**Compatibility claims remain unexercised by the adversary.** The Decision 4 addendum deferred evidence-agent routing for compatibility claims "until the adversary next runs." The adversary ran three times in Week 20 — against a performance, a comparative, and a compliance claim — and never against a compatibility claim. That deferral is still live, and Week 20 did not close it.

---

## Open

- **Disposition of the Broadcom backlog page and demonstration-bucket claims.** Scoped as manifest material; manifest shipped without them.
- **Whether the registry should model extracted spans as distinct from authored claims.** The six `vendor_compat` rows are captures, and the schema treats them as claims. Options range from a flag, to a distinct record type, to leaving the two mixed and handling the difference at each consumer. Displaying them on a page is only the first consumer to hit the distinction; the adversary and the review agent will each hit it differently, since an attack on a captured span is partly an attack on the capture. Not urgent, and not resolvable by re-authoring the text — re-authoring would change what the registry recorded, which is the one thing a capture record exists to preserve.
- **`false-premise-eval` repo scaffolding.** Week 21. Second test endpoint for the harness is not yet named; the Claims Review Agent is the first.
