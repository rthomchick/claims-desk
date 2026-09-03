export const meta = {
  name: 'arm-b-adversarial-substantiation-v2',
  description: 'Arm B: plan-in-script arm of Day 2 cost comparison (fixed convergence guard, 3/3 evidence agents)',
  phases: [
    { title: 'Claim Fetch', detail: 'Fetch claim da4bdf0a live from Claims Desk MCP via subagent' },
    { title: 'Evidence Gathering', detail: '3 parallel Haiku agents: source_existence, recency_and_currency, competitive_landscape' },
    { title: 'Adversarial Loop', detail: 'Opus adversary + Haiku defender, max 3 rounds, structural convergence guard' },
    { title: 'Synthesis', detail: 'Opus final report: verdict, evidence, attack inventory, instrumentation' },
  ],
}

const CLAIM_ID = 'da4bdf0a-5b81-4600-a52a-c3daeb35c5bb'

// ── Schemas ────────────────────────────────────────────────────────────────

const CLAIM_FETCH_SCHEMA = {
  type: 'object',
  required: ['claim_text', 'claim_type', 'verification', 'evidence_standard'],
  properties: {
    claim_text: { type: 'string' },
    claim_type: { type: 'string' },
    verification: { type: 'string' },
    evidence_standard: { type: 'string' },
    submitted_evidence: { type: 'array', items: { type: 'string' } },
    mcp_notes: { type: 'string' },
  },
}

const EVIDENCE_SCHEMA = {
  type: 'object',
  required: ['angle', 'evidence_items', 'limitations', 'tool_calls_made'],
  properties: {
    angle: { type: 'string' },
    evidence_items: {
      type: 'array',
      items: {
        type: 'object',
        required: ['finding', 'strength', 'source'],
        properties: {
          finding: { type: 'string' },
          strength: { enum: ['strong', 'moderate', 'weak'] },
          source: { type: 'string' },
          date_published: { type: 'string' },
        },
      },
    },
    limitations: { type: 'array', items: { type: 'string' } },
    tool_calls_made: { type: 'number' },
  },
}

const ADVERSARY_SCHEMA = {
  type: 'object',
  required: ['all_attacks', 'new_critical_attacks', 'verdict_assessment', 'tool_calls_made'],
  properties: {
    all_attacks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['attack', 'target', 'severity'],
        properties: {
          attack: { type: 'string' },
          target: { enum: ['source_existence', 'sample_size', 'time_window', 'comparison_baseline', 'methodology', 'other'] },
          severity: { enum: ['critical', 'major', 'minor'] },
        },
      },
    },
    new_critical_attacks: {
      type: 'array',
      description: 'Critical-severity attacks not raised in any prior round — MUST be empty array [] if none are new',
      items: { type: 'string' },
    },
    verdict_assessment: { enum: ['substantiated', 'partially', 'not_substantiated'] },
    reasoning: { type: 'string' },
    tool_calls_made: { type: 'number' },
  },
}

const DEFENDER_SCHEMA = {
  type: 'object',
  required: ['rebuttals', 'surviving_attacks', 'current_verdict', 'tool_calls_made'],
  properties: {
    rebuttals: {
      type: 'array',
      items: {
        type: 'object',
        required: ['attack_addressed', 'rebuttal', 'outcome'],
        properties: {
          attack_addressed: { type: 'string' },
          rebuttal: { type: 'string' },
          outcome: { enum: ['neutralized', 'weakened', 'survived'] },
        },
      },
    },
    surviving_attacks: { type: 'array', items: { type: 'string' } },
    current_verdict: { enum: ['substantiated', 'partially', 'not_substantiated'] },
    reasoning: { type: 'string' },
    tool_calls_made: { type: 'number' },
  },
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  required: ['verdict', 'surviving_evidence', 'attacks_withstood', 'attacks_damaged', 'executive_summary'],
  properties: {
    verdict: { enum: ['substantiated', 'partially', 'not_substantiated'] },
    surviving_evidence: { type: 'array', items: { type: 'string' } },
    attacks_withstood: { type: 'array', items: { type: 'string' } },
    attacks_damaged: { type: 'array', items: { type: 'string' } },
    executive_summary: { type: 'string' },
  },
}

// ── Phase 1: Claim Fetch ───────────────────────────────────────────────────

phase('Claim Fetch')
log(`Fetching claim ${CLAIM_ID} from Claims Desk MCP...`)

