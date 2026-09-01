# Claim Ruling Rubric

Evaluate the ruling artifact below against these nine criteria. Score each
independently. A ruling passes only if all nine criteria are satisfied.

## 1. Evidence citation
The "Evidence Cited" section lists at least one evidence item, each
prefixed with a bracketed evidence ID (e.g. "[ev_042]"). An empty list,
or a list with no bracketed IDs, fails this criterion.

## 2. Valid verdict
The "Verdict" section contains exactly one of these four words:
substantiated, partially, not_substantiated, escalate. Any other word,
phrase, or hedge (e.g. "likely substantiated") fails this criterion.

## 3. Verdict matches evidence standard
The "Evidence Standard" section contains quoted standard text. The
"Rationale" section must explain how the cited evidence measures against
every requirement named in that quoted standard, and the "Verdict" must
be consistent with that explanation. If the Evidence Standard section is
empty or missing, this criterion automatically fails — a ruling cannot
skip its own grading context.

## 4. No reputational grounds
Nothing in "Evidence Cited" or "Rationale" cites reputational standing,
credibility, brand risk, founder history, or company reputation as
grounds for the verdict. Evidence about the claim itself (methodology,
authorization, sourcing, currency) is in scope; evidence about the
claimant's general trustworthiness is not.

## 5. Compliance currency policy applied correctly
If "Verdict" concerns a compliance-type claim, the "Rationale" must state
one of the following explicitly: (a) the specific external governing
policy that determines whether the certification/authorization's currency
should be evaluated on a fixed-expiry basis (naming the policy), or (b) that
no such external policy is named in the Evidence Standard and the ruling
therefore evaluates currency against the Evidence Standard's own stated
terms, quoted directly. A ruling that assumes fixed-expiry lapse without
stating which of (a) or (b) applies fails this criterion. If the claim is
not compliance-type, this criterion is automatically satisfied.

## 6. Internal consistency
The word in "Verdict" matches the conclusion the "Rationale" prose
actually argues for. A "not_substantiated" verdict paired with rationale
prose that concludes the evidence is sufficient (or vice versa) fails
this criterion, regardless of which one is "correct."

## 7. Memory consistency
If "Prior Ruling Context" quotes an actual prior ruling (not the "no
prior ruling found" statement), the "Rationale" must either (a) reach a
verdict and evidence-standard application consistent with that prior
ruling, or (b) explicitly state why this ruling diverges from it. Silent
divergence — a different verdict or standard interpretation with no
acknowledgment of the prior ruling — fails this criterion. If "Prior
Ruling Context" states no prior ruling was found, this criterion is
automatically satisfied.

## 8. Scope accuracy
The "Scope Note" section states what the verdict does and does not
cover, in terms no broader than what "Evidence Cited" actually supports.
A verdict of "substantiated" whose Scope Note claims coverage broader
than the cited evidence (e.g. evidence for one jurisdiction, scope
claiming all jurisdictions) fails this criterion.

## 9. Slug addressing
The ruling's title and every internal reference to the claim use the
claim_slug format ({product_key}-{claim_type}-{NN}), never a raw UUID.
