# ADR-016: Claims Desk Capability Surface — MCP vs. Agent Skills

**Status:** Accepted
**Author:** Richard Thomchick
**Date:** 2026-07-10
**Repo:** `claims-desk` (monorepo; see Decision 5)

---

## Context

The Claims Desk is a marketing claims governance service: a registry of claims with substantiation status, evidence links, expiry dates, and risk classification, callable by any agent that drafts, reviews, or publishes marketing content. Week 16 builds its capability surface — a Python MCP server and two Agent Skills. This ADR records the architectural decisions governing that build, made against the MCP `2026-07-28` release candidate (locked May 21, 2026; final spec ships July 28, 2026) and the Agent Skills open standard.

This is a greenfield build. The registry is seeded with claims for Kalder products (read-only use of the fictional universe). Council-as-a-service is out of scope entirely — withdrawn to a separate private project, no dependency in either direction.

**Thesis under test:** Skills carry reasoning, MCP carries action.

**Downstream consumers this ADR must serve:** Week 17's Substantiation Adversary (pulls test claims, attacks their substantiation), Week 18's Claims Review Agent on Managed Agents (rules on claims, needs cross-session memory of past rulings), Week 19's claims-manifest product page and standalone false-premise eval harness (links to live claim status). All three read from what this week builds; none of their design is finalized here, but their known shape constrains these decisions.

---

## Decision 1: MCP vs. Agent Skills — The Split

**The question:** For each Claims Desk capability, which primitive is the right home?

**The framework:** Two questions determine the split.
- Does the capability require *persistent state, authentication, or a write operation*? → MCP
- Does the capability define *how an agent reasons, what it knows, or how it behaves*? → Skills

**Capability-by-capability assignment:**

| Capability | Assigned to | Rationale |
|---|---|---|
| `append_claim` — add a claim to the registry | MCP | Write to persistent state. Not contestable under the framework. |
| `get_claim_status` — read a claim's substantiation state | MCP | Read of persistent state. Not contestable under the framework. |
| `check_substantiation` — evaluate evidence against a claim's standard | MCP (thin, plus deterministic hygiene checks) | See edge case resolution below. |
| `classify_claim_risk` — assign a risk class to a claim | MCP | See edge case resolution below. |
| How to conduct a claim review (procedural) | Skills | Judgment and sequencing knowledge, not an action with a side effect. |
| Claim-type taxonomy with evidence standards (reference) | Skills | What an agent needs to know, not something it does. |

**Edge case resolution 1 — `classify_claim_risk`:**

The deciding question was whether classification needs to be *consistent across callers* or *contextual to the caller*. Against the three known downstream consumers: Week 17's adversary needs a risk class to calibrate how hard to attack a claim; Week 18's review agent needs a risk class to decide whether to escalate; Week 19's claims manifest needs a risk class to display to an external browsing agent. Three different callers across three different weeks, all needing to agree on what "high risk" means for the same claim. If risk classification lived in the taxonomy Skill instead, each calling agent would re-derive its own judgment from the same reference material, with no guarantee of agreement across calls or model temperature variance — a concrete, nameable failure mode given the committed downstream builds, not a hypothetical one.

**Conclusion: MCP.** One implementation, one answer, queryable by any caller without re-running inference. The tool returns the risk class *plus the factors that drove it* (not a bare label), preserving the calling agent's ability to reason about or escalate on borderline cases rather than treating the verdict as a black box.

This does not violate the thesis so much as sharpen it: the thesis is about where judgment that needs to vary by context lives versus where judgment that needs to stay consistent lives. Risk classification is the second kind, once weighed against actual downstream consumers rather than considered in the abstract.

**Edge case resolution 2 — `check_substantiation`:**

Two positions were weighed:

- *Thin* (return claim + evidence + standard, agent judges): keeps the thesis clean — MCP surfaces facts, Skills apply judgment. Keeps the taxonomy Skill as the single source of truth for "what counts as sufficient," avoiding a second copy of that judgment reimplemented as code in the tool (the same discipline `kalder_data_model.py` enforces as single source of truth across nine corpus documents).
- *Thick* (tool returns a verdict): gives Week 17's adversary a fixed, restartable ground truth to attack rather than a moving target dependent on which agent's reasoning produced the judgment. Also gives a natural enforcement point for FTC-grounded evidence standards as code rather than trusting every calling agent's prose interpretation of the Skill to be consistent.