const t0 = budget.spent()
const claimData = await agent(
  `Fetch live data for a marketing claim from the Claims Desk MCP registry. This is READ-ONLY — do NOT modify any data.

Claim ID: ${CLAIM_ID}

Step 1: Use ToolSearch to load these two tools by running ToolSearch with query:
  select:mcp__6db17c1d-acf8-4170-bc36-12d3ce50766a__get_claim_status,mcp__6db17c1d-acf8-4170-bc36-12d3ce50766a__check_substantiation

Step 2: Call get_claim_status with claim_id="${CLAIM_ID}" and note the full result.

Step 3: Call check_substantiation with claim_id="${CLAIM_ID}" and note the full result.

Return structured data with:
- claim_text: the actual marketing claim text from the registry
- claim_type: the claim type (Superlative, Performance, Comparative, or Compliance)
- verification: the verification verdict from get_claim_status
- evidence_standard: the evidence standard the registry applies to this claim type (from check_substantiation)
- submitted_evidence: list of any evidence items already submitted (from either tool result), as strings
- mcp_notes: any other notable data such as assigned adjudicator, risk level, etc.`,
  { label: 'claim-fetch', phase: 'Claim Fetch', schema: CLAIM_FETCH_SCHEMA }
)
const fetchTokens = budget.spent() - t0

log(`Claim: "${claimData.claim_text}"`)
log(`Type: ${claimData.claim_type} | Verification: ${claimData.verification}`)
log(`Evidence standard: ${claimData.evidence_standard}`)
log(`Claim fetch: ~${fetchTokens} output tokens`)

// ── Phase 2: Evidence Gathering (initial attempt + retry guard) ─────────────

phase('Evidence Gathering')
log('Launching 3 parallel Haiku evidence agents (initial attempt)...')

const ANGLES = [
  {
    angle: 'source_existence',
    task: `Find any authoritative third-party source that ranks or measures what this claim implies. For a superlative claim with no named source, source existence is the primary attack surface. Search for: (1) the specific ranking or measurement system the claim implies, (2) who produces such rankings in this industry, (3) whether this company appears in any authoritative ranking, study, or survey, (4) whether any industry association, regulator, or major publication has independently verified a superlative position for this company. If no authoritative source exists, that is a critical finding — document it explicitly.`,
  },
  {
    angle: 'recency_and_currency',
    task: `Verify that any evidence supporting this claim is still current. Superlative claims expire when conditions change. Search for: (1) when the most recent relevant industry data was published, (2) any news in the last 12-18 months that would invalidate the superlative, (3) whether the market or competitive landscape has recently shifted, (4) any regulatory changes or consumer-report updates affecting the claim's validity. Report the most recent publication dates you find for any relevant sources.`,
  },
  {
    angle: 'competitive_landscape',
    task: `Assess whether the comparison basis holds. A superlative claim requires implicit comparison against ALL competitors. Search for: (1) the main competitors in this space, (2) any independent head-to-head comparisons or third-party ratings, (3) whether any competitor makes a directly contradicting claim, (4) what metrics are commonly used to compare offerings in this category, (5) whether any competitor holds a ranking or certification that would challenge this company's superlative position.`,
  },
]

const evidencePrompt = (a, isRetry) => {
  const retryPreamble = isRetry
    ? `MANDATORY: You are on a RETRY because a prior agent completed without calling the StructuredOutput tool. You MUST call StructuredOutput before finishing — do not end your response without it. Return whatever you found, even if your evidence list is limited. Calling StructuredOutput with partial results is required; not calling it is not acceptable.

`
    : ''
  return `${retryPreamble}You are an evidence researcher for a marketing claim substantiation review.

CLAIM: "${claimData.claim_text}"
CLAIM TYPE: ${claimData.claim_type}
EVIDENCE STANDARD FROM REGISTRY: ${claimData.evidence_standard}

YOUR ANGLE: ${a.angle}
YOUR TASK: ${a.task}

INSTRUCTIONS:
1. Use ToolSearch to load web research tools: query "select:WebSearch,WebFetch"
2. Conduct 3-5 web searches using varied query terms relevant to your angle
3. For each piece of relevant evidence found, record:
   - finding: what the source says (concise summary)
   - strength: strong / moderate / weak
   - source: URL or publication name
   - date_published: when published if available
4. In limitations, list significant gaps (e.g., "no authoritative ranking found", "most recent data is 3 years old")
5. Count ALL tool calls you made (ToolSearch + WebSearch + WebFetch calls) and report in tool_calls_made

Return your structured findings.`
}

const p2InitStart = budget.spent()
const initialResults = await parallel(
  ANGLES.map(a => () => agent(
    evidencePrompt(a, false),
    { label: `evidence-${a.angle}`, phase: 'Evidence Gathering', model: 'haiku', schema: EVIDENCE_SCHEMA }
  ))
)
const p2InitTokens = budget.spent() - p2InitStart

