"""append_claim — write a new claim (and optional evidence) to the registry."""

from __future__ import annotations

from server.db.client import get_connection


def append_claim(
    product_key: str,
    claim_type: str,
    claim_text: str,
    evidence_url: str | None = None,
    evidence_date: str | None = None,
    sample_size: int | None = None,
    baseline: str | None = None,
    expiry_date: str | None = None,
) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into claims (product_key, claim_type, claim_text)
                values (%s, %s, %s)
                returning claim_id
                """,
                (product_key, claim_type, claim_text),
            )
            claim_id = cur.fetchone()[0]

            has_evidence = any(
                v is not None
                for v in (evidence_url, evidence_date, sample_size, baseline, expiry_date)
            )
            if has_evidence:
                cur.execute(
                    """
                    insert into evidence_links
                        (claim_id, evidence_url, evidence_date, sample_size, baseline, expiry_date)
                    values (%s, %s, %s, %s, %s, %s)
                    """,
                    (claim_id, evidence_url, evidence_date, sample_size, baseline, expiry_date),
                )
        conn.commit()
    finally:
        conn.close()

    return {"claim_id": str(claim_id)}
