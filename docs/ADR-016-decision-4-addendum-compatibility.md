# Decision 4 Addendum — Compatibility as a Fifth Claim Type

**Date:** 2026-08-30
**Status:** Accepted
**Amends:** Decision 4 (Claim taxonomy and the deterministic/judgment field split)
**Precedent:** follows the Decision 1 addendum pattern established when `delete_claim` was added in Week 17. The original decision text is left intact; this addendum records what changed and why.

---

## Context

Decision 4 established four claim types (Performance, Comparative, Compliance, Superlative) and, more importantly, established a design principle: each type carries its own split between a deterministic layer checked by `check_substantiation` and a judgment layer exercised by the `claim-review` skill. The split is per-type, and the type's identity is largely a statement about where that line falls.

Decision 4 also recorded two claim shapes as explicitly deferred: aspirational/roadmap claims, and environmental/sustainability claims (the latter with a specific rationale tied to the EU EmpCo Directive, binding 2026-09-27). Compatibility appears nowhere in the original decision, as in-scope or as deferred. Introducing it is a genuine taxonomy change rather than filling a gap the ADR already anticipated.

The immediate occasion is Week 19's Memory retest, which needs claims whose correctness turns on scope judgment and which can be checked against a real, fetchable certification authority. Red Hat's hardware catalog is the only source that survived fetchability testing across several sessions. But the type is not being added for the retest. Vendor compatibility claims are a routine shape in enterprise infrastructure marketing, and the registry would have encountered them regardless.

---

## Decision

Add a fifth claim type, `compatibility`: a claim that a product is certified, validated, or supported for operation with a named platform at a named version.

Its deterministic layer checks that a certification record link is present, that the platform is named, that the platform version is named distinctly from the platform itself, that the certified component revision is named, and that the platform version has not passed the lifecycle threshold defined below. Its judgment layer is the scope question in four forms: version scope, component scope, configuration scope, and support-tier implication.

---

## Why not Compliance

Both types assert a certification held by a third party, so the boundary needs stating explicitly or classification drifts.

**The certifying party differs in kind.** Compliance asserts conformance to a standard or regulatory regime, certified by a body whose role is to be independent of the claimant. Compatibility asserts interoperation with a platform, certified by the platform vendor, which runs the certification program as part of its own ecosystem strategy. That changes what the certification is evidence *of*. A compliance certificate attests that an independent body examined the claimant against a published standard. A compatibility certification attests that a vendor tested a specific configuration against its own platform. The second is narrower by construction.

**The split inverts.** Decision 4 establishes that no claim type is entirely one or the other and that the split runs within each type. It also records Compliance as the extreme case: the type where deterministic checks can carry nearly the entire verdict and judgment's role shrinks to near zero, unlike the other three. Compatibility sits at the opposite extreme. Scope is not what is left over after the deterministic checks run, it is the claim, and it decomposes into four separate judgment questions. Housing both in one type would give that type two incompatible splits, which makes the split incoherent as a design principle rather than merely inconvenient.

**The hygiene checks differ substantively.** Compliance compares a certificate expiry date to today, using data already in the registry. Compatibility compares a platform version against a vendor lifecycle calendar, which is exogenous data requiring its own source and refresh policy, and it requires a component-revision field no other type needs.

**Currency is exogenous.** This is the property most worth recording, because it has governance consequences beyond classification. Every other claim type goes stale because something about the claim or its evidence changed: the certificate expired, the ranking shifted, the competitor's pricing moved. A compatibility claim goes stale because the *platform* reached end of life, while the certificate remains valid and the product unchanged. Nothing the claimant does or fails to do causes it. Compatibility claims therefore need scheduled re-review against a platform lifecycle calendar rather than against a certificate expiry calendar.

---

## The lifecycle threshold

Compliance's currency check is a date comparison and is fully deterministic. Compatibility's analog is platform end-of-support, which is not binary: Red Hat runs Full Support, Maintenance Support, and Extended Life Cycle Support as separate paid phases, and Microsoft runs mainstream and extended. "Past end of support" has at least three defensible readings, and leaving it unspecified would push a check that belongs in the deterministic layer into the judgment layer.

