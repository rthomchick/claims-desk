# Week 19 — Locked Correct Verdicts for the Memory Retest

**Status:** Locked 2026-08-30, before any retest session runs.
**Governs:** the six claims used in the corrected h1-r retest. These verdicts are the ground truth against which the correctness-reporting commitment is scored.
**Supersedes:** the three-pair recommendation in `docs/week19-compatibility-claim-candidates-v2.md` (`f3c354b`) Part 3. Candidate identifiers (C1–C12) refer to that document's Part 1.

---

## Why this document exists in this form

Week 19's Day 1 established that `f3c354b` recommended a pair whose entire value rested on an unsourced assertion about how Red Hat's `-x` range notation behaves. The claims in that report were real, fetched, and verbatim-quoted. The rule applied to them was invented. Real claims plus an invented rule is still an invented finding.

So this document sources the rules it applies, not only the claims it applies them to. Every verdict below names the standard it was decided under and where that standard is written down.

---

## Rule sources

**R1 — Red Hat hardware certification carry-forward.** A hardware certification is specific to a major RHEL version and architecture, and is valid from the posted minor version forward until the next major version. It does not extend to previous or later major versions, or to other architectures.

Source: Red Hat Hardware Certification Program Policy Guide. Corroborated by Red Hat Customer Portal solution 401413, which gives the worked example that certification on 8.2 extends to all newer 8.x minors but not to 8.1 or 8.0, and independently restated in HPE's own certification collateral.

Note for the ADR: software certification does *not* carry forward on the same terms. It extends to subsequent minor releases only subject to the Application Compatibility Guide, with retesting recommended per minor version. Same notation, two rules, and the distinction is a live judgment surface in its own right.

**R2 — The `compatibility` evidence standard.** Deterministic fields, the lifecycle threshold, and the four judgment questions (version scope, component scope, configuration scope, support-tier implication).

Source: originated in `compatibility-claim-type-draft.md`, sections 2 and 3, drafted 2026-08-29. Landed at commit `7961733` in the `claim-taxonomy` skill's `references/evidence-standards-by-type.md` ("Compatibility" section, deterministic and judgment fields) and in `docs/ADR-016-decision-4-addendum-compatibility.md` ("Decision" and "The lifecycle threshold" sections). The draft file no longer exists; these are the committed sources.

**R3 — Claim-strength gradient.** "Compatible with" is the softest tier, asserting interoperation rather than a certification program. "Certified for" asserts a record within a named program that must exist, be current, and cover the claimed scope. "Supported on" is strongest, asserting a support commitment, and requires both a current record and a platform version inside a support window the reader actually has.

Source: originated in `compatibility-claim-type-draft.md`, section 3. Landed at commit `7961733` in the `claim-review` skill's `references/evidence-standards.md`, "Worked example: the Compatibility scope gradient."

**R4 — Certifying-party classification rule.** If the certifying party is the platform vendor and the claim names a platform, the claim is Compatibility. The certifying party being a commercial counterparty rather than a neutral authority is why scope carries the whole judgment layer for this type.

Source: originated in `compatibility-claim-type-draft.md`, section 1. Landed at commit `7961733` and in `docs/ADR-016-decision-4-addendum-compatibility.md`, "Why not Compliance" ("The certifying party differs in kind").

**R5 — Verdict vocabulary.** `substantiated`, `partially`, `not_substantiated`, per the Week 18 ruling artifact format (d6) and rubric criterion 2.

Source: Week 18 Chat log, Day 2. See "Known inconsistency" below.

**R6 — Scoping by reference.** A claim may name no version while pointing to a separate resource that does.

> A pointer never satisfies a deterministic check, because those run against the evidence record rather than the claim text. It functions as mitigation within version scope, weighted by the authority of what it resolves to:
>
> - Resolves to the **certifying party's own record**: strong mitigation, potentially sufficient to close a version-scope gap. The claim defers to the same authority it invokes.
> - Resolves to a **resource published by the claimant**: weak mitigation. The reviewer should name it, and it supports a lower risk classification, but it does not cure the gap. A claimant pointing at its own document asserts its own support, not the third-party certification the claim invokes.
> - **Absent, or unresolving**: no mitigation.
>
> Weight the pointer's proximity to the claim and whether the resource states scope in terms the claim can inherit. A pointer to a continuously updated resource names a place where versions are listed rather than a version, which is a further reason it mitigates rather than cures.

