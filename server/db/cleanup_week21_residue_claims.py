"""Week 21 pre-work cleanup — hard-delete 51 test-residue claims.

Background. The claims table accumulated test-residue rows between
2026-08-27 and 2026-09-03, written by server/tests/test_delete_claim.py
and server/tests/test_append_ruling.py before those files were placed
under transaction-rollback isolation (commit 620a026, server/tests/
conftest.py's rollback_db fixture). server/db/cleanup_week20_fixture_rulings.py
already removed the eight fixture review_rulings rows that isolation gap
produced, but that script only ever touched review_rulings — the 51
underlying claims rows (and the evidence_links rows attached to some of
them) were never removed. This script is that removal.

Provenance of the 51. All identified and classified in the residue audit
at scratchpad/claims_residue_report.md (2026-09-05), which partitions every
row in claims into REAL / RESIDUE / UNCLEAR and accounts for all 71 rows
in the table. 50 of the 51 ids below are that report's RESIDUE group
verbatim. The 51st, kalder_resolve-performance-06 (claim_id
81824fc3-9e00-4a39-9494-db5d69ace8ca, claim_text "DoD verification insert
for Week 18 d2"), was left UNCLEAR in that report because no test file or
migration script traces it. It is reclassified RESIDUE here per Week 20
correction 12 (Notion, Week 20 chat log, Day 3 block, "Amendment to D4 —
kalder_resolve-performance-06 removed, not replaced") — independently
corroborated by ai-portfolio commit ac35665, which drops
kalder_resolve-performance-06 from claims-manifest.json and the demo page
specifically because it is Week 18 test residue, and by the row's own
self-describing claim_text.

Unlike cleanup_week20_fixture_rulings.py, review_rulings is append-only by
contract (see schema.sql's table comment) and that script was already a
deliberate, one-time exception to it. claims carries no such contract —
delete_claim's own soft-delete is a product-level choice, not a table
constraint — so a hard delete here is not a second exception to the same
rule; it is an ordinary delete against a table with no append-only
contract, gated by the safety checks below instead.

Provenance of the 51 ids. Copied verbatim from
scratchpad/claims_residue_report.md's RESIDUE list plus performance-06 as
described above. Ordered by created_at, as in that report.
"""

from __future__ import annotations

import sys

from psycopg2.extras import RealDictCursor

from server.db.client import get_connection

