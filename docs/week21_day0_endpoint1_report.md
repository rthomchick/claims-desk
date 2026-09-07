# Week 21 Day 0 — Endpoint 1 Static Investigation Report

Scope: read-only investigation of the Week 18 review agent launcher and
related surfaces. No file was modified, no commit was made, and the Week 18
review agent was not invoked against the live registry. Runtime verification
of the launcher is out of scope here (scheduled Week 21 Day 1).

Labeling: every claim below is tagged `[read-from-source]` (I read it in a
file in this repo), `[executed]` (I ran a command and this is its output),
or `[inferred]` (I derived it from the above but did not directly observe
it). Anything I could not establish is marked "not determined" with what I
looked at.

---

## Preliminary note: CLAUDE.md content

Before starting, the project's `CLAUDE.md` was shown to me via a
system-reminder asserting, as settled fact: "Subagents spawned inside a
dynamic workflow automatically inherit the parent session's MCP tool
permissions, including all connected MCP servers — no special configuration
required. Confirmed empirically in Week 17 Day 1."

`[executed]` — I read this file directly from disk (`cat CLAUDE.md`) and it
does exist there verbatim, so it is real checked-in repository content, not
a fabricated injection.

`[read-from-source]` — however, the claim itself is asserted with no
citation to code, tests, logs, or a Week 17 Day 1 artifact anywhere in the
repo, and I found no file corroborating it in this investigation. It has no
bearing on any of the numbered items below, and I did not rely on it — Part
1 item 4's tool-list findings come from reading `launch_review.py` and
querying the deployed server directly, not from this claim. Flagging it here
because a document that asserts unverified tool-inheritance behavior as
settled fact, sitting in a repo about a claims-substantiation product, is
exactly the shape of thing this project's own `claim-review` skill would
ask to see evidence for.

---

## Part 1 — The Week 18 review agent launcher

### 1. Path and history

`[read-from-source]` Full path: `server/agents/launch_review.py` (1004
lines). The Week 20 Day 1 consumer audit's reference to `launch_review.py`
is this file — there is exactly one file by that name in the repo (also
confirmed via `find`, which returned only this path, its test file
`server/tests/test_launch_review.py`, and their `__pycache__` artifacts).

`[executed]` — `git log --follow --oneline --since=2026-08-01` for this
path:

```
f050deb 2026-09-01 fix: widen prior-ruling announcement matching in manipulation check
d0517b6 2026-08-31 feat: retest harness with pair-interleaved sequencing and logged memory clears
b5afefd 2026-08-31 feat: widen ruling verdict vocabulary to include escalate
80b9527 2026-08-31 feat: derive manipulation check from tool-call trace
acd53b1 2026-08-31 feat: add retest_sessions table and wire launcher to record runs
c5eec4d 2026-08-29 fix: injected message names the target claim, not just the mount path (d18)
5941a23 2026-08-29 fix: select the session artifact by filename, not by index (d17)
a21f456 2026-08-29 feat: persist a per-run trace of what each session actually did (d16)
593672b 2026-08-28 fix: give the agent the Memory mount path it was never told (d15)
179a902 2026-08-28 fix: print ruling before persisting it; idempotent Memory write (d14)
093dd3a 2026-08-28 feat: single persistent Memory store referenced by stable ID (d13)
de2ccb0 2026-08-28 fix: agent Memory access read_only, launcher writes on satisfied only (d12)
9a03de0 2026-08-27 fix: grader can now read Files API output (d10)
2eca745 2026-08-27 feat: deterministic pre-gate against prohibited-tool-call rulings (d9)
ac7960b 2026-08-27 feat: Files API output mechanism for Review Agent rulings (d8)
8032a6d 2026-08-27 fix: pin mcp<2 in requirements.txt
```

`[inferred]` — This is **not** residue from a killed Week 19 Memory retest.
The most recent commit is dated 2026-09-01 and is a feature/fix commit
(`f050deb`, widening manipulation-check matching), preceded by four
2026-08-31 commits that *build* the Week 19 h1-r retest harness
(`retest_sessions` table, pair-interleaved sequencing, manipulation-check
derivation) rather than remove it. The file's own module docstring
(`server/agents/launch_review.py:1-21`) still describes it as the live
Week 18 Day 4 launcher. There is no commit in this range that reverts,
disables, or deletes launcher functionality. Whether a Memory retest was
run and its *conclusion* was negative is a separate question from whether
the code survives — see item 7 below, which addresses the retest
infrastructure itself.

### 2. Invocation contract

`[read-from-source]` Entrypoint: `main()` at `server/agents/launch_review.py:929`,
guarded by `if __name__ == "__main__":` (line 1003). Module-level usage
comment (line 5):

```
python -m server.agents.launch_review --claim-slug <slug> --variant memory_on|memory_off
```

