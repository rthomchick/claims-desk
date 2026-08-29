"""diagnose_memory_mount.py — STANDALONE, throwaway diagnostic.

Does NOT touch launch_review.py, any prompt template, the rubric, or any
review-pipeline code. This script exists solely to answer one question:
does the sandbox filesystem mount backing the persistent Memory store
actually contain anything the agent can see, and if so, where?

Context: the persistent store (memstore_01PCBbgQ6HkoQr3ogWPsttz8) holds a
verified entry at /salesforce_govcloud-compliance.md when inspected via the
client-side memories.list/memories.retrieve API. But a review agent session
with that same store attached (read_only, per d12) reports no prior ruling,
and manual probing of /mnt/memory/claims-review-memory-persistent/ inside
the sandbox found nothing. The client-side write API and the sandbox mount
are two different access paths — one working does not imply the other
works. This script inspects the mount directly, from inside a session
configured exactly like the real review agent's memory resource, plus a
bash tool (deliberately excluded from the review agent per d10, but that
exclusion is about the review agent's toolset, not about diagnosing it).

No MCP tools, no rubric, no user.define_outcome, no memory writes. Prints
raw command output and exits. Nothing here is committed to Memory or the
claims database.

Usage:
    python -m server.agents.diagnose_memory_mount
"""

from __future__ import annotations

import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-5"

DIAGNOSTIC_PROMPT = """\
Run exactly these four commands, in order, using the bash tool. For each \
one, report the literal, verbatim output — including any error text such \
as "No such file or directory" — and nothing else. Do NOT summarize, \
interpret, explain, or draw any conclusion about what the results mean. \
Just show the raw output of each command, labeled by command.

1. ls -la /mnt/
2. ls -la /mnt/memory/
3. ls -laR /mnt/memory/
4. If any file was found in step 3, cat that file and show its opening \
lines. If no file was found, state exactly that and skip this step.
"""


def get_memory_store_id() -> str:
    memory_store_id = os.environ.get("CLAIMS_REVIEW_MEMORY_STORE_ID")
    if not memory_store_id:
        raise RuntimeError(
            "CLAIMS_REVIEW_MEMORY_STORE_ID is not set. This diagnostic "
            "inspects that specific store's mount — it will not create "
            "or guess a store."
        )
    return memory_store_id


def build_diagnostic_agent(client: anthropic.Anthropic, memory_store_id: str) -> tuple[str, int]:
    tools = [
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False},
            "configs": [
                {
                    "type": "bash",
                    "name": "bash",
                    "enabled": True,
                    "permission_policy": {"type": "always_allow"},
                },
            ],
        },
    ]

    agent = client.beta.agents.create(
        name="Memory Mount Diagnostic (throwaway)",
        model=MODEL,
        system=(
            "You are a filesystem inspection tool. You run exactly the "
            "commands you are told to run and report their raw output "
            "verbatim. You do not interpret, summarize, or theorize."
        ),
        tools=tools,
    )
    return agent.id, agent.version


def build_diagnostic_session(client: anthropic.Anthropic, agent_id: str, agent_version, memory_store_id: str):
    environment = client.beta.environments.create(
        name="claims-review-memory-diagnostic",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )

    resources = [
        {
            "type": "memory_store",
            "memory_store_id": memory_store_id,
            "access": "read_only",
        }
    ]

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": agent_id, "version": agent_version},
        environment_id=environment.id,
        title="Memory mount diagnostic (throwaway, not a review)",
        resources=resources,
    )
    return session


def run_diagnostic() -> str:
    client = anthropic.Anthropic()
    memory_store_id = get_memory_store_id()

    print(f"Using memory_store_id={memory_store_id!r}, access=read_only")

    agent_id, agent_version = build_diagnostic_agent(client, memory_store_id)
    session = build_diagnostic_session(client, agent_id, agent_version, memory_store_id)

    print(f"session_id={session.id}")
    print("=" * 70)

    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": DIAGNOSTIC_PROMPT}],
                }
            ],
        )

        for event in stream:
            if event.type in ("agent.tool_use", "agent.mcp_tool_use"):
                print(f"[tool_use] {event.name}: {getattr(event, 'input', '')}")
            elif event.type == "agent.tool_result":
                for block in getattr(event, "content", None) or []:
                    if getattr(block, "type", None) == "text":
                        print(f"[tool_result]\n{block.text}")
                    else:
                        print(f"[tool_result:{getattr(block, 'type', '?')}]")
            elif event.type == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="")

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

    print()
    print("=" * 70)
    print("No review session run, no ruling produced, nothing committed.")

    return "".join(final_text_parts)


def main() -> None:
    try:
        run_diagnostic()
    except anthropic.AuthenticationError:
        print("Error: authentication failed — check ANTHROPIC_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"Error: API request failed ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError as e:
        print(f"Error: connection failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
