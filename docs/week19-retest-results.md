# Week 19 — Retest Scoring: Blocked

**Status:** Stopped before scoring, per task instruction. Read-only analysis; no writes to `retest_sessions`.

## What was read

- `docs/week19-locked-verdicts.md` — the six locked correct verdicts (Pair A: C7/C8 `not_substantiated`; Pair B: C3/C4 `substantiated`; Pair C: C10/C11 `not_substantiated`), mapped to `claim_slug`s `vendor_compat-compatibility-01` through `-06`.
- `server/agents/review_rubric.md` — all nine grading criteria (evidence citation, valid verdict, verdict-matches-standard, no reputational grounds, compliance currency, internal consistency, memory consistency, scope accuracy, slug addressing).
- `retest_sessions` — queried live. 24 rows present, matching the expected count (23 effective rulings + 1 void: compat-01, memory_off, pair A, rep 1, per d(w19)-15).

## Finding: `criterion_scores` is null on all 24 rows

Queried `session_id, claim_slug, arm, pair_label, repetition, verdict, grading_result, criterion_scores, manipulation_check` for every row. `criterion_scores` is `None` on all 24, with no exceptions.

This is not a partial-data gap — it is structural, confirmed by tracing the write path:

- [server/agents/launch_review.py:883-895](../server/agents/launch_review.py#L883-L895) calls `write_retest_session_row(...)` with `criterion_scores=None` hard-coded at the call site.
- Nothing else writes or updates the column. `server/agents/run_retest.py` only reads `claim_slug` / `arm` / `pair_label` / `repetition` for dedup (`already recorded in retest_sessions`) and prints a final summary table from other columns — it never sets `criterion_scores`.
- `server/db/migrate_week19_item7a.py` and `server/db/schema.sql` both declare the column (`criterion_scores jsonb, -- per-criterion pass/fail`) with a schema comment stating it exists "so per-criterion agreement can be scored by query rather than by parsing gitignored run logs" — but no code path in the current tree populates it.
- The grading step (`span.outcome_evaluation_end` in the Managed Agents event stream) only surfaces `outcome_result` (an overall `satisfied`/`failed`) and `outcome_explanation` (free text). There is no per-criterion breakdown captured anywhere in the pipeline as it currently runs.

## Consequence

Per-criterion agreement (commitment 1), the exclusion accounting (commitment 4), and the wrong-standard-propagation check (commitment 15) all require a per-criterion score per ruling. None of that can be computed from `criterion_scores` as instructed.

The only path to a nine-criteria breakdown from the data that exists is parsing grader feedback out of the run logs (`runs/`, gitignored). The task instructions designate that explicitly as a different task, not a fallback to take here. No such parsing was performed.

## Not done

- Denominator, agreement scoring, correctness scoring, kill-condition check, and the observed/judgment-vs-near-constant split — none computed. All depend on per-criterion data that does not exist in `retest_sessions`.
- No writes to `retest_sessions`.
- No interpretation of what this means for h1-r's disposition.