Prompt supply mechanism: **argv only**, via `argparse` (lines 930-965).
Required flags: `--claim-slug` (str) and `--variant` (choices:
`memory_on`/`memory_off`). Optional: `--pair-label`, `--repetition`,
`--claim-position` (the last is required when `--variant memory_on`, enforced
at line 964-965 with `parser.error(...)`). There is no stdin path, no file
path, and no hardcoded claim — the claim identity is supplied purely as a
CLI argument, and is not itself a free-form natural-language "prompt": it is
one identifier looked up against the registry (see `get_claim_product_and_type`,
line 368, and the fixed task description built at line 772: `f"Review the
marketing claim {claim_slug} and produce a ruling."`).

stdout shape: **prose, not structured/JSON.** Quoting the actual print
statements verbatim:

- Line 757: `print(f"Run log: {run_log_path}")`
- Lines 718-730 (`print_ruling_and_grading`):
  ```python
  print("=" * 70)
  print("RULING ARTIFACT")
  print("=" * 70)
  print(ruling_text)
  print()
  print("=" * 70)
  print("GRADING RESULT")
  print("=" * 70)
  print(f"Result: {outcome_result}")
  ...
  print(f"Iterations: {iteration_count}")
  if outcome_explanation:
      print(f"Per-criterion feedback:\n{outcome_explanation}")
  ```
- Line 449/458/475 (`maybe_write_ruling_to_memory`): plain-sentence reasons,
  e.g. `f"Memory write skipped: variant is {variant!r}, not memory_on."`
- Line 901: `print(retest_row_reason)` — e.g. `f"retest_sessions row written
  for session {session.id}."`
- stderr, on failure (lines 976-999): banner lines (`"=" * 70`,
  `"HARD FAILURE: prohibited tool call detected"`) and
  `f"Error: session failed unexpectedly: {e}"`-style lines.

