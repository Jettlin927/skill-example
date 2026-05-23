#!/usr/bin/env python3
"""
Install or update the skill-design TL;DR block in a target file.

Behavior:
- Target does NOT exist           → create the file (and parent dirs) with just the block.
- Target exists, no markers       → append the block (preceded by a blank line).
- Target exists, has marker pair  → replace only the content between markers.

Outputs a JSON status object to stdout.

Usage:
    python3 install_tldr.py <target_path> <tldr_source_path>

Both paths can use ~ — they are expanded via pathlib.expanduser().
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


BEGIN_MARKER = "<!-- BEGIN skill-design-tldr · from github.com/Jettlin927/skill-example -->"
END_MARKER = "<!-- END skill-design-tldr -->"


def wrap(content: str) -> str:
    return f"{BEGIN_MARKER}\n{content.rstrip()}\n{END_MARKER}\n"


def install(target: Path, block: str) -> str:
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(block, encoding="utf-8")
        return "created"

    existing = target.read_text(encoding="utf-8")

    if BEGIN_MARKER in existing and END_MARKER in existing:
        start = existing.index(BEGIN_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        new = existing[:start] + block.rstrip() + existing[end:]
        target.write_text(new, encoding="utf-8")
        return "replaced"

    if existing.endswith("\n\n"):
        separator = ""
    elif existing.endswith("\n"):
        separator = "\n"
    else:
        separator = "\n\n"
    target.write_text(existing + separator + block, encoding="utf-8")
    return "appended"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(json.dumps({
            "ok": False,
            "error": "usage: install_tldr.py <target_path> <tldr_source_path>",
        }, ensure_ascii=False))
        return 2

    target = Path(argv[1]).expanduser()
    source = Path(argv[2]).expanduser()

    if not source.exists():
        print(json.dumps({
            "ok": False,
            "error": f"source not found: {source}",
        }, ensure_ascii=False))
        return 1

    tldr = source.read_text(encoding="utf-8")
    block = wrap(tldr)
    action = install(target, block)

    print(json.dumps({
        "ok": True,
        "action": action,
        "target": str(target.resolve()),
        "source": str(source.resolve()),
        "lines_in_block": block.count("\n"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
