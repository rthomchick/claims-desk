"""run_retest.py — Week 19 h1-r retest harness.

Sequences 24 launch_review.py runs (3 pairs x 2 repetitions x 4 arms:
memory_off claim 1, memory_off claim 2, memory_on claim 1, memory_on
claim 2), clearing the persistent Memory store between each chain's
memory_off and memory_on halves.

Runs are pair-interleaved rather than arm-blocked: Week 18's w2 observed
session-order effects shifting reasoning strictness with no memory
recall involved. Arm-blocking would put that whole observed effect on
the arm contrast, which is the thing this retest measures.

launch_review.py runs exactly one session per invocation and does no
sequencing; this harness calls it as a subprocess once per run so each
session gets a clean process (Week 18 precedent), sequences the 24
calls, clears Memory between chains, and records what happened. It does
not score anything — agreement scoring against the six locked verdicts
(docs/week19-locked-verdicts.md) is separate work after the runs exist.

Usage:
    python -m server.agents.run_retest --dry-run
    python -m server.agents.run_retest
    python -m server.agents.run_retest --force   # see RESUMABILITY below
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from server.agents.launch_review import RUNS_DIR, get_memory_store_id
from server.db.client import execute, fetchall_dict

load_dotenv()

REPO_ROOT = Path(__file__).parent.parent.parent
LAUNCH_REVIEW_MODULE = "server.agents.launch_review"

VERDICT_HEADING = "## Verdict"


@dataclass(frozen=True)
class PairSpec:
    label: str
    claim_1_slug: str
    claim_2_slug: str


PAIRS = [
    PairSpec("A", "vendor_compat-compatibility-01", "vendor_compat-compatibility-02"),
    PairSpec("B", "vendor_compat-compatibility-03", "vendor_compat-compatibility-04"),
    PairSpec("C", "vendor_compat-compatibility-05", "vendor_compat-compatibility-06"),
]

REPETITIONS = [1, 2]


@dataclass(frozen=True)
class RunSpec:
    """One launch_review.py invocation."""

    claim_slug: str
    variant: str  # "memory_off" | "memory_on"
    pair_label: str
    repetition: int
    claim_position: int  # 1 | 2


@dataclass(frozen=True)
class ClearSpec:
    """A Memory-store clear positioned between a chain's memory_off and
    memory_on halves."""

    pair_label: str
    repetition: int


Step = RunSpec | ClearSpec


def build_sequence() -> list[Step]:
    """Build the full 24-run, 6-clear pair-interleaved sequence.

    For each repetition, for each pair (A, B, C), in order:
      memory_off claim 1, memory_off claim 2, CLEAR, memory_on claim 1,
      memory_on claim 2.
    """
    sequence: list[Step] = []
    for repetition in REPETITIONS:
        for pair in PAIRS:
            sequence.append(
                RunSpec(pair.claim_1_slug, "memory_off", pair.label, repetition, 1)
            )
            sequence.append(
                RunSpec(pair.claim_2_slug, "memory_off", pair.label, repetition, 2)
            )
            sequence.append(ClearSpec(pair.label, repetition))
            sequence.append(
                RunSpec(pair.claim_1_slug, "memory_on", pair.label, repetition, 1)
            )
            sequence.append(
                RunSpec(pair.claim_2_slug, "memory_on", pair.label, repetition, 2)
            )
    return sequence


def format_sequence(sequence: list[Step]) -> str:
    lines = []
    run_number = 0
    for step in sequence:
        if isinstance(step, ClearSpec):
            lines.append(
                f"        CLEAR MEMORY STORE  (pair {step.pair_label} rep {step.repetition})"
            )
            continue
        run_number += 1
        lines.append(
            f"  {run_number:2d}. {step.variant:11s} {step.claim_slug:32s} "
            f"pair={step.pair_label} rep={step.repetition} claim_position={step.claim_position}"
        )
    return "\n".join(lines)


# --- Memory clearing ---------------------------------------------------


@dataclass
class ClearedEntry:
    path: str
    memory_id: str
    memory_version_id: str
    content_size_bytes: int
    content_sha256: str


@dataclass
class ClearResult:
    memory_store_id: str
    entries: list[ClearedEntry] = field(default_factory=list)
    post_delete_count: int = 0
    log_path: Path | None = None


def _verdict_value(content: str) -> str | None:
    """Extract the verdict VALUE — the line after the '## Verdict'
    heading, not the heading itself.

    Week 18's first clearing script recorded the heading text
    ("## Verdict") as the "verdict line," not the ruling value beneath
    it. Fixed here per the task: pull the line after the heading, before
    any deletion occurs, rather than relying on recovering it afterward
    from memory-version history.
    """
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == VERDICT_HEADING:
            for candidate in lines[i + 1 :]:
                if candidate.strip():
                    return candidate.strip()
            return None
    return None


def clear_memory_store(
    client: anthropic.Anthropic,
    memory_store_id: str,
    log_path: Path,
    operation_label: str,
) -> ClearResult:
    """Clear every entry in the Memory store, logging a fixity record of
    each entry before it is deleted.

    Called only between chains, never from inside run_review — deletion
    stays out of the run path, consistent with d12 making the agent's
    Memory access read-only.

    For each entry: record path, memory_id, memory_version_id,
    content_size_bytes, and a locally computed sha256 of the content,
    then delete it (guarded by that same hash via
    expected_content_sha256, so a delete never fires against content
    that changed between listing and deleting). Then list again to
    confirm zero entries remain — if the store is non-empty after
    deletion, raise rather than retry silently.
    """
    result = ClearResult(memory_store_id=memory_store_id, log_path=log_path)

    lines = [
        "=" * 70,
        f"timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        f"operation: {operation_label}",
        f"memory_store_id: {memory_store_id}",
        "=" * 70,
        "",
        "STEP 1 — record before removing",
        "-" * 70,
    ]

    items = list(client.beta.memory_stores.memories.list(memory_store_id, path_prefix="/"))
    for item in items:
        full = client.beta.memory_stores.memories.retrieve(
            item.id, memory_store_id=memory_store_id, view="full"
        )
        content: str = full.content
        content_bytes = content.encode("utf-8")
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        verdict = _verdict_value(content)

        entry = ClearedEntry(
            path=item.path,
            memory_id=item.id,
            memory_version_id=full.memory_version_id,
            content_size_bytes=len(content_bytes),
            content_sha256=sha256,
        )
        result.entries.append(entry)

        lines.append(f"path: {entry.path}")
        lines.append(f"memory_id: {entry.memory_id}")
        lines.append(f"memory_store_id: {memory_store_id}")
        lines.append(f"memory_version_id: {entry.memory_version_id}")
        lines.append(f"content_size_bytes: {entry.content_size_bytes}")
        lines.append(f"content_sha256: {entry.content_sha256}")
        lines.append(f"verdict value (line after '## Verdict' heading): {verdict}")
        lines.append("-" * 70)

    lines.append("")
    lines.append("STEP 2 — delete")
    lines.append("-" * 70)

    for entry in result.entries:
        client.beta.memory_stores.memories.delete(
            entry.memory_id,
            memory_store_id=memory_store_id,
            expected_content_sha256=entry.content_sha256,
        )
        lines.append(f"deleted: path={entry.path} memory_id={entry.memory_id}")

    lines.append("-" * 70)
    lines.append("")
    lines.append("STEP 3 — verify empty")
    lines.append("-" * 70)

    remaining = list(client.beta.memory_stores.memories.list(memory_store_id, path_prefix="/"))
    result.post_delete_count = len(remaining)
    lines.append(
        f"memories.list(memory_store_id={memory_store_id!r}) after deletion: "
        f"{result.post_delete_count} entries"
    )
    lines.append(f"entry count: {result.post_delete_count}")
    lines.append("-" * 70)

    if result.post_delete_count != 0:
        lines.append(
            "REFUSING TO PROCEED: store is non-empty after deletion. "
            f"Remaining paths: {[m.path for m in remaining]}"
        )
        lines.append("=" * 70)
        log_path.parent.mkdir(exist_ok=True)
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise RuntimeError(
            f"clear_memory_store: {result.post_delete_count} entries remain in "
            f"{memory_store_id} after deletion ({[m.path for m in remaining]}). "
            "Refusing to continue — see log at "
            f"{log_path}."
        )

    lines.append("")
    lines.append(f"DONE. {len(result.entries)} entries deleted; store itself not deleted.")
    lines.append("=" * 70)

    log_path.parent.mkdir(exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return result


def make_clear_log_path(runs_dir: Path = RUNS_DIR) -> Path:
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return runs_dir / f"memory-store-clearing-{timestamp}.log"


# --- Resumability --------------------------------------------------------


@dataclass
class ResumeState:
    completed: set[tuple[str, str, str, int]]  # (claim_slug, variant, pair_label, repetition)


def fetch_completed_runs() -> ResumeState:
    """Query retest_sessions for rows already present, keyed by the
    tuple that identifies a RunSpec (claim_slug, arm, pair_label,
    repetition) — session_id is not known ahead of a run, so it cannot
    be the resume key."""
    rows = fetchall_dict(
        "select claim_slug, arm, pair_label, repetition from retest_sessions"
    )
    completed = {
        (row["claim_slug"], row["arm"], row["pair_label"], row["repetition"]) for row in rows
    }
    return ResumeState(completed=completed)


def run_key(step: RunSpec) -> tuple[str, str, str, int]:
    return (step.claim_slug, step.variant, step.pair_label, step.repetition)


@dataclass
class PlannedStep:
    step: Step
    skip: bool = False
    skip_reason: str = ""


def plan_resume(sequence: list[Step], resume_state: ResumeState, force: bool) -> list[PlannedStep]:
    """Mark which RunSpecs in the sequence are already recorded and
    should be skipped. ClearSpecs are never skipped — they are cheap and
    idempotent (clearing an already-empty store is a no-op), and
    skipping one would risk leaving stale entries in front of a resumed
    memory_on run.

    A resumed run landing mid-chain is a problem: if resume would start
    at a memory-on claim 2 whose claim 1 is already recorded (but the
    memory_on claim 1 run is NOT in the completed set — i.e. claim 1 for
    this pair/repetition/variant hasn't actually run yet in this resume,
    only claim 2 would be attempted next), the store state may not match
    what the chain expects. That is reported and requires --force.
    """
    planned: list[PlannedStep] = []
    for step in sequence:
        if isinstance(step, ClearSpec):
            planned.append(PlannedStep(step=step))
            continue

        key = run_key(step)
        if key in resume_state.completed:
            planned.append(
                PlannedStep(
                    step=step,
                    skip=True,
                    skip_reason=f"already recorded in retest_sessions ({key})",
                )
            )
            continue

        if step.claim_position == 2:
            claim_1_key = None
            for other in sequence:
                if (
                    isinstance(other, RunSpec)
                    and other.variant == step.variant
                    and other.pair_label == step.pair_label
                    and other.repetition == step.repetition
                    and other.claim_position == 1
                ):
                    claim_1_key = run_key(other)
                    break
            claim_1_done = claim_1_key is not None and claim_1_key in resume_state.completed
            if claim_1_done:
                mid_chain_msg = (
                    f"resume would start at {step.variant} claim 2 "
                    f"({step.claim_slug}, pair {step.pair_label} rep {step.repetition}) "
                    "whose claim 1 is already recorded — Memory store state may not "
                    "match what this chain expects. Pass --force to proceed anyway."
                )
                if not force:
                    raise RuntimeError(mid_chain_msg)
                planned.append(
                    PlannedStep(
                        step=step,
                        skip=False,
                        skip_reason=f"--force override: {mid_chain_msg}",
                    )
                )
                continue

        planned.append(PlannedStep(step=step))

    return planned


# --- Subprocess invocation ------------------------------------------------


@dataclass
class RunOutcome:
    run: RunSpec
    exit_code: int
    elapsed_seconds: float
    stdout: str
    stderr: str


def invoke_run(run: RunSpec) -> RunOutcome:
    cmd = [
        sys.executable,
        "-m",
        LAUNCH_REVIEW_MODULE,
        "--claim-slug",
        run.claim_slug,
        "--variant",
        run.variant,
        "--claim-position",
        str(run.claim_position),
        "--pair-label",
        run.pair_label,
        "--repetition",
        str(run.repetition),
    ]
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    elapsed = time.monotonic() - start
    return RunOutcome(
        run=run,
        exit_code=proc.returncode,
        elapsed_seconds=elapsed,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


# --- Reporting -------------------------------------------------------------


def print_dry_run(sequence: list[Step], resume_state: ResumeState | None = None) -> None:
    print("=" * 70)
    print("DRY RUN — Week 19 retest harness sequence (24 runs, 6 clears)")
    print("=" * 70)
    print(format_sequence(sequence))
    print("=" * 70)
    print("No subprocess invoked, no Memory store touched.")


def print_run_result(index: int, total: int, outcome: RunOutcome) -> None:
    run = outcome.run
    print(
        f"[{index}/{total}] {run.claim_slug} variant={run.variant} "
        f"pair={run.pair_label} rep={run.repetition} "
        f"claim_position={run.claim_position} "
        f"exit_code={outcome.exit_code} elapsed={outcome.elapsed_seconds:.1f}s"
    )


def print_clear_result(clear: ClearResult, pair_label: str, repetition: int) -> None:
    print(
        f"CLEAR pair={pair_label} rep={repetition}: "
        f"{len(clear.entries)} entries deleted, post-delete count={clear.post_delete_count}"
    )
    for entry in clear.entries:
        print(f"    {entry.path}  sha256={entry.content_sha256}")
    print(f"    log: {clear.log_path}")


def print_final_table() -> None:
    rows = fetchall_dict(
        """
        select claim_slug, arm, pair_label, repetition, verdict,
               grading_result, manipulation_check
        from retest_sessions
        order by repetition, pair_label, arm desc, claim_slug
        """
    )
    print("=" * 70)
    print("FINAL TABLE — retest_sessions")
    print("=" * 70)
    header = (
        f"{'claim_slug':32s} {'arm':11s} {'pair':4s} {'rep':3s} "
        f"{'verdict':16s} {'grading':10s} {'manipulation_check':24s}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['claim_slug']:32s} {row['arm']:11s} {row['pair_label'] or '':4s} "
            f"{row['repetition']:<3d} {str(row['verdict']):16s} "
            f"{str(row['grading_result']):10s} {str(row['manipulation_check']):24s}"
        )


# --- Main ------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 19 retest harness.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the full 24-run sequence with clears in position; invoke nothing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Proceed even if resuming would start mid-chain at a memory_on "
        "claim 2 whose claim 1 is already recorded.",
    )
    args = parser.parse_args()

    sequence = build_sequence()

    if args.dry_run:
        print_dry_run(sequence)
        return

    resume_state = fetch_completed_runs()
    if resume_state.completed:
        print(f"Resuming: {len(resume_state.completed)} run(s) already recorded, will skip.")
        for key in sorted(resume_state.completed):
            print(f"  skip: claim_slug={key[0]} variant={key[1]} pair={key[2]} rep={key[3]}")
    else:
        print("No prior runs recorded — starting from scratch.")

    planned = plan_resume(sequence, resume_state, force=args.force)

    memory_store_id = get_memory_store_id()
    client = anthropic.Anthropic()

    total_runs = sum(1 for p in planned if isinstance(p.step, RunSpec))
    run_index = 0

    for planned_step in planned:
        step = planned_step.step

        if isinstance(step, ClearSpec):
            log_path = make_clear_log_path()
            operation_label = (
                f"Week 19 retest harness — pair {step.pair_label} rep {step.repetition} "
                "clear (memory_off half complete, about to start memory_on half)"
            )
            clear_result = clear_memory_store(client, memory_store_id, log_path, operation_label)
            print_clear_result(clear_result, step.pair_label, step.repetition)
            continue

        run_index += 1
        if planned_step.skip:
            print(f"[{run_index}/{total_runs}] SKIP {step.claim_slug} — {planned_step.skip_reason}")
            continue
        if planned_step.skip_reason:
            print(f"[{run_index}/{total_runs}] WARNING: {planned_step.skip_reason}")

        outcome = invoke_run(step)
        print_run_result(run_index, total_runs, outcome)

        if outcome.exit_code != 0:
            print("=" * 70, file=sys.stderr)
            print(
                f"HARNESS STOPPED: run {run_index}/{total_runs} failed "
                f"(claim_slug={step.claim_slug} variant={step.variant} "
                f"pair={step.pair_label} rep={step.repetition}) "
                f"exit_code={outcome.exit_code}",
                file=sys.stderr,
            )
            print("=" * 70, file=sys.stderr)
            print("--- stdout ---", file=sys.stderr)
            print(outcome.stdout, file=sys.stderr)
            print("--- stderr ---", file=sys.stderr)
            print(outcome.stderr, file=sys.stderr)
            sys.exit(1)

    print_final_table()


if __name__ == "__main__":
    main()
