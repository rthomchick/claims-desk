"""generate_variants.py — render review_agent_template.md into the two
committed prompt variants (Week 18 d7).

The template has exactly one conditional block, marked by MEMORY:ON and
MEMORY:OFF sentinel comment pairs. Rendering a variant means: keep the
sentinel'd content for that variant, drop the other variant's content and
both sentinel pairs entirely, and leave everything outside the sentinels
untouched. This is what makes `git diff` between the two generated files
a real drift check — anything outside the memory sections that differs
was not produced by this script.

Run from the repo root: python -m server.agents.generate_variants
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "review_agent_template.md"
OUTPUT_PATHS = {
    "ON": Path(__file__).parent / "review_agent_memory_on.md",
    "OFF": Path(__file__).parent / "review_agent_memory_off.md",
}

_BLOCK_RE = re.compile(
    r"<!--MEMORY:(ON|OFF):START-->\n(.*?)<!--MEMORY:\1:END-->\n?",
    re.DOTALL,
)


def render(template_text: str, keep: str) -> str:
    drop = "OFF" if keep == "ON" else "ON"

    def _replace(match: re.Match) -> str:
        variant, body = match.group(1), match.group(2)
        return body if variant == keep else ""

    rendered = _BLOCK_RE.sub(_replace, template_text)
    assert f"<!--MEMORY:{keep}:START-->" not in rendered
    assert f"<!--MEMORY:{drop}:START-->" not in rendered
    return rendered


def main() -> None:
    template_text = TEMPLATE_PATH.read_text()
    for variant, out_path in OUTPUT_PATHS.items():
        rendered = render(template_text, variant)
        out_path.write_text(rendered)
        print(f"wrote {out_path.relative_to(Path.cwd())} ({len(rendered)} chars)")


if __name__ == "__main__":
    main()
