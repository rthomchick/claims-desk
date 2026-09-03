"""
Week 20 migration, item 1 — append-only review_rulings with verdict
vocabulary. Applies against the live Supabase project via the pooler
connection (SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week20_item1

Renames review_rulings.ruling to verdict and replaces
review_rulings_ruling_check (approved/rejected/escalated) with a CHECK
on verdict matching the d6 artifact's four-value vocabulary
(substantiated/partially/not_substantiated/escalate) — see b5afefd,
which widened that vocabulary everywhere except this table. Adds
convergence (attack_exhaustion/round_cap), rounds, and
written_by_session (nullable, matching claims and evidence_links).
Adds an index on (claim_id, created_at desc) for the latest-ruling
lookup get_claim_status already performs.

Scope: schema only. Does not touch claims.status deprecation, tool
response shapes, or any consumer beyond the column rename required in
get_claim_status's own query — that is Day 2 work.

The FK (claim_id references claims(claim_id), no ON DELETE) is left
exactly as it is. The absence of ON DELETE is deliberate (Week 18 d1)
and load-bearing for append-only: rulings survive a soft-deleted claim.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_RENAME_COLUMN = """
alter table review_rulings rename column ruling to verdict;
"""

DDL_DROP_OLD_CHECK = """
alter table review_rulings drop constraint review_rulings_ruling_check;
"""

DDL_ADD_VERDICT_CHECK = """
alter table review_rulings
    add constraint review_rulings_verdict_check
    check (verdict in ('substantiated', 'partially', 'not_substantiated', 'escalate'));
"""

DDL_ADD_COLUMNS = """
alter table review_rulings
    add column convergence text check (convergence in ('attack_exhaustion', 'round_cap')),
    add column rounds integer,
    add column written_by_session text;
"""

DDL_ADD_INDEX = """
create index review_rulings_claim_id_created_at_idx
    on review_rulings (claim_id, created_at desc);
"""

DDL_COMMENT = """
comment on table review_rulings is
    'Append-only: inserts only, no updates. A correction is a superseding row (later created_at for the same claim_id), never an update to an existing one. The claim_id FK deliberately has no ON DELETE (Week 18 d1) so rulings survive a soft-deleted claim; append-only depends on that.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Renaming ruling -> verdict...")
            cur.execute(DDL_RENAME_COLUMN)

            print("Dropping review_rulings_ruling_check...")
            cur.execute(DDL_DROP_OLD_CHECK)

            print("Adding review_rulings_verdict_check...")
            cur.execute(DDL_ADD_VERDICT_CHECK)

            print("Adding convergence, rounds, written_by_session...")
            cur.execute(DDL_ADD_COLUMNS)

            print("Creating index on (claim_id, created_at desc)...")
            cur.execute(DDL_ADD_INDEX)

            print("Applying table comment...")
            cur.execute(DDL_COMMENT)

        conn.commit()
        print("\nMigration committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
