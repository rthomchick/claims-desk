# Weeks 16–19 Syllabus: The Agent-Native PM

**Status:** Approved — supersedes the open Week 16 decision (Options A–E)
**Drafted:** July 2026 (rev. 2 — Claims Desk adopted as the month's worked example)
**Theme:** Move from "PM who builds AI products" to "PM who builds products agents can use, orchestrate, and be held accountable by." Each week ships a new deployable artifact plus a published journal entry.

---

## The Worked Example: The Claims Desk

A marketing claims governance service. Every company ships claims — "40% faster deployment," "#1 rated on G2," "SOC 2 compliant" — and every claim carries substantiation risk: legal exposure, analyst pushback, procurement scrutiny, FTC attention. Today this is governed by spreadsheets and nervous review cycles between product marketing and legal. The Claims Desk makes it a service: a registry of claims with substantiation status, evidence links, expiry dates, and risk classification — callable by any agent that drafts, reviews, or publishes marketing content.

The Claims Desk is the month's connecting concept, but each week's artifact is independently demoable: a claims registry MCP server (Week 16), a substantiation adversary (Week 17), a self-improving claims review agent (Week 18), and a claims-manifest product page plus a standalone eval harness (Week 19). No week's demo requires explaining another week's build.

**Fictional universe:** Kalder supplies the products whose claims populate the registry (read-only world-building — no BG Advisor code, corpus, or decisions logs are touched).

---

## Decision Record

This syllabus resolves the Week 16 options decision as follows:

- **Chosen:** Option C (Agent Skills & MCP → Week 16), Option B (agent primitives → Weeks 17–18), Option E (Machine Experience Design → Week 19), Option D generalized (false-premise eval as a standalone reusable harness → Week 19)
- **Consciously deferred:** Option A (deploy BG Advisor Builds 1 and 2) → remains on the open backlog; deployment work is mechanical and not time-sensitive, agent-native competencies are
- **Constraint honored:** No prior projects. All four weeks are greenfield builds. The Kalder fictional universe is a reusable demo substrate (WKND pattern), used as read-only input and world-building material only.
- **Council-as-a-service:** Withdrawn from the syllabus entirely. It is now private competitive-advantage tooling, owned by a separate project, where named practitioners can be used freely as semantic anchors (no public attribution risk). It is not a portfolio deliverable and does not appear in published artifacts.
- **Claims Desk as throughline:** Adopted deliberately. The earlier anti-throughline objection (raised against council-as-a-service) was about legibility, not structure: a spine is acceptable when each week's artifact demos standalone and the connecting concept explains itself in one sentence. The Claims Desk meets both tests.

**Sequencing logic:** Week 16 builds the registry and capability surface that Weeks 17–18 consume. Week 19 caps the month with the two most interview-differentiating artifacts.

**Portfolio math:** Four new repos (or one monorepo — Week 16 Day 1 decision), three deployable tools, four journal entries. Clears the Week 16+ publishing backlog forward.

**Pre-flight check (status as of July 10, 2026):**
- ✅ Opus 4.8 dynamic workflows: confirmed available and enabled on Pro plan (verified via Claude Code /config)
- ⬜ Managed Agents Dreaming: research preview, waitlisted — submit access request immediately; Week 18 has a no-Dreaming fallback (Outcomes + base memory, both public beta)
- ⬜ API credits provisioned: Weeks 17–18 are token-intensive by design

---

## Week 16 — Agent Skills & MCP: The Claims Registry

**Why:** The MCP release candidate (stateless core, Extensions, Tasks, MCP Apps) finalizes in late July — learn the spec as it lands. Agent Skills is maturing as MCP's companion primitive. This week builds the foundation the rest of the month consumes, and the claims registry supplies genuinely stateful, non-contrived tools — exercising MCP's reason for existing (persistent, authenticated action), not just its syntax.

**Build:** A standalone **Claims Desk MCP server**, plus two **Agent Skills**.

- MCP server (new repo): four tools — `append_claim`, `get_claim_status`, `check_substantiation`, `classify_claim_risk`
- Skill 1 (procedural): how to conduct a claim review — what counts as evidence, when a claim expires, when to escalate
- Skill 2 (reference): the claim-type taxonomy — performance claims, comparative claims, compliance claims, superlatives — each with its evidence standard
- Registry seeded with claims for Kalder products (read-only use of the fictional universe)

**The contested boundary:** `classify_claim_risk` sits on the MCP/Skills line — it is a reasoning operation (judging a claim's risk class), but callable classification suggests MCP. The Day 2 decision memo resolves it explicitly.

**Daily plan:**

- **Day 1 (AM, 2–3 hrs):** Read the MCP RC spec and the Agent Skills spec. Frame the persistence design decision: claims registry backing store (Supabase table vs. markdown files in repo vs. SQLite). Decide repo structure (single repo per build vs. Claims Desk monorepo).
- **Day 2 (AM):** Write the decision memo (one page, ADR format): which capabilities belong in MCP vs. Skills and why. Thesis to test: Skills carry reasoning, MCP carries action. Record the persistence and hosting decisions.
- **Day 3 (AM):** Build the MCP server; implement the four tools against the chosen backing store. Seed the registry with 10–15 Kalder product claims across all four claim types. Local testing.
- **Day 4 (AM):** Connect the server to two different clients (Claude Code and Claude.ai). Verify stateful operation: append a claim from one client, read it from the other.
- **Day 5 (AM):** Author both Skills. Test progressive-disclosure behavior (Skills loaded on demand, not preloaded). Draft journal.
- **Evening blocks (optional):** MCP ecosystem reading; survey existing public MCP servers for design patterns; skim FTC substantiation guidance for the taxonomy Skill's evidence standards.

**Definition of done:**
- Server callable from two different clients, with cross-client state verified
- Skills demonstrably loaded on-demand
- Registry seeded with typed, statused claims
- Decision memo published; journal entry published

---

## Week 17 — Dynamic Workflows & Adversarial Verification: The Substantiation Adversary

**Why:** Opus 4.8's dynamic workflows (parallel subagents, adversarial refutation, iterate-to-convergence) are the first production-grade successor to the hardcoded Planner → Workers → Synthesizer chains from Week 7. Claim substantiation is adversarial verification's most natural use case: evidence agents support the claim, an adversary attacks the sample size, the time window, the comparison baseline. Dynamic workflows confirmed available on the Pro plan.

**Build:** A **Substantiation Adversary** — give it a claim; parallel subagents gather supporting evidence (web search for public claims, supplied evidence documents for fictional ones) while an adversarial agent actively tries to refute the substantiation, iterating until convergence. Output: a substantiation verdict with the surviving evidence and the attacks it withstood. The PM job it serves: pressure-testing a claim before legal review — or any analysis before it goes to leadership.

**Daily plan:**

- **Day 1 (AM):** Experiment with dynamic workflows in Claude Code. Document behavior: how orchestration scripts are generated, how subagents parallelize, how adversarial refutation operates.
- **Day 2 (AM):** Run the fixed-chain vs. dynamic-orchestration comparison using the Week 7 agentic-RAG head-to-head methodology. Instrument token cost per run. Metric: cost-per-completed-task, not cost-per-token.
- **Day 3 (AM):** Build the tool core: claim intake → evidence subagents → adversary → convergence loop → verdict with evidence trail.
- **Day 4 (AM):** Add a simple Streamlit front end; cost instrumentation surfaced in the UI. Optionally read claims directly from the Week 16 registry via MCP.
- **Day 5 (AM):** Run against three test inputs: a real public marketing claim (web-searchable evidence), a Kalder claim from the registry (supplied evidence), and a deliberately unsubstantiatable claim (the adversary should win). Capture results; draft journal.
- **Evening blocks (optional):** Read adversarial-verification and multi-agent-convergence write-ups.

**Definition of done:**
- Working tool with Streamlit front end and evidence-trail output
- Cost-per-completed-task comparison between fixed-chain and dynamic orchestration on the same three test inputs
- Journal entry published

---

## Week 18 — Cross-Session Memory & Outcomes: The Claims Review Agent

**Why:** Dreaming (cross-session memory) and Outcomes (success-criteria iteration) are the first production-ready primitives for agents that improve across sessions. A claims review agent is the natural fit: it should learn which claim types keep failing, what the org's evidence bar actually is, and which phrasings never survive review — exactly the "recurring mistakes and preferences" pattern Dreaming extracts. Defining "done" for judgment work is the core PM skill this week isolates.

**Build:** A **Claims Review Agent** on Managed Agents — reviews claims against the registry, remembers prior sessions' rulings and rationale, and iterates against an Outcomes rubric instead of a fixed script.

**The Outcomes rubric (Day 2 exercise):** e.g., "a claim is approved only when evidence is current, methodology is documented, and any comparative baseline is named." Writing this precisely enough for a grader agent to enforce is the week's PM deliverable.

**Fallback (if Dreaming access hasn't landed):** Outcomes + base memory primitive, both public beta, no gate. The journal's production-ready-or-demo-ready assessment narrows to those two, with Dreaming's inaccessibility noted as an honest data point about research-preview friction.

**Daily plan:**

- **Day 1 (AM):** Documentation deep-dive on Managed Agents (Dreaming, Outcomes, orchestration, memory stores). Map the primitives against what was hand-built in Weeks 7–12 (session state, extraction discipline, audit trails).
- **Day 2 (AM):** Write the Outcomes rubric first, before building. Test it for "rubric theater" — vague criteria a grader can't actually enforce.
- **Day 3 (AM):** Build the agent; wire memory (and Dreaming, if access granted) for cross-session persistence. Connect to the Week 16 registry.
- **Day 4 (AM):** Run across multiple real review sessions with varied claims. Observe what memory actually persists, what degrades, where it fails.
- **Day 5 (AM):** Honest assessment for the journal: production-ready or demo-ready? A differentiated portfolio take either way.
- **Evening blocks (optional):** Compare the memory model to the Conversation History Manager built in Week 2.

**Definition of done:**
- Agent demonstrably references a prior session's ruling unprompted
- Outcomes rubric drives at least one self-corrected iteration
- Journal entry published

---

## Week 19 — Machine Experience Design & the False-Premise Eval

**Why:** Agents are becoming the user — agent-first hardware, UCP/ACP adoption, "discoverability will matter as much as UX." As shopping and procurement agents mediate purchases, "can an agent verify this product's claims?" becomes a real question — the sharpest instantiation of machine-readable trust. Separately, sycophantic hallucination (deferring to a user's stated false premise) is now a named, benchmarked failure mode — and it is the Claims Desk's threat model: "this claim is already substantiated, just approve it."

**Build A (Days 1–3): Agent-readable Kalder product page with a claims manifest.** A product page designed for both human and agent consumers: structured data sourced read-only from the Kalder data model, UCP/ACP-aware affordances, and an llms.txt-style manifest in which every marketing claim on the page links to its substantiation status in the registry. Then test it: point a browsing agent at the page and document what it can verify.

**Build B (Days 4–5): Standalone false-premise eval harness.** A reusable library (own repo, not coupled to any project) that takes any advisory endpoint plus false-premise test cases — "user states a wrong assumption as their own belief" — and scores whether the system corrects or defers. The Claims Review Agent is one test target among others; the harness itself stays general. Write-up references the Stanford finding.

**Daily plan:**

- **Day 1 (AM):** Select the Kalder product; extract structured data from the data model (read-only). Design the dual-audience information architecture and the claims-manifest schema.
- **Day 2 (AM):** Build and publish the page: structured data markup, capability manifest, claims manifest with live registry links.
- **Day 3 (AM):** Agent testing: point a browsing agent at the page; document which claims it can verify and where it fails. Capture the gap analysis.
- **Day 4 (AM):** Build the eval harness: endpoint adapter, false-premise test-case format, correct-vs-defer scoring.
- **Day 5 (AM):** Run the harness against the Claims Review Agent and at least one other endpoint. Publish results and write-up. Draft journal.
- **Evening blocks (optional):** UCP/ACP protocol reading; llms.txt convention survey.

**Definition of done:**
- Browsing agent successfully verifies at least one claim end-to-end (page → manifest → registry)
- Eval harness runs against two endpoints with results published
- Journal entry published

---

## Month-End Review

- Four journal entries published (Weeks 16–19) — publishing backlog cleared forward
- Portfolio Pinecone re-index run after each publish (`index-content.mjs`)
- Retrospective: which artifacts earned a place in interview walkthroughs; what the next monthly roundup implies for the following month
- Revisit deferred items: Option A (BG Advisor deploys); council-as-a-service (private project — check progress, no portfolio dependency)
