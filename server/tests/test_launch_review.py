"""Unit tests for the d9 prohibited-tool-call pre-gate and the d12
grading-gated Memory write in launch_review.py.

Pure unit tests against constructed mock event data / mocked grading
results — no live Managed Agents session or API call, per d9's design
(avoid dependence on live grader behavior)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from server.agents.launch_review import (
    check_for_prohibited_tool_calls,
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
