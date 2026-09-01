# Week 19: `criterion_scores` gap in `retest_sessions`

## Observation

`criterion_scores` is null on all 24 rows in `retest_sessions`.

```
select count(*) as n, count(criterion_scores) as non_null from retest_sessions;
 n  | non_null
----+----------
 24 |        0
```

## Why the column exists

The column was created in `acd53b1` ("feat: add retest_sessions table and
wire launcher to record runs"). The table comment applied by that commit
(`server/db/migrate_week19_item7a.py`, and mirrored in
`server/db/schema.sql`) states:

> 'Week 19 h1-r retest session records. Experiment infrastructure, not
> part of the Claims Desk product surface. No MCP tool reads this table;
> it exists so per-criterion agreement can be scored by query rather than
> by parsing gitignored run logs. review_rulings remains the product''s
> ruling surface and is unaffected.'

## The write path

`write_retest_session_row` is called from `run_review` in
`server/agents/launch_review.py`. At the call site (line 894),
`criterion_scores` is hard-coded to `None`:

```python
            write_retest_session_row(
                session_id=session.id,
                agent_id=agent_id,
                claim_slug=claim_slug,
                pair_label=pair_label,
                arm=variant,
                repetition=repetition,
                verdict=parse_verdict(ruling_text),
                ruling_artifact=ruling_text,
                grading_result=outcome_result,
                grading_iterations=iteration_count,
                criterion_scores=None,
                manipulation_check=manipulation_check,
                run_log_path=str(run_log_path),
            )
```

No other code path writes or updates the column. `server/agents/run_retest.py`
reads `claim_slug`, `arm`, `pair_label`, and `repetition` from
`retest_sessions` for resume/dedup (`fetch_completed_runs`), and prints a
summary table of `verdict`, `grading_result`, and `manipulation_check`
(`print_final_table`). It never reads or writes `criterion_scores`.

## What the grading step actually captures

In `launch_review.py`, the event handler for `span.outcome_evaluation_end`
(line 825) reads only two fields off the event:

```python
                if event.type == "span.outcome_evaluation_end":
                    outcome_result = event.result
                    outcome_explanation = event.explanation
```

These become `outcome_result` and `outcome_explanation`. `outcome_result`
is written to `retest_sessions.grading_result`; `outcome_explanation` is
printed and logged as "per-criterion feedback" but is prose, not a
structured per-criterion breakdown, and is not written to any column. No
step in the pipeline captures a per-criterion score anywhere.

## Consequence

Per-criterion agreement (commitment 1), the exclusion accounting
(commitment 4), and the wrong-standard-propagation check (commitment 15)
all require a per-criterion score per ruling. None of that can be
computed from `criterion_scores` as instructed.

The only path to a nine-criteria breakdown from the data that exists is
parsing grader feedback out of the run logs (`runs/`, gitignored). The
task instructions designate that explicitly as a different task, not a
fallback to take here. No such parsing was performed.