# The 51 residue claims, by explicit claim_id, from
# scratchpad/claims_residue_report.md (RESIDUE group, 50 ids) plus
# kalder_resolve-performance-06 (see module docstring).
RESIDUE_CLAIM_IDS = (
    "9364f4d2-040c-4bdf-9eb8-edc4c81e34bf",  # kalder_resolve/performance  2026-08-27 03:28:24  delete_claim test
    "2280a8f3-d61e-4c0a-81ea-8d05fcd0c5af",  # kalder_resolve/performance  2026-08-27 03:28:29  cascade test (evidence)
    "9339c999-2ce7-477a-ba9f-0a393e75de19",  # kalder_resolve/performance  2026-08-27 03:28:51  delete_claim test
    "7e219eb0-237d-40d3-83b9-603186c96757",  # kalder_resolve/performance  2026-08-27 03:28:56  soft-delete test (evidence)
    "81824fc3-9e00-4a39-9494-db5d69ace8ca",  # kalder_resolve/performance  2026-08-27 03:29:20  DoD verification insert (Week 20 correction 12)
    "ca8e0eb3-5b6b-4d34-9677-4b458c85b3c1",  # salesforce_govcloud/compliance 2026-08-27 20:17:42  RULING ARTIFACT text pasted as a claim
    "0474ff0b-798b-4d7c-a4fd-40ee41fdfc46",  # kalder_resolve/performance  2026-08-28 23:22:16  delete_claim test
    "ed855b2f-e092-494e-9c41-f91416a45e54",  # kalder_resolve/performance  2026-08-28 23:22:19  soft-delete test (evidence)
    "99e6947c-ca70-430d-94da-33fe17a24988",  # kalder_resolve/performance  2026-08-29 04:22:43  delete_claim test
    "d905c87a-5f39-4410-8ae0-f8fdcafbcf1b",  # kalder_resolve/performance  2026-08-29 04:22:46  soft-delete test (evidence)
    "a4f440a9-51b6-4751-b2d0-51df7dac913f",  # kalder_resolve/performance  2026-08-29 07:06:59  delete_claim test
    "8e16c0d3-0acf-4249-a919-03c305f54561",  # kalder_resolve/performance  2026-08-29 07:07:03  soft-delete test (evidence)
    "b1d3386d-9dbf-41e1-ba23-19ce5c7bd925",  # kalder_resolve/performance  2026-08-29 07:13:51  delete_claim test
    "63993195-c04d-4324-8c09-3d6bea073b29",  # kalder_resolve/performance  2026-08-29 07:13:54  soft-delete test (evidence)
    "3691ac73-947f-467d-9fcc-19bd32bb4b19",  # kalder_resolve/performance  2026-08-29 07:22:07  delete_claim test
    "41b73ebc-b064-405f-b36a-9f9fea6a15ad",  # kalder_resolve/performance  2026-08-29 07:22:11  soft-delete test (evidence)
    "068d73be-f354-45e6-862e-a8acfe953bb3",  # kalder_resolve/performance  2026-08-31 23:30:55  delete_claim test
    "62f12c45-2acb-42c2-b6f3-4559b3c66bf6",  # kalder_resolve/performance  2026-08-31 23:30:59  soft-delete test (evidence)
    "17c741d4-0ac4-4c80-aae0-7b5f12c83320",  # kalder_resolve/performance  2026-09-01 01:26:25  delete_claim test
    "f8dfac69-3049-4d1d-a0d4-c1441f3c8b53",  # kalder_resolve/performance  2026-09-01 01:26:28  soft-delete test (evidence)
    "085ef4da-189b-49c0-90c1-3a06c2751eb8",  # kalder_mcp_probe/compatibility 2026-09-01 02:10:58  MCP wrapper param probe
    "2e963f51-99dd-4375-adbf-fe2978b8c803",  # kalder_resolve/performance  2026-09-01 05:07:26  delete_claim test
    "a9fdf237-dd5f-401c-ad83-6f18305a0b04",  # kalder_resolve/performance  2026-09-01 05:07:30  soft-delete test (evidence)
    "c7a81445-65fa-431b-844c-e642aaa73a58",  # kalder_resolve/performance  2026-09-01 05:52:20  delete_claim test
    "4ffa645f-c62b-431e-b908-c20cbb2f8b54",  # kalder_resolve/performance  2026-09-01 05:52:24  soft-delete test (evidence)
    "3dc1561e-4f71-4816-b54c-9d5f9a715d93",  # kalder_resolve/performance  2026-09-01 19:07:28  delete_claim test
    "bf992379-013c-4416-b109-f3762e8f1411",  # kalder_resolve/performance  2026-09-01 19:07:32  soft-delete test (evidence)
    "39c9a3cf-d85d-460a-9fa4-c5d13ed86744",  # kalder_resolve/performance  2026-09-03 06:34:29  delete_claim test
    "ab8736b7-4cd6-4219-8f38-d9e352522e2b",  # kalder_resolve/performance  2026-09-03 06:34:32  soft-delete test (evidence)
    "d8718bd4-8c3c-4c5c-b805-4555dc2988e0",  # kalder_resolve/performance  2026-09-03 06:38:15  delete_claim test
    "2363efa7-5b75-4d98-aff0-54968d3fd65e",  # kalder_resolve/performance  2026-09-03 06:38:19  soft-delete test (evidence)
    "412f0ecc-057d-4a4f-ba22-97fcf27caefe",  # kalder_resolve/performance  2026-09-03 07:47:09  delete_claim test
    "19c7cb3b-31cb-4140-a620-1a86e9f3268c",  # kalder_resolve/performance  2026-09-03 07:47:12  soft-delete test (evidence)
    "0ded1c2b-dddb-4e86-894b-4512866c961d",  # kalder_resolve/performance  2026-09-03 07:50:55  delete_claim test
    "e4526c71-5889-4ffd-b6f9-7fe425670479",  # kalder_resolve/performance  2026-09-03 07:50:58  soft-delete test (evidence)
    "ccd211e7-6d4b-47c7-a5a7-6b4c68917b5a",  # kalder_resolve/performance  2026-09-03 07:51:36  delete_claim test
    "6dab33af-9bbc-40cd-912b-2fdc5abdea69",  # kalder_resolve/performance  2026-09-03 07:51:40  soft-delete test (evidence)
    "6ab8422c-bbd4-4749-a497-c33d491a2d81",  # kalder_resolve/performance  2026-09-03 08:02:31  delete_claim test
    "318292c4-cfba-453c-a592-c88c79e1a5f5",  # kalder_resolve/performance  2026-09-03 08:02:34  soft-delete test (evidence)
    "7c32a646-031c-45b3-9043-9c036348fea5",  # kalder_resolve/performance  2026-09-03 08:18:19  append_ruling test
    "f617c983-1a69-4a53-99b4-24772808bb49",  # kalder_resolve/performance  2026-09-03 08:18:22  append_ruling test
    "468bfe64-8c9b-4c83-be39-b1737232b31c",  # kalder_resolve/performance  2026-09-03 08:18:23  append_ruling test
    "8c6207a7-7b54-4a56-8675-4b84dcdd5ab1",  # kalder_resolve/performance  2026-09-03 08:18:24  append_ruling test
    "d6181ca2-359e-4434-b3c3-53854f8d89f8",  # kalder_resolve/performance  2026-09-03 08:18:27  append_ruling test
    "655dd8bb-1528-4ec7-b7e3-c3aa3cf6ab0d",  # kalder_resolve/performance  2026-09-03 08:18:37  append_ruling test
    "b92afdba-ace5-4aca-b615-14b255f1f9ad",  # kalder_resolve/performance  2026-09-03 08:18:40  append_ruling test
    "7ded7b83-b775-4397-9d31-a08ed2d030f0",  # kalder_resolve/performance  2026-09-03 08:18:41  append_ruling test
    "b2ea5271-9747-46e9-a11d-746de8c6e537",  # kalder_resolve/performance  2026-09-03 08:18:42  append_ruling test
    "6219191c-3714-45cf-b914-1e057113fbc8",  # kalder_resolve/performance  2026-09-03 08:18:46  append_ruling test
    "4d0aba48-03dd-4ad0-81fd-4fb223c86c26",  # kalder_resolve/performance  2026-09-03 08:18:49  delete_claim test
    "bc0e6e73-f4ee-47f6-af43-b4e2af1d706f",  # kalder_resolve/performance  2026-09-03 08:18:53  soft-delete test (evidence)
)

