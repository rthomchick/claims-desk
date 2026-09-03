// ruling_gate — pure pass/fail check for whether a ruling artifact may be
// persisted. No database calls, no file reads, no network: this module
// takes the parsed ruling artifact (verdict, convergence, rounds) and
// returns a decision. A ruling that fails this gate is logged with the
// reason and never reaches review_rulings — the caller (adversary.js) is
// responsible for wiring that logging and the actual insert.
//
// Per D5 (authoritative for this commit): a ruling persists only if
// (1) verdict parses to exactly one of the four-value vocabulary, and
// (2) convergence mode is known (attack_exhaustion or round_cap). escalate
// passes like any other verdict — it is not held for review.

export const VALID_VERDICTS = ['substantiated', 'partially', 'not_substantiated', 'escalate']
export const VALID_CONVERGENCE = ['attack_exhaustion', 'round_cap']

export function checkRulingGate(artifact) {
  const verdict = artifact && artifact.verdict
  const convergence = artifact && artifact.convergence

  if (typeof verdict !== 'string' || !VALID_VERDICTS.includes(verdict)) {
    return { pass: false, reason: `verdict "${verdict}" is not one of: ${VALID_VERDICTS.join(', ')}` }
  }

  if (typeof convergence !== 'string' || !VALID_CONVERGENCE.includes(convergence)) {
    return { pass: false, reason: `convergence "${convergence}" is not one of: ${VALID_CONVERGENCE.join(', ')} — convergence mode unknown` }
  }

  return { pass: true, reason: null }
}
