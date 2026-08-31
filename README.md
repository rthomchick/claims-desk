# Claims Desk

Marketing claims governance MCP server. Registry of claims with
substantiation status, evidence links, expiry dates, and risk
classification, callable by any agent that drafts, reviews, or publishes
marketing content.

Architecture and rationale: see `ADR-016` (MCP vs. Agent Skills split,
persistence, hosting, taxonomy, repo structure).

## Status (Week 16, Day 5)

Deployed to Railway at a public HTTPS URL, running Streamable HTTP
(`stateless_http=True`, `json_response=True`). Cross-client state verified:
a claim appended via Claude Code was read back correctly via claude.ai web,
confirming both clients share the same live Supabase-backed registry.
Two Agent Skills authored and progressive-disclosure tested. Week 16 DoD
complete.

**Auth: intentionally not implemented.** Deferred per ADR-016's Resolved
Open Questions — the registry holds only fictional Kalder data with no
sensitive information, so unauthenticated remote access is an acceptable
risk profile for this build. Revisit if the data sensitivity changes.

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
  calling agent's job, guided by the `claim-review` and `claim-taxonomy`
  Skills (see "Skills" below).
- `classify_claim_risk` — five type-specific rulesets (performance,
  comparative, compliance, superlative, compatibility), each a separate
  function in `server/tools/classify_claim_risk.py`. Returns `risk_class` plus
  `risk_factors` (the specific inputs that drove the classification, not
  just the label). Writes the result back to the `claims` row.

## Day 3 verification (live database)

- Schema applied to a live Supabase project via the pooler connection
- All 12 seed claims inserted; confirmed 3-3-3-3 distribution across the
  four claim types that existed as of Day 3 (a fifth, Compatibility, was
  added later — see ADR-016 Decision 4 addendum)
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

## Day 4 verification (Railway deployment + cross-client)

- Deployed to Railway: `https://claims-desk-production-8424.up.railway.app`,
  reachable via `/mcp` (Streamable HTTP)
- MCP Inspector confirmed all four tools live and correctly schema'd
  against the deployed URL before either client was touched
- Claude Code connected as an MCP connector; all four tools visible and
  callable; `append_claim` called with a dedicated connectivity-test claim
  (`product_key: kalder_test`, distinguishable from the real seed set):
  - claim_id: `e1cfbb40-88e1-446a-b293-7e725d139678`
- claude.ai web connected as a custom connector, showed Connected with all
  four tools listed, and successfully called `get_claim_status` on that
  same claim_id — returned the exact claim appended from Claude Code,
  confirming both clients read the same live Supabase-backed state
- Auth explicitly deferred, not silently skipped — see note above

## Skills

Per ADR-016 Decision 1, both reasoning roles are absorbed by Agent Skills
rather than MCP tools. Placed at both `skills/` (authored source of truth)
and `.claude/skills/` (Claude Code's project-skill discovery path — see
Day 5 verification below for why both copies exist):

- `claim-review` — **procedural** skill: how to conduct a claim review
  (retrieve → substantiate → hygiene check first → claim-strength check →
  judge sufficiency → approve/reject/escalate → record ruling)
- `claim-taxonomy` — **reference** skill: the five claim types (Performance,
  Comparative, Compliance, Superlative, Compatibility) and their evidence
  standards, split into deterministic (hygiene-checked) and judgment
  fields per type

## Day 5 verification (Agent Skills, progressive disclosure)

- Both skills placed at `skills/<name>/SKILL.md` (as specified) and
  additionally at `.claude/skills/<name>/SKILL.md` — Claude Code's actual
  project-skill discovery path. As originally specified (top-level `skills/`
  only), Claude Code would not have discovered either skill; this was
  caught and confirmed against a known-working example (`dino-personality`
  in the `dino` project) before proceeding
- Frontmatter validated manually: both `name` fields lowercase-hyphenated
  and matching their folder names, no angle brackets, descriptions state
  both what and when to use each skill, body token counts well under the
  ~5,000-token recommendation (`claim-review` ~1,400 tokens, `claim-taxonomy`
  ~970 tokens, both rough chars/4 estimates). No `anthropics/skills`
  validator package found on npm under any tried name — not readily
  available, so not stood up per the build prompt's own guidance
- Progressive disclosure tested live, five steps, in this session:
  1. Before either skill was discovered by the harness, `Skill` calls to
     both returned `Unknown skill` — confirms tier-0 (nothing loaded)
  2. Reading a file under `claims-desk/.claude/skills/` triggered harness
     discovery (a `<system-reminder>` announcing both skills, name +
     description only, ~30-100 tokens each) — this is tier 1. Notably,
     discovery was triggered by file access under the project's
     `.claude/skills` path, not purely by session start — a session
     restart alone was necessary but not sufficient
  3. A generic, unrelated query ("good Python variable naming") produced
     a fully generic answer with no Claims-Desk-specific content —
     confirms neither skill's full body loaded for an unmatched query
  4. Invoking `claim-review` on the Day 4 test claim
     (`e1cfbb40-88e1-446a-b293-7e725d139678`) loaded its full SKILL.md body
     (tier 2) and the resulting review visibly followed the skill's exact
     7-step workflow, explicitly applying its hygiene-first rule
     (`has_evidence_link: false` → reject, no evidence to evaluate) —
     ruled **REJECT**
  5. Invoking `claim-taxonomy` on "what evidence does a Superlative claim
     need?" loaded its full body and answered using the taxonomy's exact
     four-type framework and field-level standard (source, category, date;
     shortest currency window; FTC grounding) — not generic knowledge
  6. Invoking both together (classify the same test claim's type and check
     its evidence standard) loaded both bodies simultaneously; the answer
     visibly combined `claim-taxonomy`'s type definition/evidence standard
     with `claim-review`'s procedural hygiene-first decision, converging on
     one ruling citing both — confirmed skills compose rather than
     override each other
