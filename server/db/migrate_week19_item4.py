"""
Week 19 migration, item 4 of 7 — platform_lifecycle table.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19_item4

Adds platform_lifecycle, the standard-subscription end date for a
platform major version, keyed on (platform, major_version). Populated
once from Red Hat's product life cycle API in a separate population
script (populate_week19_platform_lifecycle.py); this migration only
creates the table.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_CREATE_TABLE = """
create table platform_lifecycle (
    platform text not null,
    major_version text not null,
    standard_support_end date,
    phase_name text,
    source_url text not null,
    retrieved_at timestamptz not null,
    primary key (platform, major_version)
);
"""

DDL_COMMENT = """
comment on table platform_lifecycle is
    'Populated once, Week 19. No refresh mechanism exists. Rows are accurate as of retrieved_at and go stale silently. Any consumer must treat retrieved_at as a currency bound on its own conclusion.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Creating platform_lifecycle table...")
            cur.execute(DDL_CREATE_TABLE)

            print("Applying table comment recording the staleness limit...")
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
