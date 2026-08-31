# Evidence Standards — Reasoning and Worked Examples

This reference supports the `claim-review` skill's Step 4 (claim-strength check) and Step 5 (sufficiency judgment). It explains *why* the standards work the way they do; for the taxonomy itself (what counts as evidence per claim type), see the companion `claim-taxonomy` skill's `references/evidence-standards-by-type.md`.

## The claim-strength principle

FTC advertising substantiation doctrine (Policy Statement on Advertising Substantiation, 1984, still current doctrine) holds that when an advertisement expressly or impliedly asserts a specific level of substantiation ("tests prove," "studies show," "clinically proven"), the advertiser must possess at least that level of support. Absent an express or implied claim of a specific support level, the standard is a "reasonable basis" — what's reasonable depends on the claim, the product, the consequences of the claim being false, and the cost of obtaining better substantiation.

Practically: **read the claim's wording before you read its category.** Two claims of the same type can carry different evidentiary bars:

- "Reduces onboarding time" — soft claim, reasonable-basis standard, general directional evidence is likely sufficient
- "Reduces onboarding time by 40%, per independent testing" — hard claim, the specific number and the specific "independent testing" assertion both need to be true and substantiated at that level, not just directionally supported

This is not a mechanical rule to apply — it's a judgment about what a reasonable consumer or buyer would understand the claim to be promising, and whether the evidence on file actually promises that much.

## Worked example: Compliance is the exception

Compliance claims are the one type where the deterministic layer does almost all the work. "SOC 2 Type II certified" is either true (current, valid certificate on file) or it isn't — there's little room for a claim-strength gradient the way there is for Performance or Comparative claims. If `check_substantiation`'s hygiene check shows a valid, non-expired certificate, the sufficiency judgment is close to automatic. Don't manufacture judgment-layer complexity for a claim type that's designed to be checked, not interpreted. Where Compliance claims do need real judgment: whether the certificate's *scope* actually covers what the claim implies (e.g., a SOC 2 report covering one product line being used to support a claim about the whole platform) — that's a genuine reading-comprehension judgment call, not a lookup.

## Worked example: the Compatibility scope gradient

Compatibility claims cluster around three tiers of language that carry different implications even when pointing at the same underlying certification: "compatible with," "certified for," and "supported on." "Compatible with RHEL 9" is the weakest — it asserts interoperation without invoking a certification program at all, and a claim worded this loosely can sometimes be satisfied by evidence of testing alone. "Certified for RHEL 9" invokes the vendor's certification program specifically and needs the certification record itself, not just a test report. "Supported on RHEL 9" is the strongest — it implies an ongoing vendor support relationship, not just a point-in-time test result, and evidence that only shows a certification (a snapshot) without a support-tier record is a claim-strength mismatch even if the hygiene checks pass. Judging a Compatibility claim means reading which of the three the claim's own wording invokes, then checking that the evidence matches that specific tier rather than a weaker one dressed up in stronger language.

## Worked example: escalation in practice

A Superlative claim — "#1 rated on G2" — comes with a source link and a date, both present (hygiene checks pass). On inspection, the source is real, but the G2 category is narrow enough that "#1" is technically true only within a sub-segment the claim's wording doesn't disclose (e.g., "#1 in [Company Size] AIOps for companies under 200 employees" being advertised simply as "#1 rated AIOps platform"). This is a case for escalation, not a unilateral reject: the underlying fact is true, the presentation may be misleading, and whether that crosses a line is exactly the kind of close call a human reviewer should weigh in on rather than have silently auto-rejected or silently auto-approved.

## A note on false confidence

If you can't find or verify the specific fact that would resolve a judgment call, say so and escalate — do not fill the gap with a plausible-sounding assumption. A ruling built on an assumption you didn't verify is worse than an honest "I could not confirm X, escalating for human review."