const failedIndices = initialResults.reduce((acc, r, i) => r === null ? [...acc, i] : acc, [])
log(`Initial evidence: ${3 - failedIndices.length}/3 succeeded`)

// Retry any failed agents sequentially (one at a time for per-agent token tracking)
const retryResults = initialResults.slice()  // start with initial results
const retryInstr = []
let p2RetryTokens = 0

if (failedIndices.length > 0) {
  phase('Evidence Retry')
  log(`Retrying ${failedIndices.length} failed agent(s): ${failedIndices.map(i => ANGLES[i].angle).join(', ')}`)

  for (const idx of failedIndices) {
    const a = ANGLES[idx]
    log(`Retry: evidence-${a.angle}...`)
    const rStart = budget.spent()
    const retryResult = await agent(
      evidencePrompt(a, true),
      { label: `retry-evidence-${a.angle}`, phase: 'Evidence Retry', model: 'haiku', schema: EVIDENCE_SCHEMA }
    )
    const rTokens = budget.spent() - rStart
    retryResults[idx] = retryResult
    retryInstr.push({
      angle: a.angle,
      output_tokens: rTokens,
      succeeded: retryResult !== null,
    })
    p2RetryTokens += rTokens
    log(`Retry evidence-${a.angle}: ${retryResult !== null ? 'succeeded' : 'FAILED again'}`)
  }
}

// Abort check: need all 3
const stillFailed = ANGLES.filter((_, i) => retryResults[i] === null)
if (stillFailed.length > 0) {
  const failedAngles = stillFailed.map(a => a.angle).join(', ')
  log(`ABORT: ${stillFailed.length} evidence agent(s) failed twice: ${failedAngles}`)
  return {
    aborted: true,
    reason: `Evidence agents failed initial attempt AND retry for: ${failedAngles}. Run aborted per spec — requires clean 3/3.`,
    failed_angles: stillFailed.map(a => a.angle),
    instrumentation: {
      phase1_claim_fetch: { output_tokens: fetchTokens, tool_calls: 2 },
      phase2_initial_output_tokens: p2InitTokens,
      phase2_retry_output_tokens: p2RetryTokens,
      retry_detail: retryInstr,
    },
  }
}

const validEvidence = retryResults  // all 3 non-null
const wasRetry = ANGLES.map((_, i) => initialResults[i] === null)
const p2Tokens = p2InitTokens + p2RetryTokens
log(`3/3 evidence agents succeeded. Phase 2 total: ~${p2Tokens} output tokens`)

const evidenceSummary = validEvidence.map(e =>
  `[${e.angle}] ${e.evidence_items.length} item(s): ${e.evidence_items.map(i => `"${i.finding}" (${i.strength}, ${i.source}${i.date_published ? ', ' + i.date_published : ''})`).join('; ')}\nLimitations: ${(e.limitations || []).join('; ') || 'none noted'}`
).join('\n\n')

// ── Phase 3: Adversarial Loop ──────────────────────────────────────────────

phase('Adversarial Loop')

let prevRoundVerdict = null
let currentVerdict = null
let roundsRun = 0
let stopReason = 'hit_cap'
const roundResults = []
const roundInstr = []