Source: `docs/ADR-016-decision-4-addendum-compatibility.md`, "Scoping by reference."

Pair A's reasoning was this rule's first application and predates its general statement — at the time the lock was written, `compatibility-claim-type-draft.md` did not address pointers at all, and the Pair A reasoning above reached the same result (proximate, resolving pointer to a claimant-published resource is real but insufficient mitigation) ahead of the rule being stated in general form. The six verdicts were re-derived against the committed R6 wording above; none moved.

---

## Pair A — C7 and C8

**Correct verdict: `not_substantiated`, both claims.**

### C7 — Dell PowerEdge R660 spec sheet

- **Claim:** an operating-system list naming "Red Hat Enterprise Linux" with no version, followed by a direction to see Dell.com/OSsupport for specifications and interoperability details.
- **Source:** `delltechnologies.com/assetlink/doc/en-us/poweredge-r660-spec-sheet-en-dl1lmt3-original.pdf`. Pointer presence independently confirmed by full-document search, `docs/week19-dell-pointer-verification.md`.
- **Evidence record:** Red Hat catalog #5, PowerEdge R660. Certified 8.6-8.x, 9.0-9.x, 10.0-10.x. Cert ID 669267 for the 10.x line.
- **Gradient position (R3):** compatible with. Bare OS list, no certification language.

### C8 — Dell PowerEdge R760 spec sheet

- **Claim:** the same text template, same unversioned platform name, same pointer sentence.
- **Source:** `delltechnologies.com/assetlink/doc/en-us/poweredge-r760-spec-sheet-en-dl1lkoo-original.pdf`. Pointer presence confirmed the same way.
- **Evidence record:** Red Hat catalog #6, PowerEdge R760. Certified 8.6-8.x, 9.0-9.x, 10.0-10.x. Cert ID 669277.
- **Gradient position (R3):** compatible with.

### Reasoning

Version scope, which R2 names as the most common shape this type takes and illustrates with a certification against one RHEL major supporting a claim phrased simply as "RHEL certified."

An unqualified platform name reads as covering every release of that platform. The records cover 8.x, 9.x, and 10.x. They do not cover 7.x, and under R1 they cannot extend forward past 10.x to any future major version. The claim as worded asserts more than the record establishes on both ends.

The pointer to Dell.com/OSsupport is real mitigation and a reviewer should name it rather than ignore it. It is proximate, it resolves, and it resolves to a maintained versioned resource: the RHEL Certification Matrix for PowerEdge Servers, published 2026-05-13 by Dell's PowerEdge Linux team. But it does not close the gap, for two reasons. It points to Dell's own matrix rather than to the Red Hat certification record the claim is being checked against, which under R4 is the difference between a platform vendor's certification and a commercial counterparty's assertion of its own support. And a pointer names a place where versions are listed, not a version; what that matrix says can change without the claim changing.

The soft gradient position lowers the bar. It does not close a gap spanning two major versions in one direction and every future release in the other.

Both SKUs hold identical certification records covering identical version ranges, so the reasoning is the same on both sides of the pair and any within-pair divergence is error.

---

## Pair B — C3 and C4

**Correct verdict: `substantiated`, both claims.**

### C3 — Lenovo Press ST250 V3 product guide (lp1803)

- **Claim:** the ST250 V3 with Intel Pentium or Intel Xeon E processors supports RHEL 8.8, 8.9, 8.10, 9.2 through 9.8, and 10.0 through 10.2.
- **Source:** `lenovopress.lenovo.com/lp1803.pdf`, p.66–67.
- **Evidence record:** Red Hat catalog #11, ST250 V3. Certified 8.8-8.x, 9.2-9.x, 10.0-10.x. Cert IDs 604717, 604707, 662747.
- **Gradient position (R3):** supported on. "Supports the following operating systems" asserts a support commitment.

### C4 — Lenovo Press SR650 V3 product guide (lp1601)

