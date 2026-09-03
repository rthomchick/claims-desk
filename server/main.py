"""
Claims Desk MCP server. Six tools per ADR-016 Decision 1 + Addendum (2026-07-13)
plus Week 18 Day 1 (d3): append_claim, get_claim_status, check_substantiation,
classify_claim_risk, delete_claim, list_claims.

Transport is selected at runtime via the MCP_TRANSPORT env var:
- "stdio" (default) — local dev / Claude Code local connector
- "streamable-http" — Railway deployment. Uses the low-level SDK's direct
  transport path (mcp.run(transport="streamable-http")), not manual
  FastAPI/Starlette mounting — the mount pattern has known bugs across
  MCP Python SDK versions that a single-server build doesn't need to risk.

stateless_http=True + json_response=True: the transport-layer expression
of ADR-016's explicit-handle pattern (claim_id passed as a plain tool
argument, no hidden session state). No auth configured — deferred per
ADR-016's Resolved Open Questions (fictional Kalder data, no sensitive
information in the registry); see README for the explicit rationale.
"""

from __future__ import annotations

import os

import json

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from server.db.client import fetchone_dict
from server.tools.append_claim import append_claim as _append_claim
from server.tools.append_ruling import append_ruling as _append_ruling
from server.tools.get_claim_status import get_claim_status as _get_claim_status
from server.tools.check_substantiation import check_substantiation as _check_substantiation
from server.tools.classify_claim_risk import classify_claim_risk as _classify_claim_risk
from server.tools.delete_claim import delete_claim as _delete_claim
from server.tools.list_claims import list_claims as _list_claims

mcp = FastMCP(
    "claims-desk",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def append_claim(
    product_key: str,
    claim_type: str,
    claim_text: str,
    evidence_url: str | None = None,
    evidence_date: str | None = None,
    sample_size: int | None = None,
    baseline: str | None = None,
    expiry_date: str | None = None,
    scope: str | None = None,
    platform: str | None = None,
    platform_version: str | None = None,
    component_revision: str | None = None,
    written_by_session: str | None = None,
) -> dict:
    """Add a claim to the registry, with optional evidence. Returns the new claim_id.

    scope: the boundary the evidence covers (e.g. a specific config, region, or workload).
    platform: the platform named in a compatibility claim.
    platform_version: the platform version as the vendor publishes it. Stored
        verbatim and not normalized — do not reformat it.
    component_revision: the certified component revision for a compatibility claim.
    written_by_session: identifier of the session/agent writing this claim.
    """
    return _append_claim(
        product_key=product_key,
        claim_type=claim_type,
        claim_text=claim_text,
        evidence_url=evidence_url,
        evidence_date=evidence_date,
        sample_size=sample_size,
        baseline=baseline,
        expiry_date=expiry_date,
        scope=scope,
        platform=platform,
        platform_version=platform_version,
        component_revision=component_revision,
        written_by_session=written_by_session,
    )


@mcp.tool()
def append_ruling(
    claim_id: str,
    verdict: str,
    rationale: str | None = None,
    reviewed_by: str | None = None,
    convergence: str | None = None,
    rounds: int | None = None,
    written_by_session: str | None = None,
) -> dict:
    """Insert a review ruling. Append-only: no updates, no upserts — a
    correction is a new row with a later created_at for the same claim_id.

    verdict: one of substantiated, partially, not_substantiated, escalate.
    convergence: attack_exhaustion or round_cap — how the reviewing run
        terminated. reviewed_by: instrument identifier naming the review
        agent/tool and its version. written_by_session: identifier of the
        session/agent writing this ruling.
    """
    return _append_ruling(
        claim_id=claim_id,
        verdict=verdict,
        rationale=rationale,
        reviewed_by=reviewed_by,
        convergence=convergence,
        rounds=rounds,
        written_by_session=written_by_session,
    )


@mcp.tool()
def get_claim_status(claim_id: str) -> dict:
    """Read a claim's current status, linked evidence, and most recent review ruling."""
    return _get_claim_status(claim_id)


@mcp.tool()
def check_substantiation(claim_id: str) -> dict:
    """
    Return a claim, its evidence, the evidence standard for its claim type,
    and deterministic hygiene checks. Does not render a substantiation
    verdict — that judgment belongs to the calling agent.
    """
    return _check_substantiation(claim_id)


@mcp.tool()
def classify_claim_risk(claim_id: str) -> dict:
    """Classify a claim's risk (low/medium/high/prohibited) with contributing factors."""
    return _classify_claim_risk(claim_id)


@mcp.tool()
def delete_claim(claim_id: str) -> dict:
    """Soft-delete a claim (record_status -> 'deleted'). Returns {deleted: true, claim_id} on success."""
    return _delete_claim(claim_id)


@mcp.tool()
def list_claims(
    claim_type: str | None = None,
    status: str | None = None,
    product_key: str | None = None,
) -> list[dict]:
    """
    Enumerate claims by type/status/product. status is 'active' (default),
    'deleted', or 'all'. Returns slug-first summaries — claim_slug, claim_id,
    product_key, claim_type, status, risk_class — with no evidence payload.
    """
    return _list_claims(claim_type=claim_type, status=status, product_key=product_key)


@mcp.custom_route("/claims/{slug}.json", methods=["GET", "OPTIONS"])
async def get_claim_by_slug(request: Request) -> Response:
    """Read-only: resolve a claim by claim_slug and return get_claim_status's payload shape."""
    if request.method == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
            },
        )
    slug = request.path_params["slug"]
    claim = fetchone_dict("select claim_id from claims where claim_slug = %s", (slug,))
    if claim is None:
        return JSONResponse(
            {"error": f"no claim found with claim_slug {slug}"},
            status_code=404,
            headers={"Access-Control-Allow-Origin": "*"},
        )
    payload = json.dumps(_get_claim_status(claim["claim_id"]), default=str)
    return Response(
        payload,
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)