for (let round = 1; round <= 3; round++) {
  log(`Adversarial round ${round}/3...`)

  const priorAttacks = roundResults.length > 0
    ? roundResults.flatMap(r => r.adversary.all_attacks.map(a => a.attack))
    : []
  const priorAttacksList = priorAttacks.length > 0
    ? priorAttacks.map((a, i) => `${i + 1}. ${a}`).join('\n')
    : 'None — this is round 1; all critical attacks you raise are new.'

  const advS = budget.spent()
  const adversary = await agent(
    `You are an adversarial reviewer. Your job is to find weaknesses that would DEFEAT this marketing claim. Be rigorous and skeptical — your role is to attack, not to defend.

CLAIM: "${claimData.claim_text}"
CLAIM TYPE: ${claimData.claim_type}
CURRENT VERDICT (from prior defender, or round 1 starting assumption): ${currentVerdict || '(not yet established — round 1, assume optimistic)'}

EVIDENCE GATHERED (3 research angles):
${evidenceSummary}

ATTACKS ALREADY RAISED IN PRIOR ROUNDS (do NOT list these as new_critical_attacks — they are already in the record):
${priorAttacksList}

ATTACK SURFACES (this is a SUPERLATIVE claim with NO NAMED SOURCE — source_existence is the primary attack surface):
1. source_existence: Is there any authoritative third-party source that actually ranks or measures what this claim implies? Absence of a named source is a fatal deficiency for a superlative.
2. sample_size: If any survey or user study is referenced, is the sample size statistically sufficient?
3. time_window: Is the evidence current enough for a claim framed as an ongoing superlative?
4. comparison_baseline: Does evidence actually cover all competitors, or only a subset?
5. methodology: Is any measurement sound, reproducible, transparent, and auditable?

CRITICAL INSTRUCTIONS:
- In new_critical_attacks: list ONLY attacks with severity=critical that do NOT appear in the prior rounds list above. Return an EMPTY ARRAY [] if you have no new critical attacks to raise.
- In verdict_assessment: your honest overall verdict on whether the claim survives rigorous scrutiny.
- In tool_calls_made: report 0 — reason over the gathered evidence, no web search needed.`,
    { label: `adversary-r${round}`, phase: 'Adversarial Loop', model: 'opus', schema: ADVERSARY_SCHEMA }
  )
  const advTokens = budget.spent() - advS

  const defS = budget.spent()
  const defender = await agent(
    `You are defending a marketing claim against adversarial attacks. Use the gathered evidence to rebut each attack as strongly as the evidence allows.

CLAIM: "${claimData.claim_text}"
CLAIM TYPE: ${claimData.claim_type}

EVIDENCE GATHERED (3 research angles):
${evidenceSummary}

ADVERSARY'S ATTACKS THIS ROUND:
${adversary.all_attacks.map(a => `[${a.severity.toUpperCase()}/${a.target}] ${a.attack}`).join('\n')}

For each attack above, write a rebuttal and mark the outcome:
- "neutralized": the evidence directly and fully defeats the attack
- "weakened": the evidence partially addresses it but does not fully rebut it
- "survived": the evidence cannot address this attack (add to surviving_attacks)

After all rebuttals, set current_verdict:
- "substantiated": all critical attacks neutralized, strong supporting evidence
- "partially": some attacks survive or evidence is mixed/incomplete
- "not_substantiated": critical attacks survive that the evidence cannot rebut

In tool_calls_made: report 0 — no web search needed, reason over gathered evidence.`,
    { label: `defender-r${round}`, phase: 'Adversarial Loop', model: 'haiku', schema: DEFENDER_SCHEMA }
  )
  const defTokens = budget.spent() - defS

  const newVerdict = defender.current_verdict
  const verdictUnchanged = prevRoundVerdict !== null && newVerdict === prevRoundVerdict
  const noNewCriticalAttacks = adversary.new_critical_attacks.length === 0

  roundResults.push({ round, adversary, defender })
  roundInstr.push({
    round,
    adversary_tokens: advTokens,
    defender_tokens: defTokens,
    adversary_tool_calls: adversary.tool_calls_made || 0,
    defender_tool_calls: defender.tool_calls_made || 0,
    new_critical_attacks: adversary.new_critical_attacks.length,
    verdict: newVerdict,
  })
  prevRoundVerdict = newVerdict
  currentVerdict = newVerdict
  roundsRun = round

  log(`Round ${round}: verdict=${newVerdict}, new_critical_attacks=${adversary.new_critical_attacks.length}, verdict_unchanged=${verdictUnchanged}`)

  // Convergence gates on adversary exhaustion alone. The loop's job is to exhaust
  // the attack surface, not to stabilize a mid-loop verdict label. Verdict is
  // rendered once at synthesis, which already overrides defender verdicts.
  // Defender verdict oscillation is downstream noise and must not control loop
  // termination.
  if (noNewCriticalAttacks) {
    stopReason = 'converged'
    log(`Converged at round ${round}: no new critical attacks — adversary exhausted (defender verdict=${newVerdict}, verdict_unchanged=${verdictUnchanged})`)
    break
  }
}

log(`Adversarial loop done: ${roundsRun} round(s), stopped=${stopReason}`)

// ── Phase 4: Synthesis ────────────────────────────────────────────────────

phase('Synthesis')
log('Running Opus synthesis...')

const lastRound = roundResults[roundResults.length - 1]
const allAttacks = roundResults.flatMap(r => r.adversary.all_attacks)
const survivingAttacks = lastRound ? lastRound.defender.surviving_attacks : []
const roundVerdicts = roundResults.map(r =>
  `Round ${r.round}: adversary=${r.adversary.verdict_assessment}, defender=${r.defender.current_verdict}, new_critical_attacks=${r.adversary.new_critical_attacks.length}`
).join('\n')
const attacksFormatted = allAttacks.map(a => `[${a.severity.toUpperCase()}/${a.target}] ${a.attack}`).join('\n')