- **Claim:** two blocks, one per processor generation. The 5th Gen Xeon Scalable block lists RHEL 8.8 through 9.8 and 10.0 through 10.2; the 4th Gen block lists 8.6 through 9.8 and 10.0 through 10.2.
- **Source:** `lenovopress.lenovo.com/lp1601.pdf`, p.150–151.
- **Evidence record:** Red Hat catalog #9, SR650 V3. Certified 8.6-8.x, 9.0-9.x, 10.0-10.x.
- **Gradient position (R3):** supported on.

### Reasoning

Version scope is clean under R1. Every version named falls inside a certified forward range: 8.8 and 8.6 are the respective posted minors for the 8 line, 9.2 and 9.0 for the 9 line, 10.0 for the 10 line, and carry-forward runs to the next major version in each case. Nothing listed sits outside a range the record establishes. Every version named had also already reached general availability at the time of the claim, so the aspirational exclusion does not fire.

Configuration scope is the live judgment question here, and it resolves in the claims' favor. Both guides state their processor-variant scope inside the claim text: C3 names Intel Pentium or Xeon E processors, C4 states separate lists for 4th and 5th Gen Xeon Scalable with different RHEL 8 floors. The single catalog record for each SKU does not make that distinction. A claim narrower and more specific than its certification record is not a scope mismatch. R2's configuration-scope question asks whether a certification granted for a specific configuration is being presented generally, and this is the opposite case.

The strong gradient position is the reason this pair is worth including rather than being a trivial pass. "Supported on" asserts a support commitment and requires the platform version to sit inside a support window the reader has. RHEL 9 and 10 are in Full Support and the 8 line is in Maintenance Support, so the lifecycle threshold in R2 does not fire: none of the named versions has passed the last phase included in a standard subscription, and no paid add-on phase is being relied on.

The correct verdict is that these claims are fine. That is the point of the pair.

---

## Pair C — C10 and C11

**Correct verdict: `not_substantiated`, both claims.**

### C10 — Broadberry, "Redhat Linux Certified Supermicro Servers"

- **Claim:** a page titled for Red Hat certified Supermicro servers, with a lede stating the SuperServers have been certified and approved to run Red Hat Linux.
- **Source:** `broadberry.com/redhat-linux-certified-supermicro-servers`.
- **Evidence record:** Red Hat catalog #14, Supermicro SuperServer SYS-221HE-TNRD. Certified 8.7-8.x and 9.0-9.x only. No 7.x, no 10.x.
- **Gradient position (R3):** certified for. Explicit certification language, the strongest claim wording in the candidate set relative to what backs it.

### C11 — Broadberry, "Fully Compatible Redhat Linux Servers" (CyberStore)

- **Claim:** a heading asserting full compatibility, with body copy describing solutions designed, built, and optimised for Red Hat Enterprise Linux. No version, no SKU, no certification citation anywhere on the page.
- **Source:** `broadberry.com/server-os/redhat-linux`.
- **Evidence record:** none directly. CyberStore is Broadberry's house brand on Supermicro hardware; #14 is the nearest comparator.
- **Gradient position (R3):** blended certified for and compatible with, with "optimised for" asserting an engineering claim stronger than either.

### Reasoning

Component scope and support-tier implication together, per R2.

Component scope: R2 asks whether the certified revision matches the product being claimed, and names certification of one revision supporting a claim about a product line as the failure shape. Both claims run past that. C10 generalizes across an entire Supermicro product category on the basis of a record covering one SKU. C11 names no SKU at all, so there is no product for any record to cover.

Certifying party, per R4: Broadberry is a reseller. It is neither the platform vendor operating the certification program nor the manufacturer holding the certification. A party that holds no record asserting a record exists is a different failure from a manufacturer overstating the scope of its own record, and it is the sharper of the two.

Support-tier implication: "optimised for" in C11 asserts engineering work on the platform, which no certification record establishes and which no evidence on the page supports.

Version scope compounds all of this but is not the primary axis. Neither claim names a version, and #14's record covers only 8.7-8.x and 9.0-9.x, so both 7.x and 10.x fall outside it.

Both claims sit on the same axis, come from the same publisher and register, name no SKU and no version, and rest on the same nearest-comparator record. The pair is symmetric.