EXPECTED_DELETE_COUNT = 51
EXPECTED_SURVIVING_COUNT = 20

# Must never appear in RESIDUE_CLAIM_IDS. The real salesforce_govcloud claim,
# named explicitly because cleanup_week20_fixture_rulings.py already protects
# its ruling by this exact id.
PROTECTED_CLAIM_ID = "b4b8179d-199d-45c0-9721-38327a8087d1"

# The four claims the ai-portfolio demo manifest resolves by slug. These must
# survive with record_status='active' both before and after the delete.
MANIFEST_SLUGS = (
    "kalder_resolve-performance-01",
    "kalder_resolve-comparative-01",
    "kalder_vendor-compliance-01",
    "salesforce_govcloud-compliance-01",
)


class CleanupRefused(RuntimeError):
    """Raised when the database does not match what the script expects."""


def _preflight(cur) -> list[dict]:
    """Verify the target set exactly, returning the rows to be deleted."""
    if len(set(RESIDUE_CLAIM_IDS)) != len(RESIDUE_CLAIM_IDS):
        raise CleanupRefused("target list contains duplicate claim_ids")

    if len(RESIDUE_CLAIM_IDS) != EXPECTED_DELETE_COUNT:
        raise CleanupRefused(
            f"target list holds {len(RESIDUE_CLAIM_IDS)} ids, "
            f"expected {EXPECTED_DELETE_COUNT}"
        )

    if PROTECTED_CLAIM_ID in RESIDUE_CLAIM_IDS:
        raise CleanupRefused(
            f"target list names the protected salesforce_govcloud claim_id: {PROTECTED_CLAIM_ID}"
        )

    cur.execute(
        """
        select claim_id, product_key, claim_type, record_status, claim_slug,
               created_at, claim_text
        from claims
        where claim_id = any(%s::uuid[])
        order by created_at
        """,
        (list(RESIDUE_CLAIM_IDS),),
    )
    rows = [dict(r) for r in cur.fetchall()]

    found = {str(r["claim_id"]) for r in rows}
    missing = sorted(set(RESIDUE_CLAIM_IDS) - found)
    if missing:
        raise CleanupRefused(
            "refusing to run — these targeted claim_ids are not in the table "
            f"(already deleted, or wrong database): {missing}"
        )

    if len(rows) != EXPECTED_DELETE_COUNT:
        raise CleanupRefused(
            f"refusing to run — matched {len(rows)} rows, expected {EXPECTED_DELETE_COUNT}"
        )

    manifest_overlap = {r["claim_slug"] for r in rows} & set(MANIFEST_SLUGS)
    if manifest_overlap:
        raise CleanupRefused(
            f"target list names manifest claim_slugs: {sorted(manifest_overlap)}"
        )

    cur.execute(
        "select count(*) as n from review_rulings where claim_id = any(%s::uuid[])",
        (list(RESIDUE_CLAIM_IDS),),
    )
    ruling_count = cur.fetchone()["n"]
    if ruling_count != 0:
        raise CleanupRefused(
            f"refusing to run — {ruling_count} review_rulings row(s) reference "
            "a targeted claim_id (expected 0 per the residue audit); the "
            "claims_review_rulings_fk has no ON DELETE action and would also "
            "fail the delete, but this check runs first"
        )

    # The manifest claims must exist and stay active.
    cur.execute(
        "select claim_slug, record_status from claims where claim_slug = any(%s::text[])",
        (list(MANIFEST_SLUGS),),
    )
    manifest_rows = {r["claim_slug"]: r["record_status"] for r in cur.fetchall()}
    missing_manifest = sorted(set(MANIFEST_SLUGS) - manifest_rows.keys())
    if missing_manifest:
        raise CleanupRefused(
            f"refusing to run — manifest claim_slugs not found: {missing_manifest}"
        )
    not_active = sorted(
        slug for slug, status in manifest_rows.items() if status != "active"
    )
    if not_active:
        raise CleanupRefused(
            f"refusing to run — manifest claim_slugs not active: {not_active}"
        )

    return rows


