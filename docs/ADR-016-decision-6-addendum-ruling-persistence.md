# Decision 6 Addendum — Ruling Persistence: Append-Only Facts, Derived State

**Date:** 2026-09-03
**Status:** Accepted
**Amends:** Decision 1 (Claims Desk capability surface) — supersedes part of Decision 1: `get_claim_status` and `check_substantiation` no longer return `claims.status`, and their claim objects now carry two derived fields instead. The capability split in Decision 1 is otherwise unchanged.
**Precedent:** follows the Decision 1 and Decision 4 addendum pattern. The original decision text is left intact; this addendum records what changed and why.

---

**The question:** When the Week 17 adversary produces a verdict, where does it land, and how does a claim's published verification state relate to its ruling history?

### What was found before deciding

Three facts were established by live introspection before any option was weighed, and two of them contradicted assumptions carried into the week.

`review_rulings` was empty. Zero rows, never written to since Week 16 created it. Its `ruling` column carried a CHECK constraint on `approved` / `rejected` / `escalated`.

`review_rulings.claim_id` has **no** `ON DELETE` clause. This ADR's own downstream documentation had been read as saying a cascade fix was an outstanding Week 17 prerequisite; it is not, and `schema.sql` and `delete_claim.py` both document the absence as deliberate (Week 18 d1). `NO ACTION` is also correct under append-only: a hard delete of a claim with rulings fails loudly, and a soft delete leaves rulings intact.

`claims.status` was dead. All 47 rows read `unverified`. The column had never held another value in production, and the only write to either status field anywhere in the repo is `delete_claim.py` setting `record_status`.

### The collision

Three vocabularies described three different things, and two of them were being asked to share one column.

| Concept | Values | Owner |
|---|---|---|
| Verification state — what review found | `substantiated` / `partially` / `not_substantiated` / `escalate` | the d6 ruling artifact |
| Disposition — what the reviewer decided to do | `approved` / `rejected` / `escalated` | `review_rulings.ruling` CHECK |
| Lifecycle — is this record live | `active` / `deleted` | `claims.record_status` |

Mapping verdicts into `claims.status` (`unverified` / `substantiated` / `insufficient` / `expired`) is partial: `partially` and `escalate` have no home, and `expired` is produced by no verdict at all. That column also packs two orthogonal dimensions — verification state and temporal validity — which move independently. A substantiated claim expires with no review occurring; a claim can be both partially substantiated and expired.

### Options considered

- **A — widen both.** Widen `review_rulings.ruling` to the four verdict values and widen `claims.status` to match. One vocabulary end to end. Cost: two migrations, and `claims.status` grows values meaning review outcomes while still holding `expired`, a lifecycle state.
- **B — widen the ruling, map lossily.** `partially` collapses to `insufficient`, `escalate` to `unverified`. One migration. Rejected: the manifest would publish `insufficient` for a claim a reviewer found partially substantiated, and publishing a truthful machine-readable status is the entire premise of Build A.
- **C — read the verdict from `latest_ruling`, leave `claims.status` alone.** No mapping needed.
- **C+ — C, plus deprecate `claims.status` (chosen).**

### Conclusion: facts append, state derives

`review_rulings` is the append-only source of truth. A ruling is a fact about what a review found at a moment in time; facts are not updated, they are superseded by later facts. Verification state is a projection of that history, computed on read.

**Schema.** `ruling` renamed to `verdict` with a CHECK on the four artifact values — a rename rather than a second column, because the table was empty and adding would have left `ruling` in place holding a disposition vocabulary nothing writes. Added: `convergence` (CHECK: `attack_exhaustion` / `round_cap`), `rounds`, `written_by_session`. Index on `(claim_id, created_at DESC)`. FK left exactly as found.

**Derivation rules, authoritative.**

- `verification` — the `verdict` of the most recent row for this claim by `created_at DESC`; the literal string `unreviewed` when no ruling exists. Never null.
- `evidence_current` — computed from evidence `expiry_date` against the current date. `true` if every evidence row with an `expiry_date` is unexpired, `false` if any is expired, `null` if no evidence row carries one. Null means unknown, not current.

Neither is stored. Both are computed at read time in the tool layer.

**`claims.status` deprecated.** Not widened, not remapped. The tools stop returning it; the column remains in the table pending a later migration. `record_status` is unchanged, because lifecycle is an owned fact rather than a derivation.

**Why derive rather than store.** Every reader goes through the MCP tool layer — nothing queries the tables directly — so a computed answer is consistent everywhere by construction. In a system with many direct readers this would call for a materialized view; here the tool layer *is* the view. A stored column would require every write path that could change the answer to update it transactionally under a total mapping, and the moment that mapping is partial the column and the history disagree. That defect was already latent in `claims.status`; it was invisible only because the table was empty.

`expired` in particular should never be stored: it is a pure function of `expiry_date` and the clock, so a stored value is wrong the moment midnight passes unless something sweeps the table.

### The write gate

Derived state removes any gate between a ruling landing and an external agent reading it. The safeguard moves to the write path rather than being abandoned, following the Week 18 launcher pattern: the agent proposes, the launcher persists conditionally.

A ruling persists only if the verdict parses to one of the four values **and** the convergence guard fired with a known termination mode. `escalate` persists like any other verdict; it is not held for review, because a review queue nobody processes is worse than a published escalation. Gate failures are logged by the launcher and never become rows.

The gate checks shape, not correctness. A well-formed ruling with a wrong verdict passes. This is accepted because the tool's operating life ends with the project and no new claims will be added, bounding the window in which an uncaught verdict could mislead. A production deployment with ongoing review volume should hold escalations — while designing to keep escalation volume low, since a queue that grows faster than it drains stops functioning as a control.

