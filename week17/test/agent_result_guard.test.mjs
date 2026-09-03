import { test } from 'node:test'
import assert from 'node:assert/strict'
import { checkAgentResult } from '../lib/agent_result_guard.mjs'

const ADVERSARY_SPEC = [
  ['all_attacks', 'array'],
  ['new_critical_attacks', 'array'],
  ['reputational_attacks_excluded', 'array'],
]

test('null result rejected', () => {
  const result = checkAgentResult(null, ADVERSARY_SPEC)
  assert.equal(result.pass, false)
  assert.match(result.reason, /null/)
})

test('result missing a required field rejected', () => {
  const result = checkAgentResult({ all_attacks: [], new_critical_attacks: [] }, ADVERSARY_SPEC)
  assert.equal(result.pass, false)
  assert.match(result.reason, /reputational_attacks_excluded/)
})

test('well-formed result passes', () => {
  const result = checkAgentResult(
    { all_attacks: [], new_critical_attacks: [], reputational_attacks_excluded: [] },
    ADVERSARY_SPEC
  )
  assert.equal(result.pass, true)
  assert.equal(result.reason, null)
})

test('non-object result rejected', () => {
  const result = checkAgentResult('not an object', ADVERSARY_SPEC)
  assert.equal(result.pass, false)
})

test('string field checked correctly', () => {
  const result = checkAgentResult({ current_verdict: 'substantiated', surviving_attacks: [] }, [
    ['current_verdict', 'string'],
    ['surviving_attacks', 'array'],
  ])
  assert.equal(result.pass, true)
})
