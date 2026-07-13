"""delete_claim — delete a claim and its linked evidence from the registry.

Deletes the claim row in a single transaction; evidence_links rows cascade
automatically via the FK constraint (evidence_links_claim_id_fkey, ON DELETE CASCADE).

Note: review_rulings also has ON DELETE CASCADE per the existing schema
(review_rulings_claim_id_fkey). This means rulings ARE deleted alongside the claim,
contrary to ADR-016 Decision 1 Addendum intent. Flagged for Week 18: evaluate
making review_rulings.claim_id nullable + SET NULL to preserve the audit trail.
"""

from __future__ import annotations

from server.db.client import get_connection


def delete_claim(claim_id: str) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM claims WHERE claim_id = %s",
                (claim_id,),
            )
            deleted_count = cur.rowcount
        conn.commit()
    finally:
        conn.close()

    if deleted_count == 0:
        return {"error": f"no claim found with claim_id {claim_id}"}

    return {"deleted": True, "claim_id": claim_id}
