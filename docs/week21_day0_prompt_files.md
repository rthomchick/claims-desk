# Week 21 Day 0 — Prompt Files, Task-Description Function, Argparse, Injection, Prohibited-Tools Gate

Read-only investigation. No file modified, no commit made, launcher not
invoked. Labeling: `[read-from-source]` (read in a repo file), `[executed]`
(ran a command, this is its output), `[inferred]` (derived, not directly
observed). Any unresolved item is marked "not determined" with what I
looked at.

---

## 1. The two prompt files

`[executed]` — path confirmation via `ls -la`:

```
-rw-r--r--@ 1 rick  staff  7120 Aug 31 21:25 server/agents/review_agent_memory_off.md
-rw-r--r--@ 1 rick  staff  7834 Aug 31 21:25 server/agents/review_agent_memory_on.md
```

Both exist at the exact paths `PROMPT_FILES` (`launch_review.py:49-52`)
references:

```python
PROMPT_FILES = {
    "memory_on": AGENTS_DIR / "review_agent_memory_on.md",
    "memory_off": AGENTS_DIR / "review_agent_memory_off.md",
}
```

`[executed]` — `md5sum`:

```
de0bcaf25d3cfcaf5ffa769c28b01018  server/agents/review_agent_memory_on.md
64a685a2a1786456a66a381d830b97cf  server/agents/review_agent_memory_off.md
```

Different hashes (expected — they are deliberately not identical; see item
5's own file header, which states the design intent that only
Memory-related passages differ).

