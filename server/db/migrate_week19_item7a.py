"""
Week 19 migration, item 7a of 7 — retest_sessions table.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543).

Run directly: python -m server.db.migrate_week19_item7a

Adds retest_sessions, recording one row per h1-r retest session
(launch_review.py, per-arm/per-repetition retest runs). Experiment
infrastructure, not part of the Claims Desk product surface — see the
table comment. Does not touch review_rulings, its CHECK constraint, or
get_claim_status; connecting the review pipeline to review_rulings is
deferred to a separate piece of work after the retest.
"""

from __future__ import annotations

from server.db.client import get_connection

DDL_CREATE_TABLE = """
create table retest_sessions (
    session_id text primary key,
    agent_id text,
    claim_slug text not null,
    pair_label text,
    arm text not null,
    repetition integer not null,
    verdict text,
    ruling_artifact text,
    grading_result text,
    grading_iterations integer,
    criterion_scores jsonb,
    manipulation_check text,
    run_log_path text,
    created_at timestamptz not null default now()
);
"""

DDL_COMMENT = """
comment on table retest_sessions is
    'Week 19 h1-r retest session records. Experiment infrastructure, not part of the Claims Desk product surface. No MCP tool reads this table; it exists so per-criterion agreement can be scored by query rather than by parsing gitignored run logs. review_rulings remains the product''s ruling surface and is unaffected.';
"""


def migrate() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Creating retest_sessions table...")
            cur.execute(DDL_CREATE_TABLE)

            print("Applying table comment...")
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
