"""get_claim_status — read a claim's substantiation state, evidence, and latest ruling."""

from __future__ import annotations

from datetime import date

from server.db.client import fetchone_dict, fetchall_dict


def get_claim_status(claim_id: str) -> dict:
    claim = fetchone_dict(
        """
        select claim_id, product_key, claim_type, claim_text,
               record_status, claim_slug, risk_class, risk_factors,
               created_at, updated_at
        from claims
        where claim_id = %s
        """,
        (claim_id,),
    )
    if claim is None:
        return {"error": f"no claim found with claim_id {claim_id}"}

    evidence = fetchall_dict(
        """
        select evidence_id, evidence_url, evidence_date, sample_size, baseline, expiry_date
        from evidence_links
        where claim_id = %s
        order by created_at asc
        """,
        (claim_id,),
    )

    latest_ruling = fetchone_dict(
        """
        select ruling_id, verdict, rationale, reviewed_by, created_at
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
        "latest_ruling": latest_ruling,
    }
