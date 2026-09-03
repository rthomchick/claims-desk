"""Unit tests for compatibility claim-type handling in check_substantiation
and classify_claim_risk (ADR-016 Decision 4 addendum).

Pure unit tests against mocked DB calls — the platform_lifecycle branch is
fabricated here because no claim in the Week 19 retest trips it, so this
is the only coverage that branch gets from the experiment itself.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from server.tools import check_substantiation as cs
from server.tools import classify_claim_risk as ccr


# ---------------------------------------------------------------------------
# _platform_lifecycle_status — all three statuses, fabricated dates so no
# dependency on live platform_lifecycle contents or the current date's
# relationship to real RHEL end-of-support dates.
# ---------------------------------------------------------------------------

def test_platform_lifecycle_status_current():
    future_date = date(9999, 1, 1)
    with patch.object(cs, "fetchone_dict", return_value={"standard_support_end": future_date}):
        status = cs._platform_lifecycle_status("Red Hat Enterprise Linux", "9.0-9.x")
    assert status == "current"


def test_platform_lifecycle_status_expired():
    past_date = date(2000, 1, 1)
    with patch.object(cs, "fetchone_dict", return_value={"standard_support_end": past_date}):
        status = cs._platform_lifecycle_status("Red Hat Enterprise Linux", "6.0-6.x")
    assert status == "expired"


def test_platform_lifecycle_status_unknown_no_matching_row():
    with patch.object(cs, "fetchone_dict", return_value=None):
        status = cs._platform_lifecycle_status("Red Hat Enterprise Linux", "99.0-99.x")
    assert status == "unknown"


def test_platform_lifecycle_status_unknown_null_platform():
    status = cs._platform_lifecycle_status(None, "9.0-9.x")
    assert status == "unknown"


def test_platform_lifecycle_status_unknown_null_platform_version():
    status = cs._platform_lifecycle_status("Red Hat Enterprise Linux", None)
    assert status == "unknown"


def test_major_version_extracts_leading_digits():
    assert cs._major_version("9.0-9.x") == "9"
    assert cs._major_version("10.0-10.x") == "10"
    assert cs._major_version(None) is None
    assert cs._major_version("") is None


# ---------------------------------------------------------------------------
# check_substantiation — compatibility wiring, via mocked claim/evidence rows
# ---------------------------------------------------------------------------

def _claim_row(claim_type="compatibility"):
    return {
        "claim_id": "fake-id",
        "product_key": "acme_widget",
        "claim_type": claim_type,
        "claim_text": "Certified for Red Hat Enterprise Linux 9",
        "risk_class": None,
        "risk_factors": None,
    }


def test_check_substantiation_compatibility_expired_lifecycle():
    evidence_row = {
        "evidence_id": "ev-1",
        "evidence_url": "https://access.redhat.com/ecosystem/example",
        "evidence_date": date(2020, 1, 1),
        "sample_size": None,
        "baseline": None,
        "expiry_date": None,
        "scope": None,
        "platform": "Red Hat Enterprise Linux",
        "platform_version": "6.0-6.x",
        "component_revision": "rev-A",
    }
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(), None]
    ), patch.object(
        cs, "fetchall_dict", return_value=[evidence_row]
    ), patch.object(cs, "_platform_lifecycle_status", return_value="expired"):
        result = cs.check_substantiation("fake-id")

    assert result["hygiene_checks"]["platform_lifecycle_status"] == "expired"
    assert result["hygiene_checks"]["is_expired"] is None
    assert result["hygiene_checks"]["has_sample_size"] is None
    assert result["evidence_standard"] == cs.EVIDENCE_STANDARDS["compatibility"]
    assert result["claim"]["verification"] == "unreviewed"
    assert result["claim"]["evidence_current"] is None


def test_check_substantiation_compatibility_unknown_lifecycle_no_evidence():
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(), None]
    ), patch.object(
        cs, "fetchall_dict", return_value=[]
    ):
        result = cs.check_substantiation("fake-id")

    assert result["hygiene_checks"]["platform_lifecycle_status"] == "unknown"


def test_check_substantiation_unrecognized_claim_type_returns_error_not_keyerror():
    with patch.object(cs, "fetchone_dict", return_value=_claim_row(claim_type="aspirational")), patch.object(
        cs, "fetchall_dict", return_value=[]
    ):
        result = cs.check_substantiation("fake-id")

    assert "error" in result
    assert "aspirational" in result["error"]


def test_check_substantiation_non_compatibility_types_get_null_lifecycle_status():
    for claim_type in ("performance", "comparative", "compliance", "superlative"):
        with patch.object(
            cs, "fetchone_dict", side_effect=[_claim_row(claim_type=claim_type), None]
        ), patch.object(
            cs, "fetchall_dict", return_value=[]
        ):
            result = cs.check_substantiation("fake-id")
        assert result["hygiene_checks"]["platform_lifecycle_status"] is None, claim_type


# ---------------------------------------------------------------------------
# verification / evidence_current — read-time derivation rules (this commit)
# ---------------------------------------------------------------------------

def test_verification_is_unreviewed_when_no_ruling_exists():
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(claim_type="performance"), None]
    ), patch.object(cs, "fetchall_dict", return_value=[]):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["verification"] == "unreviewed"


def test_verification_reflects_the_single_existing_ruling():
    with patch.object(
        cs,
        "fetchone_dict",
        side_effect=[_claim_row(claim_type="performance"), {"verdict": "substantiated"}],
    ), patch.object(cs, "fetchall_dict", return_value=[]):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["verification"] == "substantiated"


def test_verification_reflects_the_most_recent_of_two_rulings():
    # review_rulings is append-only; the tool selects by created_at desc
    # limit 1, so fetchone_dict is trusted here to already hand back only
    # the most recent row — this asserts that row's verdict wins.
    with patch.object(
        cs,
        "fetchone_dict",
        side_effect=[_claim_row(claim_type="performance"), {"verdict": "escalate"}],
    ), patch.object(cs, "fetchall_dict", return_value=[]):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["verification"] == "escalate"


def test_evidence_current_true_when_all_expiries_unexpired():
    evidence = [
        {"evidence_url": "https://example.com/a", "expiry_date": date(9999, 1, 1)},
        {"evidence_url": "https://example.com/b", "expiry_date": date(9999, 6, 1)},
    ]
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(claim_type="compliance"), None]
    ), patch.object(cs, "fetchall_dict", return_value=evidence):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["evidence_current"] is True


def test_evidence_current_false_when_any_expiry_has_passed():
    evidence = [
        {"evidence_url": "https://example.com/a", "expiry_date": date(9999, 1, 1)},
        {"evidence_url": "https://example.com/b", "expiry_date": date(2000, 1, 1)},
    ]
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(claim_type="compliance"), None]
    ), patch.object(cs, "fetchall_dict", return_value=evidence):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["evidence_current"] is False


def test_evidence_current_null_when_no_evidence_carries_an_expiry():
    evidence = [{"evidence_url": "https://example.com/a", "expiry_date": None}]
    with patch.object(
        cs, "fetchone_dict", side_effect=[_claim_row(claim_type="compliance"), None]
    ), patch.object(cs, "fetchall_dict", return_value=evidence):
        result = cs.check_substantiation("fake-id")

    assert result["claim"]["evidence_current"] is None


# ---------------------------------------------------------------------------
# classify_claim_risk — compatibility ruleset
# ---------------------------------------------------------------------------

def test_classify_compatibility_no_certification_link_is_prohibited():
    risk, factors = ccr._classify_compatibility(
        {"claim_text": "Certified for RHEL 9"}, None
    )
    assert risk == "prohibited"
    assert any("no certification record link" in f for f in factors)


def test_classify_compatibility_floors_at_medium_when_clean():
    evidence = {
        "evidence_url": "https://access.redhat.com/ecosystem/example",
        "platform_version": "9.0-9.x",
        "platform_lifecycle_status": "current",
    }
    risk, factors = ccr._classify_compatibility(
        {"claim_text": "Certified for Red Hat Enterprise Linux 9"}, evidence
    )
    assert risk == "medium"


def test_classify_compatibility_no_platform_version_is_high():
    evidence = {
        "evidence_url": "https://access.redhat.com/ecosystem/example",
        "platform_version": None,
        "platform_lifecycle_status": "unknown",
    }
    risk, factors = ccr._classify_compatibility(
        {"claim_text": "Certified for Red Hat Enterprise Linux"}, evidence
    )
    assert risk == "high"
    assert any("platform version not named" in f for f in factors)


def test_classify_compatibility_expired_lifecycle_is_high():
    evidence = {
        "evidence_url": "https://access.redhat.com/ecosystem/example",
        "platform_version": "6.0-6.x",
        "platform_lifecycle_status": "expired",
    }
    risk, factors = ccr._classify_compatibility(
        {"claim_text": "Certified for Red Hat Enterprise Linux 6"}, evidence
    )
    assert risk == "high"
    assert any("lifecycle threshold" in f for f in factors)


def test_classify_compatibility_support_tier_language_elevates():
    evidence = {
        "evidence_url": "https://access.redhat.com/ecosystem/example",
        "platform_version": "9.0-9.x",
        "platform_lifecycle_status": "current",
    }
    risk, factors = ccr._classify_compatibility(
        {"claim_text": "Widget is supported on Red Hat Enterprise Linux 9"}, evidence
    )
    assert risk == "high"
    assert any("substring match on claim_text" in f for f in factors)


def test_classify_claim_risk_unrecognized_claim_type_returns_error_not_keyerror():
    with patch.object(
        ccr, "fetchone_dict", return_value={"claim_id": "fake-id", "claim_type": "aspirational", "claim_text": "x"}
    ):
        result = ccr.classify_claim_risk("fake-id")

    assert "error" in result
    assert "aspirational" in result["error"]
