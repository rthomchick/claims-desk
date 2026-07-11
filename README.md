# Claims Desk

Marketing claims governance MCP server. Registry of claims with
substantiation status, evidence links, expiry dates, and risk
classification, callable by any agent that drafts, reviews, or publishes
marketing content.

Architecture and rationale: see `ADR-016` (MCP vs. Agent Skills split,
persistence, hosting, taxonomy, repo structure).

## Status (Week 16, Day 3)

Built and unit-verified locally. **Not yet connected to a live database** —
Supabase project has not been provisioned yet. See "Deferred to Day 4"
below for what that blocks.

## Setup

```bash
python3 -m venv ../venv-claims-desk
source ../venv-claims-desk/bin/activate
pip install -r requirements.txt
```

Confirmed SDK: `mcp==1.28.1` (stable v1.x per ADR-016 Decision 3 — not the
v2 beta).

Copy `.env.example` to `.env` and fill in `SUPABASE_DB_URL` with the
**pooler** connection string (port 6543). The direct connection (port
5432) fails with IPv6 routing on Supabase — same failure mode as the SAFe
Feature Spec System's ADR-003, and the reason this server uses
`psycopg2` directly against the pooler rather than the `supabase` Python
client.

## Running

```bash
python -m server.main          # stdio transport, local dev
python -m server.smoke_test    # in-process tool-registration check, no DB needed
```

Once `.env` is populated:

```bash
python3 -c "from server.db.client import init_db; init_db()"   # apply schema.sql
python -m server.seed.seed_claims                               # seed 12 claims, run classify_claim_risk, print summary
```

## Tools

Per ADR-016 Decision 1:

- `append_claim` — write a claim (+ optional evidence) to the registry
- `get_claim_status` — read a claim, its evidence, and latest review ruling
- `check_substantiation` — **thin**: claim + evidence + evidence standard +
  deterministic hygiene booleans (`has_evidence_link`, `has_evidence_date`,
  `is_expired`, `has_sample_size`). No rendered verdict — that's the
  calling agent's job, guided by the (not-yet-written) taxonomy Skill.
- `classify_claim_risk` — four type-specific rulesets (performance,
  comparative, compliance, superlative), each a separate function in
  `server/tools/classify_claim_risk.py`. Returns `risk_class` plus
  `risk_factors` (the specific inputs that drove the classification, not
  just the label). Writes the result back to the `claims` row.

## Deferred to Day 4 (needs a live Supabase project)

Per user decision on Day 3: a new, isolated Supabase project was not
provisioned during this session. The following DoD items from the Day 3
build prompt are **not yet verified** and require `SUPABASE_DB_URL` to be
set before they can run:

- Schema applied to a live database
- 12 seed claims inserted and confirmed present with correct `claim_type`
- Claims #9 and #11 confirmed to have no `evidence_links` row
- `classify_claim_risk` run against all 12 live rows; summary table
  printed (the risk rulesets themselves ARE unit-tested — see below —
  but not exercised against live seeded rows)
- `check_substantiation` smoke-tested against claim #1 and claim #9 via
  live DB round-trip
- Railway deployment and dual-client (Day 4) verification

What WAS verified without a live DB:
- All four tools register and are callable via the SDK's in-process
  `Client` pattern (`server/smoke_test.py`)
- The four `classify_claim_risk` rulesets were unit-tested directly
  against representative inputs matching seed claims #1, #7, #9, #11,
  plus an expired-compliance case — all produced the expected risk
  classes, including both DoD-critical assertions (claims #9 and #11
  must classify `high` or `prohibited`; both classified `prohibited`)
- `check_substantiation`'s output shape confirmed by inspection to
  contain no verdict field (`claim`, `evidence`, `evidence_standard`,
  `hygiene_checks` only)

**To unblock:** create a Supabase project, get its pooler connection
string (Project Settings → Database → Connection string → "Transaction"
pooler, port 6543), put it in `.env` as `SUPABASE_DB_URL`, then run the
`init_db()` and seed commands above.
