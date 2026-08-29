"""Unit tests for the d9 prohibited-tool-call pre-gate and the d12
grading-gated Memory write in launch_review.py.

Pure unit tests against constructed mock event data / mocked grading
results — no live Managed Agents session or API call, per d9's design
(avoid dependence on live grader behavior)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import anthropic

from server.agents.launch_review import (
    PROMPT_FILES,
    build_session,
    check_for_prohibited_tool_calls,
    get_memory_mount_path,
    get_memory_store_id,
    maybe_write_ruling_to_memory,
    print_ruling_and_grading,
    write_ruling_to_memory,
)


def _conflict_error():
    response = MagicMock()
    response.status_code = 409
    return anthropic.ConflictError(
        message="memory_path_conflict_error",
        response=response,
        body={"error": {"type": "memory_path_conflict_error"}},
    )


def _tool_call(name: str, event_type: str = "agent.mcp_tool_use"):
    return SimpleNamespace(type=event_type, name=name)


def test_blocks_on_append_claim():
    events = [
        _tool_call("get_claim_status"),
        _tool_call("append_claim"),
    ]
    assert check_for_prohibited_tool_calls(events) is True


def test_blocks_on_delete_claim():
    events = [
        _tool_call("list_claims"),
        _tool_call("delete_claim"),
    ]
    assert check_for_prohibited_tool_calls(events) is True


def test_blocks_on_classify_claim_risk():
    events = [
        _tool_call("check_substantiation"),
        _tool_call("classify_claim_risk"),
    ]
    assert check_for_prohibited_tool_calls(events) is True


def test_allows_clean_session_with_only_legitimate_calls():
    events = [
        _tool_call("list_claims"),
        _tool_call("get_claim_status"),
        _tool_call("check_substantiation"),
        _tool_call("write", event_type="agent.tool_use"),
        _tool_call("get_claim_status"),
        _tool_call("list_claims"),
    ]
    assert check_for_prohibited_tool_calls(events) is False


@patch("server.agents.launch_review.write_ruling_to_memory")
@patch("server.agents.launch_review.get_claim_product_and_type")
def test_satisfied_grading_attempts_write(mock_get_claim, mock_write):
    mock_get_claim.return_value = {"product_key": "acme-widget", "claim_type": "performance"}
    client = MagicMock()

    performed = maybe_write_ruling_to_memory(
        client, "memory_on", "memstore_abc123", "satisfied", "acme-widget-performance-01", "ruling text"
    )

    assert performed is True
    mock_get_claim.assert_called_once_with("acme-widget-performance-01")
    mock_write.assert_called_once_with(
        client, "memstore_abc123", "acme-widget", "performance", "ruling text"
    )


@patch("server.agents.launch_review.write_ruling_to_memory")
@patch("server.agents.launch_review.get_claim_product_and_type")
def test_needs_revision_grading_skips_write(mock_get_claim, mock_write):
    client = MagicMock()

    performed = maybe_write_ruling_to_memory(
        client, "memory_on", "memstore_abc123", "needs_revision", "acme-widget-performance-01", "ruling text"
    )

    assert performed is False
    mock_get_claim.assert_not_called()
    mock_write.assert_not_called()


@patch("server.agents.launch_review.write_ruling_to_memory")
@patch("server.agents.launch_review.get_claim_product_and_type")
def test_max_iterations_reached_skips_write(mock_get_claim, mock_write):
    """f14's exact case: an unsatisfied outcome must never reach Memory."""
    client = MagicMock()

    performed = maybe_write_ruling_to_memory(
        client, "memory_on", "memstore_abc123", "max_iterations_reached", "acme-widget-performance-01", "ruling text"
    )

    assert performed is False
    mock_get_claim.assert_not_called()
    mock_write.assert_not_called()


@patch("server.agents.launch_review.write_ruling_to_memory")
@patch("server.agents.launch_review.get_claim_product_and_type")
def test_prohibited_tool_call_pre_gate_skips_write(mock_get_claim, mock_write):
    """A d9 pre-gate hard failure raises ProhibitedToolCallError before
    grading/write ever run — run_review never reaches
    maybe_write_ruling_to_memory in that path. This test documents that
    invariant at the call-site level: with no outcome_result available
    (the grading step never ran), the gate must not write."""
    client = MagicMock()

    performed = maybe_write_ruling_to_memory(
        client, "memory_on", "memstore_abc123", None, "acme-widget-performance-01", "ruling text"
    )

    assert performed is False
    mock_get_claim.assert_not_called()
    mock_write.assert_not_called()


# --- d13: persistent Memory store referenced by ID, no per-invocation create ---


def test_missing_env_var_raises_and_does_not_create_store(monkeypatch):
    monkeypatch.delenv("CLAIMS_REVIEW_MEMORY_STORE_ID", raising=False)

    with pytest.raises(RuntimeError, match="CLAIMS_REVIEW_MEMORY_STORE_ID"):
        get_memory_store_id()


def test_empty_string_env_var_raises_and_does_not_create_store(monkeypatch):
    monkeypatch.setenv("CLAIMS_REVIEW_MEMORY_STORE_ID", "")

    with pytest.raises(RuntimeError, match="CLAIMS_REVIEW_MEMORY_STORE_ID"):
        get_memory_store_id()


def test_valid_env_var_returns_id_without_create(monkeypatch):
    monkeypatch.setenv("CLAIMS_REVIEW_MEMORY_STORE_ID", "memstore_01PCBbgQ6HkoQr3ogWPsttz8")

    assert get_memory_store_id() == "memstore_01PCBbgQ6HkoQr3ogWPsttz8"