**Conclusion: thin, with one exception.** The tool returns claim + evidence + standard (thin) *and* runs a small set of deterministic, non-interpretive hygiene checks — evidence link present, expiry date past/not-past, sample-size field populated — as structured booleans alongside the raw material. This is data hygiene, not judgment, and follows the same deterministic-logic-in-code / generative-judgment-in-LLM split already established in the SAFe system (Weeks 8–11). The agent still renders the actual substantiation verdict; the tool doesn't perform judgment a computer shouldn't be trusted to approximate, and doesn't perform arithmetic an agent shouldn't be trusted to get right. The Skill remains sole owner of "what counts as sufficient"; Week 17's adversary gets concrete, structured facts to contest rather than an opaque verdict.

**Net result:** three of four tools land on MCP; one Skill absorbs both remaining reasoning roles (procedure, taxonomy). Worth stating plainly rather than papering over: this week's actual build leans MCP-heavy relative to the thesis's clean 50/50 framing, and the reason is downstream-consumer consistency, not a failure of the thesis. If Weeks 17–18 later reveal that consistency wasn't actually the binding constraint — that contextual judgment would have served better — that is a legitimate thesis-test finding for the journal, not something to retroactively smooth over.

---

## Decision 2: Persistence — Claims Registry Backing Store

**The question:** Where does the registry live?

**Options considered:**

- **Supabase table** — fits existing infrastructure (pooler connection pattern already proven in the SAFe system); claims are naturally relational (claim → evidence links → review rulings), suiting a real schema.
- **Markdown files in the repo** — zero infrastructure, human-readable, diffable; but no query capability, and concurrent writers (Week 17's adversary and Week 18's review agent both writing, possibly in overlapping sessions) risk corruption with no locking story worth building from scratch.
- **SQLite (local file)** — structured and queryable, but incompatible with Week 18: Managed Agents sessions run in Anthropic's sandbox and reach the registry over the network via the MCP proxy. A local file is not reachable from there — not a tradeoff to weigh, a hard incompatibility with a build two weeks out.

**Conclusion: Supabase.** New table(s) for claims, evidence links, and review rulings. Near-zero incremental operational cost given the existing pooler-connection pattern (port 6543, never direct — proven from the SAFe Feature Spec System). Clears both the Week 18 network-reachability constraint and the concurrent-writer constraint that eliminated markdown.

---

## Decision 3: MCP Server Hosting and SDK Version

**The question:** Where does the server run, and against which MCP Python SDK version?

**SDK version:** The Python SDK's stable release (`pip install mcp`, no pin) remains v1.x, supporting the 2025-11-25 spec only. A v2 beta (`mcp==2.0.0b1`) shipped June 29, 2026 with full 2026-07-28 RC support; stable v2.0.0 is targeted for July 27, 2026. **Decision: build on v1.x stable.** The RC's headline benefit — a stateless protocol core removing the need for sticky sessions — doesn't change this week's hosting calculus once Decision 2 lands on Supabase (see below), and v1.x is proven against both target clients (Claude Code, claude.ai) with zero pre-release risk. A one-week build is the wrong place to make an 11-day-old beta a load-bearing dependency for a protocol feature the target clients may not yet exercise. This can be revisited on its own schedule once v2 stabilizes; nothing about the RC deprecates v1.x on July 28 — Anthropic's SDK guidance is explicit that v1.x stays in maintenance mode indefinitely.

**Hosting options considered:**

- **Local with tunnel (e.g., ngrok)** — fastest to stand up, but fragile under the Day 4 requirement: append a claim from one client (Claude Code), read it from another (claude.ai), in one sitting. A tunnel is exactly the kind of dependency that risk applies to; this is marginal even for Day 4 verification, not just the Week 18/19 always-on requirement.
- **Vercel serverless function** — natural fit for stateless MCP-over-HTTP under the RC, but that advantage is moot while building on v1.x, which still carries the session-pinning weakness serverless handles poorly. Would also require externalized persistence, which Decision 2 already provides via Supabase, so this isn't disqualifying — just not differentiating this week.
- **Railway** — existing infrastructure (same account and mental model as Dino), persistent and always-on for the full month, zero new deployment path to learn.

**Conclusion: Railway.** With Supabase handling persistence, hosting is a pure convenience choice rather than a constrained one — Railway wins on being genuinely zero incremental infrastructure for a server that needs to survive three more weeks of downstream builds.

---

## Decision 4: The Claim-Type Taxonomy — Scope and Evidence Standards

**The question:** What claim types does v1 recognize, and what evidence standard attaches to each?

**v1 taxonomy (confirmed):**

