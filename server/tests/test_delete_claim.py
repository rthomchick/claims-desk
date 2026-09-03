"""Integration tests for delete_claim (require live DB via SUPABASE_DB_URL).

Isolation (Week 20 d2): as with test_append_ruling, every test that touches
the DB takes the `rollback_db` fixture and runs inside a transaction that is
rolled back at teardown. Earlier runs of this file left 38 soft-deleted
"throwaway" claims in production.
"""

from __future__ import annotations

import uuid

import pytest

from server.tools.append_claim import append_claim
from server.tools.delete_claim import delete_claim
from server.tools.get_claim_status import get_claim_status


def test_delete_claim_not_found(rollback_db):
    result = delete_claim(str(uuid.uuid4()))
    assert "error" in result


def test_delete_claim_success(rollback_db):
    claim_id = append_claim(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="throwaway claim for delete_claim test",
    )["claim_id"]

    status = get_claim_status(claim_id)
    assert "claim" in status, f"claim not found before delete: {status}"

    result = delete_claim(claim_id)
    assert result == {"deleted": True, "claim_id": claim_id}

    # Soft delete: the row survives with record_status flipped, not removed.
    after = get_claim_status(claim_id)
    assert "claim" in after, f"claim unexpectedly gone after soft delete: {after}"
    assert after["claim"]["record_status"] == "deleted"


def test_delete_claim_preserves_evidence(rollback_db):
    """Soft delete (Week 18 d1): the claims row is never removed, so
    evidence_links' ON DELETE CASCADE never fires and its rows survive."""
    claim_id = append_claim(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="throwaway claim with evidence for soft-delete test",
        evidence_url="https://example.com/study.pdf",
        evidence_date="2025-01-01",
        sample_size=100,
    )["claim_id"]

    status = get_claim_status(claim_id)
    assert len(status["evidence"]) == 1

    result = delete_claim(claim_id)
    assert result["deleted"] is True

    # Counted on the fixture's connection so the uncommitted rows are visible.
    with rollback_db.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM evidence_links WHERE claim_id = %s",
            (claim_id,),
        )
        count = cur.fetchone()[0]

    assert count == 1