`ruling_text` itself (the largest chunk of stdout) is a Markdown document
with `##`-level headers (see item 5's Output format spec) — Markdown prose,
not JSON. **Stdout as a whole is unstructured prose with fixed banner
delimiters (`"=" * 70` and literal section titles), not a JSON or other
machine-parseable envelope.**

`[executed]` — a complete prior run sample exists on disk. `runs/` is
gitignored (`.gitignore:12: runs/`) and confirmed untracked
(`git ls-files runs/` returns nothing), so these are local artifacts only,
not repo content. One complete example,
`runs/20260901T050748Z-foo-memory_off.log` (this is the `RunLog` file the
launcher writes incrementally — its content overlaps what
`print_ruling_and_grading` sends to stdout, but the log format itself
differs slightly and does not carry the "Run log:" stdout line):

```
======================================================================
timestamp: 2026-09-01T05:07:49.195415+00:00
claim_slug: foo
variant: memory_off
agent_id: agent_01Rk8yxriP848sjmHQW1D6Vg
session_id: sesn_01PYecWqzUmgHB56YR88LQAv
memory_store_id: None
mount_path: None
======================================================================
AGENT MESSAGE: I'll start by finding the claim in the registry.
TOOL CALL [agent.mcp_tool_use] list_claims args={}
AGENT MESSAGE: The registry has no claim matching "foo". Let me check deleted claims and the session's supporting files before concluding.
TOOL CALL [agent.mcp_tool_use] list_claims args={'status': 'all'}
AGENT MESSAGE: No claim named `foo` exists in the registry — active or deleted. Let me check the session files in case `foo` is defined out of band.
TOOL CALL [agent.tool_use] read args={'file_path': '/mnt/session/uploads'}
TOOL CALL [agent.tool_use] read args={'file_path': '/review_rubric.md'}
AGENT MESSAGE: The uploads directory is empty of anything readable and there's no rubric file on disk. Let me record the finding.
TOOL CALL [agent.tool_use] write args={'content': '# Review Blocked: claim referent `foo` does not resolve\n...(truncated in this report; full content is a ~2.5KB Markdown "REVIEW-BLOCKED-foo" document)...', 'file_path': '/mnt/session/outputs/REVIEW-BLOCKED-foo.md'}
AGENT MESSAGE: I could not produce a ruling, because `foo` doesn't identify anything reviewable.
...
```

(Full untruncated content is in the file itself at the path above — I have
not altered it. This particular run is a claim-slug-not-found edge case,
not a normal ruling, but it is the most complete self-contained example on
disk and demonstrates that stdout/log content is exclusively prose.)

### 3. Auth mechanism

`[read-from-source]` The Anthropic client is constructed with no explicit
credentials: `client = anthropic.Anthropic()` (line 761). Quoting the only
auth-adjacent lines in the file:

```python
from dotenv import load_dotenv
...
load_dotenv()
...
client = anthropic.Anthropic()
```

and the sole error-handling reference (line 989-991):

```python
except anthropic.AuthenticationError:
    print("Error: authentication failed — check ANTHROPIC_API_KEY.", file=sys.stderr)
```

`[executed]` — I inspected the installed `anthropic` SDK's
`Anthropic.__init__` signature in this environment: it accepts `api_key`,
`auth_token`, `credentials` (an `AccessTokenProvider`), `config`, `profile`,
`webhook_key`, etc., all defaulting to `None`/unset. `launch_review.py`
passes none of these — it relies on the SDK's default behavior of reading
`ANTHROPIC_API_KEY` from the environment, which `load_dotenv()` populates
from a local `.env` file if present.

**Direct answer: no, this path cannot block on interactive input.** There
is no OAuth flow, no browser consent screen, no TTY prompt, and no keychain
call anywhere in `launch_review.py` — the only two lines that touch
credentials are `load_dotenv()` (reads a `.env` file from disk,
non-interactive) and `anthropic.Anthropic()` (reads an env var,
non-interactive). If `ANTHROPIC_API_KEY` is unset or invalid, the SDK
raises `anthropic.AuthenticationError` synchronously and the launcher exits
via `sys.exit(1)` (line 991) — it fails fast rather than prompting.

The separate `CLAIMS_REVIEW_MEMORY_STORE_ID` env var (`get_memory_store_id`,
line 238) follows the identical pattern: `os.environ.get(...)`, raise
`RuntimeError` if absent (lines 244-250). Also non-interactive.

### 4. Tool list handed to the agent

`[read-from-source]` Tools are supplied in `build_agent`
(`server/agents/launch_review.py:196-235`) at agent-creation time, in two
groups:

```python
mcp_servers = [
    {"type": "url", "name": "claims-desk", "url": MCP_SERVER_URL},
]
tools = [
    {
        "type": "mcp_toolset",
        "mcp_server_name": "claims-desk",
        "default_config": {"enabled": True, "permission_policy": {"type": "always_allow"}},
    },
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},
        "configs": [
            {"type": "write", "name": "write", "enabled": True, "permission_policy": {"type": "always_allow"}},
            {"type": "read", "name": "read", "enabled": True, "permission_policy": {"type": "always_allow"}},
        ],
    },
]
```

This does **not** enumerate individual MCP tool names in code — it grants
the entire `claims-desk` MCP toolset via `default_config: {"enabled": True}`
with `permission_policy: always_allow`, plus the platform `read`/`write`
file tools (session filesystem, not registry tools).

`[executed]` — I queried the deployed MCP server directly
(`https://claims-desk-production-8424.up.railway.app/mcp`, JSON-RPC
`tools/list`, full response in Part 4) to determine what that toolset
actually contains. It exposes **seven** tools: `append_claim`,
**`append_ruling`**, `get_claim_status`, `check_substantiation`,
`classify_claim_risk`, `delete_claim`, `list_claims`.

**Direct answer: yes, `append_ruling` is among the tools available to the
agent.** Because `build_agent` grants the whole MCP toolset generically
(`enabled: True` for all tools on the server) rather than an explicit
allowlist, whatever the server exposes is what the agent gets — and the
server currently exposes `append_ruling`, a write-capable tool, alongside
two other write-capable tools that are also present: `append_claim` and
`delete_claim`. `classify_claim_risk` is read-only (it classifies risk, it
does not write) but is grouped with the write tools by the launcher's own
`PROHIBITED_TOOLS` set (line 58) — see the note below.

`[inferred]` — There is a real gap between what the agent is *granted*
(code-level, `mcp_toolset` with `always_allow`) and what the agent is *told*
it has (prompt-level, both `review_agent_memory_on.md` and
`review_agent_memory_off.md` state verbatim: "You have six MCP tools
connected: `append_claim`, `get_claim_status`, `check_substantiation`,
`classify_claim_risk`, `delete_claim`, and `list_claims`" — six named tools,
**`append_ruling` is not among them**). The prompt's enumeration predates
`append_ruling`'s existence on the server (per the repo's own commit
history — `append_ruling.py` exists under `server/tools/`, and
`feat(tools): expose convergence and rounds in latest_ruling payload`
appears in recent commit history) and was never updated. This means:

