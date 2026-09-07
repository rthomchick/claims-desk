# Claims table residue audit — 2026-09-05

Read-only. Queried via the Supabase MCP server (project `ogmhqxpzfkxybrcrkqeg`, "Claims Desk"), not a raw pooler connection. No rows modified.

## Headline numbers (re-derived, both stale figures were close but not current)

| | count |
|---|---|
| **Total rows in `claims`** | **71** |
| REAL | 20 |
| RESIDUE | 50 |
| UNCLEAR | 1 |
| RESIDUE with `record_status = 'active'` | **10** |
| Total `record_status = 'active'` (all groups) | 31 |

The task's stale snapshot ("48 of 71 rows, 10 active" as of 2026-09-03) undercounted residue by 2 rows. The active-residue count (10) hasn't changed since 2026-09-03 — no new contamination since then — but total residue grew from 48 to 50 because 2 more already-present rows (`4d0aba48…`, `bc0e6e73…`, both `record_status='deleted'`) were miscounted or omitted in that snapshot; they carry the same `test_delete_claim.py` literals and the same 2026-09-03 08:18 timestamp burst as everything else in that window.

REAL + RESIDUE + UNCLEAR = 20 + 50 + 1 = **71 = total**. ✓

---

## 1. Test files that insert into `claims`

Only one file in the repo issues `insert into claims` SQL: **`server/tools/append_claim.py`**. Everything else reaches the table through it.

| Test file | Helper used | `claim_text` literal(s) | `product_key` | Cleanup |
|---|---|---|---|---|
| `server/tests/test_delete_claim.py` | inline calls to `append_claim` | `"throwaway claim for delete_claim test"`; `"throwaway claim with evidence for soft-delete test"` | `kalder_resolve` | Now uses `rollback_db` fixture (post-620a026); file's own docstring: *"Earlier runs of this file left 38 soft-deleted 'throwaway' claims in production."* |
| `server/tests/test_append_ruling.py` | local `_claim_id()` → `append_claim` | `"throwaway claim for append_ruling test"` (identical every call) | `kalder_resolve` | Now uses `rollback_db` fixture (post-620a026). Pre-fix runs left 8 fixture `review_rulings` rows (removed by `server/db/cleanup_week20_fixture_rulings.py`, commit df10869) **and** the underlying claim rows, which cleanup script never touched. |
| `server/tests/test_compatibility_claim_type.py`, `test_launch_review.py`, `test_run_retest.py` | — | none | — | No DB writes at all; pure unit tests against mocks/fixtures. `vendor_compat-compatibility-0N` strings appear only as assertion literals in `test_run_retest.py`, never inserted. |

Shared fixture: `server/tests/conftest.py` defines `rollback_db`, which wraps a real connection so every insert/update in a test lands in one transaction rolled back at teardown. Only `test_delete_claim.py` and `test_append_ruling.py` use it — introduced by commit **620a026**, which is the fix this whole audit is measuring residue against.

Also checked and ruled out: `server/seed/seed_claims.py` (dev/demo seed script, not test-invoked — see REAL group below), `server/db/cleanup_week20_fixture_rulings.py` (a delete script, not an insert source), all `week17/*.js` (read claims only via the MCP tool layer, no direct DB access), all migration scripts.

---

## 2. Partition

### REAL — 20 rows

| Group | Rows | Rule |
|---|---|---|
| Kalder product-catalog seed | 12 | Exact `claim_text` match against every entry in `server/seed/seed_claims.py`'s `SEED_CLAIMS` list, all inserted 2026-07-11 06:29:44–50 (one deliberate `seed()` run). Confirmed not test-invoked — no test or conftest imports `seed()`. |
| `salesforce_govcloud` FedRAMP claim | 1 (`b4b8179d…`) | 2026-07-14, distinct from the seed burst; has a real adversary ruling (`1f0585ae…`, verdict `partially`) and is explicitly named as a **protected** row in `cleanup_week20_fixture_rulings.py`'s `PROTECTED_RULING_IDS` comment. |
| `kalder_govern` second compliance claim | 1 (`cabc493b…`) | 2026-08-29 05:47, distinct real-looking text ("SOC 2 Type II certified across the full Kalder governance platform"), has its own `evidence_links` row, no test file references it. |
| `vendor_compat` compatibility set | 6 (`7b38f6ae…`, `7f2057be…`, `68cd4c6a…`, `4bbede85…`, `53543a68…`, `ff97218c…`) | Slugs `vendor_compat-compatibility-01..06` are read by `server/agents/run_retest.py`'s real A/B/C pairing logic (`PairSpec` list) and asserted against in `test_run_retest.py` — but that test only asserts on the *string literals*, never inserts them. These are organic data the retest workflow operates on, not test fixtures. |

### RESIDUE — 50 rows

