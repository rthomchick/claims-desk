export const meta = {
  name: 'substantiation-adversary',
  description: 'Parameterized adversarial substantiation workflow — reads claim live, routes evidence by claim type, adversarial loop to convergence',
  phases: [
    { title: 'Claim Fetch', detail: 'Read claim from Claims Desk MCP; extract type, hygiene, risk' },
    { title: 'Evidence Gathering', detail: '3 parallel Haiku agents on claim-type-selected angles; retry guard' },
    { title: 'Adversarial Loop', detail: 'Opus adversary + Haiku defender, max 3 rounds, convergence on zero new critical attacks' },
    { title: 'Synthesis', detail: 'Opus final verdict: evidence audit, attack inventory, verdict rationale' },
    { title: 'Ruling Persistence', detail: 'Gate the ruling artifact (verdict enum + known convergence mode); insert on pass, log-only on fail' },
  ],
}

// ── Input ─────────────────────────────────────────────────────────────────
// args: { claim_id: string }  — UUID supplied by caller; no hardcoded claim IDs in script body

let CLAIM_ID = null
if (args) {
  if (typeof args === 'object' && args.claim_id) {
    CLAIM_ID = String(args.claim_id)
  } else if (typeof args === 'string') {
    // Runtime may stringify the args object; try JSON parse first
    try {
      const parsed = JSON.parse(args)
      CLAIM_ID = parsed && parsed.claim_id ? String(parsed.claim_id) : null
    } catch (e) {
      // Treat a bare string as the claim_id itself
      CLAIM_ID = args.trim() || null
    }
  }
}

if (!CLAIM_ID) {
  return { error: 'missing_input', message: 'args.claim_id is required — pass { claim_id: "<UUID>" } as workflow args' }
}

// ── Schemas ───────────────────────────────────────────────────────────────