| Claim type | Example | Evidence standard |
|---|---|---|
| Performance | "Reduces onboarding time by 40%" | Methodology documented, sample size, time window, baseline named. Substantiation bar scales with claim phrasing strength (FTC: express claims of a support level, e.g. "tests show," require at least that advertised level of substantiation; softer phrasing assumes only a "reasonable basis"). Judgment call — lives in the Skill, not a structured field. |
| Comparative | "Faster than [competitor]" | Head-to-head test or third-party benchmark; comparison basis stated; competitor data current relative to claim date. |
| Compliance | "SOC 2 Type II certified" | Current certificate; expiry tracked. The type where deterministic checks (is the expiry date past?) can carry nearly the entire verdict — judgment's role shrinks to near zero here, unlike the other three types. Worth a journal callout as a concrete instance of the deterministic/judgment split appearing inside a single tool. |
| Superlative | "#1 rated on G2" | Source, category, date. Shortest default expiry window of the four types, grounded in FTC guidance that ranking/recommendation claims (e.g. "#1 selling") require continuous re-substantiation for the duration the claim is made, not just at time of first publication. |

**Explicitly out of scope for v1** (documented in the taxonomy Skill, not silently absent):
- **Aspirational/roadmap claims** ("coming soon," "planned for Q3") — not substantiation claims at all; forcing them through an existing type's evidence standard would misfit. No current build needs this bucket.
- **Environmental/Sustainability claims** — the EU's EmpCo Directive (amending the UCPD) becomes binding September 27, 2026 and specifically targets this claim category, with Germany's transposition (UWG Third Amendment Act) already showing stricter case law in advance of the deadline (same-medium substantiation disclosure, no B2C carve-out ambiguity survives court scrutiny). Deliberately deferred: Kalder is B2B, and the German draft specifically limits enhanced forward-looking-claims scrutiny to B2C communication, narrowing near-term attack-surface probability for Week 17's adversary. Regulatory grounding retained here for future reference if this type is ever built.

