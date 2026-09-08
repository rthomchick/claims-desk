"""generate_variants.py — render review_agent_template.md into the three
committed prompt variants (Week 18 d7; GUIDANCE axis added Week 21 for
Endpoint 2).

The template has two independent conditional axes:
  - MEMORY:ON / MEMORY:OFF     — sentinel'd blocks are line-anchored
    (start sentinel immediately followed by a newline, end sentinel
    immediately preceded by one, with the trailing newline consumed).
  - GUIDANCE:ON / GUIDANCE:OFF — sentinel'd blocks are inline (they open
    and close mid-line, wrapping clauses and sentences rather than whole
    paragraphs), so they are matched without requiring adjacent newlines.

Rendering a variant means: for each axis, keep the sentinel'd content for
that axis's selected side, drop the other side's content and both
sentinel pairs entirely, and leave everything outside the sentinels
untouched. This is what makes `git diff` between the generated files a
real drift check — anything outside the conditional sections that differs
was not produced by this script.

Run from the repo root: python -m server.agents.generate_variants
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "review_agent_template.md"

VARIANTS = {
    "memory_on": {"MEMORY": "ON", "GUIDANCE": "ON"},
    "memory_off": {"MEMORY": "OFF", "GUIDANCE": "ON"},
    "memory_off_stripped": {"MEMORY": "OFF", "GUIDANCE": "OFF"},
}

OUTPUT_PATHS = {
    name: Path(__file__).parent / f"review_agent_{name}.md" for name in VARIANTS
}

# MEMORY blocks are whole paragraphs: the sentinels sit alone on their own
# line, so the regex anchors to the surrounding newlines and consumes the
# trailing one along with the block.
_MEMORY_BLOCK_RE = re.compile(
    r"<!--MEMORY:(ON|OFF):START-->\n(.*?)<!--MEMORY:\1:END-->\n?",
    re.DOTALL,
)

# GUIDANCE blocks wrap inline clauses/sentences and can open or close
# mid-line, so no newline anchoring here.
_GUIDANCE_BLOCK_RE = re.compile(
    r"<!--GUIDANCE:(ON|OFF):START-->(.*?)<!--GUIDANCE:\1:END-->",
    re.DOTALL,
)


def _render_axis(text: str, pattern: re.Pattern, axis: str, keep: str) -> str:
    drop = "OFF" if keep == "ON" else "ON"

    def _replace(match: re.Match) -> str:
        side, body = match.group(1), match.group(2)
        return body if side == keep else ""

    rendered = pattern.sub(_replace, text)
    assert f"<!--{axis}:{keep}:START-->" not in rendered
    assert f"<!--{axis}:{drop}:START-->" not in rendered
    return rendered


def render(template_text: str, selection: dict[str, str]) -> str:
    rendered = _render_axis(template_text, _MEMORY_BLOCK_RE, "MEMORY", selection["MEMORY"])
    rendered = _render_axis(rendered, _GUIDANCE_BLOCK_RE, "GUIDANCE", selection["GUIDANCE"])
    return rendered


# The top-of-file HTML comment is unconditional provenance documentation
# about the generator/template relationship itself (which variants exist,
# which sentinel axes govern them) — it is not prompt content and carries
# no sentinels. Byte-identity checks below intentionally ignore it: only
# the rendered prompt body (from the first heading onward) is required to
# match the previously committed output.
_BODY_MARKER = "# Claims Review Agent"


def _body(text: str) -> str:
    idx = text.index(_BODY_MARKER)
    return text[idx:]


def main() -> None:
    template_text = TEMPLATE_PATH.read_text()

    rendered_by_name = {name: render(template_text, sel) for name, sel in VARIANTS.items()}

    for name in ("memory_on", "memory_off"):
        out_path = OUTPUT_PATHS[name]
        existing = out_path.read_text() if out_path.exists() else None
        if existing is not None and _body(existing) != _body(rendered_by_name[name]):
            raise SystemExit(
                f"{out_path.name}'s prompt body would change but must "
                "regenerate byte-identical to its committed body "
                "(header comment excluded). Aborting without writing any "
                "file."
            )

    for name, rendered in rendered_by_name.items():
        out_path = OUTPUT_PATHS[name]
        out_path.write_text(rendered)
        print(f"wrote {out_path.relative_to(Path.cwd())} ({len(rendered)} chars)")


if __name__ == "__main__":
    main()
