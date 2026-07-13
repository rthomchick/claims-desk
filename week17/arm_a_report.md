# Arm A Report: Hand-Orchestrated Chain — Instrumented Coord/Work Split

**Run date:** 2026-07-13  
**Claim ID:** da4bdf0a-5b81-4600-a52a-c3daeb35c5bb  
**Orchestration:** Turn-by-turn with full accumulated context (no dynamic workflow; no summarization)  
**Procedure:** Identical to Arm B clean 3/3 — same models, same prompts, same convergence gate  

---

## Claim

| Field | Value |
|-------|-------|
| Text | "The most-deployed cross-product analytics platform in IT service management" |
| Type | Superlative |
| Status (registry) | unverified |
| Risk class | prohibited |
| Risk factor | no source named for ranking/recognition claim |
| Submitted evidence | 0 items |
| Evidence standard | Source, category, date — continuous re-substantiation (FTC guidance for ranking claims) |

---

## Phase 2 — Evidence Gathering (3 Haiku agents, parallel)

All 3 agents succeeded on the first attempt (no retries needed).

### source_existence
- **5 evidence items** (all moderate/weak)
- **8 limitations**
- Key finding: No authoritative third-party source measures "most-deployed cross-product analytics platform in ITSM" with quantitative data. Gartner ITSM MQ retired 2023; current Market Guide explicitly does not rank vendors. "Cross-product analytics" not a standardized category in any analyst framework.
- Tool calls: 14

### recency_and_currency
- **8 evidence items** (strong market-share data, no claim-specific validation)
- **7 limitations**
- Key finding: ServiceNow commands 44.4% ITSM market share (AppsRunTheWorld, July 2025). Most recent complete data is ~1 year stale as of July 2026. Competitive landscape shifted with OpenTelemetry. No 2026 deployment reports exist.
- Tool calls: 7

### competitive_landscape
- **7 evidence items** (some strong for broad ITSM leadership)
- **6 limitations**
- Key finding: ServiceNow leads broad ITSM market (44.4% share, 85% Fortune 500, 8,800+ customers). Gartner MQ retired 2023. No competitor explicitly contradicts the claim but also no deployment count data. "Cross-product analytics" scope ambiguous.
- Tool calls: 10

---

## Phase 3 — Adversarial Loop (converged after Round 2)

### Round 1

**Adversary (Opus):** 3 new critical attacks raised
| Severity | Target | Attack |
|----------|--------|--------|
| CRITICAL | source_existence | No authoritative source measures the exact claimed category with quantitative deployment data — fatal for an unsourced superlative |
| CRITICAL | source_existence | "Cross-product analytics platform" is not a standardized category in any analyst framework (Gartner/Forrester/IDC) — claimant appears to have invented the category |
| CRITICAL | methodology | Superlative axis is "most-deployed" (deployment count) but ALL evidence measures revenue share, customer counts, or subjective ratings — the evidence does not measure the claimed quantity |
| MAJOR | comparison_baseline | Evidence covers broad ITSM market, not the analytics sub-segment; competitors in properly-scoped comparison never enumerated |
| MAJOR | methodology | Category ambiguity ("cross-product" = multi-module within suite vs. cross-platform IT-ops) implies different comparison sets, making superlative unfalsifiable |
| MAJOR | time_window | Data ~1 year stale (July 2025); no 2026 reports; landscape shifted via OpenTelemetry |
| MAJOR | sample_size | Gartner Peer Insights sample = 73 reviews — far too small for industry-wide deployment superlative; sentiment ≠ deployment count |
| MINOR | source_existence | Gartner ITSM Magic Quadrant retired 2023; current Market Guide explicitly declines to rank vendors |

Adversary verdict_assessment: `not_substantiated`

**Defender (Haiku):** 2 critical attacks survived
- Attack 1 (no authoritative source): `survived`
- Attack 2 (undefined category): `survived`
- All others: `weakened`