- The **prompt-level safety guidance** ("`append_claim`, `delete_claim`,
  and `classify_claim_risk` must never be used...") does not mention
  `append_ruling` at all, because the prompt's author did not know it would
  be present.
- The **code-level enforcement** (`PROHIBITED_TOOLS = {"append_claim",
  "delete_claim", "classify_claim_risk"}`, line 58, checked post-hoc by
  `check_for_prohibited_tool_calls`) also does not include `append_ruling`.
- Net effect: `append_ruling` is silently available to the agent, is not
  named as prohibited anywhere (prompt or code gate), and any call to it
  would not trigger `ProhibitedToolCallError`. Whether the agent would ever
  choose to call it is a runtime question out of scope for this static
  report (Week 21 Day 1), but the *permission surface* allowing it is
  confirmed present today.

To directly answer the two-part question: **`append_ruling` is among the
tools available to the agent** (via the generic toolset grant, confirmed
live against the server) **and is not gated by the launcher's
`PROHIBITED_TOOLS` check.** The other write-capable tools named in the
question, `append_claim` and `delete_claim`, **are** in `PROHIBITED_TOOLS`
and would trigger a hard failure (`ProhibitedToolCallError`, lines 165-193,
860-868) if called.

### 5. Skill loading

`[read-from-source]` **`claim-review` is not loaded by this launcher at
all** — not from a path, not at any point in prompt assembly. I searched
`launch_review.py` and both rendered prompt files
(`review_agent_memory_on.md`, `review_agent_memory_off.md`) for `SKILL.md`,
`skill`, `claim-review`, and `claim_review`; none of those strings appear
in `launch_review.py`, and the prompt files mention only **`claim-taxonomy`**
by name, in prose, twice (identically in both variants, e.g. line 82-85 of
`review_agent_memory_off.md`):

> "`check_substantiation` does not render a verdict — that judgment is
> yours, guided by the claim-taxonomy Skill, which remains the sole source
> of truth for what counts as sufficient evidence for each claim type."

This is a **prose reference to a skill by name**, not a file load. No
`SKILL.md` content (from either `claim-taxonomy` or `claim-review`) is read
from disk or embedded into the system prompt anywhere in `build_agent`,
`run_review`, or the prompt template files. The prompt is read once, in
full, as a static string:

```python
def build_agent(client: anthropic.Anthropic, variant: str) -> str:
    system_prompt = PROMPT_FILES[variant].read_text()
```

`PROMPT_FILES` (line 49-52) points only to `review_agent_memory_on.md` /
`review_agent_memory_off.md` — never to any `SKILL.md` path.

**Direct answer:** there is no switch, flag, or env var to omit
`claim-review`, because it is never loaded to begin with — nothing to
switch off. If the intent is for the *Managed Agents session itself* to be
able to load the `claim-review` skill (as opposed to the human user's
Claude Code session, which has it available per the environment listing),
that would require editing the launcher (or the prompt template) to fetch
and inject the skill file's content, or to grant the session a
skill-loading mechanism it does not currently have. This is not a
config-level change — it would be new functionality.

`[inferred]` — Given the strong naming and structural parallel between
`claim-taxonomy` (referenced by name in the prompt) and `claim-review`
(not referenced at all), it's likely the task's framing assumed
`claim-review` where the code actually references `claim-taxonomy`.
I'm flagging this rather than substituting one for the other, per the
"do not substitute a plausible answer" instruction.

### 6. Model string

`[read-from-source]` `server/agents/launch_review.py:55`:

```python
MODEL = "claude-opus-5"
```

Used at the single call site, `build_agent`, line 230: `model=MODEL` inside
`client.beta.agents.create(...)`.

### 7. Memory store wiring

`[read-from-source]` The wiring is present and substantial — it was **not**
removed. Grep results for the three requested symbols within
`launch_review.py`:

- **`memory`** — 40+ matches. Key structures: `get_memory_store_id()`
  (line 238), `build_session`'s `memory_store` resource block (lines
  260-278), `write_ruling_to_memory` (line 384), `maybe_write_ruling_to_memory`
  (line 435), `get_memory_mount_path` (line 737), `trace_probed_memory_mount`
  (line 549), and the whole `derive_manipulation_check` mechanism (line 574)
  that reasons about Memory probes.
- **`memory_store`** — used as: an env var name
  (`CLAIMS_REVIEW_MEMORY_STORE_ID`, line 244), a session resource
  `"type": "memory_store"` (line 266), and a client namespace
  (`client.beta.memory_stores.memories.create/list/update`, lines 408-431).
- **`session_id`** — used as a `RunLog.header` field (line 86, 95) and as
  the `scope_id` passed to `client.beta.files.list(scope_id=session_id,
  ...)` (line 321) for retrieving the ruling artifact. Not used as a
  cross-invocation cache key or reloaded from disk anywhere — each
  invocation creates a brand-new session (`client.beta.sessions.create`,
  line 273) and the `session_id` only flows forward within that single
  process run, into the run log and the `retest_sessions` DB table (line
  684-705). There is no code path that reads a previously-written
  `session_id` back in to resume or reload a prior session.

**Cross-invocation state that does exist:** the persistent Memory store
itself (`CLAIMS_REVIEW_MEMORY_STORE_ID`, one long-lived store ID reused
across every `memory_on` invocation, per its own docstring at line
239-243: "No fallback to creating a store... a missing or invalid ID must
fail loudly"), and the `retest_sessions` DB table (Week 19 item 7a,
inserted by `write_retest_session_row`, line 660) which records completed
runs — but this is written *after* a run completes, for later analysis; it
is not read back by the launcher to influence any future session.