That is precisely the failure Week 18's h2 refutation exposed, so the threshold is fixed in advance:

**The check fires when the named platform version has passed the last lifecycle phase included in a standard subscription.** Phases available only as a separately purchased add-on (Red Hat ELS, Microsoft ESU) count as expired for claim purposes.

Rationale: a claim that a product is supported on a platform, where support requires the reader to buy a separate extended-support contract, materially overstates what the reader gets. Treating the paid add-on window as still-supported would let a claim stand years past the point where a reasonable buyer would consider the platform supported.

This is a decision, not a derivation. It should be revisited if a real claim surfaces where the ELS window is the honest reading.

---

## Scoping by reference

A claim may name no version while pointing to a separate resource that does. Vendor spec sheets do this routinely: an unversioned platform name in the operating-system list, with a direction to an interoperability matrix elsewhere.

A pointer never satisfies a deterministic check, because those run against the evidence record rather than the claim text. It functions as mitigation within version scope, weighted by the authority of what it resolves to:

- Resolves to the **certifying party's own record**: strong mitigation, potentially sufficient to close a version-scope gap. The claim defers to the same authority it invokes.
- Resolves to a **resource published by the claimant**: weak mitigation. The reviewer should name it, and it supports a lower risk classification, but it does not cure the gap. A claimant pointing at its own document asserts its own support, not the third-party certification the claim invokes.
- **Absent, or unresolving**: no mitigation.

Weight the pointer's proximity to the claim and whether the resource states scope in terms the claim can inherit. A pointer to a continuously updated resource names a place where versions are listed rather than a version, which is a further reason it mitigates rather than cures.

This rule is recorded here rather than on the claim-strength gradient, where an earlier pre-commitment placed it. The gradient governs how strongly a claim is worded. A pointer is not a wording strength; it is a question about whether a claim that names no version can be treated as having named one by reference, which lives inside version scope.

---

## Rejected alternatives

**Extend Compliance with optional platform and version fields.** Rejected. Optional fields that are mandatory for one subset of a type and meaningless for another are a type boundary expressed as nullable columns. The hygiene layer would have to branch on the presence of those fields to decide which checks apply, which is a type discriminator wearing a different name. It would also leave Compliance with two splits, which is the incoherence described above, reached by a longer route.

**Classify compatibility claims as Performance.** Rejected. Performance claims assert measurable capability substantiated by methodology, sample size, and baseline. A compatibility claim asserts third-party certification status, substantiated by a record lookup and a scope reading. None of the Performance hygiene fields apply, and `_SAMPLE_SIZE_NOT_APPLICABLE` would need compatibility added to it under any housing.

**Leave out of scope, following the environmental-claims precedent.** Rejected. Environmental claims were deferred because they fall under a separate regulatory regime the taxonomy is not grounded in. Compatibility claims fall squarely inside the misleading-advertising framework the taxonomy already uses, and unlike environmental claims they are a shape the registry will encounter routinely.

**Add a criterion 10 to the review rubric enforcing the lifecycle threshold directly.** Rejected for now, and worth recording as a live gap rather than a settled question. Criterion 5 exists because compliance claims carry a currency policy that must be applied rather than assumed; compatibility has the same structure but no corresponding criterion, so the threshold reaches the grader only indirectly through criterion 3 (verdict matches evidence standard). Adding a criterion during the Week 19 retest would change the instrument mid-experiment for a worse trade than the gap costs. Revisit after the retest.

---

## Consequences

**Tradeoff.** A fifth type widens the `claim_type` CHECK constraint, adds a column to `evidence_links`, requires branching in `check_substantiation` and `classify_claim_risk`, and requires a platform lifecycle data source that no other type needs. The sizing investigation (`docs/week19-compatibility-type-sizing.md`) put the core change at roughly 140 to 215 lines with no migration required on existing claims.

**Why safe.** No existing claim changes type. Existing seed claims are unaffected, and widening a CHECK constraint does not touch existing rows. The constraint widening is ordered last, after `check_substantiation` and `classify_claim_risk` handle the new type, because both contain unguarded dictionary lookups that raise `KeyError` on an unrecognized type. Widening first would make those reachable at review time rather than at insert time.

