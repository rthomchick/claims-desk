"""
Week 18 Day 1 migration — record_status (soft delete), claim_slug (stable
addressing), active_claims view. Applies against the live Supabase project
via the pooler connection (SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week18

d1: claims.status already exists with unrelated semantics (substantiation:
'unverified'/'substantiated'/'insufficient'/'expired'), consumed by
get_claim_status and check_substantiation. The soft-delete lifecycle flag
is added as a new column, record_status, rather than colliding with it.

d2: claim_slug format is {product_key}-{claim_type}-{NN}, NN zero-padded,
ordered by created_at within each product_key+claim_type pair. Slugs are
never reused — future inserts count against ALL rows ever inserted for a
pair (see append_claim.py), not just active ones.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_ADD_COLUMNS = """
alter table claims
    add column record_status text not null default 'active'
        check (record_status in ('active', 'deleted'));

alter table claims
    add column claim_slug text;
"""

DDL_DROP_RULINGS_CASCADE = """
alter table review_rulings
    drop constraint review_rulings_claim_id_fkey;

alter table review_rulings
    add constraint review_rulings_claim_id_fkey
        foreign key (claim_id) references claims(claim_id);
"""

DDL_FINALIZE_SLUG = """
alter table claims
    alter column claim_slug set not null;

alter table claims
    add constraint claims_claim_slug_key unique (claim_slug);
"""

DDL_CREATE_VIEW = """
create view active_claims as
select * from claims where record_status = 'active';
"""


def _backfill_slugs(cur) -> list[tuple[str, str]]:
    cur.execute(
        """
        select claim_id, product_key, claim_type
        from claims
        order by product_key, claim_type, created_at asc
        """
    )
    rows = cur.fetchall()

    counters: dict[tuple[str, str], int] = {}
    mapping: list[tuple[str, str]] = []
    for claim_id, product_key, claim_type in rows:
        key = (product_key, claim_type)
        counters[key] = counters.get(key, 0) + 1
        slug = f"{product_key}-{claim_type}-{counters[key]:02d}"
        mapping.append((str(claim_id), slug))

    for claim_id, slug in mapping:
        cur.execute(
            "update claims set claim_slug = %s where claim_id = %s",
            (slug, claim_id),
        )

    return mapping


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Adding record_status and claim_slug columns...")
            cur.execute(DDL_ADD_COLUMNS)

            print("Removing ON DELETE CASCADE from review_rulings.claim_id FK...")
            cur.execute(DDL_DROP_RULINGS_CASCADE)

            print("Backfilling claim_slug...")
            mapping = _backfill_slugs(cur)

            print("\nBackfill mapping (claim_id -> claim_slug):")
            print(f"{'claim_id':<38} {'claim_slug':<30}")
            print("-" * 68)
            for claim_id, slug in mapping:
                print(f"{claim_id:<38} {slug:<30}")

            print("\nFinalizing claim_slug (NOT NULL + UNIQUE)...")
            cur.execute(DDL_FINALIZE_SLUG)

            print("Creating active_claims view...")
            cur.execute(DDL_CREATE_VIEW)

        conn.commit()
        print("\nMigration committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
