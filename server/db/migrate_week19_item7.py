"""
Week 19 migration, item 7b of 7 — attribution columns.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19_item7

Adds written_by_session to both claims and evidence_links. Nullable
because all 32 existing claims and 20 evidence rows predate it and are
not backfilled.

Closes the attribution half of Week 18's f16: f16 was logged as "no way
to determine, after a run completes, what an agent session actually
did," and was reclassified from friction to existential on Day 7 after
f18 became permanently unreconstructable because of it. d16 fixed three
of its four gaps via per-run logging; this is the fourth — claim
records carried no attribution field, so a registry row could not be
traced to the session that wrote it.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_ADD_ATTRIBUTION_COLUMNS = """
alter table claims
    add column written_by_session text;

alter table evidence_links
    add column written_by_session text;
"""

DDL_COMMENTS = """
comment on column claims.written_by_session is
    'Managed Agents session.id of the session that wrote this row, when written by an agent session. Null for rows written by hand, by seed scripts, or before this column existed. Closes the attribution half of Week 18''s f16.';
comment on column evidence_links.written_by_session is
    'Managed Agents session.id of the session that wrote this row, when written by an agent session. Null for rows written by hand, by seed scripts, or before this column existed. Closes the attribution half of Week 18''s f16.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Adding written_by_session column to claims and evidence_links...")
            cur.execute(DDL_ADD_ATTRIBUTION_COLUMNS)

            print("Applying column comments...")
            cur.execute(DDL_COMMENTS)

        conn.commit()
        print("\nMigration committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