**Risk classification.** Compatibility warrants a floor at medium rather than low, because the consequence of falsity is operational rather than reputational: a buyer acting on a false compatibility claim runs an unsupported production system and discovers it during an incident. Elevate when the named platform version is within a defined window of its lifecycle threshold, since the claim is about to become false without anyone touching it, and elevate when support-tier language ("supported on") is used rather than certification language.

**Skill trees are duplicated.** The `claim-taxonomy` and `claim-review` skills exist as byte-identical copies in two directories. Every edit lands twice, and a fifth type makes the drift risk worse. Consolidating them is out of scope here but is flagged as standing debt.

---

## Knock-on edits elsewhere in this ADR

Recorded here rather than made silently, so the addendum accounts for everything it disturbs.

**Summary of Decisions, row 4.** Currently reads "4 types (Performance, Comparative, Compliance, Superlative)." Update to five, with a pointer to this addendum. The rationale column's closing clause about Aspirational and Environmental being explicitly deferred still stands unchanged.

**Out of Scope, real client claims.** The bullet states the registry is seeded exclusively with Kalder fictional-product claims plus clearly public real-world claims used as Week 17 test inputs. Week 19 adds six real vendor claims from Dell, Lenovo, and Broadberry as retest subjects. They are public marketing claims, so the substance of the exclusion holds, but the "used as Week 17 test inputs" qualifier is now too narrow and should widen to cover public real-world claims used as experiment subjects generally.

**Out of Scope, aspirational claims.** The bullet names Week 17's adversary or later Kalder corpus work as the triggers that would reopen the aspirational bucket. Week 19 supplies evidence in the other direction: two search passes across five vendor and reseller sources found no verified forward-looking compatibility claim. That is not a reason to close the question, but it belongs alongside the exclusion as the first empirical test of it.

**Decision 5 no longer describes the plan.** Decision 5's hybrid conclusion is scoped as "`claims-desk` monorepo (Weeks 16–18 + Week 19 Build A) plus a standalone harness repo (Week 19 Build B, created when that build starts)." Week 19's scope changed after Week 18's outcome: the Kalder manifest page and the false-premise eval harness moved outside the arc and their disposition is undecided. So `false-premise-eval` is not being created this week and Build A/Build B no longer name anything real.

This addendum does not resolve that. It is flagged because Decision 5 currently reads as a commitment to work that is not happening on the timeline it states, and because something downstream still assumes the manifest exists: the Broadcom backlog page and the demonstration-bucket claims (AMD SeaMicro 2012, Cisco 2009 UCS) were both scoped as manifest material. A Decision 5 addendum is warranted once that disposition is decided, and it should not be folded into this one, which is about the taxonomy.

---

## Out of scope for the type

**Roadmap compatibility** ("RHEL 10 support coming in Q3") remains excluded under the taxonomy's existing aspirational-claims exclusion. No new carve-out is needed; the reviewer flags the mismatch rather than force-fitting the claim.

Worth recording as an empirical note: two full search passes across Dell, Lenovo, Supermicro, Broadcom, and reseller sources produced no verified forward-looking compatibility claim. The exclusion is correct in principle and had no instance in the wild in this domain, which is itself a finding about how vendors write these claims.

**Self-attested compatibility**, where the platform vendor operates no certification program, is in scope. The judgment layer should weigh the absence of an independent certifying party rather than treating vendor self-attestation as equivalent to a certification record.

---

## Open

- **Lifecycle data source and refresh mechanism.** The sizing investigation recommends a periodically refreshed cache over a synchronous external call, on the grounds that no other deterministic check in the system depends on a network call at review time. For Week 19 a cache populated once and stamped with a retrieval date is sufficient; the refresh design is deferred and staleness is a stated limit, not a solved problem.
- **Evidence-agent routing for the Week 17 adversary.** The adversary hand-authors attack-round definitions per type and has none for compatibility. Not needed for the Week 19 retest, which runs the review agent rather than the adversary. Deferred until the adversary next runs.
- **Criterion 10.** See rejected alternatives. Revisit after the retest.