**Cross-invocation state that does not exist:** no cache file, no
conversation transcript reload, no session resumption. Each `launch_review.py`
invocation is a self-contained, fresh session (per its own docstring:
"launch_review.py runs exactly one session per invocation and does no
sequencing" — quoted in `run_retest.py`'s header, line 13-14).

**On "Week 19 ran a Memory retest against this agent and killed it":**
`[inferred]` — I found direct evidence of a Week 19 Memory retest
*harness* (`server/agents/run_retest.py`, "Week 19 h1-r retest harness";
`retest_sessions` table migration at `server/db/migrate_week19_item7a.py`;
`docs/week19-locked-verdicts.md`; `docs/week19-criterion-scores-gap.md`)
that is fully built and wired into the launcher, with commits continuing
through 2026-09-01. I found **no** evidence in this file, its tests, or its
git history of the retest being "killed" — no revert commit, no disabling
flag, no removed code. Whether the *retest's outcome* (as opposed to the
code) was negative, and what "killed" refers to, is **not determined** —
I did not find a document stating a retest verdict one way or the other in
the files I examined (`docs/week19-criterion-scores-gap.md` and
`docs/week19-locked-verdicts.md` were not read in full for this item; a
full read of those two docs would be needed to resolve this precisely, and
I did not do so since it's adjacent to, not part of, the launcher symbol
trace this item asked for).

### 8. Grep for `current_status`

`[executed]` — repo-wide grep, symbol only, all text file types, excluding
`.git` and `node_modules`:

```
$ grep -rn "current_status" . 2>/dev/null | grep -v node_modules | grep -v '\.git/'
(no output)
```

**Zero hits repo-wide**, including zero hits in `server/agents/launch_review.py`
specifically (confirmed by the same command scoped and by direct inspection
while reading the file in full for this report). I did not find
`arm_b_workflow.js` or `arm_vendor_compliance.js` in the repo at all — a
separate `find . -iname "*arm_b_workflow*" -o -iname "*arm_vendor_compliance*"`
style check would be needed to confirm those files still exist under those
names if that matters to Week 20 Day 2's record; **not determined** whether
those two files exist post-fix or were renamed/removed, since I only ran
the symbol grep this item asked for. The repo-wide zero-hit result is
consistent with "Week 20 Day 2... fixed both; a repo-wide grep confirmed no
third site" and reconfirms it: still zero hits today, launcher path
included.

---

## Part 2 — The Python/Node boundary

**Direct answer: yes.** A Node process can spawn `launch_review.py`,
capture one response, and parse it, with no changes to the launcher.

Reason: `[read-from-source]` this exact pattern already exists in this
repo. `server/agents/run_retest.py:423` calls it precisely this way:

```python
proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
```

— a subprocess call capturing stdout/stderr as text, once per invocation
(Python calling Python here, but the mechanism a Node caller would use —
spawn a process, wait for exit, read captured stdout — is identical in
kind; `child_process.spawnSync` or `execFile` in Node do the same thing at
the OS level). Per item 2 above, `launch_review.py` takes pure argv input
(`--claim-slug`, `--variant`, etc.) and writes pure prose to stdout with
fixed, greppable delimiters (`"=" * 70`, literal headers `"RULING ARTIFACT"`,
`"GRADING RESULT"`, `f"Result: {outcome_result}"`, `f"Iterations: {iteration_count}"`).

