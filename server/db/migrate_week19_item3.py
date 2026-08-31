"""
Week 19 migration, item 3 of 7 — structured compatibility evidence columns.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19_item3

Adds platform, platform_version, and component_revision to evidence_links
for the upcoming compatibility claim type. Nullable because the 20 existing
evidence records predate them and are not being backfilled; no other claim
type uses them.

Division of labour vs. the existing scope column (recorded as a schema
comment on all four columns, since scope now overlaps with these three and
inconsistent authoring would put ambiguity into the retest's evidence
records):
  - platform, platform_version, component_revision carry the version and
    revision facts, and are what the deterministic checks read.
  - scope carries configuration and support-tier detail that does not
    decompose into columns. Version and revision facts do NOT go here.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_ADD_COMPATIBILITY_COLUMNS = """
alter table evidence_links
    add column platform text,
    add column platform_version text,
    add column component_revision text;
"""

DDL_COMMENTS = """
comment on column evidence_links.platform is
    'Compatibility claims: certified platform/OS name, e.g. ''Red Hat Enterprise Linux''. Version and revision facts live here and in platform_version/component_revision, not in scope.';
comment on column evidence_links.platform_version is
    'Compatibility claims: certified version range, e.g. ''9.0-9.x''. Deterministic checks read this field, not scope.';
comment on column evidence_links.component_revision is
    'Compatibility claims: SKU, firmware, or driver revision covered. Deterministic checks read this field, not scope.';
comment on column evidence_links.scope is
    'Configuration and support-tier detail that does not decompose into columns. Does NOT carry version/revision facts once platform/platform_version/component_revision are populated.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Adding platform, platform_version, component_revision columns to evidence_links...")
            cur.execute(DDL_ADD_COMPATIBILITY_COLUMNS)

            print("Applying schema comments recording column division of labour...")
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
