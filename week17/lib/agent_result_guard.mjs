// agent_result_guard — pure check for whether an agent() call result is
// usable before the caller dereferences fields off it. A workflow agent()
// call can return null (provider-side error) or, in principle, an object
// missing fields the schema was supposed to guarantee. This is checked
// before any dereference so a bad result terminates the run cleanly
// instead of throwing.
//
// spec is a list of [fieldName, kind] pairs, where kind is 'string' or
// 'array'. Extend kind as needed; only the two adversary.js currently uses.

export function checkAgentResult(result, spec) {
  if (!result || typeof result !== 'object') {
    return { pass: false, reason: 'result is null or not an object' }
  }

  for (const [field, kind] of spec) {
    const value = result[field]
    const ok = kind === 'array' ? Array.isArray(value) : typeof value === kind
    if (!ok) {
      return { pass: false, reason: `field "${field}" missing or not ${kind}` }
    }
  }

  return { pass: true, reason: null }
}