Defender verdict: `not_substantiated`

### Round 2

**Adversary (Opus):** **0 new critical attacks** → convergence triggered
- Carried all 8 R1 attacks forward plus 2 incremental (major: AppsRunTheWorld methodology; minor: plurality not majority)
- new_critical_attacks = `[]` — adversary exhausted

Adversary verdict_assessment: `not_substantiated`

**Defender (Haiku):** 4 attacks survived
- No named authoritative source for exact category (survived)
- "Cross-product analytics platform" not a standardized analyst category (survived)
- Evidence measures revenue share/customer counts, not deployment counts (survived)
- Evidence covers broad ITSM market, not cross-product analytics sub-segment (survived)
- All MAJOR/MINOR attacks: `weakened`

Defender verdict: `partially` (oscillated up from R1's `not_substantiated`)

**Convergence:** adversary R2 `new_critical_attacks = []` → loop terminates. stop_reason = `converged`. rounds_run = 2.

---

## Phase 4 — Synthesis (Opus)

**FINAL VERDICT: `not_substantiated`**

Synthesis overrode defender R2's `partially` verdict, applying the evidence standard (Source, Category, Date) rigorously.

### Surviving Evidence
1. ServiceNow holds ~44.4% ITSM market share (2024), the largest single vendor (robust as market-share fact; not a deployment count, not scoped to cross-product analytics)
2. ServiceNow: ~85% Fortune 500 and 8,800+ customers worldwide (Dec 2025) (robust as customer-footprint fact; not deployment count, not analytics-scoped)
3. Gartner retired ITSM Magic Quadrant in 2023; Feb 2025 Market Guide explicitly does not rank vendors (robust fact that removes likely authoritative basis for ranking superlative)
4. ServiceNow offers Performance Analytics with 250+ ITSM KPIs (robust that capability exists; vendor claim, no independent "most-deployed" verification)

### Attacks Withstood
1. General ITSM market leadership premise (evidence robustly confirms ServiceNow is largest ITSM vendor by market share; this premise is the only element surviving intact)

### Attacks That Damaged the Claim
All 9 non-minor attacks materially weakened or defeated the claim; the 4 surviving CRITICAL attacks are listed above (phase 3 defender R2 surviving_attacks). Summary: no source, undefined category, wrong metric (revenue ≠ deployment), wrong population (broad ITSM ≠ cross-product analytics).

### Executive Summary
The claim fails substantiation. Applying the superlative evidence standard rigorously—a valid Source, a defined Category, and current Date, with continuous re-substantiation as FTC guidance requires for ranking claims—the claim fails on all three prongs simultaneously. No authoritative third-party source measures the exact claimed category; "cross-product analytics platform in IT service management" is not a category recognized or tracked by Gartner, Forrester, or IDC (and Gartner's ITSM Magic Quadrant was retired in 2023, with its current Market Guide explicitly declining to rank vendors); and the most recent usable data is July 2025, roughly a year stale against the 2026 review date, in a landscape that has since shifted. All four CRITICAL attacks survived every adversarial round unrebutted, which for a superlative is dispositive.

Most decisively, the superlative axis and the evidence do not match. "Most-deployed" asserts a deployment/unit-count ranking, yet every piece of evidence gathered measures something else—revenue-based market share (44.4%), customer counts (8,800+ customers, 85% of Fortune 500), or subjective review sentiment (G2, PeerSpot, a 73-review Gartner Peer Insights sample). Deployment counts are vendor-proprietary and undisclosed across all vendors, so the claim's own metric is never independently measured for any vendor. Compounding this, the evidence is scoped to the broad ITSM platform market rather than the narrower analytics sub-segment the claim invokes, and "cross-product" is genuinely ambiguous—the two readings imply entirely different comparison sets, leaving the superlative effectively unfalsifiable.

What survives scrutiny is only the general premise that ServiceNow is the single largest ITSM vendor by revenue share and the most widely adopted ITSM platform by customer footprint—robust, well-sourced facts, but ones that establish market leadership in the broad ITSM category, not a first-place deployment ranking in a distinct "cross-product analytics" segment. To rescue the claim, the client would need either (a) a named, current (2026) independent source that measures deployment counts in a defined cross-product-analytics category, or (b) to rewrite the claim to what the evidence actually supports (e.g., "the leading ITSM platform by market share").

---

## Instrumentation

### Work Tokens (per subagent, exact from notification usage fields)

| Phase | Agent | Model | Subagent Tokens | Tool Calls |
|-------|-------|-------|-----------------|------------|
| P1 (Claim Fetch) | direct MCP calls | orchestrator | 0* | 2 |
| P2 Evidence | source_existence | Haiku | 42,898 | 14 |
| P2 Evidence | recency_and_currency | Haiku | 37,799 | 7 |
| P2 Evidence | competitive_landscape | Haiku | 39,899 | 10 |
| P3 Adversary R1 | adversary-r1 | Opus | 44,901 | 0 |
| P3 Defender R1 | defender-r1 | Haiku | 30,364 | 0 |
| P3 Adversary R2 | adversary-r2 | Opus | 37,290 | 0 |
| P3 Defender R2 | defender-r2 | Haiku | 30,340 | 0 |
| P4 Synthesis | synthesis | Opus | 36,780 | 0 |
| **TOTAL WORK** | | | **300,271** | **33** |

*Phase 1 was executed as direct MCP calls by the orchestrator (not a subagent). This is a structural difference from Arm B (which used a subagent for claim fetch, ~10-15k additional subagent tokens). Net effect: Arm A work tokens are slightly lower on Phase 1, offset by equivalent context fed into the orchestrator's CT1 response.

### Coordination Tokens — Full-Cost Basis (a)

Estimates based on accumulated conversation history analysis. System prompt (~13,000 tokens) + deferred tools system reminder (~5,000 tokens) = ~18,000 constant overhead. The workflow file read (7,000 tokens) and MCP results add to CT1. Agent prompts are orchestrator output (300-5,700 tokens per spawn, growing as evidence summary and attack lists accumulate).

| CT | Turn description | Input (est.) | Output (est.) | Full-cost total |
|----|-----------------|--------------|---------------|-----------------|
| CT1 | Read workflow + MCP claim fetch + spawn 3 evidence agents | ~18,500 | ~14,000 | ~32,500 |
| CT2 | After recency_currency notification | ~32,250 | ~100 | ~32,350 |
| CT3 | After competitive_landscape notification | ~33,650 | ~100 | ~33,750 |
| CT4 | After source_existence — spawn adversary R1 (with full evidence summary) | ~35,250 | ~4,550 | ~39,800 |
| CT5 | After adversary R1 — spawn defender R1 (with full attacks + evidence) | ~41,500 | ~5,000 | ~46,500 |
| CT6 | After defender R1 — check convergence + spawn adversary R2 | ~48,500 | ~6,100 | ~54,600 |
| CT7 | After adversary R2 (converge flag noted) — spawn defender R2 | ~55,700 | ~6,100 | ~61,800 |
| CT8 | After defender R2 — spawn synthesis (with full 2-round context) | ~64,100 | ~5,000 | ~69,100 |
| CT9 | After synthesis — compile report + commit | ~71,600 | ~3,000 | ~74,600 |
| **TOTAL COORD** | | **~401,050** | **~44,050** | **~445,100** |

### Coordination Tokens — Raw Input Re-Sent Per Turn (b)

This is the true orchestration tax: tokens fed into each coordination turn's context window, whether or not they hit the cache.

```
CT1:  18,500  (baseline: system prompt + initial user spec)
CT2:  32,250  (+13,750: CT1 output + tool results including 7k workflow file)
CT3:  33,650  (+1,400:  recency_currency result + CT2 response)
CT4:  35,250  (+1,600:  competitive + source_existence results + CT3 response)
CT5:  41,500  (+6,250:  adversary R1 prompt output + notification result)
CT6:  48,500  (+7,000:  defender R1 prompt output + notification result)
CT7:  55,700  (+7,200:  adversary R2 prompt output + notification result)
CT8:  64,100  (+8,400:  defender R2 prompt output + notification result)
CT9:  71,600  (+7,500:  synthesis prompt output + notification result)

Accumulated orchestration tax (CT9 - CT1): +53,100 tokens
```

Growth is driven by two compounding forces:
1. Agent prompts: each spawn includes the full accumulated evidence summary (stays constant after P2) plus the growing attack list (expands each adversarial round)
2. Agent results: each notification result (1,000-2,200 tokens) becomes permanent context

The raw-input-resent series for Arm B is **flat/zero by construction** — the workflow engine carries no model context overhead. Arm A's per-turn series shows the characteristic "staircase" of plan-in-context orchestration, where each adversarial round adds ~6,000-8,500 tokens to the already-growing window.

### Totals Summary

| Component | Arm A (hand-orchestrated) | Arm B (workflow) | Delta |
|-----------|--------------------------|-------------------|-------|
| Work tokens (subagents) | 300,271 | ~305,000 (est.)* | −4,729 (~1.5%) |
| Coordination tokens full-cost | ~445,100 | 0 (workflow engine) | +445,100 |
| Coordination raw-input-resent | ~401,050 | 0 | +401,050 |
| Grand total (work + coord full-cost) | ~745,371 | ~305,000 | **+440,371 (+144%)** |

*Arm B work token estimate includes ~12k for claim-fetch subagent (not incurred in Arm A's direct MCP path).

### Wall-Clock Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| P1 Claim Fetch | ~5s | Direct MCP calls |
| P2 Evidence | ~140s | Parallel; limited by source_existence at 138s |
| P3 Round 1 | ~90s | adversary R1 (37s) + defender R1 (52s) sequential |
| P3 Round 2 | ~83s | adversary R2 (24s) + defender R2 (59s) sequential |
| P4 Synthesis | ~70s | |
| Coordination overhead | ~60s | Turn-by-turn response latency across 9 CT turns |
| **Total wall-clock** | **~448s (~7.5 min)** | |

Arm B wall-clock would be similar for work phases but with no coordination latency overhead; actual workflow engine overhead is <1s per phase boundary.

---

## Key Findings

1. **Work tokens match closely:** Arm A work tokens (300,271) are within ~1.5% of expected Arm B work tokens (~305k), confirming the identical procedure produced comparable subagent results.

2. **Coordination overhead is substantial:** Arm A accumulated ~445k coordination tokens (full-cost) vs. 0 for Arm B's workflow engine. This is a **144% total overhead** — plan-in-context orchestration costs more than the work itself.

3. **The orchestration tax curve is real and measurable:** Raw input re-sent grows from 18,500 tokens (CT1) to 71,600 tokens (CT9) — a 3.9× increase over the run. Each adversarial round adds ~6,000-8,500 tokens to the already-growing window. A 3-round run would have added another ~8,000 tokens (estimated CT10 ~80k).

4. **The growth is driven by agent prompts, not just results:** My output tokens grow each turn because I must re-serialize the full evidence summary + accumulated attack list into each new agent's prompt. This is the "manual" version of what the workflow script's variable references do automatically without token cost.

5. **Verdict consistency:** Both arms reached `not_substantiated`. The adversarial procedure converged in 2 rounds on adversary exhaustion, consistent with the claim having a saturated attack surface (5 independently fatal deficiencies, no new critical angles after R1).

6. **Synthesis override is correct:** The defender's R2 `partially` verdict was based on inferential reasoning (market leader in ITSM implies most-deployed analytics) that the synthesis agent correctly rejected under the rigorous superlative evidence standard requiring Source + Category + Date.
