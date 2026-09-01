"""
Week 19 migration, item 6 of 7 — widen claims.claim_type CHECK constraint.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19_item6

Widens claims_claim_type_check to accept 'compatibility' alongside the
existing four values, per the migrate_week18.py precedent of
DROP CONSTRAINT / ADD CONSTRAINT. Also documents the platform_version
storage convention (verbatim vendor range notation, not normalized),
since _major_version() in check_substantiation.py and
classify_claim_risk.py now depends on that convention to parse the
leading major-version digit run.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_WIDEN_CLAIM_TYPE_CHECK = """
alter table claims
    drop constraint claims_claim_type_check;

alter table claims
    add constraint claims_claim_type_check
        check (claim_type in ('performance', 'comparative', 'compliance', 'superlative', 'compatibility'));
"""

DDL_COMMENT_PLATFORM_VERSION = """
comment on column evidence_links.platform_version is
    'Stores the certification record''s range notation verbatim as the vendor publishes it (e.g. ''9.0-9.x'', ''8.6-8.x''). Not normalized. The major version is parsed as the leading digit run, so the vendor''s own format must be preserved.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Widening claims_claim_type_check to include 'compatibility'...")
            cur.execute(DDL_WIDEN_CLAIM_TYPE_CHECK)

            print("Updating platform_version column comment...")
            cur.execute(DDL_COMMENT_PLATFORM_VERSION)

        conn.commit()
        print("\nMigration committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