| Group | Count | Matching rule |
|---|---|---|
| `"throwaway claim for delete_claim test"` | 25 | Literal string match to `test_delete_claim.py:29`; all `kalder_resolve`/`performance`/`record_status='deleted'` except none active. |
| `"throwaway claim with evidence for soft-delete test"` / `"...cascade test"` | 15 | Literal string match to `test_delete_claim.py:50` (the "cascade test" wording is an earlier/renamed variant of the same literal, both `kalder_resolve`/`performance`/`deleted`). |
| `"throwaway claim for append_ruling test"` | 10 | Literal string match to `test_append_ruling.py:36`, all `kalder_resolve`/`performance`, all in the single 2026-09-03 08:18:19–46 burst (27 seconds), all `record_status='active'` — these are the claims underneath the 8 fixture rulings that `cleanup_week20_fixture_rulings.py` already removed from `review_rulings`; the script never touched `claims`. |
| MCP wrapper probe | 1 (`085ef4da…`) | Self-describing `claim_text`: "MCP wrapper param probe - safe to delete." `product_key='kalder_mcp_probe'` is itself a marker, not a real product. Not traceable to a test file — a manual, ad-hoc MCP tool call, already `record_status='deleted'`. |
| Ruling-artifact text inserted as a claim | 1 (`ca8e0eb3…`, `salesforce_govcloud`) | `claim_text` begins "RULING ARTIFACT — NOT A MARKETING CLAIM. Do not adjudicate..." — this is literally the banner string `launch_review.py` writes as ruling-artifact output (`"RULING ARTIFACT"` header, confirmed at `server/agents/launch_review.py:128,719`), evidently pasted into `append_claim` by mistake rather than stored as a ruling. Already `record_status='deleted'`. Not a pytest-traceable case — an operator/manual-entry mistake — but unambiguously not a marketing claim. |

Two of the 50 (`4d0aba48…`, `bc0e6e73…`) sit at the tail of the 2026-09-03 08:18 burst (08:18:49–53), a few seconds after the last `append_ruling` throwaway claim and carrying the `test_delete_claim.py` literals — same uncommitted pytest session, just the delete-claim tests running immediately after the append-ruling tests in one process.

### UNCLEAR — 1 row

| claim_id | Snippet | Why unclear |
|---|---|---|
| `81824fc3-9e00-4a39-9494-db5d69ace8ca` | "DoD verification insert for Week 18 d2" | `kalder_resolve`/`performance`, `record_status='active'`, created 2026-08-27 03:29:20 — 24 seconds after a burst of 4 residue rows, but its own text says it's a manual verification insert (against `migrate_week18.py`'s `d2` slug-format change), not a pytest fixture. No test file or migration script names this exact text. It reads like a deliberate one-off human sanity-check of a schema migration rather than a marketing claim or an automated test artifact — could go either way; flagging rather than guessing. |

---

## 3. Cross-check: `review_rulings` / `evidence_links` referencing RESIDUE claims

- **`review_rulings`**: table currently holds only **3 rows total**, and all 3 reference REAL claims (`4846d719…`, `2e583614…`, `b4b8179d…` — the same three protected by the cleanup script plus the salesforce one). **Zero RESIDUE claim_ids have any review_rulings row.** The 8 fixture rulings that *did* reference residue claims were already deleted by `cleanup_week20_fixture_rulings.py` (commit df10869) — this audit confirms that cleanup fully succeeded on the `review_rulings` side; it just never reached the underlying `claims` rows.
- **`evidence_links`**: 39 of 71 claims have exactly one evidence_links row each (1:1, no claim has more than one). Cross-referencing against RESIDUE: **21 RESIDUE claim_ids have an evidence_links row** — all traceable to `test_delete_claim.py::test_delete_claim_preserves_evidence`, which deliberately attaches `evidence_url="https://example.com/study.pdf"` to prove evidence survives a soft delete. These evidence rows are themselves residue, not orphans — same test, same fixture pattern, no cleanup script has touched them.

Corrected 2026-09-07: original figure was a counting error (the residue-id x evidence claim_id intersection was never counted); 21 confirmed by distinct-count reconciliation, 21 claims x 1 row each. Not a units mismatch. A prior reconciliation cited a second instance at line 46; on inspection the figure appears once.

## 4. Active-count in `list_claims` terms

`list_claims(status="active")` returns 31 rows total (using the tool's own `record_status` filter — the MCP layer's "active" maps directly to the column). Of those 31:
- 20 are the REAL rows above
- **10 are RESIDUE** — the `test_append_ruling.py` burst (2026-09-03 08:18:19–46), all still `record_status='active'` because nothing has soft-deleted them
- 1 is the UNCLEAR row (`81824fc3…`)

So the honest current answer to "how many active rows does an ordinary `list_claims` call surface that a user would mistake for real data" is **10 residue + 1 unclear = up to 11 of 31 active rows (35%)** are not genuine marketing claims.

---

## Note (unsolicited, not part of the ask)

`get_advisors`-equivalent check via `list_tables` flagged that Row Level Security is disabled on all 5 public tables including `claims`, `review_rulings`, and `evidence_links` — anon/authenticated Supabase clients can read or write every row. Not in scope for this audit and no SQL was run to change it; surfacing per the tool's own advisory since it's a live finding on the table just audited.

## Nothing was deleted or modified. Stopping here per instructions.
