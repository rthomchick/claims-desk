"""delete_claim — soft-delete a claim in the registry.

Flips claims.record_status to 'deleted' rather than removing the row.
review_rulings.claim_id has no ON DELETE CASCADE (Week 18 d1), so rulings
attached to a claim survive a soft delete, preserving the audit trail.
evidence_links keeps its hard-delete cascade unchanged (Week 17 ADR-016
addendum) — it is unaffected by this tool since the claims row itself is
never removed.
"""

from __future__ import annotations

from server.db.client import get_connection


def delete_claim(claim_id: str) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE claims SET record_status = 'deleted' WHERE claim_id = %s",
                (claim_id,),
            )
            updated_count = cur.rowcount
        conn.commit()
    finally:
        conn.close()

    if updated_count == 0:
        return {"error": f"no claim found with claim_id {claim_id}"}

    return {"deleted": True, "claim_id": claim_id}
