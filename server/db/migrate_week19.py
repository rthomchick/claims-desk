"""
Week 19 migration — evidence_links.scope. Applies against the live Supabase
project via the pooler connection (SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19

Blocking prerequisite for the Week 19 retest: scope text (platform versions,
component revisions, configurations an evidence record covers) currently has
no home and would otherwise go into evidence_url. Nullable because the 12
existing evidence records predate it and are not being backfilled.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_ADD_SCOPE = """
alter table evidence_links
    add column scope text;
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Adding scope column to evidence_links...")
            cur.execute(DDL_ADD_SCOPE)

        conn.commit()
        print("\nMigration committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