Append-only makes the residual risk tolerable in a specific way: a bad ruling cannot be quietly removed, only superseded by a visible later row.

### Deliberate deferrals

**Disposition column.** No writer produces a disposition. The d6 ruling artifact carries `## Verdict` with the four values and nothing corresponding to approve/reject; a repo-wide grep for `approve|reject|disposition` returns nothing outside parse docstrings. Shipping a nullable column now would be a column nothing populates, justified by a use case that does not exist. Add it when a writer exists.

**Provenance column.** Eight fixture rulings written by a test suite running against the live database were, on inspection, indistinguishable in shape from instrument-produced rulings. The reflex fix is a `provenance` column; it is the wrong fix, because the column would be populated by the same code paths that wrote the fixtures, and a test writing to production will write `provenance: real` without hesitation. The root cause was test isolation, and that is what was fixed: every test that writes now runs inside a rolled-back transaction. `reviewed_by` already carries the instrument identifier and is what distinguished the real rows. Revisit if a second legitimate writer appears.

**Materialized projections.** None. The scaling boundary is named rather than guessed at: at current volume, derive-on-read is not a cost. If claim count reaches a scale where a consumer filters by verification state across the whole registry, that is when a materialized view earns its complexity.

**Full event sourcing.** Explicitly not adopted. No projection tables, no replay machinery, no supersession chains. The principle taken is "facts append, state derives," implemented as one append-only table and two computed reads. Scoped this precisely so the pattern does not become a program.

### One documented exception to append-only

The eight fixture rulings were **deleted**, not superseded, via a committed script targeting explicit `ruling_id`s that refuses to run if the count differs from eight. The append-only principle protects a record of facts from silent revision; those rows were not facts. Supersession also fails mechanically here — the verdict vocabulary has no value meaning "retracted, never a real review," so a superseding row would still publish some verdict for a claim no instrument reviewed. The vocabulary could not express the correction, so deletion was the only honest mechanism available.

### Known limitation: provenance is asserted, not attested

The manifest states which instrument produced each verdict, when, and under what termination condition. Nothing cryptographically binds the manifest to the registry, and nothing independent binds the registry's verdicts to anything outside this system. An agent's remedy is the `substantiation_url` hop, where the registry speaks for itself — but the registry is the same author's system.

This was identified unprompted by an external agent during Week 20's Day 4 gap analysis, which noted that the verdicts come from the product's own automated reviewer rather than an independent third party and that this bears on how persuasive the demo is. It is recorded here rather than in a footnote because it is the honest boundary of what the artifact demonstrates: it shows that a claim's substantiation state can be made machine-readable and traversable, not that it can be made independently verifiable.

---

## Knock-on edits required elsewhere in this ADR

1. **The Decision 1 Addendum's cascade section is factually wrong and must be corrected in place.**

   `## Decision 1 Addendum: delete_claim tool (Week 17)` contains `### Known issue — review_rulings cascade (Week 18 hard prerequisite)`, which states that `review_rulings_claim_id_fkey` also has `ON DELETE CASCADE`, that `delete_claim` currently wipes rulings alongside claims, and that fixing this is "a hard prerequisite for Week 18, not a soft backlog item."

   Live introspection on 2026-09-02 found the FK has **no `ON DELETE` clause at all**. `schema.sql` carries the inline comment `-- no cascade: rulings survive a soft-deleted claim (d1)`, and `delete_claim.py`'s docstring documents the absence as deliberate. The ADR and the code it cites contradict each other, and the ADR is the one that is wrong.

   Correct it in place rather than deleting it: strike the claim, state what introspection found, and note that `NO ACTION` is the correct behavior under Decision 6's append-only design, since a hard delete of a claim with rulings fails loudly while a soft delete leaves rulings intact. A prerequisite that never existed is worth preserving as a record of how the documentation drifted — this text is the upstream source of the same error appearing in the project's standing instructions and, from there, in Week 20's own planning.

2. **Summary of Decisions** — add row 6:

| # | Decision | Options Considered | Choice | Rationale |
|---|---|---|---|---|
| 6 | Ruling persistence and verification state | Widen both / widen ruling + lossy map / read from `latest_ruling` / that plus deprecate `claims.status` | Append-only `review_rulings`; `verification` and `evidence_current` derived on read; `claims.status` deprecated | `claims.status` packed two orthogonal dimensions under a partial mapping and had never held a non-default value; all reads go through the tool layer, so computed-on-read is consistent by construction |

3. **Out of Scope** — add three entries: the disposition column, the provenance column, and materialized projections, each with the deferral reason from Decision 6 and the condition that would revisit it.

4. **Decision 1** — add a pointer noting that Decision 6 supersedes the return shape of `get_claim_status` and `check_substantiation`. The capability assignment itself is unchanged.

5. **Decision 5 and the Context section** — handled by a separate addendum, not here. The Decision 4 addendum (2026-08-30) already flagged Decision 5 in detail and explicitly reserved a Decision 5 addendum "once that disposition is decided," asking that it not be folded into another addendum. That disposition is now decided; see `ADR-016-decision-5-addendum-build-scoping.md`, which carries the week relabels, the correction that Build A spans two repos rather than living wholly in the monorepo, and the open question about the Broadcom backlog page and demonstration-bucket claims that were scoped as manifest material but did not ship in it.

6. **Not closed by this decision, and not to be implied otherwise.** The Decision 4 addendum deferred evidence-agent routing for compatibility claims "until the adversary next runs." The adversary ran three times in Week 20 — performance, comparative, compliance — and never against a compatibility claim. That deferral remains live.
