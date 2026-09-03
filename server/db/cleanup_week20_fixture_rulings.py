"""Week 20 d2 cleanup — remove eight test-fixture rulings from production.

Background. review_rulings is append-only (see schema.sql's table comment):
inserts only, a correction is a superseding row. This script is a deliberate,
one-time exception to that contract, and it is not a precedent. The eight rows
it removes are not rulings at all — they were written by pytest runs of
server/tests/test_append_ruling.py firing against the live database, before
that file was placed under transaction-rollback isolation. Leaving them would
mean a compliance table where fixture data and real verdicts are
indistinguishable to any reader.

Provenance of the eight. All were written 2026-09-03 between 08:18:19 and
08:18:46 UTC — a 27-second burst no human review could produce — and each
carries one of four canned rationales matching the literals in
test_append_ruling.py exactly ("evidence held up under adversarial review",
"first pass — evidence insufficient", "superseding pass — new evidence
submitted", "record leaves the verdict genuinely undecidable"). Each targets a
throwaway claim whose claim_text is "throwaway claim for append_ruling test".

Deliberately NOT touched, though written the same day by the same instrument
identifier: 80a5e0ea-ee0b-49ee-bcbd-e6e758a4d5ac (kalder_resolve-performance-01)
and 6e7db2d4-83c1-4d6b-ac96-383038220979 (kalder_resolve-comparative-01). Those
are real adversary runs with multi-paragraph rationales and must survive.

Safety contract. The script refuses to delete anything unless the database
matches expectations exactly: all eight ids present, none of them already gone,
and the count of rows that would be deleted equal to eight. Every targeted row
is fetched and printed in full before any delete is issued, so the record of
what was removed exists independently of this file. The delete and its
verification run in one transaction that is rolled back if the post-delete
count is not exactly eight.

Run directly:  python -m server.db.cleanup_week20_fixture_rulings
Dry run:       python -m server.db.cleanup_week20_fixture_rulings --dry-run
"""

from __future__ import annotations

import sys

from psycopg2.extras import RealDictCursor

from server.db.client import get_connection

# The eight fixture rows, by explicit ruling_id, from the Week 20 audit dump.
FIXTURE_RULING_IDS = (
    "708ebf79-2942-46dd-a067-70ad064e2043",  # row 1  substantiated      08:18:19
    "ab54f12f-c329-41e8-9492-ad6542cfa516",  # row 2  not_substantiated  08:18:25.228
    "6a35ec75-459a-490c-8d79-dfdf9fdefb24",  # row 3  substantiated      08:18:25.781
    "e44d4e58-e3c7-4b26-9ea3-23df58b2f473",  # row 4  escalate           08:18:28
    "4efcafdc-46f5-4ce4-9281-2d9212690204",  # row 5  substantiated      08:18:38
    "d148e91c-379a-4c23-9d71-a26a6330bf5b",  # row 6  not_substantiated  08:18:43.281
    "173d48c6-02e2-4b54-b419-226fed24174b",  # row 7  substantiated      08:18:43.843
    "a2b98018-f2b0-498c-9fff-1ec31a219144",  # row 8  escalate           08:18:46
)

EXPECTED_DELETE_COUNT = 8

# Must survive. Guarded explicitly so a careless edit to the list above
# cannot take out a real ruling.
PROTECTED_RULING_IDS = (
    "80a5e0ea-ee0b-49ee-bcbd-e6e758a4d5ac",  # kalder_resolve-performance-01
    "6e7db2d4-83c1-4d6b-ac96-383038220979",  # kalder_resolve-comparative-01
)


class CleanupRefused(RuntimeError):
    """Raised when the database does not match what the script expects."""


def _preflight(cur) -> list[dict]:
    """Verify the target set exactly, returning the rows to be deleted."""
    if len(set(FIXTURE_RULING_IDS)) != len(FIXTURE_RULING_IDS):
        raise CleanupRefused("target list contains duplicate ruling_ids")

    if len(FIXTURE_RULING_IDS) != EXPECTED_DELETE_COUNT:
        raise CleanupRefused(
            f"target list holds {len(FIXTURE_RULING_IDS)} ids, "
            f"expected {EXPECTED_DELETE_COUNT}"
        )

    overlap = set(FIXTURE_RULING_IDS) & set(PROTECTED_RULING_IDS)
    if overlap:
        raise CleanupRefused(f"target list names protected ruling_ids: {sorted(overlap)}")

    cur.execute(
        """
        select ruling_id, claim_id, verdict, rationale, reviewed_by,
               convergence, rounds, written_by_session, created_at
        from review_rulings
        where ruling_id = any(%s::uuid[])
        order by created_at
        """,
        (list(FIXTURE_RULING_IDS),),
    )
    rows = [dict(r) for r in cur.fetchall()]

    found = {str(r["ruling_id"]) for r in rows}
    missing = sorted(set(FIXTURE_RULING_IDS) - found)
    if missing:
        raise CleanupRefused(
            "refusing to run — these targeted ruling_ids are not in the table "
            f"(already deleted, or wrong database): {missing}"
        )

    if len(rows) != EXPECTED_DELETE_COUNT:
        raise CleanupRefused(
            f"refusing to run — matched {len(rows)} rows, expected {EXPECTED_DELETE_COUNT}"
        )

    # The protected rulings must exist and stay untouched.
    cur.execute(
        "select count(*) as n from review_rulings where ruling_id = any(%s::uuid[])",
        (list(PROTECTED_RULING_IDS),),
    )
    if cur.fetchone()["n"] != len(PROTECTED_RULING_IDS):
        raise CleanupRefused(
            "refusing to run — a protected ruling is missing; the table is not "
            "in the state this cleanup was written against"
        )

    return rows


def _print_rows(rows: list[dict]) -> None:
    print(f"Rows to be deleted ({len(rows)}), printed in full for the record:")
    print("=" * 72)
    for i, r in enumerate(rows, 1):
        print(f"--- {i}/{len(rows)} ---")
        for key, value in r.items():
            print(f"  {key}: {value!r}")
        print()


def cleanup(dry_run: bool = False) -> int:
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("select count(*) as n from review_rulings")
            before = cur.fetchone()["n"]
            print(f"review_rulings rows before: {before}\n")

            rows = _preflight(cur)
            _print_rows(rows)

            if dry_run:
                conn.rollback()
                print("DRY RUN — nothing deleted.")
                return 0

            cur.execute(
                "delete from review_rulings where ruling_id = any(%s::uuid[])",
                (list(FIXTURE_RULING_IDS),),
            )
            deleted = cur.rowcount
            if deleted != EXPECTED_DELETE_COUNT:
                conn.rollback()
                raise CleanupRefused(
                    f"rolled back — delete affected {deleted} rows, "
                    f"expected exactly {EXPECTED_DELETE_COUNT}"
                )

            cur.execute(
                "select count(*) as n from review_rulings where ruling_id = any(%s::uuid[])",
                (list(PROTECTED_RULING_IDS),),
            )
            if cur.fetchone()["n"] != len(PROTECTED_RULING_IDS):
                conn.rollback()
                raise CleanupRefused("rolled back — a protected ruling went missing")

            conn.commit()

            cur.execute("select count(*) as n from review_rulings")
            after = cur.fetchone()["n"]

        print(f"Deleted {deleted} fixture rulings.")
        print(f"review_rulings rows after: {after} (was {before})")
        return deleted
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        cleanup(dry_run="--dry-run" in sys.argv)
    except CleanupRefused as exc:
        print(f"CLEANUP REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)
