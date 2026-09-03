"""list_claims — enumerate claims by type/status/product (Week 18 d3).

Returns slug-first summaries only; full evidence and ruling payload remains
get_claim_status's job once the caller has a slug or claim_id in hand.

UNRESOLVED: the `status` input filter parameter and the `record_status`
output field now use different names for the same underlying concept
(f11 fix removed a rename that had made them match). Left asymmetric in
this commit deliberately; flagged for a separate decision rather than
resolved here.
"""

from __future__ import annotations

from server.db.client import fetchall_dict


def list_claims(
    claim_type: str | None = None,
    status: str | None = None,
    product_key: str | None = None,
) -> list[dict]:
    status = status or "active"

    where = []
    params: list[str] = []

    if status == "all":
        table = "claims"
    elif status == "active":
        table = "active_claims"
    else:
        table = "claims"
        where.append("record_status = %s")
        params.append(status)

    if claim_type is not None:
        where.append("claim_type = %s")
        params.append(claim_type)
    if product_key is not None:
        where.append("product_key = %s")
        params.append(product_key)

    query = f"""
        select claim_slug, claim_id, product_key, claim_type, record_status, risk_class
        from {table}
        {"where " + " and ".join(where) if where else ""}
        order by product_key, claim_type, claim_slug
    """

    rows = fetchall_dict(query, tuple(params))
    return rows