const p4S = budget.spent()
const synthesis = await agent(
  `Synthesize the results of this adversarial marketing claim review into a precise final report.

CLAIM: "${claimData.claim_text}"
CLAIM TYPE: ${claimData.claim_type}
EVIDENCE STANDARD: ${claimData.evidence_standard}

EVIDENCE GATHERED:
${evidenceSummary}

ADVERSARIAL LOOP: ${roundsRun} round(s) run (max 3), stopped because: ${stopReason}
ROUND-BY-ROUND RESULTS:
${roundVerdicts}

ALL ATTACKS RAISED (${allAttacks.length} total):
${attacksFormatted || 'None'}

ATTACKS SURVIVING TO FINAL ROUND:
${survivingAttacks.length > 0 ? survivingAttacks.join('\n') : 'None explicitly survived to the final round'}

FINAL DEFENDER VERDICT: ${currentVerdict}

Produce the final substantiation report:
- verdict: overall verdict (align with final defender verdict unless you have strong reason to differ)
- surviving_evidence: list only evidence items that withstood all adversarial scrutiny
- attacks_withstood: attacks that the claim successfully neutralized (defender outcome = "neutralized")
- attacks_damaged: attacks that materially weakened or defeated the claim (outcome = "weakened" or "survived")
- executive_summary: 2-3 paragraphs explaining the verdict, what evidence survived, and which attacks prevailed`,
  { label: 'synthesis', phase: 'Synthesis', model: 'opus', schema: SYNTHESIS_SCHEMA }
)
const p4Tokens = budget.spent() - p4S

log(`Final verdict: ${synthesis.verdict}`)
log(`Synthesis: ~${p4Tokens} output tokens`)

// ── Compile instrumentation and return ────────────────────────────────────

const p2EvidenceToolCalls = validEvidence.reduce((n, e) => n + (e.tool_calls_made || 0), 0)
const p3TotalTokens = roundInstr.reduce((n, r) => n + r.adversary_tokens + r.defender_tokens, 0)
const p3TotalToolCalls = roundInstr.reduce((n, r) => n + r.adversary_tool_calls + r.defender_tool_calls, 0)
const subagentOutputTokensTotal = fetchTokens + p2Tokens + p3TotalTokens + p4Tokens

return {
  claim_id: CLAIM_ID,
  claim_text: claimData.claim_text,
  claim_type: claimData.claim_type,
  verdict: synthesis.verdict,
  surviving_evidence: synthesis.surviving_evidence,
  attacks_withstood: synthesis.attacks_withstood,
  attacks_damaged: synthesis.attacks_damaged,
  rounds_run: roundsRun,
  stop_reason: stopReason,
  executive_summary: synthesis.executive_summary,
  instrumentation: {
    phase1_claim_fetch: {
      agent: 'claim-fetch',
      model: 'sonnet-4-6 (session-inherited)',
      output_tokens: fetchTokens,
      tool_calls: 2,
    },
    phase2_evidence_gathering: {
      initial_attempt: {
        phase_output_tokens_total: p2InitTokens,
        note: 'Ran in parallel — per-agent token deltas unavailable from script layer; see workflow UI',
      },
      retries: retryInstr,
      had_retries: failedIndices.length > 0,
      phase_output_tokens_total: p2Tokens,
      tool_calls_total: p2EvidenceToolCalls,
      per_agent: validEvidence.map((e, i) => ({
        agent: `evidence-${e.angle}`,
        model: 'haiku',
        tool_calls: e.tool_calls_made || 0,
        was_retry: wasRetry[i],
      })),
    },
    phase3_adversarial_loop: {
      rounds: roundInstr.map(r => ({
        round: r.round,
        adversary: { model: 'opus', output_tokens: r.adversary_tokens, tool_calls: r.adversary_tool_calls, new_critical_attacks: r.new_critical_attacks },
        defender: { model: 'haiku', output_tokens: r.defender_tokens, tool_calls: r.defender_tool_calls, verdict: r.verdict },
      })),
      total_output_tokens: p3TotalTokens,
      total_tool_calls: p3TotalToolCalls,
    },
    phase4_synthesis: {
      agent: 'synthesis',
      model: 'opus',
      output_tokens: p4Tokens,
      tool_calls: 0,
    },
    totals: {
      subagent_output_tokens: subagentOutputTokensTotal,
      orchestration_model_tokens: 0,
      wall_time_note: 'Date.now() unavailable in workflow scripts — total wall-time in workflow progress UI',
      token_counting_note: 'budget.spent() tracks output tokens; full-cost total (input+output+cache) from runtime usage field',
    },
  },
}
