---
name: claim-review
description: Conduct a marketing claim review for the Claims Desk — determine what counts as sufficient evidence, when a claim has expired, and when to escalate rather than rule directly. Use when reviewing, approving, rejecting, or triaging a marketing claim, or when asked to judge whether a claim is adequately substantiated.
license: Proprietary
metadata:
  author: richardthomchick
  version: "1.0"
  project: claims-desk
---

# Claim Review

This skill teaches how to conduct a claim review for the Claims Desk. It is a **reasoning** skill: it tells you how to judge a claim, not how to store or retrieve one. For the mechanics of reading and writing claims, use the Claims Desk MCP tools (`append_claim`, `get_claim_status`, `check_substantiation`, `classify_claim_risk`) — this skill tells you what to do with what those tools return.

## When this skill applies

Use this skill whenever you are asked to review a marketing claim: deciding whether it's adequately substantiated, whether it should be approved, rejected, or escalated, or whether it's safe to publish. This includes requests phrased as "is this claim OK to use," "review this claim," "can we say X," or any evaluation of a specific claim already in the registry.

This skill does not cover: adding a new claim to the registry (use `append_claim` directly), or determining a claim's risk classification as a standalone fact (use `classify_claim_risk` directly — that tool already applies deterministic rulesets and returns its own factors; this skill is about judgment, not repeating what that tool already computes).

## The review workflow

1. **Retrieve the claim.** Call `get_claim_status` to see the claim's current state, type, and any prior ruling. If a ruling already exists, treat it as context, not as binding — evidence and expiry status can change.

2. **Pull the substantiation material.** Call `check_substantiation`. This returns the claim, its linked evidence, the evidence standard for its claim type, and a set of deterministic hygiene checks (evidence link present, expiry status, sample size present, etc.). **This tool does not render a verdict — that judgment is yours.** Do not treat the absence of a verdict field as an oversight; it's deliberate. See `references/evidence-standards.md` for what "sufficient" means per claim type.

3. **Check the deterministic layer first.** The hygiene checks from `check_substantiation` are facts, not opinions — if `is_expired: true`, the claim fails regardless of anything else about it. If `has_evidence_link: false`, there is nothing to evaluate yet. Handle these before spending judgment on anything softer. A claim can fail on hygiene alone; don't reach for nuanced reasoning about evidence quality if the evidence doesn't exist at all.

4. **Apply the claim-strength check.** Read the claim's exact wording, not just its category. A claim phrased with an explicit support level ("tests show," "proven to," "studies confirm") carries a higher evidentiary bar than the same underlying fact phrased more softly ("up to X%," "typical results may vary"). This is judgment, not a lookup — weigh the claim's own language against what the evidence actually supports. See `references/evidence-standards.md` for the reasoning behind this and worked examples per claim type.

5. **Judge sufficiency against the claim type's evidence standard.** Each of the four claim types (Performance, Comparative, Compliance, Superlative) has a distinct standard — see `references/claim-type-taxonomy.md`, maintained by the companion reference skill. Don't apply one type's standard to another; a Superlative claim's evidence bar is not the same shape as a Performance claim's.

6. **Decide: approve, reject, or escalate.** Approve only when the deterministic checks pass and the judgment layer supports the claim as worded. Reject when either layer clearly fails. **Escalate rather than rule when the call is genuinely close** — see "When to escalate" below. Do not force a binary decision on a claim that's legitimately ambiguous; a wrong confident ruling is worse than an honest escalation.

7. **Record the ruling.** State your ruling, the specific reasoning (which hygiene checks passed/failed, what the claim-strength check found, why the evidence standard was or wasn't met), and if escalating, exactly what a human reviewer needs to resolve. Do not just state a verdict — the reasoning is what makes the ruling auditable and correctable.

## When to escalate rather than rule

Escalate when:
- The evidence technically meets the deterministic bar but the claim-strength check finds a mismatch between how confidently the claim is worded and what the evidence actually shows (e.g., "proven" language backed by a single small sample)
- A claim's risk classification (`classify_claim_risk`) returns `prohibited` or `high` but the evidence, on inspection, looks stronger than the deterministic factors suggest — this is a signal the rulesets may be missing context a human should weigh in on, not a signal to override the classifier yourself
- The claim type's evidence standard is genuinely ambiguous as applied to this specific claim (for example, a Comparative claim against a competitor whose product has since changed significantly)
- You find yourself constructing a justification for a ruling rather than reading one off the evidence — that's usually a sign the call is closer than it feels

Do not escalate reflexively for every claim with any imperfection — most claims with complete evidence and appropriately-hedged language should be ruled on directly. Escalation exists for genuine judgment calls, not as a way to avoid making any decision.

## What this skill does not do

This skill does not provide legal advice. A claim being adequately substantiated under FTC "reasonable basis" doctrine is a factual and evidentiary judgment, not a determination of legal risk or liability — those are different questions, and a legal review may still be warranted even for a claim this skill would approve.
