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


_RULESETS = {
    "performance": _classify_performance,
    "comparative": _classify_comparative,
    "compliance": _classify_compliance,
    "superlative": _classify_superlative,
}


def classify_claim_risk(claim_id: str) -> dict:
    claim = fetchone_dict(
        "select claim_id, claim_type from claims where claim_id = %s",
        (claim_id,),
    )
    if claim is None:
        return {"error": f"no claim found with claim_id {claim_id}"}

    evidence_rows = fetchall_dict(
        """
        select evidence_url, evidence_date, sample_size, baseline, expiry_date
        from evidence_links
        where claim_id = %s
        order by created_at asc
        limit 1
        """,
        (claim_id,),
    )
    evidence = evidence_rows[0] if evidence_rows else None

    ruleset = _RULESETS[claim["claim_type"]]
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
