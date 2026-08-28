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
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from server.db.client import fetchone_dict

load_dotenv()

AGENTS_DIR = Path(__file__).parent
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


def build_session(client: anthropic.Anthropic, agent_id: str, agent_version, variant: str):
    environment = client.beta.environments.create(
        name=f"claims-review-{variant}",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )

    resources = []
    memory_store_id = None
    if variant == "memory_on":
        store = client.beta.memory_stores.create(
            name="Claims Review Memory",
            description="Prior claim rulings, keyed by product + claim_type, for consistency checks across review sessions.",
        )
        memory_store_id = store.id
        resources.append(
            {
                "type": "memory_store",
                "memory_store_id": store.id,
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


def fetch_output_artifact(client: anthropic.Anthropic, session_id: str) -> str:
    """Retrieve the agent's ruling from /mnt/session/outputs via the Files API.

    Indexing lags status_idle by ~1-3s, so an empty list on the first
    attempt is not a failure — retry a couple of times before giving up.
    """
    delays = (0.0, *OUTPUT_FILE_RETRY_DELAYS)
    for delay in delays:
        if delay:
            time.sleep(delay)
        files = list(
            client.beta.files.list(scope_id=session_id, betas=[FILES_BETA])
        )
        if files:
            break
    else:
        raise RuntimeError(
            f"No output file found for session {session_id} after "
            f"{len(delays)} attempts."
        )

    file = files[0]
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
) -> None:
    """Write a satisfied ruling to Memory, scoped by product_key + claim_type.

    Called by the launcher, never the agent — the agent's memory_store
    resource is read-only (d12). Path convention matches the existing
    stores observed in Day 7's inspection: /{product_key}-{claim_type}.md
    """
    path = f"/{product_key}-{claim_type}.md"
    client.beta.memory_stores.memories.create(
        memory_store_id,
        content=ruling_text,
        path=path,
    )


def maybe_write_ruling_to_memory(
    client: anthropic.Anthropic,
    variant: str,
    memory_store_id: str | None,
    outcome_result: str | None,
    claim_slug: str,
    ruling_text: str,
) -> bool:
    """Gate the Memory write on grading == satisfied (d12). Returns whether
    a write was attempted, and always prints the reason either way — this
    observability is what f14 lacked."""
    if variant != "memory_on":
        print(f"Memory write skipped: variant is {variant!r}, not memory_on.")
        return False
    if outcome_result != "satisfied":
        print(
            f"Memory write skipped: grading result is {outcome_result!r}, "
            "not 'satisfied'."
        )
        return False

    claim = get_claim_product_and_type(claim_slug)
    write_ruling_to_memory(
        client,
        memory_store_id,
        claim["product_key"],
        claim["claim_type"],
        ruling_text,
    )
    print(
        f"Memory write performed: grading result is 'satisfied' — wrote "
        f"/{claim['product_key']}-{claim['claim_type']}.md."
    )
    return True


def run_review(claim_slug: str, variant: str) -> dict:
    client = anthropic.Anthropic()

    agent_id, agent_version = build_agent(client, variant)
    session, memory_store_id = build_session(client, agent_id, agent_version, variant)

    rubric_text = RUBRIC_FILE.read_text()
    description = f"Review the marketing claim {claim_slug} and produce a ruling."

    outcome_result = None
    outcome_explanation = None
    last_iteration = None
    tool_call_events = []

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.define_outcome",
                    "description": description,
                    "rubric": {"type": "text", "content": rubric_text},
                    "max_iterations": MAX_ITERATIONS,
                }
            ],
        )

        for event in stream:
            if event.type == "span.outcome_evaluation_end":
                outcome_result = event.result
                outcome_explanation = event.explanation
                last_iteration = event.iteration
            elif event.type in ("agent.tool_use", "agent.mcp_tool_use"):
                tool_call_events.append(event)
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

    ruling_text = fetch_output_artifact(client, session.id)
    ruling_text = ruling_text.strip()

    memory_write_performed = maybe_write_ruling_to_memory(
        client, variant, memory_store_id, outcome_result, claim_slug, ruling_text
    )

    return {
        "ruling": ruling_text,
        "outcome_result": outcome_result,
        "outcome_explanation": outcome_explanation,
        "iteration_count": (last_iteration + 1) if last_iteration is not None else None,
        "session_id": session.id,
        "memory_write_performed": memory_write_performed,
    }


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
        result = run_review(args.claim_slug, args.variant)
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

    print("=" * 70)
    print("RULING ARTIFACT")
    print("=" * 70)
    print(result["ruling"])
    print()
    print("=" * 70)
    print("GRADING RESULT")
    print("=" * 70)
    print(f"Result: {result['outcome_result']}")
    print(f"Iterations: {result['iteration_count']}")
    if result["outcome_explanation"]:
        print(f"Per-criterion feedback:\n{result['outcome_explanation']}")


if __name__ == "__main__":
    main()
