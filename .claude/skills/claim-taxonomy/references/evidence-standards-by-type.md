# Evidence Standards by Type — Field-Level Detail

This reference is the field-level companion to the `claim-taxonomy` skill's summary table. Each claim type's evidence standard is split into **deterministic fields** (checked automatically by `check_substantiation`'s hygiene layer — a computer should verify these, not an agent) and **judgment criteria** (require reasoning — see the `claim-review` skill for how to apply them).

## Performance

**Deterministic** (hygiene-checked): evidence link present, evidence date populated, baseline field populated, sample size populated.

**Judgment**: Is the sample size adequate for the claim being made? Is the baseline fairly chosen, or does it compare against an artificially weak starting point? Is the methodology sound (e.g., a controlled before/after measurement vs. an anecdotal estimate)? Does the claim's wording match the strength of what was actually measured?

## Comparative

**Deterministic**: evidence link present, named competitor/baseline field populated, comparison date present.

**Judgment**: Is the comparison basis fair — same product tier, same configuration, same use case on both sides? Is the competitor's data current relative to when this claim is being made (a comparison against a competitor's year-old pricing or feature set may no longer be accurate)? Is the comparison measuring the same thing on both sides, or is it apples-to-oranges dressed as a direct comparison?

## Compliance

**Deterministic**: certificate link present, expiry date present, **expiry date not in the past**. This last check is fully deterministic — no judgment is needed to determine whether a date has passed.

**Judgment**: Does the certificate's actual scope cover what the claim implies? A certification that covers one product or business unit being used to support a claim about the whole company is a scope mismatch, not a hygiene failure — the certificate is real and current, but the claim overstates what it covers.

This is the claim type where the deterministic layer carries nearly the entire verdict. Most Compliance claims that pass all hygiene checks should be approved without extensive additional judgment; reserve real scrutiny for the scope question above.

## Superlative

**Deterministic**: source link present, source date present, category field populated.

**Judgment**: Is the source credible (a recognized third-party ranking/review platform vs. an unverifiable or self-published claim)? Is the category specific enough that the claim isn't misleading (e.g., "#1 in mid-market B2B SaaS for companies under 200 employees" being presented simply as "#1 rated")? Is the ranking still current, given how quickly rankings on most platforms change — this is the type with the shortest default currency window of the five, per FTC guidance that "#1" and ranking claims require continuous re-substantiation for as long as the claim is made.

## Compatibility

**Deterministic**: certification record link present, platform named, platform version named distinctly from the platform itself, certified component revision named, platform version has not passed the last lifecycle phase included in a standard support subscription (phases available only as a separately purchased add-on, such as Red Hat ELS or Microsoft ESU, count as expired for claim purposes).

**Judgment**: the scope question, asked four ways. Version scope — does the certification cover the specific platform version the claim names, including where a claim points to a separate resource rather than naming a version directly (a pointer to the certifying party's own record is strong mitigation; a pointer to a claimant-published resource is weak mitigation; no pointer is no mitigation). Component scope — does the certification cover the specific product component or revision the claim is made about. Configuration scope — does the certification cover the tested configuration, or does the claim generalize beyond it. Support-tier implication — does the claim's language ("certified for" vs. "supported on") match what the certification actually establishes, since "supported on" implies an ongoing vendor support relationship that certification alone does not.

Compatibility's currency check is exogenous: unlike every other type, a Compatibility claim can go stale because the named platform reached end of life, with nothing about the claim, the evidence, or the claimant having changed.

## Why the deterministic/judgment split exists

Deterministic checks are things a computer can verify with certainty and no interpretation — a date comparison, a null check, a populated-field check. Putting these in code (via `check_substantiation`'s hygiene layer) rather than leaving them to agent judgment means they're consistent every time, fast to check, and not subject to an agent's variability across calls.

Judgment criteria require reading comprehension, contextual reasoning, or a sense of what a reasonable person would understand a claim to mean — these cannot be reduced to a boolean check without losing exactly the nuance that makes the judgment meaningful. These stay with the reviewing agent, guided by this reference and the `claim-review` skill's workflow.

No claim type is entirely one or the other. Compliance leans heavily deterministic; Performance and Comparative lean more toward judgment; Superlative sits in between, with the underlying facts (source, date, category) deterministic but the interpretation (credibility, specificity, staleness) requiring judgment. Compatibility leans furthest toward judgment, and differs from Performance and Comparative in shape as well as degree: their judgment spreads across several independent questions, while Compatibility's concentrates in one question asked four ways.
