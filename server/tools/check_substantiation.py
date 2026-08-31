"""
check_substantiation — thin tool per ADR-016 Decision 1's edge-case resolution.

Returns the claim, its linked evidence, the evidence standard for its claim
type, and a set of deterministic, non-interpretive hygiene checks. Does NOT
render a verdict (approved/rejected/insufficient) — that judgment belongs to
the calling agent, guided by the taxonomy Skill, which remains the sole
source of truth for "what counts as sufficient."
"""

from __future__ import annotations

from datetime import date

from server.db.client import fetchone_dict, fetchall_dict

# Evidence standards per ADR-016 Decision 4. Reference text only — no
# judgment logic lives here; this is what the tool hands to the calling
# agent, not what the tool decides.
EVIDENCE_STANDARDS = {
    "performance": (
        "Methodology documented, sample size, time window, baseline named. "
        "Substantiation bar scales with claim phrasing strength (FTC: express "
        'claims of a support level, e.g. "tests show," require at least that '
        'advertised level of substantiation; softer phrasing assumes only a '
        '"reasonable basis").'
    ),
    "comparative": (
        "Head-to-head test or third-party benchmark; comparison basis stated; "
        "competitor data current relative to claim date."
    ),
    "compliance": (
        "Current certificate; expiry tracked. Deterministic checks (is the "
        "expiry date past?) can carry nearly the entire verdict for this "
        "claim type."
    ),
    "superlative": (
        "Source, category, date. Shortest default expiry window of the four "
        'types, grounded in FTC guidance that ranking/recommendation claims '
        '(e.g. "#1 selling") require continuous re-substantiation for the '
        "duration the claim is made, not just at time of first publication."
    ),
}

# Claim types for which sample_size is not an applicable field.
_SAMPLE_SIZE_NOT_APPLICABLE = {"compliance", "superlative"}

# Claim types for which expiry_date is not an applicable field.
_EXPIRY_NOT_APPLICABLE = {"performance", "comparative"}


def check_substantiation(claim_id: str) -> dict:
    claim = fetchone_dict(
        """
        select claim_id, product_key, claim_type, claim_text, status,
               risk_class, risk_factors
        from claims
        where claim_id = %s
        """,
        (claim_id,),
    )
    if claim is None:
        return {"error": f"no claim found with claim_id {claim_id}"}

    evidence = fetchall_dict(
        """
        select evidence_id, evidence_url, evidence_date, sample_size, baseline, expiry_date, scope
        from evidence_links
        where claim_id = %s
        order by created_at asc
        """,
        (claim_id,),
    )

    claim_type = claim["claim_type"]
    primary_evidence = evidence[0] if evidence else None

    has_evidence_link = bool(primary_evidence and primary_evidence.get("evidence_url"))
    has_evidence_date = bool(primary_evidence and primary_evidence.get("evidence_date"))

    if claim_type in _EXPIRY_NOT_APPLICABLE:
        is_expired = None
    else:
        expiry = primary_evidence.get("expiry_date") if primary_evidence else None
        is_expired = (expiry < date.today()) if expiry else None

    if claim_type in _SAMPLE_SIZE_NOT_APPLICABLE:
        has_sample_size = None
    else:
        has_sample_size = bool(
            primary_evidence and primary_evidence.get("sample_size") is not None
        )

    return {
        "claim": claim,
        "evidence": evidence,
        "evidence_standard": EVIDENCE_STANDARDS[claim_type],
        "hygiene_checks": {
            "has_evidence_link": has_evidence_link,
            "has_evidence_date": has_evidence_date,
            "is_expired": is_expired,
            "has_sample_size": has_sample_size,
        },
    }
