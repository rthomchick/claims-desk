"""launch_review.py — launches a Claims Review Agent session via the
Managed Agents API (Week 18 Day 4, deferred Step 4 from Day 3).

Usage:
    python -m server.agents.launch_review --claim-slug <slug> --variant memory_on|memory_off

Loads the corresponding generated prompt (review_agent_memory_on.md or
review_agent_memory_off.md), connects the Claims Desk MCP server (six
tools, already live at claims-desk-production-8424.up.railway.app/mcp),
enables a Memory store only for the memory_on variant, submits the claim
as a user.define_outcome graded against review_rubric.md, retrieves the
agent's ruling artifact from /mnt/session/outputs via the Files API, and
prints it alongside the grading result, iteration count, and
per-criterion feedback.

For memory_on, the store's mount path is read from the API (the
memory_store session resource's output-only `mount_path` field, populated
once the session is created — d15) and sent to the agent as a user.message
before user.define_outcome. The system prompt never contains a literal
mount path or a substitution placeholder for one.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys
import time
import traceback
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from server.db.client import fetchone_dict

load_dotenv()

AGENTS_DIR = Path(__file__).parent
REPO_ROOT = AGENTS_DIR.parent.parent
RUNS_DIR = REPO_ROOT / "runs"
MCP_SERVER_URL = "https://claims-desk-production-8424.up.railway.app/mcp"
FILES_BETA = "managed-agents-2026-04-01"
OUTPUT_FILE_RETRY_DELAYS = (1.5, 1.5)

PROMPT_FILES = {
    "memory_on": AGENTS_DIR / "review_agent_memory_on.md",
    "memory_off": AGENTS_DIR / "review_agent_memory_off.md",
}
RUBRIC_FILE = AGENTS_DIR / "review_rubric.md"

MODEL = "claude-opus-5"
MAX_ITERATIONS = 3

PROHIBITED_TOOLS = {"append_claim", "delete_claim", "classify_claim_risk"}


class RunLog:
    """Incremental per-run diagnostic log (d16).

    Opened and flushed after every write so a crash mid-run leaves a
    partial trace on disk rather than nothing — f18's tool-call trace,
    session id, and file ids existed only in one process's memory and
    were unrecoverable once that process exited. Writing on clean exit
    only would not have helped; this writes as events occur.
    """

    def __init__(self, path: Path):
        self.path = path
        self._fh = open(path, "a", encoding="utf-8")

    def write(self, text: str) -> None:
        self._fh.write(text)
        if not text.endswith("\n"):
            self._fh.write("\n")
        self._fh.flush()

    def header(
        self,
        claim_slug: str,
        variant: str,
        agent_id: str,
        session_id: str,
        memory_store_id: str | None,
        mount_path: str | None,
    ) -> None:
        self.write("=" * 70)
        self.write(f"timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
        self.write(f"claim_slug: {claim_slug}")
        self.write(f"variant: {variant}")
        self.write(f"agent_id: {agent_id}")
        self.write(f"session_id: {session_id}")
        self.write(f"memory_store_id: {memory_store_id}")
        self.write(f"mount_path: {mount_path}")
        self.write("=" * 70)

    def tool_call(self, event_type: str, name: str, arguments: dict) -> None:
        self.write(f"TOOL CALL [{event_type}] {name} args={arguments!r}")

    def agent_message(self, text: str) -> None:
        self.write(f"AGENT MESSAGE: {text}")

    def files_list(self, files: list, selected_indices: list[int], selection_rule: str) -> None:
        self.write("-" * 70)
        self.write(f"files.list response ({len(files)} file(s)):")
        for i, f in enumerate(files):
            marker = " <-- SELECTED" if i in selected_indices else ""
            self.write(
                f"  [{i}] id={f.id} name={getattr(f, 'filename', None)} "
                f"size={getattr(f, 'size_bytes', None)} "
                f"created={getattr(f, 'created_at', None)}{marker}"
            )
        self.write(f"selection rule: {selection_rule}")
        self.write("-" * 70)

    def unexpected_artifact(self, file) -> None:
        self.write(
            "UNEXPECTED ARTIFACT (not selected): "
            f"name={getattr(file, 'filename', None)} id={file.id} "
            f"created={getattr(file, 'created_at', None)}"
        )

    def ruling(self, ruling_text: str) -> None:
        self.write("-" * 70)
        self.write("RULING ARTIFACT")
        self.write("-" * 70)
        self.write(ruling_text)

    def grading(
        self,
        outcome_result: str | None,
        outcome_explanation: str | None,
        iteration_count: int | None,
    ) -> None:
        self.write("-" * 70)
        self.write("GRADING RESULT")
        self.write(f"result: {outcome_result}")
        self.write(f"iterations: {iteration_count}")
        if outcome_explanation:
            self.write(f"per-criterion feedback:\n{outcome_explanation}")
        self.write("-" * 70)

    def memory_write_decision(self, reason: str) -> None:
        self.write(f"MEMORY WRITE DECISION: {reason}")

    def exception(self, exc: BaseException) -> None:
        self.write("=" * 70)
        self.write("EXCEPTION")
        self.write("=" * 70)
        self.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    def close(self) -> None:
        self._fh.close()


def make_run_log_path(claim_slug: str, variant: str) -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return RUNS_DIR / f"{timestamp}-{claim_slug}-{variant}.log"


class ProhibitedToolCallError(RuntimeError):
    """Raised when the session's tool-call history shows a call to a
    tool the Review Agent must never invoke (append_claim, delete_claim,
    classify_claim_risk). Blocks grading — see d9."""

    def __init__(self, prohibited_calls: list[str]):
        self.prohibited_calls = prohibited_calls
        super().__init__(
            "Prohibited tool call(s) detected in session history: "
            + ", ".join(prohibited_calls)
        )


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


def build_agent(client: anthropic.Anthropic, variant: str) -> str:
    system_prompt = PROMPT_FILES[variant].read_text()

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
                {
                    "type": "write",
                    "name": "write",
                    "enabled": True,
                    "permission_policy": {"type": "always_allow"},
                },
                {
                    "type": "read",
                    "name": "read",
                    "enabled": True,
                    "permission_policy": {"type": "always_allow"},
                },
            ],
        },
    ]

    agent = client.beta.agents.create(
        name=f"Claims Review Agent ({variant})",
        model=MODEL,
        system=system_prompt,
        mcp_servers=mcp_servers,
        tools=tools,
    )
    return agent.id, agent.version


def get_memory_store_id() -> str:
    """Resolve the persistent Memory store ID from the environment (d13).

    No fallback to creating a store: a missing or invalid ID must fail
    loudly here rather than silently isolating each session in its own
    store, which is the failure mode that hid for a week (w5)."""
    memory_store_id = os.environ.get("CLAIMS_REVIEW_MEMORY_STORE_ID")
    if not memory_store_id:
        raise RuntimeError(
            "CLAIMS_REVIEW_MEMORY_STORE_ID is not set. The memory_on variant "
            "requires the persistent Memory store ID — it will not create a "
            "new store."
        )
    return memory_store_id


def build_session(client: anthropic.Anthropic, agent_id: str, agent_version, variant: str):
    environment = client.beta.environments.create(
        name=f"claims-review-{variant}",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )

    resources = []
    memory_store_id = None
    if variant == "memory_on":
        memory_store_id = get_memory_store_id()
        resources.append(
            {
                "type": "memory_store",
                "memory_store_id": memory_store_id,
                "access": "read_only",
                "instructions": "Check for a prior ruling on this product + claim_type before ruling.",
            }
        )

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": agent_id, "version": agent_version},
        environment_id=environment.id,
        title=f"Claims review ({variant})",
        resources=resources or None,
    )
    return session, memory_store_id


def fetch_output_artifact(
    client: anthropic.Anthropic,
    session_id: str,
    claim_slug: str,
    run_log: RunLog | None = None,
) -> str:
    """Retrieve the agent's ruling from /mnt/session/outputs via the Files API.

    Indexing lags status_idle by ~1-3s, so an empty list on the first
    attempt is not a failure — retry a couple of times before giving up.

    Selects by filename, not index (d17 — fixes f17). The agent is told in
    its system prompt to write its ruling to
    `/mnt/session/outputs/{claim_slug}.md` (see review_agent_memory_on.md
    and review_agent_memory_off.md, "Delivering the ruling"), so the
    expected filename is derived from the claim_slug the launcher was
    invoked with — not from position in the list.

    - Exactly one file matching `{claim_slug}.md`: select it.
    - Zero matches: retry (the indexing lag above), then raise naming the
      expected filename and what was actually present.
    - More than one match: raise immediately — an ambiguous match is not
      safe to guess at, and retrying won't resolve a duplicate.

    Any other file present (not matching the expected name) is logged as
    a named anomaly, since a stray artifact from a prior run in the same
    session's outputs is exactly how f18 happened.

    The full files.list response is logged regardless of outcome, so the
    log records what was actually there rather than hiding it.
    """
    expected_filename = f"{claim_slug}.md"
    delays = (0.0, *OUTPUT_FILE_RETRY_DELAYS)
    matches: list = []
    files: list = []
    for delay in delays:
        if delay:
            time.sleep(delay)
        files = list(
            client.beta.files.list(scope_id=session_id, betas=[FILES_BETA])
        )
        matches = [f for f in files if getattr(f, "filename", None) == expected_filename]
        if matches:
            break

    if len(matches) > 1:
        if run_log is not None:
            run_log.files_list(
                files,
                selected_indices=[files.index(f) for f in matches],
                selection_rule=f"filename == {expected_filename!r} (d17)",
            )
        raise RuntimeError(
            f"Multiple output files matched {expected_filename!r} for session "
            f"{session_id}: {[getattr(f, 'filename', None) for f in matches]}. "
            "Refusing to guess which is authoritative."
        )

    if not matches:
        if run_log is not None:
            run_log.files_list(
                files,
                selected_indices=[],
                selection_rule=f"filename == {expected_filename!r} (d17)",
            )
        raise RuntimeError(
            f"No output file named {expected_filename!r} found for session "
            f"{session_id} after {len(delays)} attempts. Files present: "
            f"{[getattr(f, 'filename', None) for f in files]}."
        )

    file = matches[0]
    if run_log is not None:
        run_log.files_list(
            files,
            selected_indices=[files.index(file)],
            selection_rule=f"filename == {expected_filename!r} (d17)",
        )
        for f in files:
            if f is not file:
                run_log.unexpected_artifact(f)

    content = client.beta.files.download(file.id, betas=[FILES_BETA])
    return content.read().decode("utf-8")


def get_claim_product_and_type(claim_slug: str) -> dict:
    """Look up a claim's product_key and claim_type by claim_slug.

    Reads the claims table directly rather than parsing claim_slug — the
    slug's {product_key}-{claim_type}-{NN} shape is a d2 convention for
    display, not a reliable inverse mapping.
    """
    claim = fetchone_dict(
        "select product_key, claim_type from claims where claim_slug = %s",
        (claim_slug,),
    )
    if claim is None:
        raise RuntimeError(f"no claim found with claim_slug {claim_slug}")
    return claim


def write_ruling_to_memory(
    client: anthropic.Anthropic,
    memory_store_id: str,
    product_key: str,
    claim_type: str,
    ruling_text: str,
) -> str:
    """Write a satisfied ruling to Memory, scoped by product_key + claim_type.

    Called by the launcher, never the agent — the agent's memory_store
    resource is read-only (d12). Path convention matches the existing
    stores observed in Day 7's inspection: /{product_key}-{claim_type}.md

    OVERWRITE semantics: one current ruling per {product_key}-{claim_type}
    path. `create` makes the first write; if the path already exists,
    `create` 409s (memory_path_conflict_error) and we resolve the existing
    memory's id via `list` and `update` it instead (d14 — the update API
    is keyed by memory_id, not path, so there is no direct upsert-by-path).

    Returns "wrote" or "updated existing" so the caller can print which
    case occurred — that distinction is what made f14 findable (d12).
    """
    path = f"/{product_key}-{claim_type}.md"
    try:
        client.beta.memory_stores.memories.create(
            memory_store_id,
            content=ruling_text,
            path=path,
        )
        return "wrote"
    except anthropic.ConflictError:
        existing = next(
            (
                item
                for item in client.beta.memory_stores.memories.list(
                    memory_store_id, path_prefix="/"
                )
                if item.path == path
            ),
            None,
        )
        if existing is None:
            raise
        client.beta.memory_stores.memories.update(
            existing.id,
            memory_store_id=memory_store_id,
            content=ruling_text,
        )
        return "updated existing"


def maybe_write_ruling_to_memory(
    client: anthropic.Anthropic,
    variant: str,
    memory_store_id: str | None,
    outcome_result: str | None,
    claim_slug: str,
    ruling_text: str,
    run_log: RunLog | None = None,
) -> bool:
    """Gate the Memory write on grading == satisfied (d12). Returns whether
    a write was attempted, and always prints the reason either way — this
    observability is what f14 lacked."""
    if variant != "memory_on":
        reason = f"Memory write skipped: variant is {variant!r}, not memory_on."
        print(reason)
        if run_log is not None:
            run_log.memory_write_decision(reason)
        return False
    if outcome_result != "satisfied":
        reason = (
            f"Memory write skipped: grading result is {outcome_result!r}, "
            "not 'satisfied'."
        )
        print(reason)
        if run_log is not None:
            run_log.memory_write_decision(reason)
        return False

    claim = get_claim_product_and_type(claim_slug)
    write_reason = write_ruling_to_memory(
        client,
        memory_store_id,
        claim["product_key"],
        claim["claim_type"],
        ruling_text,
    )
    reason = (
        f"Memory write performed: grading result is 'satisfied' — {write_reason} "
        f"/{claim['product_key']}-{claim['claim_type']}.md."
    )
    print(reason)
    if run_log is not None:
        run_log.memory_write_decision(reason)
    return True


def print_ruling_and_grading(
    ruling_text: str,
    outcome_result: str | None,
    outcome_explanation: str | None,
    last_iteration: int | None,
    run_log: RunLog | None = None,
) -> None:
    """Print the ruling artifact and grading result. Must run before any
    Memory write is attempted (d14) — the deliverable has to reach stdout
    even if the subsequent persistence step fails."""
    print("=" * 70)
    print("RULING ARTIFACT")
    print("=" * 70)
    print(ruling_text)
    print()
    print("=" * 70)
    print("GRADING RESULT")
    print("=" * 70)
    print(f"Result: {outcome_result}")
    iteration_count = (last_iteration + 1) if last_iteration is not None else None
    print(f"Iterations: {iteration_count}")
    if outcome_explanation:
        print(f"Per-criterion feedback:\n{outcome_explanation}")

    if run_log is not None:
        run_log.ruling(ruling_text)
        run_log.grading(outcome_result, outcome_explanation, iteration_count)


def get_memory_mount_path(session) -> str | None:
    """Read the memory_store resource's API-provided mount_path off a
    created session (d15). Output-only field, populated by the server —
    never derived client-side. Returns None if the session has no
    memory_store resource attached (memory_off).
    """
    for resource in session.resources:
        if resource.type == "memory_store":
            return resource.mount_path
    return None


def run_review(claim_slug: str, variant: str) -> dict:
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
                                f"The Memory store for this session is mounted "
                                f"at {mount_path}."
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
            "iteration_count": (last_iteration + 1) if last_iteration is not None else None,
            "session_id": session.id,
            "memory_write_performed": memory_write_performed,
        }
    except BaseException as e:
        run_log.exception(e)
        raise
    finally:
        run_log.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch a Claims Review Agent session.")
    parser.add_argument("--claim-slug", required=True, type=str)
    parser.add_argument(
        "--variant",
        required=True,
        choices=["memory_on", "memory_off"],
        help="Memory configuration — no default, explicit choice required.",
    )
    args = parser.parse_args()

    try:
        run_review(args.claim_slug, args.variant)
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


if __name__ == "__main__":
    main()
