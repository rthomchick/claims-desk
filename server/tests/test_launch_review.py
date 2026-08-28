"""Unit tests for the d9 prohibited-tool-call pre-gate and the d12
grading-gated Memory write in launch_review.py.

Pure unit tests against constructed mock event data / mocked grading
results — no live Managed Agents session or API call, per d9's design
(avoid dependence on live grader behavior)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from server.agents.launch_review import (
    build_session,
    check_for_prohibited_tool_calls,
    get_memory_store_id,
    maybe_write_ruling_to_memory,
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
