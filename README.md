# Claims Desk

Marketing claims governance MCP server. Registry of claims with
substantiation status, evidence links, expiry dates, and risk
classification, callable by any agent that drafts, reviews, or publishes
marketing content.

Architecture and rationale: see `ADR-016` (MCP vs. Agent Skills split,
persistence, hosting, taxonomy, repo structure).

## Status (Week 16, Day 3)

Built and verified against a live Supabase project (`ogmhqxpzfkxybrcrkqeg`).
Schema applied, all 12 seed claims inserted, `classify_claim_risk` run
against all 12 live rows, `check_substantiation` smoke-tested against
claims #1 and #9. Day 3 DoD complete.

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

## Day 3 verification (live database)

- Schema applied to a live Supabase project via the pooler connection
- All 12 seed claims inserted; confirmed 3-3-3-3 distribution across the
  four claim types
- Claims #9 (`kalder_vendor`, fabricated FedRAMP) and #11 (`kalder_insight`,
  no named source) confirmed to have zero `evidence_links` rows
- `classify_claim_risk` run against all 12 live rows — claims #9 and #11
  both classified `prohibited` (DoD required `high` or `prohibited`)
- `check_substantiation` smoke-tested against claim #1 and claim #9 live —
  confirmed thin output (`claim`, `evidence`, `evidence_standard`,
  `hygiene_checks`, no verdict field) in both cases
- All four tools register and are callable via the SDK's in-process
  `Client` pattern (`server/smoke_test.py`)

**Note on claim #11's seed data:** the original seed included an
`evidence_date` with no `evidence_url` on claim #11, to model "a date was
floated but no source named." `append_claim` inserts an `evidence_links`
row whenever *any* evidence field is present, so this produced a row with
`evidence_url: None` rather than zero rows — the risk classification
(`prohibited`) and hygiene check (`has_evidence_link: False`) were both
still correct, but it didn't literally satisfy "no evidence_links row."
Reseeded with no evidence fields at all on #11 to match the DoD literally.

## Deferred to Day 4

- Railway deployment (Streamable HTTP transport — `server/main.py`
  currently runs stdio only; `railway.toml`'s `startCommand` assumes HTTP
  wiring that hasn't been added yet)
- Dual-client verification (Claude Code + claude.ai in one sitting)
