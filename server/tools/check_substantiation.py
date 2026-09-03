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
    "compatibility": (
        "Certification record link present, platform named, platform version "
        "named distinctly from the platform itself, certified component "
        "revision named, platform version has not passed the last lifecycle "
        "phase included in a standard support subscription (phases available "
        "only as a separately purchased add-on, such as Red Hat ELS or "
        "Microsoft ESU, count as expired for claim purposes)."
    ),
}

# Claim types for which sample_size is not an applicable field.
_SAMPLE_SIZE_NOT_APPLICABLE = {"compliance", "superlative", "compatibility"}

# Claim types for which expiry_date is not an applicable field.
_EXPIRY_NOT_APPLICABLE = {"performance", "comparative", "compatibility"}


def _major_version(platform_version: str | None) -> str | None:
    """Extract a bare major version ('9') from a certified version range
    ('9.0-9.x') for lookup against platform_lifecycle.major_version, which
    is keyed on major version only. No documented format contract exists
    for platform_version beyond the 'certified version range' example in
    the migration comment, so this takes the leading run of digits before
    the first non-digit character."""
    if not platform_version:
        return None
    digits = ""
    for ch in platform_version:
        if ch.isdigit():
            digits += ch
        else:
            break
    return digits or None


def _platform_lifecycle_status(platform: str | None, platform_version: str | None) -> str:
    if not platform or not platform_version:
        return "unknown"

    major_version = _major_version(platform_version)
    if major_version is None:
        return "unknown"

    row = fetchone_dict(
        """
        select standard_support_end
        from platform_lifecycle
        where platform = %s and major_version = %s
        """,
        (platform, major_version),
    )
    if row is None or row.get("standard_support_end") is None:
        return "unknown"

    return "expired" if row["standard_support_end"] < date.today() else "current"


def check_substantiation(claim_id: str) -> dict:
    claim = fetchone_dict(
        """
        select claim_id, product_key, claim_type, claim_text,
               risk_class, risk_factors
        from claims
        where claim_id = %s
        """,
        (claim_id,),
    )
    if claim is None:
        return {"error": f"no claim found with claim_id {claim_id}"}

    claim_type = claim["claim_type"]
    if claim_type not in EVIDENCE_STANDARDS:
        return {"error": f"unrecognized claim_type: {claim_type}"}

    evidence = fetchall_dict(
        """
        select evidence_id, evidence_url, evidence_date, sample_size, baseline, expiry_date,
               scope, platform, platform_version, component_revision
        from evidence_links
        where claim_id = %s
        order by created_at asc
        """,
        (claim_id,),
    )

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

    if claim_type == "compatibility":
        platform_lifecycle_status = _platform_lifecycle_status(
            primary_evidence.get("platform") if primary_evidence else None,
            primary_evidence.get("platform_version") if primary_evidence else None,
        )
    else:
        platform_lifecycle_status = None

    latest_ruling = fetchone_dict(
        """
        select verdict
        from review_rulings
        where claim_id = %s
        order by created_at desc
        limit 1
        """,
        (claim_id,),
    )
    claim["verification"] = latest_ruling["verdict"] if latest_ruling else "unreviewed"

    expiries = [row["expiry_date"] for row in evidence if row.get("expiry_date") is not None]
    if not expiries:
        claim["evidence_current"] = None
    else:
        claim["evidence_current"] = all(expiry >= date.today() for expiry in expiries)

    return {
        "claim": claim,
        "evidence": evidence,
        "evidence_standard": EVIDENCE_STANDARDS[claim_type],
        "hygiene_checks": {
            "has_evidence_link": has_evidence_link,
            "has_evidence_date": has_evidence_date,
            "is_expired": is_expired,
            "has_sample_size": has_sample_size,
            "platform_lifecycle_status": platform_lifecycle_status,
        },
    }
