"""Unit tests for the d9 prohibited-tool-call pre-gate in launch_review.py.

Pure unit tests against constructed mock event data — no live Managed
Agents session or API call, per d9's design (avoid dependence on live
grader behavior)."""

from __future__ import annotations

from types import SimpleNamespace

from server.agents.launch_review import check_for_prohibited_tool_calls


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
