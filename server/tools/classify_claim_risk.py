"""
classify_claim_risk — MCP per ADR-016 Decision 1 (cross-caller consistency).

Four type-specific rulesets, kept as separate functions rather than one
tangled conditional, since Week 17's adversary will probe this directly.
Each ruleset returns (risk_class, risk_factors) given the claim and its
linked evidence. The computed result is written back to the claims row.
"""

from __future__ import annotations

from datetime import date

from server.db.client import fetchone_dict, fetchall_dict, execute
from server.tools.check_substantiation import _platform_lifecycle_status
import json

RISK_CLASSES = ("low", "medium", "high", "prohibited")

# Rank for taking the max of several factors within one ruleset.
_RANK = {c: i for i, c in enumerate(RISK_CLASSES)}


def _worse(a: str, b: str) -> str:
    return a if _RANK[a] >= _RANK[b] else b


def _classify_performance(claim: dict, evidence: dict | None) -> tuple[str, list[str]]:
    factors: list[str] = []
    risk = "low"

    if evidence is None or not evidence.get("evidence_url"):
        factors.append("no evidence link")
        risk = _worse(risk, "high")
    if evidence is None or evidence.get("sample_size") is None:
        factors.append("no sample size")
        risk = _worse(risk, "medium")
    if evidence is None or not evidence.get("baseline"):
        factors.append("no baseline named")
        risk = _worse(risk, "medium")
    if evidence is None or not evidence.get("evidence_date"):
        factors.append("no evidence date")
        risk = _worse(risk, "medium")

    if not factors:
        factors.append("evidence link, sample size, baseline, and date all present")

    return risk, factors


def _classify_comparative(claim: dict, evidence: dict | None) -> tuple[str, list[str]]:
    factors: list[str] = []
    risk = "low"

    if evidence is None or not evidence.get("evidence_url"):
        factors.append("no evidence link")
        risk = _worse(risk, "high")
    if evidence is None or not evidence.get("baseline"):
        factors.append("no comparison basis / competitor named")
        risk = _worse(risk, "high")
    if evidence is None or evidence.get("sample_size") is None:
        factors.append("no sample size")
        risk = _worse(risk, "medium")
    if evidence is None or not evidence.get("evidence_date"):
        factors.append("no evidence date")
        risk = _worse(risk, "medium")

    if not factors:
        factors.append("evidence link, comparison basis, sample size, and date all present")

    return risk, factors


def _classify_compliance(claim: dict, evidence: dict | None) -> tuple[str, list[str]]:
    factors: list[str] = []
    risk = "low"

    if evidence is None or not evidence.get("evidence_url"):
        factors.append("no evidence link (no certificate on file)")
        risk = _worse(risk, "prohibited")

    expiry = evidence.get("expiry_date") if evidence else None
    if expiry is None:
        factors.append("no expiry date on file")
        risk = _worse(risk, "high")
    elif expiry < date.today():
        factors.append(f"certification expired {expiry.isoformat()}")
        risk = _worse(risk, "high")

    if not factors:
        factors.append("certificate on file with valid, non-expired expiry date")

    return risk, factors


def _classify_superlative(claim: dict, evidence: dict | None) -> tuple[str, list[str]]:
    factors: list[str] = []
    risk = "low"

    if evidence is None or not evidence.get("evidence_url"):
        factors.append("no source named for ranking/recognition claim")
        risk = _worse(risk, "prohibited")
    else:
        if not evidence.get("evidence_date"):
            factors.append("source exists but no date given — cannot confirm currency")
            risk = _worse(risk, "medium")
        else:
            days_old = (date.today() - evidence["evidence_date"]).days
            if days_old > 365:
                factors.append(f"source is {days_old} days old — superlative claims require continuous re-substantiation")
                risk = _worse(risk, "high")

    if not factors:
        factors.append("source, category, and recent date all present")

    return risk, factors


def _classify_compatibility(claim: dict, evidence: dict | None) -> tuple[str, list[str]]:
    factors: list[str] = []
    # Floor at medium per the Decision 4 addendum: falsity here is
    # operational (unsupported production system), not just reputational.
    risk = "medium"

    if evidence is None or not evidence.get("evidence_url"):
        factors.append("no certification record link")
        risk = _worse(risk, "prohibited")

    if evidence is None or not evidence.get("platform_version"):
        factors.append("platform version not named")
        risk = _worse(risk, "high")

    lifecycle_status = evidence.get("platform_lifecycle_status") if evidence else None
    if lifecycle_status == "expired":
        factors.append("platform version past standard support lifecycle threshold")
        risk = _worse(risk, "high")

    # Crude heuristic: substring match on claim_text, not language
    # understanding. Flagged here per the instruction that this detection
    # method must be visible in risk_factors, not buried.
    claim_text = (claim.get("claim_text") or "").lower()
    if "supported on" in claim_text:
        factors.append(
            "support-tier language (\"supported on\") detected via substring "
            "match on claim_text — a crude heuristic, not language understanding"
        )
        risk = _worse(risk, "high")

    if not factors:
        factors.append("certification record, platform version, and current lifecycle status all present")

    return risk, factors


_RULESETS = {
    "performance": _classify_performance,
    "comparative": _classify_comparative,
    "compliance": _classify_compliance,
    "superlative": _classify_superlative,
    "compatibility": _classify_compatibility,
}


def classify_claim_risk(claim_id: str) -> dict:
    claim = fetchone_dict(
        "select claim_id, claim_type, claim_text from claims where claim_id = %s",
        (claim_id,),
    )
    if claim is None:
        return {"error": f"no claim found with claim_id {claim_id}"}

    claim_type = claim["claim_type"]
    if claim_type not in _RULESETS:
        return {"error": f"unrecognized claim_type: {claim_type}"}

    evidence_rows = fetchall_dict(
        """
        select evidence_url, evidence_date, sample_size, baseline, expiry_date,
               platform, platform_version, component_revision
        from evidence_links
        where claim_id = %s
        order by created_at asc
        limit 1
        """,
        (claim_id,),
    )
    evidence = evidence_rows[0] if evidence_rows else None

    if claim_type == "compatibility" and evidence is not None:
        evidence["platform_lifecycle_status"] = _platform_lifecycle_status(
            evidence.get("platform"), evidence.get("platform_version")
        )

    ruleset = _RULESETS[claim_type]
    risk_class, risk_factors = ruleset(claim, evidence)

    execute(
        """
        update claims
        set risk_class = %s, risk_factors = %s, updated_at = now()
        where claim_id = %s
        """,
        (risk_class, json.dumps(risk_factors), claim_id),
    )

    return {
        "claim_id": str(claim_id),
        "risk_class": risk_class,
        "risk_factors": risk_factors,
    }
