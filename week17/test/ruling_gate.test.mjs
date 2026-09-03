import { test } from 'node:test'
import assert from 'node:assert/strict'
import { checkRulingGate } from '../lib/ruling_gate.mjs'

test('valid verdict with attack_exhaustion passes', () => {
  const result = checkRulingGate({ verdict: 'substantiated', convergence: 'attack_exhaustion' })
  assert.equal(result.pass, true)
})

test('valid verdict with round_cap passes', () => {
  const result = checkRulingGate({ verdict: 'not_substantiated', convergence: 'round_cap' })
  assert.equal(result.pass, true)
})

test('escalate passes rather than being held for review', () => {
  const result = checkRulingGate({ verdict: 'escalate', convergence: 'attack_exhaustion' })
  assert.equal(result.pass, true)
})

test('verdict outside the enum fails', () => {
  const result = checkRulingGate({ verdict: 'approved', convergence: 'round_cap' })
  assert.equal(result.pass, false)
  assert.match(result.reason, /verdict/)
})

test('run with no convergence mode fails', () => {
  const result = checkRulingGate({ verdict: 'substantiated', convergence: null })
  assert.equal(result.pass, false)
  assert.match(result.reason, /convergence/)
})

test('missing verdict fails', () => {
  const result = checkRulingGate({ convergence: 'round_cap' })
  assert.equal(result.pass, false)
})

test('unparseable (non-string) verdict fails', () => {
  const result = checkRulingGate({ verdict: { verdict_assessment: 'substantiated' }, convergence: 'round_cap' })
  assert.equal(result.pass, false)
})
