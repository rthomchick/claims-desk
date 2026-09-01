"""Unit tests for server/agents/run_retest.py — the Week 19 retest harness.

Pure unit tests against a mocked anthropic client / mocked DB rows. No
live Managed Agents session, Memory store, or database — consistent
with test_launch_review.py's approach."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from server.agents.run_retest import (
    ClearSpec,
    RunSpec,
    ResumeState,
    build_sequence,
    clear_memory_store,
    plan_resume,
    run_key,
)


# --- build_sequence: pair-interleaved, 24 runs + 6 clears -----------------


def test_sequence_has_24_runs_and_6_clears():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    clears = [s for s in sequence if isinstance(s, ClearSpec)]
    assert len(runs) == 24
    assert len(clears) == 6


def test_sequence_is_pair_interleaved_not_arm_blocked():
    sequence = build_sequence()
    pair_labels_in_order = [s.pair_label for s in sequence]
    # First chain (rep 1) must be entirely pair A before pair B appears.
    first_b_index = pair_labels_in_order.index("B")
    assert all(label == "A" for label in pair_labels_in_order[:first_b_index])


def test_each_chain_is_memory_off_pair_clear_memory_on_pair():
    sequence = build_sequence()
    chain = sequence[:5]
    assert isinstance(chain[0], RunSpec) and chain[0].variant == "memory_off"
    assert isinstance(chain[1], RunSpec) and chain[1].variant == "memory_off"
    assert isinstance(chain[2], ClearSpec)
    assert isinstance(chain[3], RunSpec) and chain[3].variant == "memory_on"
    assert isinstance(chain[4], RunSpec) and chain[4].variant == "memory_on"


def test_claim_positions_are_1_then_2_within_each_arm_half():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    for i in range(0, len(runs), 2):
        assert runs[i].claim_position == 1
        assert runs[i + 1].claim_position == 2
        assert runs[i].pair_label == runs[i + 1].pair_label
        assert runs[i].variant == runs[i + 1].variant
        assert runs[i].repetition == runs[i + 1].repetition


def test_claim_slugs_match_pair_assignment():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    pair_a_slugs = {r.claim_slug for r in runs if r.pair_label == "A"}
    pair_b_slugs = {r.claim_slug for r in runs if r.pair_label == "B"}
    pair_c_slugs = {r.claim_slug for r in runs if r.pair_label == "C"}
    assert pair_a_slugs == {"vendor_compat-compatibility-01", "vendor_compat-compatibility-02"}
    assert pair_b_slugs == {"vendor_compat-compatibility-03", "vendor_compat-compatibility-04"}
    assert pair_c_slugs == {"vendor_compat-compatibility-05", "vendor_compat-compatibility-06"}


def test_both_repetitions_present_for_every_pair_and_arm():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    for pair_label in ("A", "B", "C"):
        for variant in ("memory_off", "memory_on"):
            reps = {r.repetition for r in runs if r.pair_label == pair_label and r.variant == variant}
            assert reps == {1, 2}


# --- clear_memory_store: mocked Memory API ---------------------------------


def _memory_item(memory_id: str, path: str):
    return SimpleNamespace(id=memory_id, path=path)


def _memory_full(memory_id: str, content: str, version_id: str):
    return SimpleNamespace(id=memory_id, content=content, memory_version_id=version_id)


def test_clear_memory_store_empty_case(tmp_path):
    client = MagicMock()
    client.beta.memory_stores.memories.list.return_value = []

    log_path = tmp_path / "clear.log"
    result = clear_memory_store(client, "memstore_abc", log_path, "test clear")

    assert result.entries == []
    assert result.post_delete_count == 0
    client.beta.memory_stores.memories.delete.assert_not_called()
    assert log_path.exists()
    content = log_path.read_text()
    assert "memstore_abc" in content
    assert "DONE. 0 entries deleted" in content


def test_clear_memory_store_populated_case(tmp_path):
    client = MagicMock()
    ruling_content = "# Ruling\n\n## Verdict\nsubstantiated\n"
    client.beta.memory_stores.memories.list.side_effect = [
        [_memory_item("mem_1", "/acme-widget-compatibility.md")],
        [],  # post-delete verification
    ]
    client.beta.memory_stores.memories.retrieve.return_value = _memory_full(
        "mem_1", ruling_content, "memver_1"
    )

    log_path = tmp_path / "clear.log"
    result = clear_memory_store(client, "memstore_abc", log_path, "test clear")

    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.path == "/acme-widget-compatibility.md"
    assert entry.memory_id == "mem_1"
    assert entry.memory_version_id == "memver_1"
    assert entry.content_size_bytes == len(ruling_content.encode("utf-8"))

    import hashlib

    expected_sha = hashlib.sha256(ruling_content.encode("utf-8")).hexdigest()
    assert entry.content_sha256 == expected_sha

    client.beta.memory_stores.memories.delete.assert_called_once_with(
        "mem_1",
        memory_store_id="memstore_abc",
        expected_content_sha256=expected_sha,
    )
    assert result.post_delete_count == 0

    log_content = log_path.read_text()
    assert "mem_1" in log_content
    assert expected_sha in log_content
    assert "verdict value (line after '## Verdict' heading): substantiated" in log_content


def test_clear_memory_store_extracts_verdict_value_not_heading(tmp_path):
    """Week 18's first clearing script captured the '## Verdict' heading
    text itself rather than the value on the line beneath it. This must
    extract the line AFTER the heading."""
    client = MagicMock()
    content = "# Ruling: x\n\n## Verdict\nnot_substantiated\n\n## Other section\n"
    client.beta.memory_stores.memories.list.side_effect = [
        [_memory_item("mem_1", "/x-compatibility.md")],
        [],
    ]
    client.beta.memory_stores.memories.retrieve.return_value = _memory_full(
        "mem_1", content, "memver_1"
    )

    log_path = tmp_path / "clear.log"
    clear_memory_store(client, "memstore_abc", log_path, "test clear")

    log_content = log_path.read_text()
    assert "verdict value (line after '## Verdict' heading): not_substantiated" in log_content
    assert "verdict value (line after '## Verdict' heading): ## Verdict" not in log_content


def test_clear_memory_store_refuses_if_non_empty_after_delete(tmp_path):
    client = MagicMock()
    content = "## Verdict\nsubstantiated\n"
    client.beta.memory_stores.memories.list.side_effect = [
        [_memory_item("mem_1", "/a.md")],
        [_memory_item("mem_1", "/a.md")],  # still present after "delete" — bug scenario
    ]
    client.beta.memory_stores.memories.retrieve.return_value = _memory_full(
        "mem_1", content, "memver_1"
    )

    log_path = tmp_path / "clear.log"
    with pytest.raises(RuntimeError, match="1 entries remain"):
        clear_memory_store(client, "memstore_abc", log_path, "test clear")

    # Must not retry the delete call.
    client.beta.memory_stores.memories.delete.assert_called_once()
    log_content = log_path.read_text()
    assert "REFUSING TO PROCEED" in log_content


def test_clear_memory_store_multiple_entries_all_recorded_and_deleted(tmp_path):
    client = MagicMock()
    items = [
        _memory_item("mem_1", "/a-compatibility.md"),
        _memory_item("mem_2", "/b-compatibility.md"),
    ]
    client.beta.memory_stores.memories.list.side_effect = [items, []]
    client.beta.memory_stores.memories.retrieve.side_effect = [
        _memory_full("mem_1", "## Verdict\nsubstantiated\n", "memver_1"),
        _memory_full("mem_2", "## Verdict\nnot_substantiated\n", "memver_2"),
    ]

    log_path = tmp_path / "clear.log"
    result = clear_memory_store(client, "memstore_abc", log_path, "test clear")

    assert len(result.entries) == 2
    assert client.beta.memory_stores.memories.delete.call_count == 2
    assert result.post_delete_count == 0


# --- Resumability -----------------------------------------------------------


def test_plan_resume_no_prior_runs_nothing_skipped():
    sequence = build_sequence()
    resume_state = ResumeState(completed=set())

    planned = plan_resume(sequence, resume_state, force=False)

    assert all(not p.skip for p in planned)


def test_plan_resume_skips_completed_runs():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    first_two = runs[:2]
    resume_state = ResumeState(completed={run_key(r) for r in first_two})

    planned = plan_resume(sequence, resume_state, force=False)

    skipped_keys = {run_key(p.step) for p in planned if isinstance(p.step, RunSpec) and p.skip}
    assert skipped_keys == {run_key(r) for r in first_two}


def test_plan_resume_clears_never_skipped():
    sequence = build_sequence()
    resume_state = ResumeState(completed=set())

    planned = plan_resume(sequence, resume_state, force=False)

    clear_steps = [p for p in planned if isinstance(p.step, ClearSpec)]
    assert len(clear_steps) == 6
    assert all(not p.skip for p in clear_steps)


def test_plan_resume_mid_chain_without_force_raises():
    """Claim 1 of a memory_on pair is recorded but claim 2 is not (and
    claim 2 is not itself in the completed set) — resuming would start
    at memory_on claim 2 whose claim 1 is already done. Must raise
    without --force."""
    sequence = build_sequence()
    claim_1_memory_on = next(
        s
        for s in sequence
        if isinstance(s, RunSpec)
        and s.variant == "memory_on"
        and s.pair_label == "A"
        and s.repetition == 1
        and s.claim_position == 1
    )
    resume_state = ResumeState(completed={run_key(claim_1_memory_on)})

    with pytest.raises(RuntimeError, match="--force"):
        plan_resume(sequence, resume_state, force=False)


def test_plan_resume_mid_chain_with_force_proceeds():
    sequence = build_sequence()
    claim_1_memory_on = next(
        s
        for s in sequence
        if isinstance(s, RunSpec)
        and s.variant == "memory_on"
        and s.pair_label == "A"
        and s.repetition == 1
        and s.claim_position == 1
    )
    resume_state = ResumeState(completed={run_key(claim_1_memory_on)})

    planned = plan_resume(sequence, resume_state, force=True)

    claim_2_planned = next(
        p
        for p in planned
        if isinstance(p.step, RunSpec)
        and p.step.variant == "memory_on"
        and p.step.pair_label == "A"
        and p.step.repetition == 1
        and p.step.claim_position == 2
    )
    assert claim_2_planned.skip is False
    assert "force" in claim_2_planned.skip_reason.lower()


def test_plan_resume_full_pair_completed_all_skipped():
    sequence = build_sequence()
    runs = [s for s in sequence if isinstance(s, RunSpec)]
    pair_a_rep_1_off = [
        r for r in runs if r.pair_label == "A" and r.repetition == 1 and r.variant == "memory_off"
    ]
    resume_state = ResumeState(completed={run_key(r) for r in pair_a_rep_1_off})

    planned = plan_resume(sequence, resume_state, force=False)

    for p in planned:
        if (
            isinstance(p.step, RunSpec)
            and p.step.pair_label == "A"
            and p.step.repetition == 1
            and p.step.variant == "memory_off"
        ):
            assert p.skip is True
