"""Integration tests for delete_claim (require live DB via SUPABASE_DB_URL)."""

from __future__ import annotations

import uuid

import pytest

from server.db.client import get_connection
from server.tools.append_claim import append_claim
from server.tools.delete_claim import delete_claim
from server.tools.get_claim_status import get_claim_status


def test_delete_claim_not_found():
    result = delete_claim(str(uuid.uuid4()))
    assert "error" in result


def test_delete_claim_success():
    claim_id = append_claim(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="throwaway claim for delete_claim test",
    )["claim_id"]

    status = get_claim_status(claim_id)
    assert "claim" in status, f"claim not found before delete: {status}"

    result = delete_claim(claim_id)
    assert result == {"deleted": True, "claim_id": claim_id}

    after = get_claim_status(claim_id)
    assert "error" in after


def test_delete_claim_cascades_evidence():
    claim_id = append_claim(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="throwaway claim with evidence for cascade test",
        evidence_url="https://example.com/study.pdf",
        evidence_date="2025-01-01",
        sample_size=100,
    )["claim_id"]

    status = get_claim_status(claim_id)
    assert len(status["evidence"]) == 1

    result = delete_claim(claim_id)
    assert result["deleted"] is True

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM evidence_links WHERE claim_id = %s",
                (claim_id,),
            )
            count = cur.fetchone()[0]
    finally:
        conn.close()

    assert count == 0