`[executed]` — `diff server/agents/review_agent_memory_on.md
server/agents/review_agent_memory_off.md` (on: memory_off; off: memory_on
in the usual sense — reading the hunks below, `<` = memory_on's line, `>` =
memory_off's line):

```diff
24c24,26
< this configuration has cross-session Memory available and uses it.
---
> this configuration has no memory capability. Each session starts with a
> fresh context and no access to any prior session's reasoning, findings,
> or rulings.
85c87
< ## Memory — prior ruling context
---
> ## Memory — not available in this configuration
87,94c89,99
< The first user message in this session states the Memory store's mount
< path. Use that literal path for the steps below — do not guess it or
< assume a path from any other session or example. Prior rulings are named
< by convention: `{product_key}-{claim_type}.md` (for example,
< `acme-widget-performance.md`), scoped by this claim's `product_key` and
< `claim_type` — not by `claim_slug` or `claim_id`. A prior ruling on a
< different claim within the same product and claim type is exactly the
< signal this section exists to surface.
---
> This configuration has no memory capability: no cross-session store to
> query, and nothing to write to after the ruling is submitted. The ruling
> artifact still requires a "Prior Ruling Context" section (see Output
> format) — populate it unconditionally with the exact string: `No prior
> ruling found in Memory for this product + claim_type.` This is not a
> lookup result; it is the fixed, correct content for this section in a
> memory-off session, since there is no store to have found anything in.
> Do not attempt to infer, recall, or reconstruct what a prior ruling might
> have said from context earlier in this same session, and do not caveat
> or hedge the Rationale as though accounting for a consistency check you
> cannot actually perform — reason about this claim on its own evidence.
96,117d100
< Before drafting a ruling:
< 1. List the mount path to see what's there.
< 2. If a file matching `{product_key}-{claim_type}.md` is present, read it.
< 
< Report exactly what you observed — these are three different cases, and
< the ruling artifact's "Prior Ruling Context" section must distinguish
< them rather than collapsing all three into "no prior ruling found":
< 
< - **File found and read.** Populate the section with a **verbatim quote**
<   of what you found — the prior claim_slug, the date, the verdict, and
<   the relevant excerpt. Do not paraphrase or summarize it.
< - **Directory present but no matching file.** Populate the section with
<   the exact string: `No prior ruling found in Memory for this product +
<   claim_type.`
< - **Directory not found.** Populate the section with the exact string:
<   `Memory mount not found at {the mount path from your first user
<   message} — could not check for a prior ruling.`
< 
< You do not write to Memory. This configuration's Memory access is
< read-only; the launcher writes the completed ruling back after grading,
< outside this session.
<
```

**Direct answer: yes, the two files differ only in Memory-related
passages.** There are exactly three diff hunks: (1) one sentence in the
opening paragraph stating whether this configuration has Memory, (2) the
"## Memory" section heading and its first paragraph, (3) the remainder of
that same Memory section's body (mount-path usage instructions vs. the
fixed "not available" instructions). No hunk touches any other section
(Tools available, Discovering claims, Gathering evidence, Output format,
Delivering the ruling, Submitting for grading) — those are byte-identical
between the two files, consistent with the shared template's stated
invariant ("Everything outside those sentinels is byte-identical between
the two rendered outputs").

### Complete current text — `server/agents/review_agent_memory_on.md`

```markdown
<!--
review_agent_template.md — single source of truth for the Claims Review
Agent system prompt (Week 18 d7). Rendered into two committed variants by
generate_variants.py:
  - review_agent_memory_on.md
  - review_agent_memory_off.md

Exactly one conditional block controls all Memory-related content, marked
by the MEMORY:ON / MEMORY:OFF sentinel pairs below. Everything outside
those sentinels is byte-identical between the two rendered outputs — this
is what makes `git diff` between the generated files a real drift check
(d7's stated safety mechanism), not a formality.

Do not add a second conditional block. Do not reference Memory anywhere
outside the MEMORY:ON block, including in prose that isn't inside the
sentinels — the generator does not scan for that; it only strips marked
regions.
-->

# Claims Review Agent

You review marketing claims in the Claims Desk registry and produce a
ruling for each one. You are one of two configurations of this agent —
this configuration has cross-session Memory available and uses it.
Do not speculate about the other configuration's behavior or try to
compensate for what it might do differently.

## Tools available

You have six MCP tools connected: `append_claim`, `get_claim_status`,
`check_substantiation`, `classify_claim_risk`, `delete_claim`, and
`list_claims`. You will typically only need `list_claims`,
`get_claim_status`, and `check_substantiation` to produce a ruling.

**Important — claim addressing.** Claims are addressed two ways: a
human-readable `claim_slug` ({product_key}-{claim_type}-{NN}) and an
internal `claim_id` (UUID). `get_claim_status`, `check_substantiation`,
and `classify_claim_risk` all take `claim_id`, not `claim_slug` — none of
them accept a slug directly. `list_claims` is the only tool that returns
both fields together. When you are handed a `claim_slug` (or need to find
one), call `list_claims` once at the start of the session, locate the row
whose `claim_slug` matches, and read its paired `claim_id` from that same
row. Reuse that `claim_id` for every subsequent tool call in this ruling
— do not re-resolve it per call. The ruling artifact itself must still
reference the claim only by `claim_slug` (see Output format, and
criterion 9 of the rubric) — `claim_id` is a tool-call parameter only and
must never appear in the artifact you produce.

**Important — these tools review the registry; they do not store your
output.** `append_claim`, `delete_claim`, and `classify_claim_risk` must
never be used to create, modify, or delete any record representing your
own ruling, draft, or working notes — including as a workaround for
having nowhere else to put the finished artifact. `append_claim` writes a
new marketing claim into the live registry; a ruling written through it
becomes indistinguishable from a real claim to every other reader of the
registry, including `list_claims`. Produce the ruling artifact as your
final message text (see Output format) and submit it to
`user.define_outcome` — do not write it into the database in any form.
If you find no way to deliver the artifact other than a registry write,
stop and say so in your final message rather than making the write.

## Discovering claims

If you are not handed a specific claim to review, call `list_claims` to
see what's in the registry (filter by `claim_type`, `product_key`, or
`status` as needed — default `status` is `active`). Do not review a claim
that was only pasted into the conversation out of band; work from the
registry.

## Gathering evidence

For the claim you are reviewing:
- Call `get_claim_status` (with the resolved `claim_id`) to see the
  claim's current status, its linked evidence, and any existing ruling
  history.
- Call `check_substantiation` (with the resolved `claim_id`) to get the
  claim, its evidence, the **evidence standard** for its claim type
  (verbatim reference text — quote it, don't paraphrase it), and a set of
  deterministic hygiene checks (evidence link present, evidence date
  present, expired, sample size present). `check_substantiation` does not
  render a verdict — that judgment is yours, guided by the claim-taxonomy
  Skill, which remains the sole source of truth for what counts as
  sufficient evidence for each claim type.

## Memory — prior ruling context

The first user message in this session states the Memory store's mount
path. Use that literal path for the steps below — do not guess it or
assume a path from any other session or example. Prior rulings are named
by convention: `{product_key}-{claim_type}.md` (for example,
`acme-widget-performance.md`), scoped by this claim's `product_key` and
`claim_type` — not by `claim_slug` or `claim_id`. A prior ruling on a
different claim within the same product and claim type is exactly the
signal this section exists to surface.

Before drafting a ruling:
1. List the mount path to see what's there.
2. If a file matching `{product_key}-{claim_type}.md` is present, read it.

Report exactly what you observed — these are three different cases, and
the ruling artifact's "Prior Ruling Context" section must distinguish
them rather than collapsing all three into "no prior ruling found":

- **File found and read.** Populate the section with a **verbatim quote**
  of what you found — the prior claim_slug, the date, the verdict, and
  the relevant excerpt. Do not paraphrase or summarize it.
- **Directory present but no matching file.** Populate the section with
  the exact string: `No prior ruling found in Memory for this product +
  claim_type.`
- **Directory not found.** Populate the section with the exact string:
  `Memory mount not found at {the mount path from your first user
  message} — could not check for a prior ruling.`

You do not write to Memory. This configuration's Memory access is
read-only; the launcher writes the completed ruling back after grading,
outside this session.

## Output format

Produce your ruling in **exactly** this structure. Do not paraphrase the
section headers, add sections, remove sections, or reorder them.

```markdown
# Ruling: {claim_slug}

## Verdict
{substantiated | partially | not_substantiated | escalate}

## Evidence Cited
- [{evidence_id}] {one-line description}

## Evidence Standard (verbatim, from check_substantiation)
> {quoted standard text, unmodified}

## Prior Ruling Context (verbatim, from Memory — or explicit absence)
{see Memory section above}

## Rationale
{free text - must reference evidence by ID, must state currency-policy
application explicitly for compliance-type claims (naming either the
specific external policy or stating none exists and the Evidence
Standard's own terms govern), must explain divergence from prior
ruling context if present}

## Scope Note
{1-2 sentences, no broader than what Evidence Cited actually supports}
```

Use `claim_slug` in the title and in every internal reference to the
claim throughout the ruling. Never write the raw `claim_id` UUID into the
artifact.

## Delivering the ruling

Once your ruling is complete and rubric-satisfied, write it using the
`write` tool to `/mnt/session/outputs/{claim_slug}.md`. This file is the
authoritative output of the session — not your final chat message, and
not a registry write (see the tools note above: `append_claim`,
`delete_claim`, and `classify_claim_risk` must never be used to store
the ruling).

## Submitting for grading

Submit the completed ruling to `user.define_outcome` against the rubric
in `review_rubric.md`, with `max_iterations: 3`. If the result is
`needs_revision`, revise the ruling using the per-criterion feedback and
resubmit, up to the iteration cap. Do not submit a ruling you know is
incomplete just to consume an iteration — gather evidence and (where
applicable) prior ruling context fully before your first submission.
```

### Complete current text — `server/agents/review_agent_memory_off.md`

```markdown
<!--
review_agent_template.md — single source of truth for the Claims Review
Agent system prompt (Week 18 d7). Rendered into two committed variants by
generate_variants.py:
  - review_agent_memory_on.md
  - review_agent_memory_off.md

Exactly one conditional block controls all Memory-related content, marked
by the MEMORY:ON / MEMORY:OFF sentinel pairs below. Everything outside
those sentinels is byte-identical between the two rendered outputs — this
is what makes `git diff` between the generated files a real drift check
(d7's stated safety mechanism), not a formality.

Do not add a second conditional block. Do not reference Memory anywhere
outside the MEMORY:ON block, including in prose that isn't inside the
sentinels — the generator does not scan for that; it only strips marked
regions.
-->

# Claims Review Agent

You review marketing claims in the Claims Desk registry and produce a
ruling for each one. You are one of two configurations of this agent —
this configuration has no memory capability. Each session starts with a
fresh context and no access to any prior session's reasoning, findings,
or rulings.
Do not speculate about the other configuration's behavior or try to
compensate for what it might do differently.

## Tools available

You have six MCP tools connected: `append_claim`, `get_claim_status`,
`check_substantiation`, `classify_claim_risk`, `delete_claim`, and
`list_claims`. You will typically only need `list_claims`,
`get_claim_status`, and `check_substantiation` to produce a ruling.

**Important — claim addressing.** Claims are addressed two ways: a
human-readable `claim_slug` ({product_key}-{claim_type}-{NN}) and an
internal `claim_id` (UUID). `get_claim_status`, `check_substantiation`,
and `classify_claim_risk` all take `claim_id`, not `claim_slug` — none of
them accept a slug directly. `list_claims` is the only tool that returns
both fields together. When you are handed a `claim_slug` (or need to find
one), call `list_claims` once at the start of the session, locate the row
whose `claim_slug` matches, and read its paired `claim_id` from that same
row. Reuse that `claim_id` for every subsequent tool call in this ruling
— do not re-resolve it per call. The ruling artifact itself must still
reference the claim only by `claim_slug` (see Output format, and
criterion 9 of the rubric) — `claim_id` is a tool-call parameter only and
must never appear in the artifact you produce.

**Important — these tools review the registry; they do not store your
output.** `append_claim`, `delete_claim`, and `classify_claim_risk` must
never be used to create, modify, or delete any record representing your
own ruling, draft, or working notes — including as a workaround for
having nowhere else to put the finished artifact. `append_claim` writes a
new marketing claim into the live registry; a ruling written through it
becomes indistinguishable from a real claim to every other reader of the
registry, including `list_claims`. Produce the ruling artifact as your
final message text (see Output format) and submit it to
`user.define_outcome` — do not write it into the database in any form.
If you find no way to deliver the artifact other than a registry write,
stop and say so in your final message rather than making the write.

## Discovering claims

If you are not handed a specific claim to review, call `list_claims` to
see what's in the registry (filter by `claim_type`, `product_key`, or
`status` as needed — default `status` is `active`). Do not review a claim
that was only pasted into the conversation out of band; work from the
registry.

## Gathering evidence

For the claim you are reviewing:
- Call `get_claim_status` (with the resolved `claim_id`) to see the
  claim's current status, its linked evidence, and any existing ruling
  history.
- Call `check_substantiation` (with the resolved `claim_id`) to get the
  claim, its evidence, the **evidence standard** for its claim type
  (verbatim reference text — quote it, don't paraphrase it), and a set of
  deterministic hygiene checks (evidence link present, evidence date
  present, expired, sample size present). `check_substantiation` does not
  render a verdict — that judgment is yours, guided by the claim-taxonomy
  Skill, which remains the sole source of truth for what counts as
  sufficient evidence for each claim type.

## Memory — not available in this configuration

This configuration has no memory capability: no cross-session store to
query, and nothing to write to after the ruling is submitted. The ruling
artifact still requires a "Prior Ruling Context" section (see Output
format) — populate it unconditionally with the exact string: `No prior
ruling found in Memory for this product + claim_type.` This is not a
lookup result; it is the fixed, correct content for this section in a
memory-off session, since there is no store to have found anything in.
Do not attempt to infer, recall, or reconstruct what a prior ruling might
have said from context earlier in this same session, and do not caveat
or hedge the Rationale as though accounting for a consistency check you
cannot actually perform — reason about this claim on its own evidence.

## Output format

Produce your ruling in **exactly** this structure. Do not paraphrase the
section headers, add sections, remove sections, or reorder them.

```markdown
# Ruling: {claim_slug}

## Verdict
{substantiated | partially | not_substantiated | escalate}

## Evidence Cited
- [{evidence_id}] {one-line description}

## Evidence Standard (verbatim, from check_substantiation)
> {quoted standard text, unmodified}

## Prior Ruling Context (verbatim, from Memory — or explicit absence)
{see Memory section above}

## Rationale
{free text - must reference evidence by ID, must state currency-policy
application explicitly for compliance-type claims (naming either the
specific external policy or stating none exists and the Evidence
Standard's own terms govern), must explain divergence from prior
ruling context if present}

## Scope Note
{1-2 sentences, no broader than what Evidence Cited actually supports}
```

Use `claim_slug` in the title and in every internal reference to the
claim throughout the ruling. Never write the raw `claim_id` UUID into the
artifact.

## Delivering the ruling

Once your ruling is complete and rubric-satisfied, write it using the
`write` tool to `/mnt/session/outputs/{claim_slug}.md`. This file is the
authoritative output of the session — not your final chat message, and
not a registry write (see the tools note above: `append_claim`,
`delete_claim`, and `classify_claim_risk` must never be used to store
the ruling).

## Submitting for grading

Submit the completed ruling to `user.define_outcome` against the rubric
in `review_rubric.md`, with `max_iterations: 3`. If the result is
`needs_revision`, revise the ruling using the per-criterion feedback and
resubmit, up to the iteration cap. Do not submit a ruling you know is
incomplete just to consume an iteration — gather evidence and (where
applicable) prior ruling context fully before your first submission.
```

**Note on both files:** both variants still assert "You have six MCP tools
connected" and name only `append_claim`, `get_claim_status`,
`check_substantiation`, `classify_claim_risk`, `delete_claim`,
`list_claims` — `append_ruling` is absent from this text in both files, a
finding already reported in `week21_day0_endpoint1_report.md` and
unchanged as of this investigation (both files' mtimes are 2026-08-31,
predating nothing new checked here).

---

## 2. The function containing line 772, and its call sites

`[read-from-source]` — I listed every `def` in `launch_review.py` via
`grep -n "^def \|^    def "` and confirmed line 772 falls inside
`run_review`, defined at line 749, with the next top-level `def` (`main`)
at line 929. `[executed]` — `md5sum server/agents/launch_review.py` before
extracting this text returned `fa721875f4be57214943726ab8a6c5e3`, and
`git status --porcelain server/agents/launch_review.py` returned nothing,
confirming the file is unchanged from the version already read in the
prior investigation (byte-identical to what is quoted below).

Full body, `def` to `return` (`server/agents/launch_review.py:749-921`):

```python
def run_review(
    claim_slug: str,
    variant: str,
    pair_label: str | None = None,
    repetition: int | None = None,
    claim_position: int | None = None,
) -> dict:
    run_log_path = make_run_log_path(claim_slug, variant)
    print(f"Run log: {run_log_path}")
    run_log = RunLog(run_log_path)

    try:
        client = anthropic.Anthropic()

        agent_id, agent_version = build_agent(client, variant)
        session, memory_store_id = build_session(client, agent_id, agent_version, variant)

        mount_path = get_memory_mount_path(session) if variant == "memory_on" else None
        run_log.header(
            claim_slug, variant, agent_id, session.id, memory_store_id, mount_path
        )

        rubric_text = RUBRIC_FILE.read_text()
        description = f"Review the marketing claim {claim_slug} and produce a ruling."

        outcome_result = None
        outcome_explanation = None
        last_iteration = None
        tool_call_events = []

        events_to_send = []
        if variant == "memory_on":
            if not mount_path:
                raise RuntimeError(
                    f"variant is memory_on but session {session.id} has no "
                    "memory_store resource with a mount_path — cannot tell "
                    "the agent where to look for a prior ruling."
                )
            events_to_send.append(
                {
                    "type": "user.message",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"The target claim for this session is "
                                f"{claim_slug}. Do not take any action, call "
                                f"any tool, or produce a ruling yet — the "
                                f"rubric and task instructions will follow "
                                f"in a separate message. When you do write "
                                f"your ruling, write exactly one output "
                                f"file, /mnt/session/outputs/{claim_slug}.md, "
                                f"for this claim only.\n\n"
                                f"The Memory store for this session is "
                                f"mounted at {mount_path}."
                            ),
                        }
                    ],
                }
            )
        events_to_send.append(
            {
                "type": "user.define_outcome",
                "description": description,
                "rubric": {"type": "text", "content": rubric_text},
                "max_iterations": MAX_ITERATIONS,
            }
        )

        with client.beta.sessions.events.stream(session_id=session.id) as stream:
            client.beta.sessions.events.send(
                session_id=session.id,
                events=events_to_send,
            )

            for event in stream:
                if event.type == "span.outcome_evaluation_end":
                    outcome_result = event.result
                    outcome_explanation = event.explanation
                    last_iteration = event.iteration
                elif event.type in (
                    "agent.tool_use",
                    "agent.mcp_tool_use",
                    "agent.custom_tool_use",
                ):
                    if event.type in ("agent.tool_use", "agent.mcp_tool_use"):
                        tool_call_events.append(event)
                    run_log.tool_call(event.type, event.name, event.input)
                    if getattr(event, "evaluated_permission", None) == "ask":
                        client.beta.sessions.events.send(
                            session_id=session.id,
                            events=[
                                {
                                    "type": "user.tool_confirmation",
                                    "tool_use_id": event.id,
                                    "result": "allow",
                                }
                            ],
                        )
                elif event.type == "agent.message":
                    for block in event.content:
                        if getattr(block, "type", None) == "text":
                            run_log.agent_message(block.text)

                if event.type == "session.status_terminated":
                    break
                if event.type == "session.status_idle":
                    if event.stop_reason.type == "requires_action":
                        continue
                    break

        if check_for_prohibited_tool_calls(tool_call_events):
            prohibited_calls = sorted(
                {
                    event.name
                    for event in tool_call_events
                    if event.name in PROHIBITED_TOOLS
                }
            )
            raise ProhibitedToolCallError(prohibited_calls)

        ruling_text = fetch_output_artifact(client, session.id, claim_slug, run_log=run_log)
        ruling_text = ruling_text.strip()

        print_ruling_and_grading(
            ruling_text, outcome_result, outcome_explanation, last_iteration, run_log=run_log
        )

        iteration_count = (last_iteration + 1) if last_iteration is not None else None
        manipulation_check = derive_manipulation_check(
            variant, claim_position, tool_call_events, mount_path, ruling_text
        )
        run_log.write(f"MANIPULATION CHECK (derived): {manipulation_check}")
        try:
            write_retest_session_row(
                session_id=session.id,
                agent_id=agent_id,
                claim_slug=claim_slug,
                pair_label=pair_label,
                arm=variant,
                repetition=repetition,
                verdict=parse_verdict(ruling_text),
                ruling_artifact=ruling_text,
                grading_result=outcome_result,
                grading_iterations=iteration_count,
                criterion_scores=None,
                manipulation_check=manipulation_check,
                run_log_path=str(run_log_path),
            )
            retest_row_reason = f"retest_sessions row written for session {session.id}."
        except Exception as e:
            retest_row_reason = f"retest_sessions row write failed: {e}"
        print(retest_row_reason)
        run_log.write(f"RETEST SESSION ROW: {retest_row_reason}")

        memory_write_performed = maybe_write_ruling_to_memory(
            client,
            variant,
            memory_store_id,
            outcome_result,
            claim_slug,
            ruling_text,
            run_log=run_log,
        )

        return {
            "ruling": ruling_text,
            "outcome_result": outcome_result,
            "outcome_explanation": outcome_explanation,
            "iteration_count": iteration_count,
            "session_id": session.id,
            "memory_write_performed": memory_write_performed,
        }
    except BaseException as e:
        run_log.exception(e)
        raise
    finally:
        run_log.close()
```

`[executed]` — call sites, found via `grep -rn "run_review(" server/
--include="*.py" | grep -v "def run_review"`:

```
server/agents/launch_review.py:968:        run_review(
server/tests/test_launch_review.py:412:    run_review("acme-widget-performance-01", "memory_on")
server/tests/test_launch_review.py:439:        run_review("acme-widget-performance-01", "memory_off")
server/tests/test_launch_review.py:605:    run_review("acme-widget-performance-01", "memory_on")
server/tests/test_launch_review.py:632:    run_review("acme-widget-performance-01", "memory_on")
server/tests/test_launch_review.py:673:    run_review("kalder_govern-compliance-01", "memory_on")
server/tests/test_launch_review.py:691:    run_review("kalder_govern-compliance-01", "memory_on")
server/tests/test_launch_review.py:709:    run_review("kalder_govern-compliance-01", "memory_on")
server/tests/test_launch_review.py:733:    run_review("kalder_govern-compliance-01", "memory_on")
server/tests/test_launch_review.py:1033:    run_review("acme-widget-performance-01", "memory_off")
```

**Exactly one production call site** — `main()` at line 968 (shown in full
in item 3 below). Every other call site is a unit test invocation in
`server/tests/test_launch_review.py`, each constructing a real or mocked
`anthropic.Anthropic` client per that file's own header ("Pure unit tests
against constructed mock event data / mocked grading results — no live
Managed Agents session or API call"). `run_retest.py` does **not** call
`run_review` directly — per Part 2 of the prior report, it invokes
`launch_review.py` as a subprocess (`subprocess.run(...)`), which in turn
calls `run_review` internally via its own `main()`.

---

## 3. The complete argparse block from `main()`

`[read-from-source]` — verbatim, `server/agents/launch_review.py:929-1004`
(the full function; the task named lines ~929-1000, but the argparse block
plus the exception-handling block that follows it — required to show
`main()` completely — run through line 1004, immediately before the
`if __name__ == "__main__":` guard):

```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Launch a Claims Review Agent session.")
    parser.add_argument("--claim-slug", required=True, type=str)
    parser.add_argument(
        "--variant",
        required=True,
        choices=["memory_on", "memory_off"],
        help="Memory configuration — no default, explicit choice required.",
    )
    parser.add_argument(
        "--pair-label",
        default=None,
        help="Retest harness pair label ('A', 'B', 'C'). Optional — only "
        "meaningful for h1-r retest runs.",
    )
    parser.add_argument(
        "--repetition",
        type=int,
        default=None,
        help="Retest harness repetition number (1 or 2). Optional — only "
        "meaningful for h1-r retest runs.",
    )
    parser.add_argument(
        "--claim-position",
        type=int,
        default=None,
        choices=[1, 2],
        help="Position of this claim within its h1-r retest pair/chain "
        "(1 = first claim reviewed for a product+claim_type, 2 = second, "
        "reviewed after the first is in Memory). Required for memory_on "
        "retest runs — it is what the manipulation check is derived "
        "against; not used for memory_off.",
    )
    args = parser.parse_args()

    if args.variant == "memory_on" and args.claim_position is None:
        parser.error("--claim-position is required when --variant is memory_on")

    try:
        run_review(
            args.claim_slug,
            args.variant,
            pair_label=args.pair_label,
            repetition=args.repetition,
            claim_position=args.claim_position,
        )
    except ProhibitedToolCallError as e:
        print("=" * 70, file=sys.stderr)
        print("HARD FAILURE: prohibited tool call detected", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(
            f"The session called prohibited tool(s): {', '.join(e.prohibited_calls)}",
            file=sys.stderr,
        )
        print(
            "Grading was skipped — this run cannot be trusted regardless of "
            "what the grader would have concluded.",
            file=sys.stderr,
        )
        sys.exit(1)
    except anthropic.AuthenticationError:
        print("Error: authentication failed — check ANTHROPIC_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"Error: API request failed ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError as e:
        print(f"Error: connection failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: session failed unexpectedly: {e}", file=sys.stderr)
        sys.exit(1)
```

---

## 4. Mechanism to supply additional free-form text into the agent's first user turn

`[executed]` — searched for the four named symbols across
`launch_review.py` and `run_retest.py`:

```
$ grep -n "injected_message\|inject\|extra_context" server/agents/launch_review.py server/agents/run_retest.py
(no output — zero hits)
```

**Negative result, explicit: none of `injected_message`, `inject`, or
`extra_context` appears anywhere in either file.** I also broadened this
to the whole repo as a sanity check beyond just these two files:

```
$ grep -rn "injected_message\|extra_context" . --include="*.py" 2>/dev/null | grep -v node_modules
(no output — zero hits repo-wide, all .py files)
```

`[executed]` — `user_message` / `user.message` search:

```
$ grep -n "user_message\|user\.message" server/agents/launch_review.py
18:once the session is created — d15) and sent to the agent as a user.message
```

```
789:                    "type": "user.message",
```

There is exactly **one** `user.message` event constructed in the entire
launcher, at `launch_review.py:787-808` (shown in full in item 2's
function body above, inside `run_review`, gated by `if variant ==
"memory_on":`). It is built as a single literal f-string, inline, at the
point of use — there is no separate function, no parameter, and no
constant named anything like `injected_message` or `extra_context` that
holds or assembles this text. The two variables interpolated into it are
`claim_slug` and `mount_path`, both already fixed by the time `run_review`
constructs the event; there is no path by which arbitrary caller-supplied
free text reaches this string.

`[executed]` — commit `c5eec4d`'s actual diff (`git show c5eec4d`) shows it
introduced no new symbol at all. It **edited the pre-existing inline
f-string in place** — before the commit, the `user.message` text was:

```python
f"The Memory store for this session is mounted at {mount_path}."
```

After the commit, the same f-string (same call site, same variable, no new
function) became the longer text quoted in item 2 (claim_slug + no-action
instruction + output path + mount path). The commit message itself
confirms there was no dedicated injection abstraction before or after:
it describes "d15's injected message" and "d18's injected user.message" as
prose labels for this literal, not as a named code construct. The test
file additions in the same commit (`test_injected_message_names_claim_slug`,
etc.) test the content of this f-string by substring assertion
(`assert "kalder_govern-compliance-01" in text`), not any structured
injection API.

**Direct answer: no mechanism exists today to supply additional free-form
text into the agent's first user turn.** The only text sent before
`user.define_outcome` is this one hardcoded f-string (memory_on only —
memory_off sends no `user.message` at all, confirmed by
`test_memory_off_sends_no_injected_message`, and explicitly flagged as a
known, deliberately-unfixed asymmetry in `c5eec4d`'s own commit message:
"memory_off receives no injected message at all... Belongs in h1's limits;
adding a parity message to memory_off is its own decision with its own
tradeoff"). There is no CLI flag, no environment variable, no config file,
and no function parameter on `run_review`, `build_agent`, or `build_session`
through which a caller could inject arbitrary additional text into that
turn — `run_review`'s only inputs are `claim_slug`, `variant`,
`pair_label`, `repetition`, and `claim_position` (see its signature in item
2), none of which is a free-text field. Adding one would require editing
`run_review`'s body directly (a new parameter plus a change to the
f-string construction at lines 787-808), which is source modification, not
something this read-only investigation performed or found already
supported.

---

## 5. `PROHIBITED_TOOLS` and `check_for_prohibited_tool_calls`

`[read-from-source]` — `server/agents/launch_review.py:58`:

```python
PROHIBITED_TOOLS = {"append_claim", "delete_claim", "classify_claim_risk"}
```

`[read-from-source]` — full body, `server/agents/launch_review.py:178-193`:

```python
def check_for_prohibited_tool_calls(tool_call_events: list) -> bool:
    """Inspect a session's tool-call event history for calls to
    append_claim, delete_claim, or classify_claim_risk.

    Accepts any objects exposing `.type` (one of "agent.tool_use" /
    "agent.mcp_tool_use") and `.name` (the tool name) — real SDK
    events or plain mocks both work.

    Returns True if any prohibited tool was called, False otherwise.
    """
    for event in tool_call_events:
        if event.type not in ("agent.tool_use", "agent.mcp_tool_use"):
            continue
        if event.name in PROHIBITED_TOOLS:
            return True
    return False
```

**Call site relative to response capture** — `[read-from-source]`, within
`run_review` (item 2's full body above): the streaming loop that populates
`tool_call_events` (appending every `agent.tool_use` / `agent.mcp_tool_use`
event as it arrives, lines 824-858) runs to completion first — the loop
exits only on `session.status_terminated` or a non-`requires_action`
`session.status_idle`. **Only after that `with client.beta.sessions.events.stream(...)`
block has fully exited** does the check run, at lines 860-868:

```python
if check_for_prohibited_tool_calls(tool_call_events):
    prohibited_calls = sorted(
        {
            event.name
            for event in tool_call_events
            if event.name in PROHIBITED_TOOLS
        }
    )
    raise ProhibitedToolCallError(prohibited_calls)

ruling_text = fetch_output_artifact(client, session.id, claim_slug, run_log=run_log)
```

So the check is **post-hoc over the entire session's accumulated tool-call
history, after the session has already ended** — not a live, per-call gate
that could block a prohibited call before it executes. It runs *before*
`fetch_output_artifact` (the ruling is not even retrieved if a prohibited
call is found — the function raises immediately) and, transitively, before
grading is reported or any Memory write is attempted, per the module's own
d9 docstring at the top of the file ("deterministic pre-gate against
prohibited-tool-call rulings... Blocks grading — see d9"). By the time this
runs, however, the prohibited tool call — if one occurred — has already
been executed against the live MCP server; the gate prevents the *ruling
from being trusted/graded/persisted*, not the underlying write from
happening. This is consistent with `ProhibitedToolCallError`'s own
docstring (lines 165-168): "Raised when the session's tool-call history
shows a call to a tool the Review Agent must never invoke... Blocks
grading."

`[inferred]` — per the finding already reported in
`week21_day0_endpoint1_report.md` Part 1 item 4, `PROHIBITED_TOOLS` does
not include `append_ruling`, which the live server exposes and the
launcher's generic `mcp_toolset` grant makes available to the agent. This
gate — being both post-hoc and scoped to only three of the server's
write-capable/classification tools — would not fire at all on a session
that called `append_ruling` and nothing else in `PROHIBITED_TOOLS`.

---

## Definition-of-done

- Report written to `week21_day0_prompt_files.md` at repo root: done.
- Printed to stdout: done (this message).
- Not staged, not committed: confirmed below.
- Every item answered from source; no "not determined" was required this
  round — items 1-5 were all resolvable from the repo as it exists today.
- Every claim labeled `[read-from-source]`, `[executed]`, or `[inferred]`.
- No source file modified; launcher not invoked.