def _print_rows(rows: list[dict]) -> None:
    print(f"Rows to be deleted ({len(rows)}), printed in full for the record:")
    print("=" * 72)
    for i, r in enumerate(rows, 1):
        print(f"--- {i}/{len(rows)} ---")
        print(f"  claim_id:      {r['claim_id']!r}")
        print(f"  product_key:   {r['product_key']!r}")
        print(f"  record_status: {r['record_status']!r}")
        print(f"  claim_text:    {r['claim_text'][:80]!r}")
        print()


def _print_survivors(rows: list[dict]) -> None:
    print(f"\nSurviving rows ({len(rows)}):")
    print("=" * 72)
    for r in rows:
        print(f"  {r['claim_id']}  {r['product_key']:<20} {r['record_status']}")


def cleanup(dry_run: bool = False) -> int:
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("select count(*) as n from claims")
            before = cur.fetchone()["n"]
            print(f"claims rows before: {before}\n")

            rows = _preflight(cur)
            _print_rows(rows)

            if dry_run:
                conn.rollback()
                print("DRY RUN — nothing deleted.")
                return 0

            cur.execute(
                "select count(*) as n from evidence_links where claim_id = any(%s::uuid[])",
                (list(RESIDUE_CLAIM_IDS),),
            )
            evidence_before = cur.fetchone()["n"]

            cur.execute(
                "delete from claims where claim_id = any(%s::uuid[])",
                (list(RESIDUE_CLAIM_IDS),),
            )
            deleted = cur.rowcount
            if deleted != EXPECTED_DELETE_COUNT:
                conn.rollback()
                raise CleanupRefused(
                    f"rolled back — delete affected {deleted} rows, "
                    f"expected exactly {EXPECTED_DELETE_COUNT}"
                )

            cur.execute(
                "select count(*) as n from evidence_links where claim_id = any(%s::uuid[])",
                (list(RESIDUE_CLAIM_IDS),),
            )
            evidence_after = cur.fetchone()["n"]
            evidence_cascaded = evidence_before - evidence_after

            # Post-delete verification, inside the same transaction.
            cur.execute("select count(*) as n from claims")
            after = cur.fetchone()["n"]
            if after != EXPECTED_SURVIVING_COUNT:
                conn.rollback()
                raise CleanupRefused(
                    f"rolled back — {after} claims remain, expected exactly "
                    f"{EXPECTED_SURVIVING_COUNT}"
                )

            cur.execute(
                "select claim_slug, record_status from claims where claim_slug = any(%s::text[])",
                (list(MANIFEST_SLUGS),),
            )
            manifest_after = {r["claim_slug"]: r["record_status"] for r in cur.fetchall()}
            missing_manifest = sorted(set(MANIFEST_SLUGS) - manifest_after.keys())
            not_active = sorted(
                slug for slug, status in manifest_after.items() if status != "active"
            )
            if missing_manifest or not_active:
                conn.rollback()
                raise CleanupRefused(
                    "rolled back — manifest claims not intact after delete: "
                    f"missing={missing_manifest} not_active={not_active}"
                )

            cur.execute(
                "select claim_id, product_key, record_status from claims order by created_at"
            )
            survivors = [dict(r) for r in cur.fetchall()]

            conn.commit()

        print(f"Deleted {deleted} residue claims.")
        print(f"claims rows after: {after} (was {before})")
        print(f"evidence_links rows cascaded: {evidence_cascaded} (before={evidence_before}, after={evidence_after})")
        print("\nPost-delete verification:")
        print(f"  1. claims count == {EXPECTED_SURVIVING_COUNT}: PASS ({after})")
        print(f"  2. manifest claims active: PASS ({sorted(manifest_after.keys())})")
        print("  3. surviving rows:")
        _print_survivors(survivors)
        return deleted
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        cleanup(dry_run="--confirm" not in sys.argv)
    except CleanupRefused as exc:
        print(f"CLEANUP REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)