def test_build_session_memory_on_references_env_store_no_create(monkeypatch):
    monkeypatch.setenv("CLAIMS_REVIEW_MEMORY_STORE_ID", "memstore_01PCBbgQ6HkoQr3ogWPsttz8")
    client = MagicMock()
    client.beta.environments.create.return_value = SimpleNamespace(id="env_123")
    client.beta.sessions.create.return_value = SimpleNamespace(id="sess_123")

    session, memory_store_id = build_session(client, "agent_123", 1, "memory_on")

    assert memory_store_id == "memstore_01PCBbgQ6HkoQr3ogWPsttz8"
    client.beta.memory_stores.create.assert_not_called()
    _, kwargs = client.beta.sessions.create.call_args
    assert kwargs["resources"] == [
        {
            "type": "memory_store",
            "memory_store_id": "memstore_01PCBbgQ6HkoQr3ogWPsttz8",
            "access": "read_only",
            "instructions": "Check for a prior ruling on this product + claim_type before ruling.",
        }
    ]


def test_build_session_memory_on_missing_env_raises_before_session_create(monkeypatch):
    monkeypatch.delenv("CLAIMS_REVIEW_MEMORY_STORE_ID", raising=False)
    client = MagicMock()
    client.beta.environments.create.return_value = SimpleNamespace(id="env_123")

    with pytest.raises(RuntimeError, match="CLAIMS_REVIEW_MEMORY_STORE_ID"):
        build_session(client, "agent_123", 1, "memory_on")

    client.beta.memory_stores.create.assert_not_called()
    client.beta.sessions.create.assert_not_called()


def test_build_session_memory_off_never_touches_memory_store_id(monkeypatch):
    monkeypatch.delenv("CLAIMS_REVIEW_MEMORY_STORE_ID", raising=False)
    client = MagicMock()
    client.beta.environments.create.return_value = SimpleNamespace(id="env_123")
    client.beta.sessions.create.return_value = SimpleNamespace(id="sess_123")

    session, memory_store_id = build_session(client, "agent_123", 1, "memory_off")

    assert memory_store_id is None
    client.beta.memory_stores.create.assert_not_called()
    _, kwargs = client.beta.sessions.create.call_args
    assert kwargs["resources"] is None


# --- d14: reorder (ruling prints before Memory write) + idempotent write ---


def test_path_does_not_exist_create_is_called():
    client = MagicMock()

    reason = write_ruling_to_memory(
        client, "memstore_abc123", "acme-widget", "performance", "ruling text"
    )

    assert reason == "wrote"
    client.beta.memory_stores.memories.create.assert_called_once_with(
        "memstore_abc123",
        content="ruling text",
        path="/acme-widget-performance.md",
    )
    client.beta.memory_stores.memories.update.assert_not_called()


def test_path_already_exists_update_is_called_not_create():
    client = MagicMock()
    client.beta.memory_stores.memories.create.side_effect = _conflict_error()
    client.beta.memory_stores.memories.list.return_value = [
        SimpleNamespace(id="mem_existing123", path="/acme-widget-performance.md"),
        SimpleNamespace(id="mem_other456", path="/other-product-comparative.md"),
    ]

    reason = write_ruling_to_memory(
        client, "memstore_abc123", "acme-widget", "performance", "new ruling text"
    )

    assert reason == "updated existing"
    client.beta.memory_stores.memories.create.assert_called_once()
    client.beta.memory_stores.memories.update.assert_called_once_with(
        "mem_existing123",
        memory_store_id="memstore_abc123",
        content="new ruling text",
    )


def test_memory_write_raises_ruling_already_printed(capsys):
    client = MagicMock()
    client.beta.memory_stores.memories.create.side_effect = RuntimeError("boom")

    print_ruling_and_grading("the ruling text", "satisfied", None, 0)

    with pytest.raises(RuntimeError, match="boom"):
        write_ruling_to_memory(
            client, "memstore_abc123", "acme-widget", "performance", "the ruling text"
        )

    out = capsys.readouterr().out
    assert "the ruling text" in out
    assert "RULING ARTIFACT" in out


# --- d15: mount path is API-read, delivered via user.message, never a
# hardcoded or template-substituted string ---


def test_get_memory_mount_path_reads_api_field_from_session():
    session = SimpleNamespace(
        resources=[
            SimpleNamespace(
                type="memory_store",
                memory_store_id="memstore_abc123",
                mount_path="/mnt/memory/claims-review-memory-persistent",
            )
        ]
    )

    assert (
        get_memory_mount_path(session)
        == "/mnt/memory/claims-review-memory-persistent"
    )


def test_get_memory_mount_path_none_when_no_memory_store_resource():
    session = SimpleNamespace(resources=[])

    assert get_memory_mount_path(session) is None


def test_get_memory_mount_path_ignores_non_memory_resources():
    session = SimpleNamespace(
        resources=[
            SimpleNamespace(type="file", mount_path="/mnt/session/uploads/foo"),
        ]
    )

    assert get_memory_mount_path(session) is None


def test_memory_off_prompt_has_no_mount_path_or_memory_references():
    text = PROMPT_FILES["memory_off"].read_text()

    assert "/mnt/memory" not in text
    assert "{{MEMORY_MOUNT_PATH}}" not in text
    assert "mount_path" not in text
    assert "mounted at" not in text
    assert "no memory capability" in text


def test_memory_on_prompt_has_no_literal_or_placeholder_path():
    """The system prompt states the mechanism (path arrives via the first
    user message) but never contains a literal mount path or an
    unresolved {{...}} substitution token — the launcher injects the
    real value into a user.message event at runtime, not into this file."""
    text = PROMPT_FILES["memory_on"].read_text()

    assert "{{MEMORY_MOUNT_PATH}}" not in text
    assert "/mnt/memory" not in text
    assert "first user message" in text