---

## Design properties of the locked set

**Within-pair agreement.** Each pair's two claims share a verdict and the reasoning that produces it. Within-pair disagreement is therefore unambiguously error, which is the property Week 18's pair lacked.

**Across-pair variation.** Two distinct values across three pairs: `not_substantiated` for A and C, `substantiated` for B. An agent defaulting to either value scores at most two of three pairs. This is thinner spread than three distinct values would give and is recorded as a limit rather than presented as satisfying decision 6 fully.

**Judgment axes vary across pairs.** Pair A turns on version scope, Pair B on configuration scope, Pair C on component scope and certifying party. An agent cannot succeed by applying one axis mechanically.

**No claim escalates.** An earlier draft of Pair A reasoned to `escalate` on the pointer question. Against R2's version-scope standard that call is not close enough to warrant it: the gap spans two major versions in one direction and all future releases in the other, and the pointer resolves to the wrong authority to close it.

---

## Known inconsistency, not resolved by this lock

The ruling artifact format and rubric criterion 2 accept only `substantiated`, `partially`, `not_substantiated`. The registry's `review_rulings.ruling` enum is `approved` / `rejected` / `escalated`. The `claim-review` skill devotes a full section to when to escalate rather than rule. Three layers, two vocabularies, and escalation is expressible in the registry but not in the artifact that the rubric grades.

No locked verdict is `escalate`, so this does not block the lock. It remains live for the runs: an agent that reasons its way to escalation on any of these six claims produces a ruling that fails criterion 2 mechanically, fails grading, and yields no data point. Given that R2 describes this type's claims as close calls by construction, that is a realistic outcome rather than a theoretical one.

Resolving it means widening criterion 2 and the d6 format to four values. **Decided, not yet shipped:** decision d(w19)-4 (Week 19 chat log) widens criterion 2 and the d6 format to four values, adding `escalate`. That is a rubric change during a retest and is recorded here as a decision with its reasoning, per the paragraph above — implementation (the actual criterion-2 and d6-format widening) has not yet landed in the rubric or artifact format.

---

## Open items this lock depends on but does not settle