**Evidence-standard field split** (resolves the Skill-vs.-structured-field question, echoing Decision 1's thin/thick resolution): deterministic, checkable facts (evidence link present, date fields populated, expiry past/not-past) live as structured registry fields, checked by `check_substantiation`'s hygiene layer. Judgment criteria (is the sample size adequate, is the comparison basis fair, is the source credible) live in the taxonomy Skill as the agent's rendering guide. No claim type is entirely one or the other; the split runs within each type.

**Risk classes:** Single global enum — low / medium / high / prohibited — rather than per-type enums, for the same cross-caller-consistency reason as Decision 1's `classify_claim_risk` resolution: a `prohibited` Superlative claim and a `prohibited` Compliance claim must trigger the same downstream behavior even though they're different claim types. The *inputs* to classification differ by type (for Compliance, "expired" alone may justify `high`; for Superlative, "no source at all" may be `prohibited` while "source exists but category is gerrymandered" is only `medium`) — those four type-specific rulesets live inside `classify_claim_risk`'s MCP implementation, not duplicated in the Skill.

**Grounding:** FTC Policy Statement Regarding Advertising Substantiation (1984, still current doctrine) — the "reasonable basis" doctrine and its claim-strength-relative standard. EU/national regulations (EmpCo, German UWG amendment, French transposition) reviewed and consciously excluded from v1 scope given Kalder's B2B posture; retained as documented context only.

---

## Decision 5: Repo Structure — Per-Build Repos vs. Claims Desk Monorepo

**The question:** Does each week get its own repo, or does the Claims Desk live in one monorepo?

**Options considered:**

- **Per-build repos** — each artifact demos standalone, but the claim schema would need re-declaring in three separate places across Weeks 16–18, and Week 19's claims manifest needs to reference live status from all of them. Real duplication cost for marginal demo-cleanliness gain.
- **Single monorepo including the harness** — Week 19 Build B (the false-premise eval harness) is explicitly designed to be reusable and decoupled from any one project; welding it into the Claims Desk repo undercuts its own stated purpose.
- **Hybrid** — Claims Desk monorepo (Weeks 16–18 + Week 19 Build A) plus a standalone harness repo (Week 19 Build B, created when that build starts).

**Conclusion: hybrid.** One `claims-desk` monorepo now — shared claim types defined once, mirrors the BG Advisor monorepo precedent. The `false-premise-eval` repo is deliberately not scaffolded yet; it gets created in Week 19 when Build B actually starts, since scaffolding it four weeks early serves no purpose and the harness's whole design premise is standing apart from this project.

---

## Summary of Decisions

| # | Decision | Options Considered | Choice | Rationale |
|---|---|---|---|---|
| 1 | MCP vs. Skills split (incl. two edge cases) | Per capability; thin vs. thick tools | 3 of 4 tools → MCP; both Skills as scoped | Cross-caller consistency (3 downstream consumers across 3 weeks) outweighs contextual judgment for both edge cases; thin `check_substantiation` + deterministic hygiene layer keeps the taxonomy Skill sole-sourced |
| 2 | Registry backing store | Supabase / Markdown / SQLite | Supabase | Week 18 Managed Agents network-reachability requirement rules out SQLite; concurrent-writer risk (Adversary + Review Agent) rules out Markdown |
| 3 | Server hosting + SDK version | Local+tunnel / Railway / Vercel; v1.x / v2 beta | Railway; MCP Python SDK v1.x stable | Local+tunnel fails the Day 4 dual-client bar; Vercel's stateless advantage is moot on v1.x; Railway is zero incremental infrastructure. v2 beta is an unnecessary dependency risk for a one-week build |
| 4 | Claim-type taxonomy + evidence standards | v1 scope; Skill vs. structured fields | 4 types (Performance, Comparative, Compliance, Superlative); deterministic/judgment field split within each type | FTC "reasonable basis" doctrine grounds all four; Aspirational and Environmental/Sustainability types explicitly deferred and documented, not silently excluded |
| 5 | Repo structure | Per-build / monorepo / hybrid | Hybrid: `claims-desk` monorepo now, standalone `false-premise-eval` repo in Week 19 | Shared claim types defined once; harness's reusability premise requires it to stand apart, but not before it exists |

---

## Out of Scope

- **Council-as-a-service:** withdrawn to a separate private project; no dependency in either direction. The Claims Desk shares no code, state, or personas with it.
- **Real client claims:** the registry is seeded exclusively with Kalder fictional-product claims plus clearly public real-world claims used as Week 17 test inputs.
- **Legal advice posture:** the Claims Desk surfaces substantiation status; it does not render legal judgments. The taxonomy Skill states this boundary explicitly.
- **Aspirational/roadmap claims and Environmental/Sustainability claims** (v1 taxonomy scope — see Decision 4): documented exclusions, not silent gaps. Candidates for a future v2 taxonomy revision if Week 17's adversary or later Kalder corpus work surfaces a concrete need.
- **EU/national claim-substantiation regulation** (FTC serves as sole grounding source for v1): reviewed during Day 1 spec reading — EmpCo Directive (binding Sept 27, 2026), German UWG amendment and case law (BGH rulings on "klimaneutral" and offsetting claims), French transposition (proposed penalties up to 80% of ad spend) — all specific to environmental/sustainability claims, not a general stricter-substantiation regime. Consciously excluded given Kalder's B2B posture; German draft's B2B carve-out further narrows near-term relevance.

---

## Resolved Open Questions (from Day 1 reading)

- **Does the MCP RC spec require server-side authentication, or is auth optional for development use?** Optional for `stdio` (local; trusts the parent process). Strongly recommended, not strictly required, for remote/Streamable HTTP under OAuth 2.1 — the spec permits unauthenticated remote servers (e.g. context7), but retrofitting OAuth 2.1 later costs more than including it from the first Railway deploy if the registry's data sensitivity ever warrants it.
- **What transport does claude.ai use to connect to MCP servers?** Streamable HTTP (single endpoint, POST for calls, optional GET for an SSE stream). SSE-only transport is deprecated. Confirmed for both local (stdio default) and remote use.
- **Are Skills loaded per-session or per-turn?** Per-turn-matched, client-managed, three-tier progressive disclosure: name + description at startup (~30–100 tokens/skill) → full SKILL.md body loads when a task matches the description (recommended under 5,000 tokens) → reference files/scripts load only during execution. Not explicitly invoked by the calling agent — the host decides when a Skill's description matches the current task.
- **Can a Managed Agents session (Week 18) call an arbitrary remote MCP server, and what does its network access require?** Yes — Managed Agents sessions declare `mcp_servers` (up to 20) directly in the agent definition with `type`, `name`, and `url`; a dedicated credential proxy injects auth server-side, and the sandbox itself never sees tokens. This is the supported, non-gated case (MCP tunnels, for private/non-public servers, are a separate research-preview feature not needed here since the Claims Desk will be a public or auth-gated public endpoint on Railway).

---

## Notes on the MCP 2026-07-28 Release Candidate (context for future ADRs)

Not binding on this week's decisions but relevant to how the server is designed for forward compatibility:

- The RC removes the `initialize` handshake and `Mcp-Session-Id` header entirely — every tool call becomes a single, self-contained request. Cross-call state, if ever needed, is handled via an **explicit handle pattern**: a tool returns an ID (e.g. a `claim_id`, already present in this design) and the model threads it back as an ordinary argument on later calls. This is directly compatible with the registry's existing primary-key design and requires no rework if the server migrates to v2 later.
- Tool `outputSchema` becomes unrestricted under full JSON Schema 2020-12 support (`oneOf`/`anyOf`/`allOf`, `$ref`) — relevant if `check_substantiation`'s structured output ever needs type-specific branching (e.g. Compliance's expiry-date check vs. Superlative's source-currency check) beyond what v1's flat structure requires.
- Tasks graduated from core spec to an optional extension in the RC — not relevant to this week's four-tool, CRUD-shaped server.

---

*This ADR is the Day 2 deliverable for Week 16, completed same-day following Day 1 spec reading. Decisions 2 and 5 were closed first (persistence and repo structure), followed by Decision 3 (hosting and SDK version, contingent on the persistence choice), then Decision 1 (the MCP/Skills split, informed by the RC's stateless-core and JSON-Schema findings), then Decision 4 (taxonomy, informed by FTC substantiation doctrine and a deliberate scope decision on EU/national environmental-claims regulation). Published alongside the repo and Week 16 journal entry.*

---

## Decision 1 Addendum: delete_claim tool (Week 17, 2026-07-13)

**Status:** Accepted
**Date:** 2026-07-13

### What changed

`delete_claim` is added to the MCP capability surface. Also in this commit: `append_claim` write-verification fix and FK constraint confirmation.

### Why the original decision excluded it

Decision 1 (Week 16) excluded a delete tool on the grounds that no planned build required it and that irreversible state mutation introduced risk without compensating benefit within the four-week arc.

### What changed the calculus

During Week 17 Day 3 pre-build, a misuse of `append_claim` as an enumeration mechanism produced a silent failure: the tool returned a claim_id for a row that never persisted. Recovery required direct DB access — not acceptable for a tool surface agents will use autonomously. Without `delete_claim`, any write-tool misuse or seed-data error that does persist has no MCP-layer recovery path.

The `append_claim` silent-failure is itself a separate bug (a tool that returns a claim_id for a row that didn't land violates the tool contract — must error instead); that fix is also in this commit.

### Tool contract

`delete_claim(claim_id: str) -> {deleted: bool, claim_id: str}`

- Accepts claim_id (UUID) only — consistent with all other tools.
- Cascades to evidence rows via FK (`evidence_links_claim_id_fkey`, ON DELETE CASCADE — confirmed live from Week 16 `schema.sql`).
- Returns `{deleted: true, claim_id}` on success.
- Returns explicit not-found error if claim_id doesn't exist — consistent with `get_claim_status` not-found behavior.
- One claim_id per call. No bulk delete.

### Known issue — review_rulings cascade (Week 18 hard prerequisite)

`review_rulings_claim_id_fkey` also has ON DELETE CASCADE in the existing schema, meaning `delete_claim` currently wipes rulings alongside claims — contradicting the audit-trail preservation intent. Documented in `server/tools/delete_claim.py` with a Week 18 flag.

**Must be fixed before the Week 18 review agent writes any rulings.** Fix options: make `claim_id` nullable + `SET NULL` on delete, or soft-delete claims rather than hard-deleting. This is a hard prerequisite for Week 18, not a soft backlog item.

### Also in this commit

- **`append_claim` write verification** (`server/tools/append_claim.py:50-55`): after `conn.commit()`, verifies row existence on the same connection (not a second `get_connection()` — avoids pgBouncer replica-lag race window) before returning `claim_id`. Raises `RuntimeError` if row not found. Tool must either succeed and return a verified ID, or fail and raise.
- **FK constraint confirmed live**: `evidence_links_claim_id_fkey`, `delete_rule = CASCADE`. Already present in `schema.sql` from Week 16; no migration needed.

### Updated Decision 1 capability table

| Capability | Assigned to | Rationale |
|---|---|---|
| `append_claim` — add a claim to the registry | MCP | Write to persistent state. |
| `get_claim_status` — read a claim's substantiation state | MCP | Read of persistent state. |
| `check_substantiation` — evaluate evidence against a claim's standard | MCP (thin + hygiene) | Cross-caller consistency; deterministic hygiene layer. |
| `classify_claim_risk` — assign a risk class to a claim | MCP | Cross-caller consistency. |
| `delete_claim` — remove a claim and its evidence from the registry | MCP | Write (destructive) to persistent state. Added Week 17. |
| How to conduct a claim review (procedural) | Skills | Judgment and sequencing, not a side-effecting action. |
| Claim-type taxonomy with evidence standards (reference) | Skills | What an agent needs to know, not something it does. |