const CLAIM_FETCH_SCHEMA = {
  type: 'object',
  properties: {
    error: { type: 'string', description: 'Set to "claim_not_found" if registry returns no record for this ID; leave absent otherwise' },
    claim_text: { type: 'string' },
    claim_type: { type: 'string', description: 'Superlative | Performance | Comparative | Compliance' },
    verification: { type: 'string' },
    risk_class: { type: 'string' },
    risk_factors: { type: 'array', items: { type: 'string' } },
    evidence_standard: { type: 'string' },
    submitted_evidence: { type: 'array', items: { type: 'string' } },
    hygiene_checks: { type: 'object', description: 'Full hygiene_checks object from check_substantiation (has_evidence_link, named_source, has_expiry, methodology_stated, etc.)' },
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
  required: ['all_attacks', 'new_critical_attacks', 'reputational_attacks_excluded', 'verdict_assessment', 'tool_calls_made'],
  properties: {
    all_attacks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['attack', 'target', 'severity'],
        properties: {
          attack: { type: 'string' },
          target: { enum: [
            'source_existence', 'sample_size', 'time_window', 'comparison_baseline', 'methodology',
            'benchmark_source', 'competitor_currency', 'comparison_basis',
            'certificate_existence', 'authorization_scope', 'authorization_currency', 'product_alignment',
            'other',
          ]},
          severity: { enum: ['critical', 'major', 'minor'] },
        },
      },
    },
    new_critical_attacks: {
      type: 'array',
      description: 'Critical-severity CLAIM-EVIDENCE attacks not raised in prior rounds — MUST be [] if none. Reputational/credibility/history attacks go in reputational_attacks_excluded, not here.',
      items: { type: 'string' },
    },
    reputational_attacks_excluded: {
      type: 'array',
      description: 'Attacks identified but excluded because they concern claimant reputation, credibility, or company history rather than claim-evidence quality. Out of scope per review mandate.',
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
  required: ['verdict', 'verdict_rationale', 'surviving_evidence', 'attacks_withstood', 'attacks_that_landed'],
  properties: {
    verdict: { enum: ['substantiated', 'partially', 'not_substantiated', 'escalate'] },
    verdict_rationale: { type: 'string', description: '2-3 paragraphs: overall verdict, what evidence survived, which attacks prevailed' },
    surviving_evidence: { type: 'array', items: { type: 'string' } },
    attacks_withstood: { type: 'array', items: { type: 'string' } },
    attacks_that_landed: {
      type: 'array',
      items: {
        type: 'object',
        required: ['attack', 'severity', 'outcome'],
        properties: {
          attack: { type: 'string' },
          severity: { enum: ['critical', 'major', 'minor'] },
          outcome: { type: 'string' },
        },
      },
    },
  },
}

// ── Evidence angles by claim type ─────────────────────────────────────────
// Keyed by lowercase claim_type value from registry.
// Each claim type gets exactly 3 angles: angle name + task description.

const ANGLES_BY_TYPE = {
  superlative: [
    {
      angle: 'evidence-source_existence',
      task: `Find any authoritative third-party source that ranks or measures what this claim implies. For a superlative claim with no named source, source existence is the primary attack surface. Search for: (1) the specific ranking or measurement system the claim implies, (2) who produces such rankings in this industry, (3) whether this company appears in any authoritative ranking, study, or survey, (4) whether any industry association, regulator, or major publication has independently verified a superlative position for this company. If no authoritative source exists, that is a critical finding — document it explicitly.`,
    },
    {
      angle: 'evidence-recency_and_currency',
      task: `Verify that any evidence supporting this claim is still current per FTC continuous re-substantiation guidance. Superlative claims expire when conditions change. Search for: (1) when the most recent relevant industry data was published, (2) any news in the last 12–18 months that would invalidate the superlative, (3) whether the market or competitive landscape has recently shifted, (4) any regulatory changes or consumer-report updates affecting the claim's validity. Report the most recent publication dates you find for any relevant sources.`,
    },
    {
      angle: 'evidence-competitive_landscape',
      task: `Assess whether the comparison basis holds. A superlative claim requires implicit comparison against ALL competitors. Search for: (1) the main competitors in this space, (2) any independent head-to-head comparisons or third-party ratings, (3) whether any competitor makes a directly contradicting claim, (4) what metrics are commonly used to compare offerings in this category, (5) whether the category is defined by an independent ranker or gerrymandered by the claimant.`,
    },
  ],

  performance: [
    {
      angle: 'evidence-methodology',
      task: `Find the study or test behind the metric claim. Search for: (1) any published study, whitepaper, or test report that this performance claim cites or implies, (2) who conducted the test and whether they are genuinely independent, (3) the methodology — is the test reproducible, auditable, and transparent?, (4) whether testing conditions reflect real-world use cases. If no named study exists, document that explicitly — absence of a cited study is a critical finding for a performance claim.`,
    },
    {
      angle: 'evidence-baseline',
      task: `Find what the comparison baseline actually is. Performance claims imply a comparison (faster than what? better than what?). Search for: (1) what baseline is explicitly or implicitly stated in the claim, (2) whether the baseline is the company's prior product, industry average, or a specific competitor, (3) independent benchmarks or reviews that establish the baseline in this product category, (4) whether the claimant cherry-picked a favorable baseline. If the baseline is unstated or ambiguous, document that as a critical finding.`,
    },
    {
      angle: 'evidence-sample_size',
      task: `Verify sample size and population validity for any user study or survey behind the claim. Search for: (1) the sample size cited in any supporting study, (2) whether the population is representative of the claimed audience, (3) any published critiques of the study's statistical methodology, (4) whether confidence intervals or margins of error are disclosed. If the claim rests on an unreportably small sample or a biased population, document that explicitly.`,
    },
  ],

  comparative: [
    {
      angle: 'evidence-benchmark_source',
      task: `Find the third-party benchmark or study cited in the comparative claim. Search for: (1) the specific benchmark or source the claim cites or implies, (2) who produced the benchmark and whether they are genuinely independent, (3) whether the benchmark is public and auditable, (4) any criticism of the benchmark's methodology or independence. If no named benchmark exists, document that explicitly — absence of a cited benchmark source is a critical finding for a comparative claim.`,
    },
    {
      angle: 'evidence-competitor_currency',
      task: `Verify whether the competitor data used in the comparison is current. Comparative claims can become misleading when competitor products have since improved. Search for: (1) when the competitor data cited was collected, (2) any product updates by named competitors since the comparison was made, (3) whether competitors now outperform the claimant on the comparison metric, (4) any new independent reviews that contradict the comparison. Report the most recent publication dates for all relevant sources.`,
    },
    {
      angle: 'evidence-comparison_basis',
      task: `Determine whether the comparison methodology is stated, fair, and complete. Search for: (1) whether the comparison is apples-to-apples (same product tier, same test conditions), (2) whether the claimant disclosed the methodology, (3) any independent evaluation that uses the same comparison criteria, (4) whether named competitors agree with or contest the comparison, (5) any regulatory guidance on comparative advertising in this industry that would require specific disclosures.`,
    },
  ],

  compliance: [
    {
      angle: 'evidence-certificate_existence',
      task: `Determine whether a valid compliance certificate matching this claim actually exists in an official registry. Search the authoritative registries for the specific certification claimed (e.g., FedRAMP Marketplace at marketplace.fedramp.gov, SOC report directories, ISO certification registries, CMMC C3PAO listings, etc.). Look for: (1) any entry for this company under all certificate statuses, (2) the critical distinction between AUTHORIZED status vs. preparatory statuses (e.g., FedRAMP Ready, In-Process) — only AUTHORIZED constitutes a live compliance claim, (3) any official announcements from the company claiming this certification, (4) any government procurement records referencing the company with this certification. If no AUTHORIZED entry is found, document that explicitly — absence from official registries is strong evidence the authorization does not exist.`,
    },
    {
      angle: 'evidence-authorization_scope',
      task: `If any compliance certificate exists, verify it covers the specific product and use case in the claim. Compliance certifications are product- and version-specific, not company-wide. Search for: (1) the exact product name and version listed on any authorization (the claim's product must match), (2) whether the use case in the claim falls within the authorized scope, (3) whether the company has multiple products and only some carry the certification, (4) any documentation showing which products are covered vs. excluded. If no certification exists (per evidence-certificate_existence angle), document that scope verification is moot — the predicate does not exist.`,
    },
    {
      angle: 'evidence-authorization_currency',
      task: `Verify that any compliance certificate is current and not lapsed, revoked, or superseded. Compliance authorizations require continuous monitoring and periodic renewal. Search for: (1) the authorization date and any listed expiry or reauthorization date, (2) any news of the authorization being revoked, suspended, or downgraded, (3) whether the official listing shows an active status, (4) any continuous monitoring reports or annual assessment results, (5) whether an authorization predating 2024 without a confirmed renewal warrants currency scrutiny given the current date (July 2026). If no authorization is found, document that currency verification is moot.`,
    },
  ],
}

// ── Claim-type-specific attack surface guidance (for adversary prompt) ────

const ATTACK_SURFACES_BY_TYPE = {
  superlative: `ATTACK SURFACES (this is a SUPERLATIVE claim — source_existence is the primary attack surface):
1. source_existence: Is there any authoritative third-party source that actually ranks or measures what this claim implies? Absence of a named source is a fatal deficiency for a superlative.
2. time_window: Is the evidence current enough for a claim framed as an ongoing superlative? FTC continuous re-substantiation guidance requires evidence currency.
3. comparison_baseline: Does evidence actually cover all competitors, or only a subset? Is the category definition gerrymandered by the claimant?
4. methodology: Is any measurement sound, reproducible, transparent, and auditable?`,

  performance: `ATTACK SURFACES (this is a PERFORMANCE claim — methodology and baseline are primary attack surfaces):
1. methodology: Is the study or test behind the metric published, reproducible, and conducted by an independent party?
2. comparison_baseline: Is the performance baseline explicitly stated and fairly chosen (not cherry-picked)?
3. sample_size: Is any user study statistically sufficient? Is the population representative?
4. time_window: Is the performance data current, or has the competitive landscape changed since the test?`,

  comparative: `ATTACK SURFACES (this is a COMPARATIVE claim — benchmark independence and competitor currency are primary attack surfaces):
1. benchmark_source: Is the benchmark cited genuine, public, and conducted by an independent party?
2. competitor_currency: Is the competitor data current? Have competitors materially improved since the comparison?
3. comparison_basis: Is the comparison methodology stated, fair, and apples-to-apples?
4. methodology: Are disclosure requirements for comparative advertising (e.g., FTC guidelines) met?`,

  compliance: `ATTACK SURFACES (this is a COMPLIANCE claim — certificate_existence is the primary, near-dispositive attack surface):
1. certificate_existence: Does a valid, AUTHORIZED certificate matching this claim exist on official registries? Absence from official registries is near-dispositive. "FedRAMP Ready" or "In Process" do NOT constitute authorization.
2. authorization_scope: Even if a certificate exists, does it cover the specific product and use case in the claim?
3. authorization_currency: Is any found authorization current, or has it lapsed, been revoked, or expired without renewal?
4. product_alignment: Does the claimed product category actually correspond to the certified product scope?`,
}

// ── Synthesis verdict guidance by claim type ──────────────────────────────

const SYNTHESIS_TYPE_GUIDANCE = {
  compliance: 'For a compliance claim: if no AUTHORIZED certificate was found on official registries, the verdict MUST be not_substantiated — certificate existence is the primary and nearly dispositive evidence requirement.',
  superlative: 'For a superlative claim: if no authoritative third-party source was found that independently substantiates the superlative position, the claim cannot be substantiated.',
  performance: 'For a performance claim: if no independent, reproducible study with a clearly stated and fair baseline was found, the claim cannot be substantiated.',
  comparative: 'For a comparative claim: if the benchmark source is not genuinely independent, not publicly auditable, or competitor data is materially outdated, the claim cannot be substantiated.',
}

// ── Phase 1: Claim Fetch ──────────────────────────────────────────────────

phase('Claim Fetch')
log(`Fetching claim ${CLAIM_ID} from Claims Desk MCP...`)

const t0 = budget.spent()
const claimData = await agent(
  `Fetch live data for a marketing claim from the Claims Desk MCP registry. This is READ-ONLY — do NOT call append_claim, delete_claim, or any write tool.

Claim ID: ${CLAIM_ID}

Step 1: Use ToolSearch to load these two tools:
  select:mcp__6db17c1d-acf8-4170-bc36-12d3ce50766a__get_claim_status,mcp__6db17c1d-acf8-4170-bc36-12d3ce50766a__check_substantiation

Step 2: Call get_claim_status with claim_id="${CLAIM_ID}". If the registry returns an error or "not found", set error="claim_not_found" and return immediately — do not call check_substantiation.

Step 3: Call check_substantiation with claim_id="${CLAIM_ID}". Note the full result.

Return structured data with ALL of the following fields (where available):
- error: set to "claim_not_found" ONLY if the registry returned an error or no record for this claim ID; leave absent or null otherwise
- claim_text: the actual marketing claim text
- claim_type: Superlative | Performance | Comparative | Compliance (exact casing from registry)
- verification: the verification verdict from get_claim_status
- risk_class: the risk classification (e.g., high, medium, low)
- risk_factors: list of risk factors from the registry (array of strings)
- evidence_standard: the evidence standard the registry applies to this claim type
- submitted_evidence: list of any evidence items already submitted, as strings
- hygiene_checks: the FULL hygiene_checks object from check_substantiation (include all fields: has_evidence_link, named_source, has_expiry, methodology_stated, etc. — do not summarize, return the raw object)
- mcp_notes: any other notable data such as assigned adjudicator, dates, flags`,
  { label: 'claim-fetch', phase: 'Claim Fetch', schema: CLAIM_FETCH_SCHEMA }
)
const fetchTokens = budget.spent() - t0

if (!claimData) {
  log('Claim fetch agent failed — aborting')
  return { error: 'fetch_agent_failed', claim_id: CLAIM_ID }
}

if (claimData.error === 'claim_not_found') {
  log(`Claim ${CLAIM_ID} not found in registry — aborting`)
  return { error: 'claim_not_found', claim_id: CLAIM_ID }
}

log(`Claim: "${claimData.claim_text}"`)
log(`Type: ${claimData.claim_type} | Verification: ${claimData.verification} | Risk: ${claimData.risk_class}`)
log(`Evidence standard: ${claimData.evidence_standard}`)
log(`Claim fetch: ~${fetchTokens} output tokens`)

// ── Claim type routing ────────────────────────────────────────────────────

const claimTypeKey = (claimData.claim_type || '').toLowerCase()
const ANGLES = ANGLES_BY_TYPE[claimTypeKey]

if (!ANGLES) {
  log(`Unknown claim type "${claimData.claim_type}" — cannot select evidence angles. Aborting.`)
  return { error: 'unknown_claim_type', claim_id: CLAIM_ID, claim_type: claimData.claim_type }
}

log(`Evidence angles selected for ${claimData.claim_type}: ${ANGLES.map(a => a.angle).join(', ')}`)

const attackSurfaces = ATTACK_SURFACES_BY_TYPE[claimTypeKey]
const synthesisTypeGuidance = SYNTHESIS_TYPE_GUIDANCE[claimTypeKey] || ''

// ── Hygiene context string for evidence agents ────────────────────────────

const hygieneCtx = claimData.hygiene_checks
  ? `HYGIENE CHECKS FROM REGISTRY:\n${JSON.stringify(claimData.hygiene_checks, null, 2)}\nWeight your findings accordingly — hygiene flags indicate where evidence gaps are most critical.`
  : ''

// ── Phase 2: Evidence Gathering ───────────────────────────────────────────

phase('Evidence Gathering')
log(`Launching 3 parallel Haiku evidence agents (initial attempt)...`)

const evidencePrompt = (a, isRetry) => {
  const retryPreamble = isRetry
    ? `MANDATORY: You are on a RETRY because a prior agent completed without calling the StructuredOutput tool. You MUST call StructuredOutput before finishing — do not end your response without it. Return whatever you found, even if your evidence list is limited. Calling StructuredOutput with partial results is required; not calling it is not acceptable.\n\n`
    : ''
  return `${retryPreamble}You are an evidence researcher for a marketing claim substantiation review.

CLAIM: "${claimData.claim_text}"
CLAIM TYPE: ${claimData.claim_type}
EVIDENCE STANDARD FROM REGISTRY: ${claimData.evidence_standard}
${hygieneCtx ? '\n' + hygieneCtx + '\n' : ''}
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
4. In limitations, list significant gaps (e.g., "no authoritative source found", "most recent data is 3 years old", "company not found in official registry")
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

const retryResults = initialResults.slice()
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
    retryInstr.push({ angle: a.angle, output_tokens: rTokens, succeeded: retryResult !== null })
    p2RetryTokens += rTokens
    log(`Retry evidence-${a.angle}: ${retryResult !== null ? 'succeeded' : 'FAILED again'}`)
  }
}

const stillFailed = ANGLES.filter((_, i) => retryResults[i] === null)
if (stillFailed.length > 0) {
  const failedAngles = stillFailed.map(a => a.angle).join(', ')
  log(`ABORT: ${stillFailed.length} evidence agent(s) failed twice: ${failedAngles}`)
  return {
    aborted: true,
    reason: `Evidence agents failed initial attempt AND retry for: ${failedAngles}. Run aborted — requires clean 3/3.`,
    failed_angles: stillFailed.map(a => a.angle),
  }
}

const validEvidence = retryResults
const wasRetry = ANGLES.map((_, i) => initialResults[i] === null)
const p2Tokens = p2InitTokens + p2RetryTokens
log(`3/3 evidence agents succeeded. Phase 2 total: ~${p2Tokens} output tokens`)

const evidenceSummary = validEvidence.map(e =>
  `[${e.angle}] ${e.evidence_items.length} item(s): ${e.evidence_items.map(i => `"${i.finding}" (${i.strength}, ${i.source}${i.date_published ? ', ' + i.date_published : ''})`).join('; ')}\nLimitations: ${(e.limitations || []).join('; ') || 'none noted'}`
).join('\n\n')

// ── Phase 3: Adversarial Loop ─────────────────────────────────────────────

phase('Adversarial Loop')

let prevRoundVerdict = null
let currentVerdict = null
let roundsRun = 0
let stopReason = 'round_cap'
const roundResults = []
const roundInstr = []
const allReputationalFiltered = []

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

${attackSurfaces}

SCOPE CONSTRAINT — HARD RULE:
Attack ONLY on claim-evidence grounds: source existence, methodology, currency, scope, sample size, comparison basis. Do NOT attack based on the claimant's reputation, credibility, company history, prior incidents, or any factor external to the claim's evidence. If you identify such a reputational attack, put it in reputational_attacks_excluded — NOT in new_critical_attacks or all_attacks.

CRITICAL INSTRUCTIONS:
- In new_critical_attacks: list ONLY severity=critical CLAIM-EVIDENCE attacks that do NOT appear in the prior rounds list. Return [] if none are new.
- In reputational_attacks_excluded: list any attacks you identified but excluded because they are reputational/credibility/history-based. Return [] if none.
- In verdict_assessment: your honest overall verdict on whether the claim survives rigorous evidence scrutiny.
- In tool_calls_made: report 0 — reason over the gathered evidence, no web search needed.`,
    { label: `adversary-r${round}`, phase: 'Adversarial Loop', model: 'opus', schema: ADVERSARY_SCHEMA }
  )
  const advTokens = budget.spent() - advS

  // Log and accumulate reputational attacks filtered by adversary self-sorting
  const repFiltered = adversary.reputational_attacks_excluded || []
  if (repFiltered.length > 0) {
    log(`Round ${round}: ${repFiltered.length} reputational attack(s) filtered (out of scope): ${repFiltered.join(' | ')}`)
    repFiltered.forEach(a => allReputationalFiltered.push({ round, attack: a, filter_source: 'adversary_self_sort' }))
  }

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
    reputational_filtered: repFiltered.length,
    verdict: newVerdict,
  })
  prevRoundVerdict = newVerdict
  currentVerdict = newVerdict
  roundsRun = round

  log(`Round ${round}: verdict=${newVerdict}, new_critical_attacks=${adversary.new_critical_attacks.length}, verdict_unchanged=${verdictUnchanged}`)

  // Convergence gates on adversary exhaustion alone. The loop's job is to exhaust
  // the attack surface, not to stabilize a mid-loop verdict label. Verdict is
  // rendered once at synthesis, which already overrides defender verdicts.
  // Defender verdict oscillation is downstream noise on borderline claims and
  // must not control loop termination.
  if (noNewCriticalAttacks) {
    stopReason = 'attack_exhaustion'
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

VERDICT ARBITER NOTE: You are the authoritative verdict arbiter. You MAY override the defender's final verdict if the full attack/defense record warrants it — this is by design. Synthesis is the single authoritative verdict source.
${synthesisTypeGuidance ? '\nCLAIM-TYPE GUIDANCE: ' + synthesisTypeGuidance : ''}

Produce the final substantiation report:
- verdict: overall verdict (substantiated / partially / not_substantiated / escalate). Align with the evidence record — override defender if warranted. Use escalate if the record leaves the verdict genuinely undecidable by this review rather than merely unfavorable.
- verdict_rationale: 2-3 paragraphs explaining the verdict, what evidence survived, and which attacks prevailed.
- surviving_evidence: list only evidence items that withstood all adversarial scrutiny
- attacks_withstood: list attacks the claim successfully neutralized (defender outcome = "neutralized")
- attacks_that_landed: for each attack that materially weakened or defeated the claim, provide the attack text, its severity (critical/major/minor), and the outcome (what damage it caused to the claim's substantiation)`,
  { label: 'synthesis', phase: 'Synthesis', model: 'opus', schema: SYNTHESIS_SCHEMA }
)
const p4Tokens = budget.spent() - p4S

log(`Final verdict: ${synthesis.verdict}`)
log(`Synthesis: ~${p4Tokens} output tokens`)
if (allReputationalFiltered.length > 0) {
  log(`Reputational attacks filtered total: ${allReputationalFiltered.length} (excluded from convergence check)`)
}

// ── Phase 5: Ruling Persistence ───────────────────────────────────────────
// Gate per D5 (authoritative for this commit): a ruling persists only if
// (1) verdict parses to exactly one of the four-value vocabulary, and
// (2) convergence mode is known (attack_exhaustion or round_cap — stopReason
// already carries this, since the loop's own termination reason IS the
// convergence mode). escalate passes like any other verdict — not held.
//
// This check is a deliberate inline duplicate of week17/lib/ruling_gate.mjs
// (checkRulingGate), which carries the same condition as a pure, independently
// tested function — see week17/test/ruling_gate.test.mjs. Workflow scripts have
// no filesystem/module access, so the logic can't be imported here; keep the
// two in sync if this condition ever changes.

phase('Ruling Persistence')

const RULING_VERDICT_VOCAB = ['substantiated', 'partially', 'not_substantiated', 'escalate']
const RULING_CONVERGENCE_VOCAB = ['attack_exhaustion', 'round_cap']

const rulingArtifact = {
  claim_id: CLAIM_ID,
  verdict: synthesis.verdict,
  rationale: synthesis.verdict_rationale,
  convergence: stopReason,
  rounds: roundsRun,
}

const verdictOk = typeof rulingArtifact.verdict === 'string' && RULING_VERDICT_VOCAB.includes(rulingArtifact.verdict)
const convergenceOk = typeof rulingArtifact.convergence === 'string' && RULING_CONVERGENCE_VOCAB.includes(rulingArtifact.convergence)

let rulingPersisted = false
let rulingGateFailureReason = null
let rulingId = null

if (!verdictOk) {
  rulingGateFailureReason = `verdict "${rulingArtifact.verdict}" is not one of: ${RULING_VERDICT_VOCAB.join(', ')}`
} else if (!convergenceOk) {
  rulingGateFailureReason = `convergence "${rulingArtifact.convergence}" is not one of: ${RULING_CONVERGENCE_VOCAB.join(', ')} — convergence mode unknown`
}

if (rulingGateFailureReason) {
  log(`Ruling gate FAILED — not persisted: ${rulingGateFailureReason}`)
} else {
  log(`Ruling gate passed (verdict=${rulingArtifact.verdict}, convergence=${rulingArtifact.convergence}, rounds=${rulingArtifact.rounds}) — writing to review_rulings...`)

  // written_by_session: no session identifier is exposed to a workflow script
  // (no such global among args/budget/log/phase/agent/parallel/pipeline/workflow).
  // append_claim's own contract is "supplied parameter, no inference, no default"
  // (server/tools/append_claim.py) — followed here by passing null rather than
  // fabricating an identifier. A null means unknown; a fabricated value would
  // assert something false.
  const writeResult = await agent(
    `Write a review ruling to the Claims Desk MCP registry. This is a WRITE call — call append_ruling exactly once with the exact arguments given below, then return its result. Do not call any other write tool.

Step 1: Use ToolSearch to load: select:mcp__6db17c1d-acf8-4170-bc36-12d3ce50766a__append_ruling

Step 2: Call append_ruling with:
  claim_id: "${rulingArtifact.claim_id}"
  verdict: "${rulingArtifact.verdict}"
  rationale: ${JSON.stringify(rulingArtifact.rationale)}
  reviewed_by: "substantiation-adversary/v1"
  convergence: "${rulingArtifact.convergence}"
  rounds: ${rulingArtifact.rounds}
  written_by_session: null

Step 3: Return the tool's result verbatim as {ruling_id, claim_id}. If the call errors, return {error: "<the error message>"}.`,
    {
      label: 'ruling-write',
      phase: 'Ruling Persistence',
      schema: {
        type: 'object',
        properties: {
          ruling_id: { type: 'string' },
          claim_id: { type: 'string' },
          error: { type: 'string' },
        },
      },
    }
  )

  if (writeResult && writeResult.ruling_id) {
    rulingPersisted = true
    rulingId = writeResult.ruling_id
    log(`Ruling persisted: ruling_id=${rulingId}`)
  } else {
    log(`Ruling write FAILED: ${writeResult && writeResult.error ? writeResult.error : 'no ruling_id returned'}`)
  }
}

// ── Output report ─────────────────────────────────────────────────────────

const p2EvidenceToolCalls = validEvidence.reduce((n, e) => n + (e.tool_calls_made || 0), 0)
const p3TotalTokens = roundInstr.reduce((n, r) => n + r.adversary_tokens + r.defender_tokens, 0)
const p3TotalToolCalls = roundInstr.reduce((n, r) => n + r.adversary_tool_calls + r.defender_tool_calls, 0)
const subagentOutputTokensTotal = fetchTokens + p2Tokens + p3TotalTokens + p4Tokens

return {
  claim_id: CLAIM_ID,
  claim_text: claimData.claim_text,
  claim_type: claimData.claim_type,
  verdict: synthesis.verdict,
  verdict_rationale: synthesis.verdict_rationale,
  surviving_evidence: synthesis.surviving_evidence,
  attacks_withstood: synthesis.attacks_withstood,
  attacks_that_landed: synthesis.attacks_that_landed,
  rounds_run: roundsRun,
  stop_reason: stopReason,
  hygiene_checks: claimData.hygiene_checks || null,
  ruling: {
    persisted: rulingPersisted,
    ruling_id: rulingId,
    gate_failure_reason: rulingGateFailureReason,
    artifact: rulingArtifact,
  },
  instrumentation: {
    phase1_claim_fetch: {
      agent: 'claim-fetch',
      model: 'sonnet-4-6 (session-inherited)',
      output_tokens: fetchTokens,
      tool_calls: 2,
    },
    phase2_evidence_gathering: {
      claim_type_routing: claimData.claim_type,
      angles_selected: ANGLES.map(a => a.angle),
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
        adversary: { model: 'opus', output_tokens: r.adversary_tokens, tool_calls: r.adversary_tool_calls, new_critical_attacks: r.new_critical_attacks, reputational_filtered: r.reputational_filtered },
        defender: { model: 'haiku', output_tokens: r.defender_tokens, tool_calls: r.defender_tool_calls, verdict: r.verdict },
      })),
      total_output_tokens: p3TotalTokens,
      total_tool_calls: p3TotalToolCalls,
      reputational_attacks_filtered: allReputationalFiltered,
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
