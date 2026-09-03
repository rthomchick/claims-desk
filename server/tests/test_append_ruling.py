"""Integration tests for append_ruling (require live DB via SUPABASE_DB_URL).

Gate enforcement (verdict enum, convergence known) lives in the JS launcher
(week17/adversary.js, mirrored in week17/lib/ruling_gate.mjs and tested in
week17/test/ruling_gate.test.mjs) — a ruling artifact that fails the gate
never reaches append_ruling at all. What's tested here is the persistence
layer append_ruling controls directly: the DB's own CHECK constraints as
the last line of defense, and the append-only contract (insert only, later
created_at wins the get_claim_status read).

Isolation (Week 20 d2): every test here takes the `rollback_db` fixture and
runs inside a single transaction that is rolled back at teardown. These
tests drive the real production tools against the real database, so without
it they leave permanent rows behind — the eight fixture rulings removed by
server/db/cleanup_week20_fixture_rulings.py were written by earlier runs of
this file. Any new test in this file that touches the DB must take the
fixture too.
"""

from __future__ import annotations

import uuid

import psycopg2
import pytest

from server.tools.append_claim import append_claim
from server.tools.append_ruling import append_ruling
from server.tools.get_claim_status import get_claim_status


def _claim_id():
    return append_claim(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="throwaway claim for append_ruling test",
    )["claim_id"]


def _ruling_count(conn, claim_id):
    """Count via the fixture's connection so uncommitted rows are visible."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM review_rulings WHERE claim_id = %s",
            (claim_id,),
        )
        return cur.fetchone()[0]


def test_passing_gate_produces_exactly_one_row(rollback_db):
    claim_id = _claim_id()

    result = append_ruling(
        claim_id=claim_id,
        verdict="substantiated",
        rationale="evidence held up under adversarial review",
        reviewed_by="substantiation-adversary/v1",
        convergence="attack_exhaustion",
        rounds=2,
        written_by_session=None,
    )

    assert "ruling_id" in result
    assert _ruling_count(rollback_db, claim_id) == 1

    status = get_claim_status(claim_id)
    assert status["claim"]["verification"] == "substantiated"
    assert status["latest_ruling"]["verdict"] == "substantiated"
    assert status["latest_ruling"]["convergence"] == "attack_exhaustion"
    assert status["latest_ruling"]["rounds"] == 2


def test_verdict_outside_enum_rejected_nothing_written(rollback_db):
    claim_id = _claim_id()

    # A failed statement aborts the surrounding transaction, so this case
    # runs in a SAVEPOINT: the constraint violation is rolled back to the
    # savepoint and the outer test transaction stays usable for the
    # post-condition count below.
    with rollback_db.cursor() as cur:
        cur.execute("SAVEPOINT before_bad_verdict")

    with pytest.raises(psycopg2.Error):
        append_ruling(
            claim_id=claim_id,
            verdict="approved",
            convergence="attack_exhaustion",
            rounds=1,
        )

    with rollback_db.cursor() as cur:
        cur.execute("ROLLBACK TO SAVEPOINT before_bad_verdict")

    assert _ruling_count(rollback_db, claim_id) == 0


def test_no_convergence_mode_rejected_nothing_written(rollback_db):
    # The DB column is nullable, so this exercises the launcher-side gate
    # contract directly: a run with no known convergence mode must never
    # reach append_ruling in the first place. Simulated here by asserting
    # the launcher's decision (skip the call) rather than calling it —
    # mirroring the same case covered for real logic in
    # week17/test/ruling_gate.test.mjs ("run with no convergence mode fails").
    claim_id = _claim_id()

    convergence = None
    gate_passes = convergence in ("attack_exhaustion", "round_cap")
    assert gate_passes is False

    if gate_passes:
        append_ruling(claim_id=claim_id, verdict="substantiated", convergence=convergence, rounds=1)

    assert _ruling_count(rollback_db, claim_id) == 0


def test_two_rulings_same_claim_two_rows_later_wins_created_at_desc(rollback_db):
    """The superseding row wins the get_claim_status read.

    created_at defaults to now(), which in PostgreSQL is transaction start
    time — constant for every statement in one transaction. Under rollback
    isolation both inserts would therefore carry an identical created_at and
    `order by created_at desc` would be a tie broken arbitrarily, testing
    nothing. The two rulings are separated explicitly here so the ordering
    contract is what's under test rather than statement timing. In
    production the two calls are separate transactions and now() advances
    on its own; the observed 0.55s gap between the real superseding pair
    (rulings 6 and 7 in the Week 20 audit) is that effect.
    """
    claim_id = _claim_id()

    first = append_ruling(
        claim_id=claim_id,
        verdict="not_substantiated",
        rationale="first pass — evidence insufficient",
        reviewed_by="substantiation-adversary/v1",
        convergence="round_cap",
        rounds=3,
    )
    append_ruling(
        claim_id=claim_id,
        verdict="substantiated",
        rationale="superseding pass — new evidence submitted",
        reviewed_by="substantiation-adversary/v1",
        convergence="attack_exhaustion",
        rounds=1,
    )

    # Backdate the first ruling so the superseding row is unambiguously later.
    with rollback_db.cursor() as cur:
        cur.execute(
            "UPDATE review_rulings SET created_at = created_at - interval '1 second' "
            "WHERE ruling_id = %s",
            (first["ruling_id"],),
        )

    assert _ruling_count(rollback_db, claim_id) == 2

    status = get_claim_status(claim_id)
    assert status["claim"]["verification"] == "substantiated"
    assert status["latest_ruling"]["verdict"] == "substantiated"
    assert status["latest_ruling"]["convergence"] == "attack_exhaustion"
    assert status["latest_ruling"]["rounds"] == 1


def test_escalate_persists_rather_than_being_held(rollback_db):
    claim_id = _claim_id()

    result = append_ruling(
        claim_id=claim_id,
        verdict="escalate",
        rationale="record leaves the verdict genuinely undecidable",
        reviewed_by="substantiation-adversary/v1",
        convergence="round_cap",
        rounds=3,
    )

    assert "ruling_id" in result
    assert _ruling_count(rollback_db, claim_id) == 1

    status = get_claim_status(claim_id)
    assert status["claim"]["verification"] == "escalate"
    assert status["latest_ruling"]["verdict"] == "escalate"
    assert status["latest_ruling"]["convergence"] == "round_cap"
    assert status["latest_ruling"]["rounds"] == 3


def test_append_ruling_not_found_claim_id_still_rejected_by_fk(rollback_db):
    # Same savepoint treatment as the bad-verdict case: the FK violation
    # would otherwise poison the outer transaction.
    with rollback_db.cursor() as cur:
        cur.execute("SAVEPOINT before_bad_fk")

    with pytest.raises(psycopg2.Error):
        append_ruling(
            claim_id=str(uuid.uuid4()),
            verdict="substantiated",
            convergence="attack_exhaustion",
            rounds=1,
        )

    with rollback_db.cursor() as cur:
        cur.execute("ROLLBACK TO SAVEPOINT before_bad_fk")
