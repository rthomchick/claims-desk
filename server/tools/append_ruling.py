"""append_ruling — write a review ruling to the append-only registry.

Insert only, per review_rulings' append-only contract (Week 20 d1): no
updates, no upserts, no delete-then-insert. A correction is a superseding
row with a later created_at for the same claim_id — get_claim_status
already reads by created_at desc limit 1, so the newest row wins.

Gate enforcement (verdict enum, convergence known) is the caller's
responsibility — see week17/adversary.js. This tool trusts its arguments;
the DB's review_rulings_verdict_check and convergence CHECK constraints
are the last line of defense, not the gate.

Convention (Week 20 d2): production writes come only from gated instrument
runs; tests use rollback isolation (server/tests/conftest.py); a provenance
column distinguishing the two is deliberately deferred to an ADR — until it
exists, nothing in a row identifies its writer, which is why eight fixture
rulings were indistinguishable from real verdicts on inspection.
"""

from __future__ import annotations

from server.db.client import get_connection


def append_ruling(
    claim_id: str,
    verdict: str,
    rationale: str | None = None,
    reviewed_by: str | None = None,
    convergence: str | None = None,
    rounds: int | None = None,
    written_by_session: str | None = None,
) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into review_rulings
                    (claim_id, verdict, rationale, reviewed_by, convergence, rounds, written_by_session)
                values (%s, %s, %s, %s, %s, %s, %s)
                returning ruling_id
                """,
                (claim_id, verdict, rationale, reviewed_by, convergence, rounds, written_by_session),
            )
            ruling_id = cur.fetchone()[0]
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM review_rulings WHERE ruling_id = %s", (ruling_id,))
            if cur.fetchone() is None:
                raise RuntimeError(
                    f"append_ruling: INSERT reported ruling_id {ruling_id} but row not found after commit"
                )
    finally:
        conn.close()

    return {"ruling_id": str(ruling_id), "claim_id": claim_id}
