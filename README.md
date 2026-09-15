# Claims Desk

Marketing claims governance as an MCP service. A registry of claims with
substantiation status, evidence links, expiry dates, and risk
classification — callable by any agent that drafts, reviews, or publishes
marketing content.

Every company ships claims ("40% faster deployment," "#1 rated on G2,"
"SOC 2 compliant"), and every claim carries substantiation risk: legal
exposure, analyst pushback, procurement scrutiny. Usually this is governed
by spreadsheets and nervous review cycles. The Claims Desk makes it a
service an agent can call.

The registry is populated with claims for **Kalder**, a fictional product
universe used as demo substrate. No real company's claims are stored here.

Architecture and rationale: see [`docs/ADR-016`](docs/ADR-016-claims-desk-capability-surface.md)
(MCP vs. Agent Skills split, persistence, hosting, taxonomy, repo
structure) and its three addenda.

## Status

**The MCP server is deployed and serving.** All seven tools respond over
Streamable HTTP at `claims-desk-production-8424.up.railway.app/mcp`.

**The backing Supabase database is live**, and the read-only
`/claims/{slug}.json` route returns claims end-to-end.

One operational note worth knowing before you clone this: the database runs
on Supabase's free tier, which **auto-pauses a project after a stretch of
inactivity**. A paused project's pooler tenant stops resolving, which
surfaces as `FATAL: (ENOTFOUND) tenant/user ... not found` on every
database-backed call and a 500 from the slug route. The MCP transport layer
stays healthy throughout, so this looks worse than it is: no data is lost
and no application code is implicated. Restoring the project from the
Supabase dashboard brings the whole surface back in a few minutes. Expect
this to recur whenever the project sits idle.

Two other things a reader should know before trusting this tree:

- `server/smoke_test.py` is stale. It asserts a five-tool list and now
  fails against the seven registered tools. The failure is the assertion,
  not the server.
- `retest_sessions.criterion_scores` was never populated — it is written as
  a hard-coded `None`. Per-criterion agreement scoring can't be computed
  from the table as it stands. See
  [`docs/week19-criterion-scores-gap.md`](docs/week19-criterion-scores-gap.md).

Test suite: **124 passing.** Nine of those exercise `append_ruling` and
`delete_claim` against a live database connection, so they error rather
than fail whenever the project is paused.

**Auth: intentionally not implemented.** Deferred per ADR-016's Resolved
Open Questions — the registry holds only fictional Kalder data with no
sensitive information, so unauthenticated remote access is an acceptable
risk profile for this build. Revisit if the data sensitivity changes.

## Tools

Seven MCP tools, per ADR-016 Decision 1 and its addenda:

| Tool | Purpose |
| --- | --- |
| `append_claim` | Write a claim (+ optional structured evidence) to the registry |
| `append_ruling` | Insert a review ruling. Append-only — a correction is a new row, never an update |
| `get_claim_status` | Read a claim, its evidence, and its most recent ruling |
| `check_substantiation` | Claim + evidence + evidence standard + deterministic hygiene booleans |
| `classify_claim_risk` | Classify risk (`low`/`medium`/`high`/`prohibited`) with contributing factors |
| `list_claims` | Enumerate claims by type/status/product; slug-first summaries, no evidence payload |
| `delete_claim` | Soft-delete (`record_status → 'deleted'`); evidence and rulings survive |

Plus one read-only HTTP route outside the MCP surface —
`GET /claims/{slug}.json` — which resolves a claim by its slug and returns
`get_claim_status`'s payload shape, CORS-enabled, for agent-readable
product pages.

**`check_substantiation` is deliberately thin.** It returns the evidence
standard and deterministic hygiene checks (`has_evidence_link`,
`has_evidence_date`, `is_expired`, `has_sample_size`,
`platform_lifecycle_status`) but renders **no verdict**. That judgment
belongs to the calling agent, guided by the Skills below. The absence of a
verdict field is the design, not an oversight.

`classify_claim_risk` implements five type-specific rulesets as separate
functions, and returns `risk_factors` — the specific inputs that drove the
classification — rather than a bare label.

## Skills

Both reasoning roles are absorbed by Agent Skills rather than MCP tools —
the thesis ADR-016 tests is *Skills carry reasoning, MCP carries action*.

- **`claim-review`** — procedural: how to conduct a review (retrieve →
  substantiate → hygiene check first → claim-strength check → judge
  sufficiency → approve/reject/escalate → record ruling), including when
  to escalate rather than rule.
- **`claim-taxonomy`** — reference: the five claim types and their evidence
  standards, split into deterministic and judgment fields per type.

