"""
Claims Desk MCP server. Four tools per ADR-016 Decision 1:
append_claim, get_claim_status, check_substantiation, classify_claim_risk.

Runs over stdio by default (local dev / Claude Code). Railway deployment
(Streamable HTTP) is a Day 4 concern per ADR-016 Decision 3 — not wired
up here yet.
"""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from server.tools.append_claim import append_claim as _append_claim
from server.tools.get_claim_status import get_claim_status as _get_claim_status
from server.tools.check_substantiation import check_substantiation as _check_substantiation
from server.tools.classify_claim_risk import classify_claim_risk as _classify_claim_risk

mcp = FastMCP("claims-desk")


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
) -> dict:
    """Add a claim to the registry, with optional evidence. Returns the new claim_id."""
    return _append_claim(
        product_key=product_key,
        claim_type=claim_type,
        claim_text=claim_text,
        evidence_url=evidence_url,
        evidence_date=evidence_date,
        sample_size=sample_size,
        baseline=baseline,
        expiry_date=expiry_date,
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


if __name__ == "__main__":
    mcp.run()