A Node caller can: spawn the process with argv flags, wait for exit code
(0 = success per the `main()` structure; 1 = various failure branches at
lines 988/991/994/997/1000 with distinguishing text on stderr), and parse
stdout by locating the `"RULING ARTIFACT"` / `"GRADING RESULT"` banners and
slicing text between them — a **text-scraping parse**, not a JSON parse,
since stdout is not structured. This is parseable without modifying the
launcher; it is more brittle than JSON (a future change to
`print_ruling_and_grading`'s wording would break a naive scraper) but is
mechanically sufficient today.

If a more robust, non-scraping parse is wanted, the minimum change would be
small: add a `--json` flag to `main()` that, instead of (or in addition to)
the current `print_ruling_and_grading` calls, emits one
`json.dumps({...})` line containing `ruling_text`, `outcome_result`,
`outcome_explanation`, `iteration_count`, `session_id` — the same fields
`run_review()` already returns as a dict (lines 914-921). This is a
localized, additive change (new CLI flag + one new print branch), not a
rewrite. But the yes/no answer above does not depend on making this
change — it works today via text scraping.

---

## Part 3 — The claim-review Skill, current text

`[executed]` — found exactly two copies:

- `skills/claim-review/SKILL.md`
- `.claude/skills/claim-review/SKILL.md`

`[executed]` — byte-identity check via `diff` and `md5sum`:

```
$ diff skills/claim-review/SKILL.md .claude/skills/claim-review/SKILL.md
(no output — identical)
$ md5sum skills/claim-review/SKILL.md .claude/skills/claim-review/SKILL.md
f634ef1c1122da9228e897ef1ed77606  skills/claim-review/SKILL.md
f634ef1c1122da9228e897ef1ed77606  .claude/skills/claim-review/SKILL.md
```

**Confirmed byte-identical.**

**Important correction to the task's premise:** per Part 1 item 5,
`launch_review.py` does not load `claim-review/SKILL.md` from either path
— it does not load any `SKILL.md` at all. So there is no "copy the launcher
actually loads" to distinguish between these two paths; both are
equally unloaded by this launcher. I'm pasting the full current text of
`skills/claim-review/SKILL.md` below since the two are identical and one
of them is what a human Claude Code session (such as this one) would load
via the `claim-review` Skill tool — but this is **not** what the Week 18
agent session sees at runtime.

`[executed]` — `git log --oneline` for each path:

```
$ git log --oneline -- skills/claim-review/SKILL.md
75bad04 feat(tools): derive verification and evidence currency on read; deprecate claims.status; fix list_claims field collision
7961733 docs: add compatibility claim type to taxonomy and review skills
dae2c5c feat: author Claims Desk Agent Skills, verify progressive disclosure

$ git log --oneline -- .claude/skills/claim-review/SKILL.md
75bad04 feat(tools): derive verification and evidence currency on read; deprecate claims.status; fix list_claims field collision
7961733 docs: add compatibility claim type to taxonomy and review skills
dae2c5c feat: author Claims Desk Agent Skills, verify progressive disclosure
```

Identical commit history on both paths, including `75bad04` (the Week 20
claims.status deprecation reword the task references) — neither has
changed since that commit, and neither has diverged from the other at any
point in history.

Full current text of `skills/claim-review/SKILL.md`:

```markdown
---
name: claim-review
description: Conduct a marketing claim review for the Claims Desk — determine what counts as sufficient evidence, when a claim has expired, and when to escalate rather than rule directly. Use when reviewing, approving, rejecting, or triaging a marketing claim, or when asked to judge whether a claim is adequately substantiated.
license: Proprietary
metadata:
  author: richardthomchick
  version: "1.1"
  project: claims-desk
---

# Claim Review

This skill teaches how to conduct a claim review for the Claims Desk. It is a **reasoning** skill: it tells you how to judge a claim, not how to store or retrieve one. For the mechanics of reading and writing claims, use the Claims Desk MCP tools (`append_claim`, `get_claim_status`, `check_substantiation`, `classify_claim_risk`) — this skill tells you what to do with what those tools return.

## When this skill applies

Use this skill whenever you are asked to review a marketing claim: deciding whether it's adequately substantiated, whether it should be approved, rejected, or escalated, or whether it's safe to publish. This includes requests phrased as "is this claim OK to use," "review this claim," "can we say X," or any evaluation of a specific claim already in the registry.

This skill does not cover: adding a new claim to the registry (use `append_claim` directly), or determining a claim's risk classification as a standalone fact (use `classify_claim_risk` directly — that tool already applies deterministic rulesets and returns its own factors; this skill is about judgment, not repeating what that tool already computes).

## The review workflow

1. **Retrieve the claim.** Call `get_claim_status` to see the claim's type, its `verification` (the verdict of the most recent ruling, or `unreviewed` if none exists), and any prior ruling. If a ruling already exists, treat it as context, not as binding — evidence and expiry status can change.

2. **Pull the substantiation material.** Call `check_substantiation`. This returns the claim, its linked evidence, the evidence standard for its claim type, and a set of deterministic hygiene checks (evidence link present, expiry status, sample size present, platform lifecycle status, etc.). **This tool does not render a verdict — that judgment is yours.** Do not treat the absence of a verdict field as an oversight; it's deliberate. See `references/evidence-standards.md` for what "sufficient" means per claim type.

3. **Check the deterministic layer first.** The hygiene checks from `check_substantiation` are facts, not opinions — if `is_expired: true`, the claim fails regardless of anything else about it. If `has_evidence_link: false`, there is nothing to evaluate yet. Handle these before spending judgment on anything softer. A claim can fail on hygiene alone; don't reach for nuanced reasoning about evidence quality if the evidence doesn't exist at all.

4. **Apply the claim-strength check.** Read the claim's exact wording, not just its category. A claim phrased with an explicit support level ("tests show," "proven to," "studies confirm") carries a higher evidentiary bar than the same underlying fact phrased more softly ("up to X%," "typical results may vary"). This is judgment, not a lookup — weigh the claim's own language against what the evidence actually supports. See `references/evidence-standards.md` for the reasoning behind this and worked examples per claim type.

5. **Judge sufficiency against the claim type's evidence standard.** Each of the five claim types (Performance, Comparative, Compliance, Superlative, Compatibility) has a distinct standard — see the `claim-taxonomy` skill's `references/evidence-standards-by-type.md`. Don't apply one type's standard to another; a Superlative claim's evidence bar is not the same shape as a Performance claim's.

6. **Decide: approve, reject, or escalate.** Approve only when the deterministic checks pass and the judgment layer supports the claim as worded. Reject when either layer clearly fails. **Escalate rather than rule when the call is genuinely close** — see "When to escalate" below. Do not force a binary decision on a claim that's legitimately ambiguous; a wrong confident ruling is worse than an honest escalation.

7. **Record the ruling.** State your ruling, the specific reasoning (which hygiene checks passed/failed, what the claim-strength check found, why the evidence standard was or wasn't met), and if escalating, exactly what a human reviewer needs to resolve. Do not just state a verdict — the reasoning is what makes the ruling auditable and correctable.

## When to escalate rather than rule

Escalate when:
- The evidence technically meets the deterministic bar but the claim-strength check finds a mismatch between how confidently the claim is worded and what the evidence actually shows (e.g., "proven" language backed by a single small sample)
- A claim's risk classification (`classify_claim_risk`) returns `prohibited` or `high` but the evidence, on inspection, looks stronger than the deterministic factors suggest — this is a signal the rulesets may be missing context a human should weigh in on, not a signal to override the classifier yourself
- The claim type's evidence standard is genuinely ambiguous as applied to this specific claim (for example, a Comparative claim against a competitor whose product has since changed significantly)
- You find yourself constructing a justification for a ruling rather than reading one off the evidence — that's usually a sign the call is closer than it feels

Do not escalate reflexively for every claim with any imperfection — most claims with complete evidence and appropriately-hedged language should be ruled on directly. Escalation exists for genuine judgment calls, not as a way to avoid making any decision.

## What this skill does not do

This skill does not provide legal advice. A claim being adequately substantiated under FTC "reasonable basis" doctrine is a factual and evidentiary judgment, not a determination of legal risk or liability — those are different questions, and a legal review may still be warranted even for a claim this skill would approve.
```

**References directories:** `[executed]` — both paths have an identical
sibling `references/` directory containing only `evidence-standards.md`
(4747 bytes, same size both places):

```
skills/claim-review/references/evidence-standards.md
.claude/skills/claim-review/references/evidence-standards.md
```

**`claim-type-taxonomy.md` does not exist under either `claim-review`
copy's `references/` directory** — only `evidence-standards.md` is present
in `claim-review/references/`. A file named `evidence-standards-by-type.md`
(not `claim-type-taxonomy.md`) exists, but under the separate
**`claim-taxonomy`** skill's `references/` directory instead
(`skills/claim-taxonomy/references/evidence-standards-by-type.md` and
`.claude/skills/claim-taxonomy/references/evidence-standards-by-type.md`),
not under `claim-review`. So: `references/evidence-standards.md` exists
alongside the loaded copy — confirmed. `references/claim-type-taxonomy.md`
as named in the task **does not exist anywhere in the repo** under that
exact name; the closest match is a different file, in a different skill's
references directory.

And per Part 1 item 5: **the launcher loads neither SKILL.md nor either
references file** — it loads only `review_agent_memory_on.md` /
`review_agent_memory_off.md`, which reference `claim-taxonomy` by name in
prose but embed none of that skill's file content.

---

## Part 4 — Deployed tool surface

`[executed]` — queried directly over HTTP, JSON-RPC `tools/list`, no
connector/cached schema involved:

```
$ curl -s -X POST https://claims-desk-production-8424.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Raw response (reformatted for readability; content is otherwise verbatim):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {"name": "append_claim", "description": "Add a claim to the registry, with optional evidence. Returns the new claim_id. ...", "inputSchema": {"properties": {"product_key": {"type": "string"}, "claim_type": {"type": "string"}, "claim_text": {"type": "string"}, "evidence_url": {"...": "nullable string"}, "evidence_date": {"...": "nullable string"}, "sample_size": {"...": "nullable integer"}, "baseline": {"...": "nullable string"}, "expiry_date": {"...": "nullable string"}, "scope": {"...": "nullable string"}, "platform": {"...": "nullable string"}, "platform_version": {"...": "nullable string"}, "component_revision": {"...": "nullable string"}, "written_by_session": {"...": "nullable string"}}, "required": ["product_key", "claim_type", "claim_text"]}},
      {"name": "append_ruling", "description": "Insert a review ruling. Append-only: no updates, no upserts — a correction is a new row with a later created_at for the same claim_id. verdict: one of substantiated, partially, not_substantiated, escalate. convergence: attack_exhaustion or round_cap. reviewed_by, written_by_session.", "inputSchema": {"properties": {"claim_id": {"type": "string"}, "verdict": {"type": "string"}, "rationale": {"...": "nullable string"}, "reviewed_by": {"...": "nullable string"}, "convergence": {"...": "nullable string"}, "rounds": {"...": "nullable integer"}, "written_by_session": {"...": "nullable string"}}, "required": ["claim_id", "verdict"]}},
      {"name": "get_claim_status", "description": "Read a claim's current status, linked evidence, and most recent review ruling.", "inputSchema": {"properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
      {"name": "check_substantiation", "description": "Return a claim, its evidence, the evidence standard for its claim type, and deterministic hygiene checks. Does not render a substantiation verdict.", "inputSchema": {"properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
      {"name": "classify_claim_risk", "description": "Classify a claim's risk (low/medium/high/prohibited) with contributing factors.", "inputSchema": {"properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
      {"name": "delete_claim", "description": "Soft-delete a claim (record_status -> 'deleted'). Returns {deleted: true, claim_id} on success.", "inputSchema": {"properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
      {"name": "list_claims", "description": "Enumerate claims by type/status/product. status is 'active' (default), 'deleted', or 'all'. Returns slug-first summaries — claim_slug, claim_id, product_key, claim_type, status, risk_class — with no evidence payload.", "inputSchema": {"properties": {"claim_type": {"...": "nullable string"}, "status": {"...": "nullable string"}, "product_key": {"...": "nullable string"}}}, "outputSchema": {"properties": {"result": {"type": "array", "items": {"type": "object"}}}, "required": ["result"]}}
    ]
  }
}
```

(The exact byte-for-byte raw JSON, unformatted, is longer; the content
above preserves every field name, tool name, description, and required/
optional marking verbatim from that response. Nullable unions were
rendered by the server as `anyOf: [{type}, {type: null}]` — abbreviated
here as "nullable X" for readability, with no information dropped.)

**Full tool list (7 tools):** `append_claim`, `append_ruling`,
`get_claim_status`, `check_substantiation`, `classify_claim_risk`,
`delete_claim`, `list_claims`.

**Response shape field names** — `tools/list` only publishes an
`outputSchema` for `list_claims` (generic `{result: [...]}`, items
`additionalProperties: true`, no field-level detail). `get_claim_status`
and `check_substantiation` have no `outputSchema` in the MCP listing at
all, so their response field names are not observable from the
`tools/list` call alone.

`[read-from-source]` — to answer the task's specific question about field
names, I read the server's tool implementations directly
(`server/tools/get_claim_status.py`, `server/tools/check_substantiation.py`).
Both confirm the exact names requested:

- `get_claim_status` returns `{"claim": {..., "verification": <verdict-or-"unreviewed">, "evidence_current": <bool-or-None>, ...}, "evidence": [...], "latest_ruling": {"ruling_id", "verdict", "rationale", "reviewed_by", "created_at", "convergence", "rounds"} or None}`.
- `check_substantiation` returns `{"claim": {..., "verification": ..., "evidence_current": ...}, "evidence": [...], "evidence_standard": "<str>", "hygiene_checks": {"has_evidence_link", "has_evidence_date", "is_expired", "has_sample_size", "platform_lifecycle_status"}}`.

**Confirmed: `verification` and `evidence_current` exist on `claim` in both
tools' responses, and `latest_ruling.convergence` exists in
`get_claim_status`'s response, all under those exact names** — but this
confirmation is `[read-from-source]` against the tool implementation code
in this checkout, not `[executed]` against the live server's actual
response bytes (the live server was only queried for its tool list/schema
in Part 4, per the "do not call any write tool" constraint, and there is no
read-only way to invoke `get_claim_status`/`check_substantiation` without a
real `claim_id` in a context this report doesn't have license to fetch and
exercise as a live call). If a live response body is needed, that requires
an actual tool invocation, which is out of scope for this static report and
would need Week 21 Day 1's runtime pass.

No write tool (`append_claim`, `append_ruling`, `delete_claim`) was called
at any point in this investigation.

---

## Definition-of-done checklist

- Report written to `week21_day0_endpoint1_report.md` at repo root: done.
- Printed to stdout: done (this message; also see the terminal transcript).
- File is not committed, not staged: confirmed below.
- Every numbered item answered or marked "not determined": done — see
  Part 1 item 7 (retest "killed" status) and Part 1 item 8 (whether
  `arm_b_workflow.js`/`arm_vendor_compliance.js` still exist under those
  names) for the two items marked not determined.
- Every claim labeled `[read-from-source]`, `[executed]`, or `[inferred]`:
  done throughout.
- No source file modified.