Each lives at both `skills/<name>/` (authored source of truth) and
`.claude/skills/<name>/` (Claude Code's project-skill discovery path).
Both copies are required: Claude Code does not discover skills from a
top-level `skills/` directory.

## Claim taxonomy

Five types, each with its own evidence standard, grounded in the FTC Policy
Statement Regarding Advertising Substantiation (1984) — the "reasonable
basis" standard and its claim-strength-relative variant.

| Type | Asserts | Evidence standard turns on |
| --- | --- | --- |
| **Performance** | Own measurable capability | Methodology, sample size, time window, baseline |
| **Comparative** | Measured against a competitor | Head-to-head or third-party benchmark; basis stated |
| **Compliance** | Certification or regulatory conformance | Current valid certificate; expiry tracked |
| **Superlative** | Ranking / "#1" / "best-in-class" | Source, category, date; shortest currency window |
| **Compatibility** | Certified for a named platform at a named version | Certification record, platform + version, component revision, lifecycle phase |

Compliance and Compatibility both assert third-party certification;
they're separated by certifying party (standards body vs. platform vendor).

Deliberately **out of scope for v1**: aspirational/roadmap claims (not
present-fact assertions) and environmental/sustainability claims (a
different regulatory regime). Flag these rather than force-fitting them.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

SDK pinned to `mcp<2` (stable v1.x per ADR-016 Decision 3 — not the v2 beta).

Copy `.env.example` to `.env` and set `SUPABASE_DB_URL` to the **pooler**
connection string (port 6543). The direct connection (port 5432) fails with
IPv6 routing on Supabase — which is why this server uses `psycopg2` against
the pooler rather than the `supabase` Python client. `ANTHROPIC_API_KEY` is
required only for the review-agent harness.

```bash
python3 -c "from server.db.client import init_db; init_db()"  # apply schema.sql
python -m server.seed.seed_claims                             # seed 12 claims + classify
```

## Running

```bash
python -m server.main        # stdio transport, local dev
python -m pytest server/tests -q
```

Railway runs the same entrypoint with `MCP_TRANSPORT=streamable-http`.
Transport is selected at runtime; the deployment uses the SDK's direct
transport path rather than manual Starlette mounting, which has known bugs
across SDK versions.

`stateless_http=True` + `json_response=True` is the transport-layer
expression of ADR-016's explicit-handle pattern: `claim_id` travels as a
plain tool argument, with no hidden session state.

## Data model

`claims` → `evidence_links` (cascade) and `claims` → `review_rulings`
(**no** cascade — rulings deliberately survive a soft-deleted claim, which
is what makes the append-only guarantee hold).

`review_rulings` is append-only by design: inserts only, no updates. A
correction is a superseding row with a later `created_at`.

Two tables are experiment infrastructure rather than product surface, and
no MCP tool reads either: `platform_lifecycle` (populated once, with no
refresh mechanism — rows go stale silently, so treat `retrieved_at` as a
currency bound) and `retest_sessions`.

## The review agent and memory experiment

`server/agents/` holds a Claims Review Agent built on the Managed Agents
API. It connects the live MCP server, reviews a claim by slug, and is
graded against a nine-criterion rubric (`review_rubric.md`) covering
evidence citation, verdict validity, scope accuracy, and slug addressing.

The agent runs in three prompt variants, generated from a single template
by `generate_variants.py` along two independent axes — MEMORY (whether a
persistent cross-session Memory store is mounted) and GUIDANCE (whether
inline reasoning scaffolding is retained):

| Variant | Memory | Guidance |
| --- | --- | --- |
| `memory_on` | ✅ | ✅ |
| `memory_off` | — | ✅ |
| `memory_off_stripped` | — | — |

Generating all three from one template is what makes `git diff` between
them a genuine drift check: anything differing outside the sentinel blocks
was not produced by the generator.

Run logs live in `runs/` and are **gitignored on purpose** — this repo is
public, and run logs capture full tool-call traces and API responses, where
a single unhandled traceback could put a credential into permanent git
history.

`week17/` holds an earlier substantiation adversary: parallel evidence
subagents against an adversarial refuter, iterating to convergence, with a
hand-orchestrated arm instrumented for cost comparison.

## Repo layout

```text
server/
  main.py          MCP server: 7 tools + read-only slug route
  tools/           one module per tool
  db/              schema, client, migrations, cleanup scripts
  agents/          review agent, prompt variants, retest harness
  tests/           115 passing; 9 need a live DB
  seed/            12 Kalder seed claims
skills/            authored Skills (mirrored to .claude/skills/)
docs/              ADR-016 + addenda, investigation reports
week17/            substantiation adversary
```

## A note on provenance

`docs/` contains investigation reports that audit this project's own data
and correct its own earlier numbers — including a residue audit that
identified 51 test-artifact rows contaminating the claims table (since
removed) and reconciled a miscounted evidence-link figure.

That is deliberate. A project about claim substantiation should hold its
own claims to the standard it enforces, and its own review skill would ask
for evidence behind any assertion here. Where a number in these docs was
wrong, the correction is recorded rather than quietly overwritten.
