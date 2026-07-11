---
name: claim-taxonomy
description: Reference for the Claims Desk's four marketing claim types (Performance, Comparative, Compliance, Superlative) and their evidence standards. Use when classifying a claim by type, determining what evidence a claim type requires, or checking whether a claim falls within v1 scope.
license: Proprietary
metadata:
  author: richardthomchick
  version: "1.0"
  project: claims-desk
---

# Claim-Type Taxonomy

This is a **reference** skill: it describes what the four claim types are and what evidence each requires. It does not tell you how to conduct a review — for that, see the companion `claim-review` skill, which uses this taxonomy as its evidentiary standard.

## The four claim types

| Type | Definition | Example |
|---|---|---|
| **Performance** | A claim about the product's own measurable capability or outcome | "Reduces incident resolution time by 40%" |
| **Comparative** | A claim measured against a named or implied competitor or alternative | "Faster time-to-resolution than [Competitor]" |
| **Compliance** | A claim of certification, authorization, or regulatory/standards conformance | "SOC 2 Type II certified" |
| **Superlative** | A ranking, "best-in-class," or "#1" claim | "#1 rated on G2" |

Every claim in the registry must be classified as exactly one of these four types. If a claim seems to span two types (e.g., "40% faster than [Competitor], per independent testing" is both Performance and Comparative), classify it by its **primary assertion** — what a reasonable reader would take as the claim's main point — and note the secondary dimension in the claim record for context.

## Evidence standard, per type

Full field-level detail (deterministic vs. judgment split, exact hygiene checks) is in `references/evidence-standards-by-type.md`. Summary:

- **Performance**: methodology documented, sample size, time window, and baseline named. Substantiation bar scales with how strongly the claim is worded (see `claim-review`'s evidence-standards reference for this reasoning).
- **Comparative**: head-to-head test or third-party benchmark; comparison basis stated; competitor data current relative to the claim date.
- **Compliance**: current, valid certificate on file; expiry tracked. The type where deterministic checks carry nearly the whole verdict.
- **Superlative**: source, category, and date named. Shortest default currency window of the four types — ranking and "#1" claims require continuous re-substantiation for as long as the claim is made, not just substantiation at time of first publication.

## Out of scope for v1

Two claim shapes are deliberately **not** covered by this taxonomy and should not be forced into one of the four types above:

- **Aspirational / roadmap claims** ("coming soon," "planned for Q3," "in beta") — these are expectation-setting statements, not substantiation claims. They don't have an evidence standard because they aren't asserting a present fact. If a claim is roadmap language being reviewed under one of the four types above, flag the mismatch rather than force-fitting it.
- **Environmental / sustainability claims** — deliberately deferred. These fall under a different, largely consumer-facing (B2C) regulatory regime (the EU's Green Claims Directive, still in the EU legislative process as of mid-2026, not binding law) rather than the FTC "reasonable basis" doctrine this taxonomy is grounded in. Kalder's B2B posture places any of its claims under the misleading-advertising framework (EU Directive 2006/114/EC) rather than an environmental-claims-specific regime. If a claim asserts something like "carbon-neutral infrastructure," it does not have a defined evidence standard in this taxonomy yet — treat it as out of scope and flag it rather than approximating with the Performance or Compliance standard.

## Grounding

This taxonomy and its evidence standards are grounded in the FTC Policy Statement Regarding Advertising Substantiation (1984, still current doctrine) — the "reasonable basis" standard, and its claim-strength-relative variant for claims that expressly or impliedly assert a specific level of support. See ADR-016 (Decision 4) for the full architectural reasoning behind this taxonomy's scope and the deterministic/judgment field split.