- **Pointer-scoping: CLOSED.** Now [R6](#rule-sources). The rule is committed in `docs/ADR-016-decision-4-addendum-compatibility.md`, "Scoping by reference," and quoted in full there. See the 2026-08-31 amendment below.
- **Uncommitted draft: CLOSED.** R2, R3, and R4 now cite committed sources (commit `7961733`, plus the ADR-016 Decision 4 addendum). All six verdicts were re-derived against the committed wording; none moved. See the amendment below.
- **The lifecycle threshold is not exercised, and this now stands confirmed against live data.** Every platform version named across the six claims is inside a standard-subscription support phase, so R2's threshold never fires. It is locked and stated but untested by this set. Confirmed against the live registry (`get_claim_status` on all six rows, 2026-08-31): every one of the six seeded claims returns `platform_lifecycle_status: current`. The threshold remains unexercised by construction of this claim set, not by omission.

---

## Amendment — 2026-08-31

**What changed in the sources since the 2026-08-30 lock.** At lock time, R2, R3, and R4 cited `compatibility-claim-type-draft.md`, an uncommitted draft dated 2026-08-29, and pointer-scoping had no rule at all — the draft did not address it. Commit `7961733` (2026-08-31) landed the compatibility claim type into both skill trees: the `claim-taxonomy` skill's `references/evidence-standards-by-type.md` (deterministic fields and the four judgment questions) and the `claim-review` skill's `references/evidence-standards.md` (the claim-strength gradient worked example). `docs/ADR-016-decision-4-addendum-compatibility.md` (accepted 2026-08-30) committed the type definition, the certifying-party rule, the lifecycle threshold, and — in its "Scoping by reference" section — the pointer-scoping rule that did not exist in any committed form at lock time. The draft file `compatibility-claim-type-draft.md` no longer exists on disk; it was superseded by these committed sources rather than left in place alongside them.

**Re-derivation result.** All six locked verdicts (Pair A: C7, C8 `not_substantiated`; Pair B: C3, C4 `substantiated`; Pair C: C10, C11 `not_substantiated`) were re-derived against the committed R2–R4 wording and the newly-committed R6. **None moved.** The Pair A reasoning's treatment of the Dell.com/OSsupport pointer — proximate, resolving, but pointing to the claimant's own matrix rather than to Red Hat's certification record, and therefore weak mitigation that does not cure the version-scope gap — matches R6's committed rule exactly: a pointer to "a resource published by the claimant" is "weak mitigation," named but not curing.

**Scope of R6 across the three pairs.** Pairs B and C contain no scoping pointers, so R6 does not apply to them. Pair B's claims (C3, C4) name their RHEL versions directly in the claim text; there is no unversioned platform name for a pointer to rescue. Pair C's claims (C10, C11) name no version and no pointer — C10 and C11 both fail on component scope and certifying party (R4), axes R6 does not touch.

**C4 and Pair A's pointer axis.** C4's claim text (`docs/week19-claim-text-verbatim.md`) carries a trailing pointer sentence: *"For a complete list of supported, certified and tested operating systems, plus additional details and links to relevant web sites, see the Operating System Interoperability Guide: `https://lenovopress.lenovo.com/osig#servers=sr650-v3-7d75-7d76-7d77`."* This is a pointer to a resource published by the claimant (Lenovo), the same structural shape as C7 and C8's Dell.com/OSsupport pointer — which makes Pair B structurally parallel to Pair A on the pointer axis. It does not change C4's verdict: C4 names its RHEL versions directly and in full in the claim text itself, so the pointer is redundant to an already-closed version-scope question rather than mitigation for an open one. R6 has nothing to cure in C4; the claim does not rely on the pointer the way C7/C8 do.

---

## Registry rows

The six claims are seeded in the registry under `product_key = vendor_compat`, `claim_type = compatibility`. Mapping from candidate identifier (C1–C12, per `docs/week19-compatibility-claim-candidates-v2.md` Part 1) to registry row, confirmed against live `get_claim_status` reads, 2026-08-31:

| Candidate | `claim_slug`                     | `claim_id`                             |
| --------- | -------------------------------- | --------------------------------------- |
| C7        | `vendor_compat-compatibility-01` | `7b38f6ae-a8ac-4d97-bc5e-85234a351825` |
| C8        | `vendor_compat-compatibility-02` | `7f2057be-23cf-49a9-b43b-3466587ef390` |
| C3        | `vendor_compat-compatibility-03` | `68cd4c6a-6dbb-4505-89b2-7dd6a866b189` |
| C4        | `vendor_compat-compatibility-04` | `4bbede85-4cd6-4cf5-93bc-a14c3aee5068` |
| C10       | `vendor_compat-compatibility-05` | `53543a68-7c38-4a06-8171-d0956a09b10e` |
| C11       | `vendor_compat-compatibility-06` | `ff97218c-6b28-4a0a-b202-085a76bad1a7` |

`claim_text` for all six rows is sourced from `docs/week19-claim-text-verbatim.md`, not from the descriptions given in the Pair A/B/C sections above. Those descriptions stay as they are — they describe the claims for this document's reasoning, they are not the claim text a retest session is given.

---

## Limits observed at seeding

**C11 is the only one of the six carrying experimenter-written text inside its `claim_text`, and the only one whose evidence framing above rests on a comparator rather than a direct record.** Two pieces: a bracketed non-contiguity marker inside `claim_text` itself (`"[Non-contiguous on the source page. The following appears further down, in a separate \"Features\" subsection, after a call-to-action block and a duplicate re-render of the hero above.]"`), and the nearest-comparator framing in this document's own "Evidence record" line for C11 above (Red Hat catalog record #14, the SYS-221HE-TNRD, is the nearest comparator for a page that names no SKU — there is no record for CyberStore itself). No other claim among the six carries either.

**Hygiene checks and risk classification are identical across all six.** Every row's `risk_factors` reads "certification record, platform version, and current lifecycle status all present," and every row is `risk_class: medium`. The deterministic layer does not differentiate this set at all — it passes uniformly. All measured variance in the six verdicts therefore runs through the judgment layer, concentrated in rubric criteria 3 (verdict matches evidence standard) and 8, not through any deterministic hygiene signal.
