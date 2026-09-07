"""Unit tests for the d9 prohibited-tool-call pre-gate and the d12
grading-gated Memory write in launch_review.py.

Pure unit tests against constructed mock event data / mocked grading
results — no live Managed Agents session or API call, per d9's design
(avoid dependence on live grader behavior)."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import anthropic

from server.agents import launch_review
from server.agents.launch_review import (
    PROMPT_FILES,
    RunLog,
    artifact_found_prior_ruling,
    build_session,
    check_for_prohibited_tool_calls,
    derive_manipulation_check,
    fetch_output_artifact,
    get_memory_mount_path,
    get_memory_store_id,
    make_run_log_path,
    maybe_write_ruling_to_memory,
    print_ruling_and_grading,
    run_review,
    trace_probed_memory_mount,
    write_ruling_to_memory,
)

RUNS_DIR = Path(__file__).parent.parent.parent / "runs"


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


# --- d16: incremental run log ---


def _stub_client(monkeypatch, runs_dir):
    """Build a fully mocked anthropic.Anthropic() client and patch
    run_review's dependencies so it runs end-to-end against fakes: no
    live session, no network. Returns (client, stream_events) so a test
    can populate stream_events before calling run_review."""
    monkeypatch.setattr(launch_review, "RUNS_DIR", runs_dir)

    client = MagicMock()

    monkeypatch.setattr(
        launch_review,
        "build_agent",
        lambda client, variant: ("agent_abc123", 1),
    )

    session = SimpleNamespace(id="sess_xyz789", resources=[])

    def fake_build_session(client, agent_id, agent_version, variant):
        return session, ("memstore_test123" if variant == "memory_on" else None)

    monkeypatch.setattr(launch_review, "build_session", fake_build_session)
    monkeypatch.setattr(
        launch_review, "get_memory_mount_path", lambda s: "/mnt/memory/store"
    )
    monkeypatch.setattr(
        launch_review,
        "RUBRIC_FILE",
        SimpleNamespace(read_text=lambda: "rubric text"),
    )
    monkeypatch.setattr(
        launch_review, "check_for_prohibited_tool_calls", lambda events: False
    )
    monkeypatch.setattr(
        launch_review,
        "maybe_write_ruling_to_memory",
        lambda *a, **k: False,
    )

    stream_events = []

    class FakeStream:
        def __enter__(self):
            return iter(stream_events)

        def __exit__(self, *exc_info):
            return False

    client.beta.sessions.events.stream.return_value = FakeStream()

    return client, stream_events


def _idle_event():
    return SimpleNamespace(type="session.status_idle", stop_reason=SimpleNamespace(type="done"))


def test_log_file_created_with_header_before_any_agent_turn(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())

    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_on")

    logs = list(tmp_path.glob("*.log"))
    assert len(logs) == 1
    content = logs[0].read_text()
    assert "claim_slug: acme-widget-performance-01" in content
    assert "variant: memory_on" in content
    assert "agent_id: agent_abc123" in content
    assert "session_id: sess_xyz789" in content
    assert "memory_store_id: memstore_test123" in content
    assert "mount_path: /mnt/memory/store" in content


def test_partial_log_survives_mid_run_exception(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)

    class BoomStream:
        def __enter__(self):
            raise RuntimeError("simulated mid-run failure")

        def __exit__(self, *exc_info):
            return False

    client.beta.sessions.events.stream.return_value = BoomStream()
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)

    with pytest.raises(RuntimeError, match="simulated mid-run failure"):
        run_review("acme-widget-performance-01", "memory_off")

    logs = list(tmp_path.glob("*.log"))
    assert len(logs) == 1
    content = logs[0].read_text()
    assert "claim_slug: acme-widget-performance-01" in content
    assert "agent_id: agent_abc123" in content
    assert "EXCEPTION" in content
    assert "simulated mid-run failure" in content
    assert "Traceback" in content


def test_multi_file_files_list_logs_all_files_not_just_first(tmp_path):
    """Multiple unrelated files present, only one matches the expected
    filename — that one is selected and logged, regardless of position."""
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_first", filename="ruling_a.md", size_bytes=100, created_at="t1"),
        SimpleNamespace(id="file_second", filename="acme-widget-performance-01.md", size_bytes=200, created_at="t2"),
        SimpleNamespace(id="file_third", filename="ruling_c.md", size_bytes=300, created_at="t3"),
    ]
    client.beta.files.list.return_value = files
    download_response = MagicMock()
    download_response.read.return_value = b"ruling content"
    client.beta.files.download.return_value = download_response

    fetch_output_artifact(client, "sess_xyz789", "acme-widget-performance-01", run_log=run_log)
    run_log.close()

    content = (tmp_path / "test.log").read_text()
    assert "file_first" in content
    assert "file_second" in content
    assert "file_third" in content
    assert "ruling_a.md" in content
    assert "acme-widget-performance-01.md" in content
    assert "ruling_c.md" in content
    assert "[1]" in content and "SELECTED" in content
    client.beta.files.download.assert_called_once_with("file_second", betas=[launch_review.FILES_BETA])


# --- d17: filename-based selection, not index (fixes f17) ---


def test_exactly_one_matching_file_selected_no_raise(tmp_path):
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_a", filename="acme-widget-performance-01.md", size_bytes=100, created_at="t1"),
    ]
    client.beta.files.list.return_value = files
    download_response = MagicMock()
    download_response.read.return_value = b"ruling content"
    client.beta.files.download.return_value = download_response

    result = fetch_output_artifact(client, "sess_xyz789", "acme-widget-performance-01", run_log=run_log)
    run_log.close()

    assert result == "ruling content"
    client.beta.files.download.assert_called_once_with("file_a", betas=[launch_review.FILES_BETA])


def test_zero_matching_files_retries_then_raises_naming_expected_and_found(tmp_path):
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_a", filename="other-claim-01.md", size_bytes=100, created_at="t1"),
    ]
    client.beta.files.list.return_value = files

    with pytest.raises(RuntimeError) as excinfo:
        fetch_output_artifact(client, "sess_xyz789", "acme-widget-performance-01", run_log=run_log)
    run_log.close()

    assert "acme-widget-performance-01.md" in str(excinfo.value)
    assert "other-claim-01.md" in str(excinfo.value)
    assert client.beta.files.list.call_count == 3
    client.beta.files.download.assert_not_called()


def test_two_matching_files_raises_immediately_no_retry(tmp_path):
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_a", filename="acme-widget-performance-01.md", size_bytes=100, created_at="t1"),
        SimpleNamespace(id="file_b", filename="acme-widget-performance-01.md", size_bytes=100, created_at="t2"),
    ]
    client.beta.files.list.return_value = files

    with pytest.raises(RuntimeError, match="Multiple output files matched"):
        fetch_output_artifact(client, "sess_xyz789", "acme-widget-performance-01", run_log=run_log)
    run_log.close()

    assert client.beta.files.list.call_count == 1
    client.beta.files.download.assert_not_called()


def test_matching_file_plus_unexpected_file_selects_match_and_logs_anomaly(tmp_path):
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_a", filename="acme-widget-performance-01.md", size_bytes=100, created_at="t1"),
        SimpleNamespace(id="file_b", filename="stray-leftover.md", size_bytes=50, created_at="t2"),
    ]
    client.beta.files.list.return_value = files
    download_response = MagicMock()
    download_response.read.return_value = b"ruling content"
    client.beta.files.download.return_value = download_response

    fetch_output_artifact(client, "sess_xyz789", "acme-widget-performance-01", run_log=run_log)
    run_log.close()

    content = (tmp_path / "test.log").read_text()
    client.beta.files.download.assert_called_once_with("file_a", betas=[launch_review.FILES_BETA])
    assert "UNEXPECTED ARTIFACT" in content
    assert "stray-leftover.md" in content
    assert "file_b" in content


def test_f18_case_two_files_selects_01_logs_02_as_unexpected(tmp_path):
    """The exact f18 scenario: kalder_govern-compliance-01.md and -02.md
    both present in the session's outputs. Invoked for -01, must select
    -01.md and log -02.md as a named anomaly — never take index 0
    unconditionally."""
    run_log = RunLog(tmp_path / "test.log")
    client = MagicMock()
    files = [
        SimpleNamespace(id="file_00", filename="kalder_govern-compliance-02.md", size_bytes=100, created_at="t1"),
        SimpleNamespace(id="file_01", filename="kalder_govern-compliance-01.md", size_bytes=120, created_at="t2"),
    ]
    client.beta.files.list.return_value = files
    download_response = MagicMock()
    download_response.read.return_value = b"ruling for -01"
    client.beta.files.download.return_value = download_response

    result = fetch_output_artifact(client, "sess_xyz789", "kalder_govern-compliance-01", run_log=run_log)
    run_log.close()

    assert result == "ruling for -01"
    client.beta.files.download.assert_called_once_with("file_01", betas=[launch_review.FILES_BETA])
    content = (tmp_path / "test.log").read_text()
    assert "UNEXPECTED ARTIFACT" in content
    assert "kalder_govern-compliance-02.md" in content
    assert "file_00" in content


def test_tool_call_arguments_appear_in_log(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(
        SimpleNamespace(
            type="agent.mcp_tool_use",
            id="tu_1",
            name="list_claims",
            input={"product_key": "kalder_govern"},
            evaluated_permission=None,
        )
    )
    stream_events.append(_idle_event())

    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_on")

    logs = list(tmp_path.glob("*.log"))
    content = logs[0].read_text()
    assert "list_claims" in content
    assert "product_key" in content
    assert "kalder_govern" in content


def test_agent_conversational_message_logged(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(
        SimpleNamespace(
            type="agent.message",
            id="msg_1",
            content=[SimpleNamespace(type="text", text="Checking prior rulings first.")],
        )
    )
    stream_events.append(_idle_event())

    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_on")

    logs = list(tmp_path.glob("*.log"))
    content = logs[0].read_text()
    assert "AGENT MESSAGE" in content
    assert "Checking prior rulings first." in content


def test_make_run_log_path_creates_runs_dir(monkeypatch, tmp_path):
    runs_dir = tmp_path / "runs"
    monkeypatch.setattr(launch_review, "RUNS_DIR", runs_dir)

    path = make_run_log_path("acme-widget-performance-01", "memory_off")

    assert runs_dir.is_dir()
    assert path.parent == runs_dir
    assert "acme-widget-performance-01" in path.name


# --- d18: injected user.message names the target claim and forbids early
# action (fixes f18: agent picked its own claim before user.define_outcome
# arrived) ---


def _sent_events(client):
    """Extract the `events` kwarg from the single events.send() call made
    by run_review for the pre-outcome injection + define_outcome."""
    _, kwargs = client.beta.sessions.events.send.call_args
    return kwargs["events"]


def test_injected_message_names_claim_slug(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("kalder_govern-compliance-01", "memory_on")

    events = _sent_events(client)
    message_event = next(e for e in events if e["type"] == "user.message")
    text = message_event["content"][0]["text"]
    assert "kalder_govern-compliance-01" in text


def test_injected_message_carries_mount_path(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("kalder_govern-compliance-01", "memory_on")

    events = _sent_events(client)
    message_event = next(e for e in events if e["type"] == "user.message")
    text = message_event["content"][0]["text"]
    assert "/mnt/memory/store" in text


def test_injected_message_forbids_action_before_outcome(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("kalder_govern-compliance-01", "memory_on")

    events = _sent_events(client)
    assert events[0]["type"] == "user.message"
    assert events[1]["type"] == "user.define_outcome"
    text = events[0]["content"][0]["text"]
    lowered = text.lower()
    assert "not" in lowered and ("tool" in lowered or "action" in lowered)
    assert "ruling" in lowered


def test_injected_claim_slug_matches_define_outcome_source(monkeypatch, tmp_path):
    """Both the injected message and user.define_outcome must name the same
    claim, derived from the same run_review argument — not two independent
    sources of truth."""
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("kalder_govern-compliance-01", "memory_on")

    events = _sent_events(client)
    message_event = next(e for e in events if e["type"] == "user.message")
    outcome_event = next(e for e in events if e["type"] == "user.define_outcome")
    message_text = message_event["content"][0]["text"]
    outcome_description = outcome_event["description"]

    assert "kalder_govern-compliance-01" in message_text
    assert "kalder_govern-compliance-01" in outcome_description


# --- manipulation-check derivation (replaces --manipulation-check) ---

TOOL_CALL_LINE = re.compile(r"^TOOL CALL \[(?P<event_type>[^\]]+)\] (?P<name>\S+) args=(?P<args>.+)$")
RULING_ARTIFACT_HEADER = "RULING ARTIFACT"
GRADING_RESULT_HEADER = "GRADING RESULT"


def _load_real_run_log(filename: str) -> tuple[list, str, str]:
    """Parse a real Week 18 run log into (tool_call_events, mount_path,
    ruling_text) using the exact same line shape RunLog.tool_call writes:
    'TOOL CALL [{event_type}] {name} args={input!r}'.

    Reconstructs SimpleNamespace(type=, name=, input=) events — the same
    attributes run_review's stream loop reads off real SDK events — by
    ast.literal_eval-ing the repr'd args dict back into a dict. Used so
    at least one derivation test runs against a genuine recorded trace
    and artifact rather than a hand-built fixture.
    """
    text = (RUNS_DIR / filename).read_text()

    mount_path = None
    for line in text.splitlines():
        if line.startswith("mount_path: "):
            mount_path = line.removeprefix("mount_path: ").strip()
            break

    tool_call_events = []
    for line in text.splitlines():
        match = TOOL_CALL_LINE.match(line)
        if not match:
            continue
        event_type = match.group("event_type")
        if event_type not in ("agent.tool_use", "agent.mcp_tool_use"):
            continue
        tool_call_events.append(
            SimpleNamespace(
                type=event_type,
                name=match.group("name"),
                input=ast.literal_eval(match.group("args")),
            )
        )

    artifact_start = text.rindex(RULING_ARTIFACT_HEADER)
    artifact_end = text.index(GRADING_RESULT_HEADER, artifact_start)
    artifact_lines = text[artifact_start:artifact_end].splitlines()
    # Drop the "RULING ARTIFACT" banner line and its bracketing dash rules,
    # plus the trailing blank line before the next banner's dash rule.
    ruling_text = "\n".join(artifact_lines[2:-2]).strip()

    return tool_call_events, mount_path, ruling_text


WEEK18_MEMORY_ON_LOGS = {
    "claim_1_first_attempt": "20260829T073109Z-kalder_govern-compliance-01-memory_on.log",
    "claim_1_retry": "20260829T075256Z-kalder_govern-compliance-01-memory_on.log",
    "claim_2": "20260829T075553Z-kalder_govern-compliance-02-memory_on.log",
}


def test_artifact_found_prior_ruling_true_on_real_claim_2_log():
    _, _, ruling_text = _load_real_run_log(WEEK18_MEMORY_ON_LOGS["claim_2"])
    assert artifact_found_prior_ruling(ruling_text) is True


def test_artifact_found_prior_ruling_false_on_real_claim_1_logs():
    for key in ("claim_1_first_attempt", "claim_1_retry"):
        _, _, ruling_text = _load_real_run_log(WEEK18_MEMORY_ON_LOGS[key])
        assert artifact_found_prior_ruling(ruling_text) is False


def test_artifact_found_prior_ruling_does_not_misread_quoted_prior_absence():
    """The claim-2 artifact quotes the claim-1 prior verbatim, and that
    quoted prior's own Prior-Ruling-Context subsection reads 'No prior
    ruling found ...'. A naive substring search over the whole section
    would misread this as absence. Only the section's own opening
    statement should be consulted."""
    _, _, ruling_text = _load_real_run_log(WEEK18_MEMORY_ON_LOGS["claim_2"])
    assert "No prior ruling found in Memory for this product" in ruling_text
    assert artifact_found_prior_ruling(ruling_text) is True


def test_artifact_found_prior_ruling_none_when_section_missing():
    assert artifact_found_prior_ruling("# Ruling: x\n\n## Verdict\nsubstantiated\n") is None


def _ruling_with_prior_ruling_context(opening: str) -> str:
    return (
        "# Ruling: x\n\n"
        "## Verdict\npartially\n\n"
        f"## Prior Ruling Context (verbatim, from Memory — or explicit absence)\n{opening}\n\n"
        "## Rationale\ntext\n"
    )


# Verbatim opening lines observed across the six Week 18/19 memory_on
# claim-2 runs (d(w19)-14) — four distinct found-phrasings.
OBSERVED_FOUND_OPENINGS = [
    "Prior ruling file found and read at "
    "`/mnt/memory/claims-review-memory-persistent/vendor_compat-compatibility.md`, "
    "recording a ruling on `vendor_compat-compatibility-01`.",
    "A prior ruling file for this product + claim_type was found at\n"
    "`/mnt/memory/claims-review-memory-persistent/kalder_govern-compliance.md`.\n"
    "It records a ruling on a different claim within the same product and\n"
    "claim_type. Verbatim excerpts follow.",
    "A prior ruling file was found at "
    "`/mnt/memory/claims-review-memory-persistent/vendor_compat-compatibility.md` "
    "and read. It records a ruling on a different claim within the same product + claim_type.",
    "File found and read at "
    "`/mnt/memory/claims-review-memory-persistent/vendor_compat-compatibility.md`. "
    "It records a prior ruling on a different claim within this same product + claim_type.",
]


@pytest.mark.parametrize("opening", OBSERVED_FOUND_OPENINGS)
def test_artifact_found_prior_ruling_true_on_observed_phrasings(opening):
    ruling_text = _ruling_with_prior_ruling_context(opening)
    assert artifact_found_prior_ruling(ruling_text) is True


def test_artifact_found_prior_ruling_false_on_absence_phrasing():
    ruling_text = _ruling_with_prior_ruling_context(
        "No prior ruling found in Memory for this product + claim_type."
    )
    assert artifact_found_prior_ruling(ruling_text) is False


def test_artifact_found_prior_ruling_none_on_unparseable_opening():
    ruling_text = _ruling_with_prior_ruling_context(
        "Memory was consulted and nothing further is reported here."
    )
    assert artifact_found_prior_ruling(ruling_text) is None


def test_trace_probed_memory_mount_true_on_real_claim_2_log():
    tool_call_events, mount_path, _ = _load_real_run_log(WEEK18_MEMORY_ON_LOGS["claim_2"])
    assert trace_probed_memory_mount(tool_call_events, mount_path) is True


def test_trace_probed_memory_mount_false_with_no_matching_reads():
    events = [
        SimpleNamespace(type="agent.mcp_tool_use", name="list_claims", input={}),
        SimpleNamespace(type="agent.tool_use", name="write", input={"file_path": "/mnt/session/outputs/x.md"}),
    ]
    assert trace_probed_memory_mount(events, "/mnt/memory/claims-review-memory-persistent") is False


def test_trace_probed_memory_mount_ignores_reads_outside_mount():
    events = [
        SimpleNamespace(type="agent.tool_use", name="read", input={"file_path": "/mnt/session/uploads/rubric.md"}),
    ]
    assert trace_probed_memory_mount(events, "/mnt/memory/claims-review-memory-persistent") is False


# The six rules-table rows, plus the mismatch case and the claim-1-found
# case that falls outside the table.

CLAIM_1_NOT_FOUND_ARTIFACT = (
    "## Prior Ruling Context (verbatim, from Memory — or explicit absence)\n"
    "No prior ruling found in Memory for this product + claim_type.\n"
)
CLAIM_2_FOUND_ARTIFACT = (
    "## Prior Ruling Context (verbatim, from Memory — or explicit absence)\n"
    "A prior ruling file for this product + claim_type was found at\n"
    "`/mnt/memory/claims-review-memory-persistent/acme-widget-performance.md`.\n"
)

MOUNT = "/mnt/memory/claims-review-memory-persistent"


def _read_event(file_path: str):
    return SimpleNamespace(type="agent.tool_use", name="read", input={"file_path": file_path})


def test_rule_memory_on_claim_1_probed_not_found_passes():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    result = derive_manipulation_check(
        "memory_on", 1, events, MOUNT, CLAIM_1_NOT_FOUND_ARTIFACT
    )
    assert result == "pass:probed_not_found"


def test_rule_memory_on_claim_2_probed_found_passes():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    result = derive_manipulation_check(
        "memory_on", 2, events, MOUNT, CLAIM_2_FOUND_ARTIFACT
    )
    assert result == "pass:probed_found"


def test_rule_memory_on_claim_2_probed_not_found_voids():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    result = derive_manipulation_check(
        "memory_on", 2, events, MOUNT, CLAIM_1_NOT_FOUND_ARTIFACT
    )
    assert result == "void:probed_not_found"


def test_rule_memory_on_no_probe_voids_for_claim_1():
    events = [SimpleNamespace(type="agent.mcp_tool_use", name="list_claims", input={})]
    result = derive_manipulation_check(
        "memory_on", 1, events, MOUNT, CLAIM_1_NOT_FOUND_ARTIFACT
    )
    assert result == "void:no_probe"


def test_rule_memory_on_no_probe_voids_for_claim_2():
    events = [SimpleNamespace(type="agent.mcp_tool_use", name="list_claims", input={})]
    result = derive_manipulation_check(
        "memory_on", 2, events, MOUNT, CLAIM_2_FOUND_ARTIFACT
    )
    assert result == "void:no_probe"


def test_rule_memory_off_no_probe_passes():
    events = [SimpleNamespace(type="agent.mcp_tool_use", name="check_substantiation", input={})]
    result = derive_manipulation_check("memory_off", None, events, None, CLAIM_1_NOT_FOUND_ARTIFACT)
    assert result == "pass:no_probe"


def test_rule_memory_off_any_probe_voids():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    result = derive_manipulation_check("memory_off", None, events, MOUNT, CLAIM_1_NOT_FOUND_ARTIFACT)
    assert result == "void:memory_off_probed"


def test_mismatch_artifact_section_unparseable_voids_distinctly():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    unparseable_artifact = "# Ruling: x\n\n## Verdict\nsubstantiated\n"
    result = derive_manipulation_check("memory_on", 2, events, MOUNT, unparseable_artifact)
    assert result == "void:trace_artifact_mismatch"


def test_claim_1_found_prior_is_not_reported_as_mismatch():
    """A claim-1 run that probed and found something is outside the
    six-row table (Memory wasn't actually clean going into the pair) —
    it must get its own diagnosable code, not be folded into the
    trace/artifact mismatch code, since the two sources actually agree
    here (both say a probe happened and something was found)."""
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    result = derive_manipulation_check("memory_on", 1, events, MOUNT, CLAIM_2_FOUND_ARTIFACT)
    assert result == "void:claim_1_found_prior"


def test_memory_on_missing_claim_position_raises():
    events = [_read_event(f"{MOUNT}/acme-widget-performance.md")]
    with pytest.raises(ValueError, match="claim_position"):
        derive_manipulation_check("memory_on", None, events, MOUNT, CLAIM_1_NOT_FOUND_ARTIFACT)


# --- sanity check: derived value for each of the three real Week 18
# memory_on runs, cross-checked against known history. Runs 1 and 2 are
# both claim_1 (the first is the off-target attempt on -02 before the
# operator corrected the target to -01; the second is the corrected
# retry actually reviewing -01, the first-ever ruling for that
# product+claim_type). Run 3 is claim_2 (-02, reviewed after -01's
# ruling was written to Memory) and found the claim_1 prior. ---


def test_week18_run_sanity_claim_1_first_attempt_is_probed_not_found():
    events, mount_path, ruling_text = _load_real_run_log(
        WEEK18_MEMORY_ON_LOGS["claim_1_first_attempt"]
    )
    result = derive_manipulation_check("memory_on", 1, events, mount_path, ruling_text)
    assert result == "pass:probed_not_found"


def test_week18_run_sanity_claim_1_retry_is_probed_not_found():
    events, mount_path, ruling_text = _load_real_run_log(WEEK18_MEMORY_ON_LOGS["claim_1_retry"])
    result = derive_manipulation_check("memory_on", 1, events, mount_path, ruling_text)
    assert result == "pass:probed_not_found"


def test_week18_run_sanity_claim_2_is_probed_found():
    events, mount_path, ruling_text = _load_real_run_log(WEEK18_MEMORY_ON_LOGS["claim_2"])
    result = derive_manipulation_check("memory_on", 2, events, mount_path, ruling_text)
    assert result == "pass:probed_found"


def test_memory_off_sends_no_injected_message(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off")

    events = _sent_events(client)
    assert len(events) == 1
    assert events[0]["type"] == "user.define_outcome"


# --- Week 21: --user-premise channel + append_ruling permission denial ---

EXPECTED_OUTCOME_DESCRIPTION = (
    "Review the marketing claim {claim_slug} and produce a ruling."
)


def test_no_user_premise_memory_off_sends_only_define_outcome(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off")

    events = _sent_events(client)
    assert len(events) == 1
    assert events[0]["type"] == "user.define_outcome"
    assert events[0]["description"] == EXPECTED_OUTCOME_DESCRIPTION.format(
        claim_slug="acme-widget-performance-01"
    )
    assert events[0]["rubric"] == {"type": "text", "content": "rubric text"}


def test_user_premise_memory_off_sends_premise_then_outcome(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off", user_premise="SOME TEXT")

    events = _sent_events(client)
    assert len(events) == 2
    assert events[0]["type"] == "user.message"
    assert events[0]["content"] == [{"type": "text", "text": "SOME TEXT"}]
    assert events[1]["type"] == "user.define_outcome"
    assert events[1]["description"] == EXPECTED_OUTCOME_DESCRIPTION.format(
        claim_slug="acme-widget-performance-01"
    )
    assert events[1]["rubric"] == {"type": "text", "content": "rubric text"}


def test_user_premise_memory_on_sends_mount_message_then_premise_then_outcome(
    monkeypatch, tmp_path
):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("kalder_govern-compliance-01", "memory_on", user_premise="SOME TEXT")

    events = _sent_events(client)
    assert len(events) == 3
    assert events[0]["type"] == "user.message"
    assert "kalder_govern-compliance-01" in events[0]["content"][0]["text"]
    assert events[1]["type"] == "user.message"
    assert events[1]["content"] == [{"type": "text", "text": "SOME TEXT"}]
    assert events[2]["type"] == "user.define_outcome"
    assert events[2]["description"] == EXPECTED_OUTCOME_DESCRIPTION.format(
        claim_slug="kalder_govern-compliance-01"
    )
    assert events[2]["rubric"] == {"type": "text", "content": "rubric text"}


def test_denied_tools_contains_only_append_ruling():
    assert launch_review.DENIED_TOOLS == {"append_ruling"}


def test_prohibited_tools_unchanged_by_denied_tools_addition():
    assert launch_review.PROHIBITED_TOOLS == {
        "append_claim",
        "delete_claim",
        "classify_claim_risk",
    }


def _mcp_tool_use_event(name: str, evaluated_permission: str | None, tool_use_id: str = "tu_1"):
    return SimpleNamespace(
        type="agent.mcp_tool_use",
        id=tool_use_id,
        name=name,
        input={},
        evaluated_permission=evaluated_permission,
    )


def test_append_ruling_ask_permission_sends_deny(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_mcp_tool_use_event("append_ruling", "ask", tool_use_id="tu_deny"))
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off")

    confirmation_calls = [
        call
        for call in client.beta.sessions.events.send.call_args_list
        if call.kwargs["events"][0]["type"] == "user.tool_confirmation"
    ]
    assert len(confirmation_calls) == 1
    confirmation_event = confirmation_calls[0].kwargs["events"][0]
    assert confirmation_event["tool_use_id"] == "tu_deny"
    assert confirmation_event["result"] == "deny"


def test_get_claim_status_ask_permission_sends_allow(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_mcp_tool_use_event("get_claim_status", "ask", tool_use_id="tu_allow"))
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off")

    confirmation_calls = [
        call
        for call in client.beta.sessions.events.send.call_args_list
        if call.kwargs["events"][0]["type"] == "user.tool_confirmation"
    ]
    assert len(confirmation_calls) == 1
    confirmation_event = confirmation_calls[0].kwargs["events"][0]
    assert confirmation_event["tool_use_id"] == "tu_allow"
    assert confirmation_event["result"] == "allow"


def test_denied_append_ruling_run_completes_without_exception(monkeypatch, tmp_path):
    """A denied append_ruling call must not raise or terminate the
    session: fetch_output_artifact still runs and run_review returns its
    normal dict."""
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_mcp_tool_use_event("append_ruling", "ask", tool_use_id="tu_deny"))
    stream_events.append(
        SimpleNamespace(
            type="span.outcome_evaluation_end",
            result="satisfied",
            explanation=None,
            iteration=0,
        )
    )
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)

    fetch_calls = []

    def fake_fetch(client, session_id, claim_slug, run_log=None):
        fetch_calls.append((session_id, claim_slug))
        return "the ruling"

    monkeypatch.setattr(launch_review, "fetch_output_artifact", fake_fetch)

    result = run_review("acme-widget-performance-01", "memory_off")

    assert len(fetch_calls) == 1
    assert result["ruling"] == "the ruling"
    assert result["outcome_result"] == "satisfied"
    assert result["session_id"] == "sess_xyz789"


# --- Week 21: verbatim user-premise logging ---


def _premise_log_text(runs_dir):
    logs = list(runs_dir.glob("*.log"))
    assert len(logs) == 1
    return logs[0].read_text()


def test_user_premise_written_verbatim_to_log_exactly_once(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off", user_premise="SOME TEXT")

    content = _premise_log_text(tmp_path)
    assert "USER PREMISE (verbatim):" in content
    assert content.count("SOME TEXT") == 1
    assert "(none supplied)" not in content


def test_no_user_premise_writes_explicit_absence_line(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    run_review("acme-widget-performance-01", "memory_off")

    content = _premise_log_text(tmp_path)
    assert "USER PREMISE: (none supplied)" in content
    assert "USER PREMISE (verbatim):" not in content


def test_multiline_quoted_premise_round_trips_verbatim(monkeypatch, tmp_path):
    client, stream_events = _stub_client(monkeypatch, tmp_path)
    stream_events.append(_idle_event())
    monkeypatch.setattr(anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(
        launch_review,
        "fetch_output_artifact",
        lambda client, session_id, claim_slug, run_log=None: "the ruling",
    )

    premise = 'first line with " quote\nsecond line'
    run_review("acme-widget-performance-01", "memory_off", user_premise=premise)

    content = _premise_log_text(tmp_path)
    assert premise in content
    assert content.count(premise) == 1
